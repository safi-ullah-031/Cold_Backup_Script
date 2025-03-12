import os
import psutil
import shutil
import zipfile
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import threading

# Global variables
backup_thread = None
backup_cancelled = False

# Detect available drives
def get_available_drives():
    drives = []
    if os.name == 'nt':  # Windows
        from string import ascii_uppercase
        drives = [f"{d}:/" for d in ascii_uppercase if os.path.exists(f"{d}:/")]
    else:  # Linux/Mac
        partitions = psutil.disk_partitions()
        drives = [p.mountpoint for p in partitions]
    return drives

# Zip directory with progress tracking
def zip_directory(source_dir, zip_path, progress_bar, progress_label):
    global backup_cancelled
    try:
        file_list = []
        for root, _, files in os.walk(source_dir):
            for file in files:
                file_list.append(os.path.join(root, file))
        
        total_files = len(file_list)
        if total_files == 0:
            messagebox.showwarning("Warning", "No files found for backup.")
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

# Start backup process
def start_backup():
    global backup_thread
    selected_items = [drive for drive, var in checkboxes.items() if var.get()] + folder_list

    if not selected_items:
        messagebox.showwarning("Warning", "Please select at least one drive or folder to back up.")
        return

    destination_folder = filedialog.askdirectory(title="Select Backup Location")
    if not destination_folder:
        messagebox.showwarning("Warning", "Please select a destination folder for backup.")
        return

    progress_bar["value"] = 0
    progress_label.config(text="Starting backup...")

    backup_thread = threading.Thread(target=lambda: backup_selected_items(selected_items, destination_folder))
    backup_thread.start()

# Backup selected drives or folders
def backup_selected_items(selected_items, destination_folder):
    global backup_cancelled
    backup_cancelled = False  

    for item in selected_items:
        backup_folder = os.path.join(destination_folder, f"Backup_{os.path.basename(item).strip('/')}")

        try:
            shutil.copytree(item, backup_folder)
        except PermissionError:
            messagebox.showerror("Error", f"Permission Denied: Cannot access {item}")
            continue
        except Exception as e:
            messagebox.showerror("Error", f"Error copying {item}: {e}")
            continue

        zip_path = backup_folder + ".zip"

        if zip_directory(backup_folder, zip_path, progress_bar, progress_label):
            shutil.rmtree(backup_folder)
            messagebox.showinfo("Backup Completed", f"Backup saved as {zip_path}")

# Cancel backup process
def cancel_backup():
    global backup_cancelled
    backup_cancelled = True

# Select a folder for backup
def add_folder():
    folder_path = filedialog.askdirectory(title="Select a Folder to Backup")
    if folder_path:
        folder_list.append(folder_path)
        folder_display.insert(tk.END, folder_path)

# Remove selected folder from the list
def remove_selected_folder():
    selected_index = folder_display.curselection()
    if selected_index:
        folder_list.pop(selected_index[0])
        folder_display.delete(selected_index)

# GUI Setup
root = tk.Tk()
root.title("Drive & Folder Backup Tool")
root.geometry("500x500")
root.configure(bg="#2c3e50")

tk.Label(root, text="Select Drives to Backup:", font=("Arial", 12, "bold"), fg="white", bg="#2c3e50").pack(pady=5)

checkboxes = {}
available_drives = get_available_drives()
frame = tk.Frame(root, bg="#2c3e50")
frame.pack()

for drive in available_drives:
    var = tk.BooleanVar()
    checkboxes[drive] = var
    tk.Checkbutton(frame, text=drive, variable=var, font=("Arial", 10), bg="#34495e", fg="white", selectcolor="#2c3e50").pack(anchor="w")

tk.Label(root, text="Select Folders to Backup:", font=("Arial", 12, "bold"), fg="white", bg="#2c3e50").pack(pady=5)

folder_list = []
folder_display = tk.Listbox(root, height=4, width=50, bg="#ecf0f1", font=("Arial", 10))
folder_display.pack(pady=5)

tk.Button(root, text="Add Folder", command=add_folder, font=("Arial", 10), bg="#3498db", fg="white").pack(pady=2)
tk.Button(root, text="Remove Selected", command=remove_selected_folder, font=("Arial", 10), bg="#e74c3c", fg="white").pack(pady=2)

tk.Button(root, text="Start Backup", command=start_backup, font=("Arial", 12, "bold"), bg="#27ae60", fg="white").pack(pady=10)
tk.Button(root, text="Cancel Backup", command=cancel_backup, font=("Arial", 12, "bold"), bg="#c0392b", fg="white").pack(pady=10)

progress_label = tk.Label(root, text="Progress: 0%", font=("Arial", 10), fg="white", bg="#2c3e50")
progress_label.pack()

progress_bar = ttk.Progressbar(root, length=400, mode="determinate")
progress_bar.pack(pady=10)

root.mainloop()
