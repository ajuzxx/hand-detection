import cv2

class CameraService:
    def __init__(self, source=0):
        self.source = source
        self.cap = None

    def start(self):
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            raise ValueError("Could not open video device")

    def get_frame(self):
        if self.cap and self.cap.isOpened():
            success, frame = self.cap.read()
            if success:
                # Resize immediately for performance and consistency
                return True, cv2.resize(frame, (720, 540))
        return False, None

    def stop(self):
        if self.cap:
            self.cap.release()