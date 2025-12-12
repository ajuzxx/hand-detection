import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import time
import platform
from plyer import notification
import cv2 # Essential for text drawing and colors

# Import our custom modules
import config
from modules.camera import CameraService
from modules.detector import DetectionService
from modules.logger import LoggerService

ctk.set_appearance_mode(config.THEME_MODE)
ctk.set_default_color_theme(config.THEME_COLOR)

class ModernProctorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Services
        self.camera = CameraService()
        self.detector = DetectionService()
        self.logger = LoggerService()
        
        # State Variables
        self.running = False
        self.registered = False
        self.current_status = "NORMAL"
        self.status_start = time.time()
        self.alert_stage = 0
        self.frame_cache = None

        # Setup UI
        self.title(config.APP_TITLE)
        self.geometry(config.APP_SIZE)
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.create_sidebar()
        self.create_main_view()
        self.style_treeview()
        self.refresh_logs_ui()

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1)

        ctk.CTkLabel(self.sidebar, text="PROCTOR AI", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10))
        
        ctk.CTkLabel(self.sidebar, text="Student ID:", anchor="w").grid(row=1, column=0, padx=20, pady=(10, 0))
        self.entry_id = ctk.CTkEntry(self.sidebar, placeholder_text="e.g. S7_001")
        self.entry_id.grid(row=2, column=0, padx=20, pady=(0, 20))

        self.btn_start = ctk.CTkButton(self.sidebar, text="START CAMERA", command=self.start_exam, height=40)
        self.btn_start.grid(row=3, column=0, padx=20, pady=10)
        
        self.btn_register = ctk.CTkButton(self.sidebar, text="REGISTER TABLE", command=self.register_table, state="disabled", fg_color="gray", height=40)
        self.btn_register.grid(row=4, column=0, padx=20, pady=10)

        self.btn_stop = ctk.CTkButton(self.sidebar, text="STOP EXAM", command=self.stop_exam, state="disabled", fg_color="#D32F2F", hover_color="#B71C1C", height=40)
        self.btn_stop.grid(row=5, column=0, padx=20, pady=10)

        self.status_box = ctk.CTkFrame(self.sidebar, height=100, fg_color="transparent")
        self.status_box.grid(row=7, column=0, padx=20, pady=20, sticky="ew")
        
        self.lbl_status = ctk.CTkLabel(self.status_box, text="SYSTEM IDLE", font=("Arial", 16, "bold"), text_color="gray")
        self.lbl_status.place(relx=0.5, rely=0.5, anchor="center")

    def create_main_view(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(0, weight=3)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.video_frame = ctk.CTkFrame(self.main_frame, corner_radius=15)
        self.video_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 20))
        
        self.video_label = ctk.CTkLabel(self.video_frame, text="Camera Feed Inactive", text_color="gray")
        self.video_label.place(relx=0.5, rely=0.5, anchor="center")

        self.log_container = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.log_container.grid(row=1, column=0, sticky="nsew")
        
        cols = ("Student ID", "Time", "Event", "Duration", "Severity")
        self.tree = ttk.Treeview(self.log_container, columns=cols, show="headings", height=8)
        
        widths = [100, 100, 150, 80, 100]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w)
            
        vsb = ttk.Scrollbar(self.log_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        vsb.pack(side="right", fill="y", pady=5)

    def style_treeview(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", rowheight=25)
        style.configure("Treeview.Heading", background="#1f538d", foreground="white", font=("Arial", 10, "bold"))
        style.map("Treeview", background=[('selected', '#1f538d')])
        self.tree.tag_configure('danger', foreground='#ff5252')
        self.tree.tag_configure('safe', foreground='#69f0ae')

    def start_exam(self):
        if not self.entry_id.get():
            messagebox.showerror("Missing Info", "Please enter a Student ID.")
            return
        
        try:
            self.camera.start()
            self.running = True
            self.registered = False
            
            self.btn_start.configure(state="disabled", fg_color="gray")
            self.btn_register.configure(state="normal", fg_color="#1f538d")
            self.btn_stop.configure(state="normal", fg_color="#D32F2F")
            self.lbl_status.configure(text="SETUP MODE", text_color="orange")
            
            self.video_loop()
        except Exception as e:
            messagebox.showerror("Camera Error", str(e))

    def register_table(self):
        if self.frame_cache is not None:
            self.detector.set_reference_frame(self.frame_cache)
            self.registered = True
            self.status_start = time.time()
            self.current_status = "NORMAL" # Reset status on register
            
            self.btn_register.configure(state="disabled", fg_color="gray")
            self.lbl_status.configure(text="MONITORING ACTIVE", text_color="#69f0ae")
            self.status_box.configure(fg_color="#1b5e20")

    def stop_exam(self):
        self.running = False
        self.camera.stop()
        self.video_label.configure(image=None, text="Exam Ended")
        
        self.btn_start.configure(state="normal", fg_color="#1f538d")
        self.btn_register.configure(state="disabled", fg_color="gray")
        self.btn_stop.configure(state="disabled", fg_color="gray")
        self.lbl_status.configure(text="EXAM STOPPED", text_color="gray")
        self.status_box.configure(fg_color="transparent")

    def video_loop(self):
        if not self.running: return

        success, frame = self.camera.get_frame()
        if success:
            self.frame_cache = frame
            
            # 1. AI Processing
            processed_frame, detected_status = self.detector.process_frame(frame, self.registered)
            
            # 2. Logic Handling (Alerts & Beeps)
            self.handle_status_change(detected_status, processed_frame)
            
            # 3. DRAW TEXT OVERLAYS (Restored Section)
            duration = time.time() - self.status_start
            
            if self.registered:
                # Monitoring Mode
                color = (0, 255, 0) if self.current_status == "NORMAL" else (0, 0, 255)
                cv2.putText(processed_frame, f"Status: {self.current_status}", (20, 40), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                
                if self.current_status != "NORMAL":
                    cv2.putText(processed_frame, f"Away: {duration:.1f}s", (20, 80), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                # Setup Mode
                cv2.putText(processed_frame, "POINT AT TABLE -> PRESS REGISTER", (50, 250), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

            # 4. Display Image
            img_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            imgtk = ImageTk.PhotoImage(image=img_pil)
            self.video_label.configure(image=imgtk)
            self.video_label.image = imgtk

        self.after(10, self.video_loop)

    def handle_status_change(self, new_status, frame):
        # State Change Logic
        if new_status != self.current_status:
            
            # Log the previous state duration before switching
            old_duration = time.time() - self.status_start
            if old_duration > 1.0:
                 # Only log if it wasn't a flicker (< 1s)
                sev = "GOOD" if self.current_status == "NORMAL" else ("HIGH" if old_duration > 10 else "LOW")
                self.logger.log_incident(self.entry_id.get(), self.current_status, old_duration, sev)
                self.refresh_logs_ui()

            # Beep if entering a BAD state
            if new_status != "NORMAL":
                self.play_beep()

            self.current_status = new_status
            self.status_start = time.time()
            self.alert_stage = 0
            
            # Update UI Colors
            if new_status == "NORMAL":
                self.lbl_status.configure(text="MONITORING ACTIVE", text_color="#69f0ae")
                self.status_box.configure(fg_color="#1b5e20")
            else:
                self.lbl_status.configure(text="SUSPICIOUS ACTIVITY", text_color="#ff5252")
                self.status_box.configure(fg_color="#b71c1c")

        # Ongoing Alerts (Time-based)
        current_duration = time.time() - self.status_start
        if self.current_status != "NORMAL":
            if current_duration > config.WARNING_THRESHOLD and self.alert_stage == 0:
                self.send_notification(current_duration)
                self.alert_stage = 1
            elif current_duration > 10 and self.alert_stage == 1:
                evidence_file = self.logger.save_evidence(frame, self.entry_id.get(), self.current_status)
                self.logger.log_incident(self.entry_id.get(), self.current_status, current_duration, "CRITICAL", evidence_file)
                self.refresh_logs_ui()
                self.alert_stage = 2

    def refresh_logs_ui(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        df = self.logger.get_recent_logs()
        if not df.empty:
            for _, row in df.iterrows():
                sev = str(row['severity']).upper()
                tags = ('danger',) if sev in ["HIGH", "CRITICAL"] else (('safe',) if sev == "GOOD" else ())
                # Ensure we only insert the first 5 columns (matching treeview)
                vals = list(row)[:5] 
                self.tree.insert("", "end", values=vals, tags=tags)

    def play_beep(self):
        if platform.system() == "Windows":
            try:
                import winsound
                winsound.Beep(1500, 200)
            except: pass

    def send_notification(self, duration):
        try:
            notification.notify(title='EXAM WARNING', message=f'Hands gone for {duration:.1f}s', app_name='ProctorAI', timeout=2)
        except: pass
        if platform.system() == "Windows":
            try:
                import winsound
                winsound.Beep(1000, 500)
            except: pass