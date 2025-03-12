import os
import psutil
import shutil
import zipfile
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime

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

def zip_directory(source_dir, zip_path):
    """Compress an entire directory into a ZIP file."""
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, arcname)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create ZIP: {e}")
        return False

def backup_drive(drive, destination_folder):
    """Clone an entire drive and create a ZIP backup."""
    backup_folder = os.path.join(destination_folder, f"Backup_{os.path.basename(drive).strip('/')}_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    
    # Copy the entire drive to a temporary backup folder
    try:
        shutil.copytree(drive, backup_folder)
    except PermissionError:
        messagebox.showerror("Error", f"Permission Denied: Cannot access {drive}")
        return
    except Exception as e:
        messagebox.showerror("Error", f"Error copying {drive}: {e}")
        return

    # Create a ZIP file from the copied drive
    zip_path = backup_folder + ".zip"
    if zip_directory(backup_folder, zip_path):
        shutil.rmtree(backup_folder)  # Remove temporary copied folder after zipping
        messagebox.showinfo("Backup Completed", f"Backup saved as {zip_path}")

def start_backup():
    """Start the backup process when the user clicks the button."""
    selected_drives = [drive for drive, var in checkboxes.items() if var.get()]
    
    if not selected_drives:
        messagebox.showwarning("Warning", "Please select at least one drive to back up.")
        return

    destination_folder = filedialog.askdirectory(title="Select Backup Location")
    if not destination_folder:
        messagebox.showwarning("Warning", "Please select a destination folder for backup.")
        return

    for drive in selected_drives:
        backup_drive(drive, destination_folder)

# GUI Setup
root = tk.Tk()
root.title("Drive Backup Tool")
root.geometry("400x350")
root.configure(bg="#2c3e50")

tk.Label(root, text="Select Drives to Backup:", font=("Arial", 12, "bold"), fg="white", bg="#2c3e50").pack(pady=10)

# Checkbox List
checkboxes = {}
available_drives = get_available_drives()

frame = tk.Frame(root, bg="#2c3e50")
frame.pack()

for drive in available_drives:
    var = tk.BooleanVar()
    checkboxes[drive] = var
    tk.Checkbutton(frame, text=drive, variable=var, font=("Arial", 10), bg="#34495e", fg="white", selectcolor="#2c3e50").pack(anchor="w")

# Backup Button
tk.Button(root, text="Start Backup", command=start_backup, font=("Arial", 12, "bold"), bg="#27ae60", fg="white").pack(pady=20)

root.mainloop()
