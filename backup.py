import os
import psutil
import shutil
import zipfile
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from datetime import datetime
import threading
import schedule
import time

# Global variables
backup_thread = None
backup_cancelled = False

def get_available_drives():
    """Detect available drives on Windows and Linux."""
    drives = []
    if os.name == 'nt':  # Windows
        from string import ascii_uppercase
        drives = [f"{d}:/" for d in ascii_uppercase if os.path.exists(f"{d}:/")]
    else:  # Linux/Mac
        partitions = psutil.disk_partitions()
        drives = [p.mountpoint for p in partitions]
    return drives

def zip_directory(source_dir, zip_path, progress_bar, progress_label):
    """Compress an entire directory into a ZIP file with a progress bar."""
    global backup_cancelled
    try:
        file_list = []
        for root, _, files in os.walk(source_dir):
            for file in files:
                file_list.append(os.path.join(root, file))
        
        total_files = len(file_list)
        if total_files == 0:
            messagebox.showwarning("Warning", "No files found in the selected drive.")
            return False
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for i, file in enumerate(file_list):
                if backup_cancelled:
                    messagebox.showinfo("Backup Cancelled", "Backup process was cancelled.")
                    return False
                
                arcname = os.path.relpath(file, source_dir)
                zipf.write(file, arcname)
                
                progress = int((i + 1) / total_files * 100)
                progress_bar["value"] = progress
                progress_label.config(text=f"Progress: {progress}%")
                root.update_idletasks()
        
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create ZIP: {e}")
        return False

def backup_drive(drive, destination_folder, progress_bar, progress_label):
    """Clone an entire drive and create a ZIP backup."""
    global backup_cancelled
    backup_cancelled = False  # Reset cancel flag

    backup_folder = os.path.join(destination_folder, f"Backup_{os.path.basename(drive).strip('/')}_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    
    try:
        shutil.copytree(drive, backup_folder)
    except PermissionError:
        messagebox.showerror("Error", f"Permission Denied: Cannot access {drive}")
        return
    except Exception as e:
        messagebox.showerror("Error", f"Error copying {drive}: {e}")
        return

    zip_path = backup_folder + ".zip"

    if zip_directory(backup_folder, zip_path, progress_bar, progress_label):
        shutil.rmtree(backup_folder)
        messagebox.showinfo("Backup Completed", f"Backup saved as {zip_path}")

def start_backup():
    """Start the backup process in a new thread."""
    global backup_thread
    selected_drives = [drive for drive, var in checkboxes.items() if var.get()]
    
    if not selected_drives:
        messagebox.showwarning("Warning", "Please select at least one drive to back up.")
        return

    destination_folder = filedialog.askdirectory(title="Select Backup Location")
    if not destination_folder:
        messagebox.showwarning("Warning", "Please select a destination folder for backup.")
        return

    progress_bar["value"] = 0
    progress_label.config(text="Starting backup...")

    backup_thread = threading.Thread(target=lambda: [backup_drive(drive, destination_folder, progress_bar, progress_label) for drive in selected_drives])
    backup_thread.start()

def cancel_backup():
    """Cancel the ongoing backup process."""
    global backup_cancelled
    backup_cancelled = True

def schedule_backup():
    """Schedule the backup at a user-defined interval."""
    interval = schedule_var.get()
    
    if interval == "Daily":
        schedule.every().day.at("02:00").do(start_backup)
    elif interval == "Weekly":
        schedule.every().monday.at("02:00").do(start_backup)
    elif interval == "Monthly":
        schedule.every(30).days.at("02:00").do(start_backup)
    else:
        messagebox.showwarning("Warning", "Please select a valid backup frequency.")
        return

    messagebox.showinfo("Scheduled", f"Backup scheduled: {interval}")
    
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)

    threading.Thread(target=run_scheduler, daemon=True).start()

# GUI Setup
root = tk.Tk()
root.title("Drive Backup Tool")
root.geometry("400x450")
root.configure(bg="#2c3e50")

tk.Label(root, text="Select Drives to Backup:", font=("Arial", 12, "bold"), fg="white", bg="#2c3e50").pack(pady=10)

checkboxes = {}
available_drives = get_available_drives()

frame = tk.Frame(root, bg="#2c3e50")
frame.pack()

for drive in available_drives:
    var = tk.BooleanVar()
    checkboxes[drive] = var
    tk.Checkbutton(frame, text=drive, variable=var, font=("Arial", 10), bg="#34495e", fg="white", selectcolor="#2c3e50").pack(anchor="w")

tk.Button(root, text="Start Backup", command=start_backup, font=("Arial", 12, "bold"), bg="#27ae60", fg="white").pack(pady=10)
tk.Button(root, text="Cancel Backup", command=cancel_backup, font=("Arial", 12, "bold"), bg="#c0392b", fg="white").pack(pady=10)

progress_label = tk.Label(root, text="Progress: 0%", font=("Arial", 10), fg="white", bg="#2c3e50")
progress_label.pack()

progress_bar = ttk.Progressbar(root, length=300, mode="determinate")
progress_bar.pack(pady=10)

schedule_var = tk.StringVar(root)
schedule_var.set("Select Backup Frequency")
schedule_menu = tk.OptionMenu(root, schedule_var, "Daily", "Weekly", "Monthly")
schedule_menu.pack(pady=5)

tk.Button(root, text="Schedule Backup", command=schedule_backup, font=("Arial", 12, "bold"), bg="#2980b9", fg="white").pack(pady=5)

root.mainloop()
