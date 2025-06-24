import os
import sys
import time
import threading
import smtplib
import tkinter as tk
from tkinter import messagebox, filedialog
from email.mime.text import MIMEText
from datetime import datetime
import subprocess
import psutil
import atexit

# Global flags and lock
monitoring_started = False
lock_file = os.path.join(os.path.expanduser("~"), "ping_monitor.lock")

# Initialize Tkinter root early for dialogs
root = tk.Tk()
root.withdraw()


# ---------------------- Instance Check ----------------------
def check_single_instance():
    if os.path.exists(lock_file):
        try:
            with open(lock_file, "r") as f:
                existing_pid = int(f.read().strip())
            if psutil.pid_exists(existing_pid):
                messagebox.showerror("Already Running", "Another instance is already running.")
                sys.exit(0)
            else:
                os.remove(lock_file)  # Remove stale lock
        except Exception:
            os.remove(lock_file)

    with open(lock_file, "w") as f:
        f.write(str(os.getpid()))


def remove_lock_file():
    if os.path.exists(lock_file):
        os.remove(lock_file)


# Ensure lock is removed at exit
atexit.register(remove_lock_file)
check_single_instance()
root.deiconify()


# ---------------------- Helper Functions ----------------------
def log_message(message):
    def safe_log():
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        log_box.insert(tk.END, log_msg)
        log_box.yview(tk.END)

        log_filename = f"ping_monitor_{datetime.now().strftime('%Y-%m-%d')}.txt"
        with open(log_filename, "a", encoding="utf-8") as log_file:
            log_file.write(log_msg + "\n")

    root.after(0, safe_log)


def send_email(sender, password, receivers, subject, body):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = ", ".join(receivers)

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)

        log_message("✔️ Email alert sent!")
    except Exception as e:
        log_message(f"❌ Failed to send email: {e}")


def read_ip_list(file_path):
    try:
        with open(file_path, "r") as file:
            return [ip.strip() for ip in file if ip.strip()]
    except FileNotFoundError:
        log_message(f"⚠️ IP list file not found: {file_path}")
        return []


import subprocess
import os

def is_ping_successful(ip, timeout=2):
    param = "-n" if os.name == "nt" else "-c"
    cmd = ["ping", param, "1", ip]

    # Windows-only flags to suppress the console window
    creationflags = 0
    startupinfo = None
    if os.name == "nt":
        creationflags = subprocess.CREATE_NO_WINDOW
        # Alternatively, use STARTUPINFO to hide window
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo = si

    try:
        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
            creationflags=creationflags,
            startupinfo=startupinfo
        )
        return True
    except subprocess.CalledProcessError:
        return False



def start_monitoring(ip_list, sender, password, receiver):
    #global monitoring_started
    receiver_list = [email.strip() for email in receiver.split(",")]

    def monitor(ip):
        while monitoring_started:
            success = False
            for attempt in range(2):  # Retry 2 times
                if is_ping_successful(ip):
                    success = True
                    break
                time.sleep(2)  # short wait before retry

            if success:
                log_message(f"✅ Ping to {ip} successful.")
            else:
                log_message(f"❌ Ping to {ip} FAILED.")
                subject = f"❌ Ping to {ip} failed"
                body = f"{datetime.now()}: Ping to {ip} failed."
                send_email(sender, password, receiver_list, subject, body)

            time.sleep(60)  # Wait 60 seconds before next ping

    for ip in ip_list:
        thread = threading.Thread(target=monitor, args=(ip,), daemon=True)
        thread.start()
        time.sleep(0.1)  # slight stagger


# ---------------------- GUI Functions ----------------------
def on_start():
    global monitoring_started
    if monitoring_started:
        messagebox.showinfo("Already Running", "Monitoring is already running.")
        return

    ip_file = ip_file_path.get()
    sender = sender_entry.get().strip()
    password = password_entry.get().strip()
    receiver = receiver_entry.get().strip()

    if not ip_file or not sender or not password or not receiver:
        messagebox.showerror("Missing Info", "Please fill in all fields.")
        return

    ip_list = read_ip_list(ip_file)
    if not ip_list:
        messagebox.showerror("Error", "No IPs found in the file.")
        return

    log_message(" Starting monitoring...")
    monitoring_started = True
    start_monitoring(ip_list, sender, password, receiver)


def on_stop():
    global monitoring_started
    monitoring_started = False
    log_message(" Monitoring stopped.")


def browse_file():
    file_path = filedialog.askopenfilename(title="Select IP List File", filetypes=[("Text Files", "*.txt")])
    if file_path:
        ip_file_path.set(file_path)


def on_closing():
    root.destroy()


# ---------------------- GUI Setup ----------------------
root.title("Ping Monitor")
root.geometry("540x500")
ip_file_path = tk.StringVar()

tk.Label(root, text="Select IP List File:").pack()
file_frame = tk.Frame(root)
file_frame.pack(pady=2)
tk.Entry(file_frame, textvariable=ip_file_path, width=45).pack(side=tk.LEFT)
tk.Button(file_frame, text="Browse", command=browse_file).pack(side=tk.LEFT, padx=5)

tk.Label(root, text="Sender Email (Gmail):").pack()
sender_entry = tk.Entry(root, width=50)
sender_entry.pack()

tk.Label(root, text="App Password:").pack()
password_entry = tk.Entry(root, show="*", width=50)
password_entry.pack()

tk.Label(root, text="Receiver Email (comma separated):").pack()
receiver_entry = tk.Entry(root, width=50)
receiver_entry.pack()

tk.Button(root, text="Start Monitoring", command=on_start).pack(pady=10)
tk.Button(root, text="Stop Monitoring", command=on_stop).pack(pady=5)

log_box = tk.Listbox(root, width=75, height=15)
log_box.pack(pady=10)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
