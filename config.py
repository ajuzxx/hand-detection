import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "exam_audit_log.csv")
EVIDENCE_FOLDER = os.path.join(BASE_DIR, "evidence_photos")

# Thresholds
TABLE_SIMILARITY_THRESHOLD = 5000000 
WARNING_THRESHOLD = 5.0 

# App Settings
APP_TITLE = "AI Proctor System | Engineering Project"
APP_SIZE = "1400x800"
THEME_MODE = "Dark"
THEME_COLOR = "blue"