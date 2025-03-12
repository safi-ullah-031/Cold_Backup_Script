import os
import psutil

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

if __name__ == "__main__":
    available_drives = get_available_drives()
    print("Available Drives:", available_drives)
