import os
import shutil
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import time
import psutil

# Global variables
backup_thread = None
backup_cancelled = False
backup_paused = threading.Event()
backup_paused.set()

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

# Handle permission errors
def remove_readonly(func, path, _):
    """Clears read-only attributes and retries deletion."""
    import stat
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception as e:
        print(f"Failed to remove {path}: {e}")

# Zip directory with progress tracking
def zip_directory(source_dir, zip_path):
    global backup_cancelled
    try:
        file_list = [os.path.join(root, file) for root, _, files in os.walk(source_dir) for file in files]
        total_files = len(file_list)
        if total_files == 0:
            messagebox.showwarning("Warning", "No files found for backup.")
            return False

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for i, file in enumerate(file_list):
                while not backup_paused.is_set():
                    time.sleep(0.5)  # Wait while paused

                if backup_cancelled:
                    messagebox.showinfo("Backup Cancelled", "Backup process was cancelled.")
                    return False

                arcname = os.path.relpath(file, source_dir)
                zipf.write(file, arcname)

                progress = int((i + 1) / total_files * 100)
                root.after(0, update_progress, progress)

        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create ZIP: {e}")
        return False

# Update progress bar safely
def update_progress(progress):
    progress_bar["value"] = progress
    progress_label.config(text=f"Progress: {progress}%")

# Start backup process
def start_backup():
    global backup_thread, backup_cancelled
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
    backup_cancelled = False  
    backup_paused.set()  # Ensure it's running

    backup_thread = threading.Thread(target=backup_selected_items, args=(selected_items, destination_folder))
    backup_thread.start()

# Backup selected drives or folders
def backup_selected_items(selected_items, destination_folder):
    global backup_cancelled

    for item in selected_items:
        if backup_cancelled:
            return

        safe_name = os.path.basename(item).strip('/\\').replace(":", "_")
        backup_folder = os.path.join(destination_folder, f"Backup_{safe_name}")

        try:
            shutil.copytree(item, backup_folder)
        except PermissionError:
            messagebox.showerror("Error", f"Permission Denied: Cannot access {item}")
            continue
        except Exception as e:
            messagebox.showerror("Error", f"Error copying {item}: {e}")
            continue

        zip_path = backup_folder + ".zip"

        if zip_directory(backup_folder, zip_path):
            shutil.rmtree(backup_folder, onerror=remove_readonly)
            messagebox.showinfo("Backup Completed", f"Backup saved as {zip_path}")

# Cancel backup process
def cancel_backup():
    global backup_cancelled
    backup_cancelled = True
    backup_paused.set()

# Pause or resume backup process
def toggle_pause():
    if backup_paused.is_set():
        backup_paused.clear()
        pause_button.config(text="Resume")
    else:
        backup_paused.set()
        pause_button.config(text="Pause")

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
root.geometry("500x450")
root.configure(bg="#2c3e50")

tk.Label(root, text="Select Drives to Backup:", font=("Arial", 10, "bold"), fg="white", bg="#2c3e50").pack(pady=5)

checkboxes = {}
available_drives = get_available_drives()
frame = tk.Frame(root, bg="#2c3e50")
frame.pack()

for drive in available_drives:
    var = tk.BooleanVar()
    checkboxes[drive] = var
    tk.Checkbutton(frame, text=drive, variable=var, font=("Arial", 9), bg="#34495e", fg="white", selectcolor="#2c3e50").pack(anchor="w")

tk.Label(root, text="Select Folders to Backup:", font=("Arial", 10, "bold"), fg="white", bg="#2c3e50").pack(pady=5)

folder_list = []
folder_display = tk.Listbox(root, height=4, width=50, bg="#ecf0f1", font=("Arial", 9))
folder_display.pack(pady=5)

folder_button_frame = tk.Frame(root, bg="#2c3e50")
folder_button_frame.pack(pady=2)

tk.Button(folder_button_frame, text="Add Folder", command=add_folder, font=("Arial", 9), bg="#3498db", fg="white").grid(row=0, column=0, padx=5)
tk.Button(folder_button_frame, text="Remove", command=remove_selected_folder, font=("Arial", 9), bg="#e74c3c", fg="white").grid(row=0, column=1, padx=5)

button_frame = tk.Frame(root, bg="#2c3e50")
button_frame.pack(pady=10)

start_button = tk.Button(button_frame, text="Start Backup", command=start_backup, font=("Arial", 10, "bold"), bg="#27ae60", fg="white")
start_button.grid(row=0, column=0, padx=5)

pause_button = tk.Button(button_frame, text="Pause", command=toggle_pause, font=("Arial", 10, "bold"), bg="#f39c12", fg="white")
pause_button.grid(row=0, column=1, padx=5)

cancel_button = tk.Button(button_frame, text="Cancel", command=cancel_backup, font=("Arial", 10, "bold"), bg="#c0392b", fg="white")
cancel_button.grid(row=0, column=2, padx=5)

progress_label = tk.Label(root, text="Progress: 0%", font=("Arial", 10), fg="white", bg="#2c3e50")
progress_label.pack()

progress_bar = ttk.Progressbar(root, length=400, mode="determinate")
progress_bar.pack(pady=10)

root.mainloop()
