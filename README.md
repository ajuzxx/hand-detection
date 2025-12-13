# 🕵️ Exam Auditor (AI Proctor System)

A computer vision application that ensures exam integrity by monitoring student behavior in real-time. Built with **Python**, **OpenCV**, and **MediaPipe**.

## 🚀 Key Features
* **Real-time Hand Detection:** Uses Google's MediaPipe to track hand presence.
* **Anti-Cheat Logic:** Detects if a student leaves the desk or blocks the camera using structural similarity checks.
* **Automated Logging:** Records suspicious events (timestamp, duration, severity) to a CSV file.
* **Evidence Capture:** Automatically snaps photos during critical alerts for audit trails.
* **Modern UI:** Built with `CustomTkinter` for a professional Dark Mode interface.

## 🛠️ Tech Stack
* **Language:** Python 3.11
* **Computer Vision:** OpenCV, MediaPipe
* **GUI:** CustomTkinter
* **Data Handling:** Pandas, CSV

## 📸 Screenshots

<img width="1907" height="956" alt="image" src="https://github.com/user-attachments/assets/6a39a29b-d690-4aec-97af-d0ace74a8168" />
<img width="1713" height="833" alt="image" src="https://github.com/user-attachments/assets/0e18e44f-2d07-4214-8f0f-e53b7b5ad6d0" />



## ⚙️ How to Run
1.  Clone the repository:
    ```bash
    git clone [https://github.com/ajuzxx/hand-detection.git](https://github.com/ajuzxx/hand-detection.git)
    cd "exam auditor"
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the application:
    ```bash
    python main.py
    ```

## 🔮 Future Improvements
* Face gaze tracking integration.
* Cloud database syncing for logs.
