import cv2
import mediapipe as mp
import numpy as np
import config

class DetectionService:
    def __init__(self):
        self.mp_hands = mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=2)
        self.mp_draw = mp.solutions.drawing_utils
        self.table_ref = None

    def set_reference_frame(self, frame):
        """Register the empty table"""
        self.table_ref = frame.copy()

    def process_frame(self, frame, is_monitoring=False):
        """
        Returns: 
        1. Processed Frame (with drawings)
        2. Detected Status (String)
        """
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.mp_hands.process(img_rgb)
        
        hands_visible = False
        if results.multi_hand_landmarks:
            hands_visible = True
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)

        status = "NORMAL"
        
        if is_monitoring and self.table_ref is not None:
            if not hands_visible:
                # Compare current frame vs reference frame
                gray1 = cv2.cvtColor(self.table_ref, cv2.COLOR_BGR2GRAY)
                gray2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                diff = np.sum(cv2.absdiff(gray1, gray2))
                
                # Logic: Low diff = Image looks like empty table (hands gone)
                # High diff (but no hands) = Camera blocked or object placed
                status = "HANDS_OFF_TABLE" if diff < config.TABLE_SIMILARITY_THRESHOLD else "CAMERA_BLOCKED"

        return frame, status