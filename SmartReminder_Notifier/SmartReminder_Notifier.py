from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime, timezone
import threading
import time

# =============================================================
# App metadata / initialization
# =============================================================
app = FastAPI(
    title="SmartReminder Notifier",
    version="1.2.0",
    description="A lightweight reminder API with a background checker that triggers reminders at the scheduled time."
)

# =============================================================
# Models
# =============================================================
class Reminder(BaseModel):
    """
    Reminder model representing a scheduled reminder.
    `remind_at` must be a future datetime when creating a reminder.
    """
    id: int = Field(..., description="Unique reminder ID")
    title: str = Field(..., min_length=1, description="Short title for the reminder")
    message: str = Field(..., min_length=1, description="Detailed message for the reminder")
    remind_at: datetime = Field(..., description="Datetime when the reminder should trigger (UTC/local)")

    # ✅ Updated for Pydantic v2 and timezone-safe validation
    @field_validator("remind_at")
    @classmethod
    def remind_at_must_be_future(cls, v: datetime):
        now = datetime.now(timezone.utc)
        # If the given datetime has no timezone, assume UTC
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        if v <= now:
            raise ValueError("remind_at must be a future datetime (UTC).")
        return v


# =============================================================
# In-memory "database"
# =============================================================
reminders_db: List[Reminder] = []


# =============================================================
# Utilities & Helpers
# =============================================================
def log(msg: str) -> None:
    """Simple timestamped logger for debugging and audit purposes."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


def find_reminder(reminder_id: int) -> Optional[Reminder]:
    """Return a reminder by ID or None if not found."""
    for r in reminders_db:
        if r.id == reminder_id:
            return r
    return None


# =============================================================
# Background reminder checker (runs in a daemon thread)
# =============================================================
def reminder_checker(stop_event: threading.Event):
    """
    Background loop that checks for due reminders every 10 seconds.
    When a reminder's time has come, it prints a notification and removes it.
    """
    log("Reminder checker thread started.")
    while not stop_event.is_set():
        now = datetime.now(timezone.utc)
        for reminder in reminders_db[:]:  # Safe iteration over copy
            try:
                # Convert reminder.remind_at to UTC if not set
                remind_time = reminder.remind_at
                if remind_time.tzinfo is None:
                    remind_time = remind_time.replace(tzinfo=timezone.utc)

                if now >= remind_time:
                    log(f"🔔 Reminder Triggered — ID:{reminder.id} | Title:'{reminder.title}' | Message:'{reminder.message}'")
                    reminders_db.remove(reminder)
            except Exception as e:
                log(f"⚠️ Error while processing reminder ID {reminder.id}: {e}")
        stop_event.wait(10)
    log("Reminder checker thread stopping.")


# Start background thread
_stop_event = threading.Event()
_thread = threading.Thread(target=reminder_checker, args=(_stop_event,), daemon=True)
_thread.start()


# =============================================================
# Routes / Endpoints
# =============================================================

@app.get("/", tags=["Home"])
def home():
    """API root - basic info and usage hint."""
    log("Home endpoint accessed.")
    return {
        "status": "ok",
        "message": "Welcome to SmartReminder Notifier",
        "hint": "Use POST /reminders to schedule a reminder."
    }


@app.post("/reminders", response_model=Reminder, status_code=status.HTTP_201_CREATED, tags=["Reminders"])
def create_reminder(reminder: Reminder):
    """Create a new reminder."""
    if find_reminder(reminder.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Reminder ID {reminder.id} already exists. Use a unique ID."
        )

    reminders_db.append(reminder)
    log(f"✅ Created reminder ID:{reminder.id} | Title:'{reminder.title}' | RemindAt:{reminder.remind_at}")
    return reminder


@app.get("/reminders", response_model=List[Reminder], tags=["Reminders"])
def list_reminders():
    """Return a list of scheduled reminders."""
    log("Listed all reminders.")
    return reminders_db


@app.get("/reminders/{reminder_id}", response_model=Reminder, tags=["Reminders"])
def get_reminder(reminder_id: int):
    """Fetch a reminder by its ID."""
    r = find_reminder(reminder_id)
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Reminder ID {reminder_id} not found.")
    log(f"Fetched reminder ID:{reminder_id}")
    return r


@app.delete("/reminders/{reminder_id}", response_model=dict, tags=["Reminders"])
def delete_reminder(reminder_id: int):
    """Delete a scheduled reminder by ID."""
    r = find_reminder(reminder_id)
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Reminder ID {reminder_id} not found.")
    reminders_db.remove(r)
    log(f"🗑️ Deleted reminder ID:{reminder_id} | Title:'{r.title}'")
    return {"status": "success", "message": f"Reminder '{r.title}' deleted successfully."}


# =============================================================
# Notes
# =============================================================
# - Fully Pydantic v2 compatible (uses @field_validator)
# - Timezone-safe (uses datetime.now(timezone.utc))
# - Background thread handles reminders automatically
# - Uses in-memory DB (for demo only)
# =============================================================
