import os
import shutil
from datetime import datetime

def log_message(message: str, level: str = "INFO"):
    """Log messages with timestamps and levels."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{level}] {timestamp} — {message}")

def create_folders(base_path: str, categories: dict):
    """Create categorized folders if they don't exist."""
    for folder in categories.keys():
        folder_dir = os.path.join(base_path, folder)
        if not os.path.exists(folder_dir):
            os.mkdir(folder_dir)
            log_message(f"Created folder: {folder_dir}", "SETUP")

def get_category(file_name: str, categories: dict) -> str:
    """Determine which category the file belongs to."""
    ext = os.path.splitext(file_name)[1].lower()
    for category, extensions in categories.items():
        if ext in extensions:
            return category
    return "Others"

def organize_folder(folder_path: str):
    """Organize files in the given folder into categorized subfolders."""

    # --- 1️⃣ Input Validation ---
    if not os.path.exists(folder_path):
        log_message("Error: Folder path does not exist!", "ERROR")
        return

    if not os.path.isdir(folder_path):
        log_message("Error: Provided path is not a folder!", "ERROR")
        return

    # --- 2️⃣ File Type Definitions ---
    file_types = {
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
        "Documents": [".pdf", ".docx", ".doc", ".txt", ".xls", ".xlsx", ".pptx"],
        "Videos": [".mp4", ".mkv", ".mov", ".avi"],
        "Music": [".mp3", ".wav", ".aac"],
        "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
        "Programs": [".exe", ".msi", ".bat"],
        "Scripts": [".py", ".js", ".html", ".css"],
        "Others": []
    }

    # --- 3️⃣ Create Folders ---
    create_folders(folder_path, file_types)
    log_message("Folders verified and ready.", "INFO")

    # --- 4️⃣ File Processing ---
    total_files = 0
    organized_files = 0

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        if os.path.isfile(file_path):
            total_files += 1
            category = get_category(file_name, file_types)
            destination = os.path.join(folder_path, category, file_name)

            try:
                shutil.move(file_path, destination)
                organized_files += 1
                log_message(f"Moved: {file_name} → {category}", "SUCCESS")
            except PermissionError:
                log_message(f"Permission denied for file: {file_name}", "WARNING")
            except Exception as e:
                log_message(f"Unexpected error moving '{file_name}': {e}", "ERROR")

    # --- 5️⃣ Summary ---
    log_message(f"Organized {organized_files}/{total_files} files successfully.", "INFO")
    log_message("🎉 File organization complete!", "DONE")

def main():
    """Main entry point of the program."""
    print("📁 Welcome to FileMaster Organizer!")
    print("💡 Tip: Use full folder path like C:/Users/YourName/Desktop/MyFolder\n")

    folder_input = input("Enter the folder path to organize: ").strip('"')

    if not folder_input:
        log_message("No folder path provided. Exiting program.", "ERROR")
        return

    organize_folder(folder_input)

if __name__ == "__main__":
    main()
