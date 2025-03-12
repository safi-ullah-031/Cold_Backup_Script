import os
import psutil
import tkinter as tk
from tkinter import messagebox, filedialog

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

    # Placeholder for backup logic
    messagebox.showinfo("Backup Started", f"Backing up {', '.join(selected_drives)} to {destination_folder}...")
    
    # Call the backup function (to be implemented in the next step)
    # backup_drives(selected_drives, destination_folder)

# GUI Setup
root = tk.Tk()
root.title("Drive Backup Tool")
root.geometry("400x300")
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
