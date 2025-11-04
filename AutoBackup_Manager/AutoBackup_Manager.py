import os
import shutil
import time
import threading
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, validator

# =============================================================
# App metadata / initialization
# =============================================================
app = FastAPI(
    title="AutoBackup Manager",
    version="1.2.0",
    description="A lightweight auto-backup API. Start/stop scheduled copying of files from a source folder to a backup folder."
)

# =============================================================
# Models
# =============================================================
class BackupConfig(BaseModel):
    """
    Configuration model for the auto-backup service.
    """
    source_folder: str = Field(..., description="Folder path to copy files FROM")
    backup_folder: str = Field(..., description="Folder path to copy files TO")
    interval_minutes: int = Field(..., gt=0, description="Backup interval in minutes (must be > 0)")

    @validator("source_folder", "backup_folder")
    def strip_quotes_and_whitespace(cls, v: str) -> str:
        # Accept paths with or without surrounding quotes and strip whitespace
        return v.strip().strip('"').strip("'")

# =============================================================
# Global state (kept simple for demo purposes)
# =============================================================
_current_config: Optional[BackupConfig] = None
_backup_thread: Optional[threading.Thread] = None
_stop_event = threading.Event()
_thread_lock = threading.Lock()  # prevent race conditions when starting/stopping


# =============================================================
# Helpers / Utilities
# =============================================================
def log(message: str) -> None:
    """Simple timestamped logger for console output."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {message}")


def safe_copy_file(src_path: str, dest_path: str) -> None:
    """
    Copy a file from src_path to dest_path safely, preserving metadata.
    Errors are logged but do not stop the backup process.
    """
    try:
        shutil.copy2(src_path, dest_path)
        log(f"Copied: {src_path} → {dest_path}")
    except PermissionError:
        log(f"Permission denied when copying: {src_path}")
    except Exception as e:
        log(f"Unexpected error copying '{src_path}': {e}")


def run_backup_loop(config_getter, stop_event: threading.Event):
    """
    Background loop that periodically copies files according to the current config.
    `config_getter` is a callable that returns the current BackupConfig or None.
    """
    log("Backup thread started.")
    while not stop_event.is_set():
        config = config_getter()
        if config:
            src = os.path.abspath(config.source_folder)
            dst = os.path.abspath(config.backup_folder)
            interval = max(1, config.interval_minutes)  # safety: at least 1 minute

            if os.path.exists(src) and os.path.isdir(src):
                try:
                    if not os.path.exists(dst):
                        os.makedirs(dst, exist_ok=True)
                        log(f"Created backup folder: {dst}")

                    # Copy each file (non-recursive). Directories are ignored.
                    for filename in os.listdir(src):
                        src_path = os.path.join(src, filename)
                        dest_path = os.path.join(dst, filename)
                        if os.path.isfile(src_path):
                            safe_copy_file(src_path, dest_path)

                    log(f"✅ Backup completed from '{src}' → '{dst}'")
                except Exception as e:
                    log(f"❌ Backup error: {e}")
            else:
                log(f"Source folder not found or not a directory: {src}")

            # Wait for the configured interval (in seconds) or until stop event
            stop_event.wait(interval * 60)
        else:
            # No config set — wait a short while and check again
            stop_event.wait(5)
    log("Backup thread stopping.")


def get_current_config_copy() -> Optional[BackupConfig]:
    """Return a shallow copy of _current_config to safely use in background thread."""
    global _current_config
    return _current_config  # BackupConfig is immutable-like for our use; fine to return directly


# =============================================================
# Routes / Endpoints
# =============================================================
@app.get("/", tags=["Home"])
def home():
    """Root endpoint — simple service info."""
    return {
        "status": "ok",
        "message": "AutoBackup Manager is ready.",
        "note": "Use POST /start-backup to begin periodic backups and POST /stop-backup to stop them."
    }


@app.post("/start-backup", status_code=status.HTTP_200_OK, tags=["Backup"])
def start_backup(config: BackupConfig):
    """
    Start the background auto-backup process using the provided configuration.
    If a backup is already running, returns a 409 Conflict error.
    """
    global _current_config, _backup_thread, _stop_event

    with _thread_lock:
        if _backup_thread and _backup_thread.is_alive():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A backup process is already running. Stop it before starting a new one."
            )

        # Validate source folder existence
        if not os.path.exists(config.source_folder) or not os.path.isdir(config.source_folder):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Source folder does not exist or is not a directory: {config.source_folder}"
            )

        # Ensure backup folder path is writable (try to create if missing)
        try:
            os.makedirs(config.backup_folder, exist_ok=True)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unable to create/access backup folder: {config.backup_folder}. Error: {e}"
            )

        # Set new config and start thread
        _current_config = config
        _stop_event.clear()
        _backup_thread = threading.Thread(target=run_backup_loop, args=(get_current_config_copy, _stop_event), daemon=True)
        _backup_thread.start()

        log(f"Backup started with interval {config.interval_minutes} minute(s) — from '{config.source_folder}' to '{config.backup_folder}'")
        return {
            "status": "running",
            "message": f"Backup started every {config.interval_minutes} minute(s).",
            "source": os.path.abspath(config.source_folder),
            "backup": os.path.abspath(config.backup_folder),
            "interval_minutes": config.interval_minutes
        }


@app.post("/stop-backup", status_code=status.HTTP_200_OK, tags=["Backup"])
def stop_backup_process():
    """
    Stop the running backup process. Safe to call even if no process is running.
    """
    global _stop_event, _backup_thread, _current_config

    with _thread_lock:
        if not (_backup_thread and _backup_thread.is_alive()):
            return {"status": "stopped", "message": "No backup process was running."}

        _stop_event.set()
        # Wait briefly for thread to stop (non-blocking in typical use)
        _backup_thread.join(timeout=5)

        # Clear thread and config
        _backup_thread = None
        _current_config = None
        log("Backup process stopped by user request.")
        return {"status": "stopped", "message": "Backup process stopped successfully."}


@app.get("/status", status_code=status.HTTP_200_OK, tags=["Backup"])
def get_status():
    """
    Report the current status of the backup service.
    Returns whether running, the config, and a friendly timestamp.
    """
    if _backup_thread and _backup_thread.is_alive() and _current_config:
        return {
            "status": "running",
            "source": os.path.abspath(_current_config.source_folder),
            "backup": os.path.abspath(_current_config.backup_folder),
            "interval_minutes": _current_config.interval_minutes,
            "started_at": _current_config.__dict__.get("started_at", "unknown"),
            "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    return {
        "status": "stopped",
        "message": "No active backup process.",
        "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


# =============================================================
# Developer Notes
# - This implementation uses an in-memory config and a background thread.
# - For production use consider a more robust scheduler (APScheduler) and persistent storage.
# - The background thread is a daemon and will stop when the server process exits.
# =============================================================
