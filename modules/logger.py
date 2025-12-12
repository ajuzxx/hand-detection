import csv
import os
import pandas as pd
from datetime import datetime
import cv2
import config

class LoggerService:
    def __init__(self):
        self._ensure_files_exist()

    def _ensure_files_exist(self):
        if not os.path.exists(config.EVIDENCE_FOLDER):
            os.makedirs(config.EVIDENCE_FOLDER)

    def log_incident(self, student_id, event, duration, severity, evidence_file="N/A"):
        file_exists = os.path.isfile(config.CSV_FILE)
        
        with open(config.CSV_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists: 
                writer.writerow(["student_id", "timestamp", "event", "duration", "severity", "evidence_image"])
            
            writer.writerow([
                student_id, 
                datetime.now().strftime("%H:%M:%S"), 
                event, 
                f"{duration:.2f}", 
                severity, 
                evidence_file
            ])

    def save_evidence(self, frame, student_id, event):
        fname = f"{student_id}_{event}_{datetime.now().strftime('%M%S')}.jpg"
        path = os.path.join(config.EVIDENCE_FOLDER, fname)
        cv2.imwrite(path, frame)
        return fname

    def get_recent_logs(self, limit=15):
        if os.path.exists(config.CSV_FILE):
            try:
                df = pd.read_csv(config.CSV_FILE)
                if not df.empty:
                    return df.tail(limit).iloc[::-1] # Return reversed
            except:
                pass
        return pd.DataFrame()