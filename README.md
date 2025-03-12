# **Cold Backup Script**  

A Python script to create a local backup of an existing drive and store it in a selected destination drive.
## **Features**  
✅ Detects available drives automatically.  
✅ Creates a backup of selected folders or the entire drive.  
✅ Supports ZIP compression to save space.  
✅ Allows storing backups on an external or secondary drive.  
✅ Can be scheduled for automated backups.  
✅ Logs errors and backup status for reliability.  

## **Installation**  
1. **Clone this repository:**  
   ```bash
   git clone https://github.com/safi-ullah-031/cold-backup.git
   cd cold-backup
   ```
2. **Install dependencies (if needed):**  
   ```bash
   pip install -r requirements.txt
   ```

## **Usage**  
Run the script to start the backup process:  
```bash
python backup.py
```

## **Configuration**  
Modify the `config.json` file to:  
- Choose the source drive (`C:\`, `D:\`, etc.).  
- Set the backup destination drive.  
- Enable or disable ZIP compression.  

## **Future Improvements**  
- Incremental backups (only new/modified files).  
- Cloud storage support (Google Drive, OneDrive, etc.).  
- GUI interface for easier use.  

---