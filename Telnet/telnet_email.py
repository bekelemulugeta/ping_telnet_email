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
import socket

# Global flags and lock
monitoring_started = False
lock_file = os.path.join(os.path.expanduser("~"), "telnet_monitor.lock")

# Initialize Tkinter root early for dialogs
root = tk.Tk()
root.withdraw()

# Ensure only one instance is running
def check_single_instance():
    if os.path.exists(lock_file):
        try:
            with open(lock_file, "r") as f:
                existing_pid = int(f.read().strip())
            if psutil.pid_exists(existing_pid):
                messagebox.showerror("Already Running", "Another instance is already running.")
                sys.exit(0)
            else:
                os.remove(lock_file)
        except Exception:
            os.remove(lock_file)

    with open(lock_file, "w") as f:
        f.write(str(os.getpid()))

def remove_lock_file():
    if os.path.exists(lock_file):
        os.remove(lock_file)

check_single_instance()
root.deiconify()

# ---------------------- Helper Functions ----------------------

def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    log_box.insert(tk.END, log_msg)
    log_box.yview(tk.END)

    log_filename = f"telnet_monitor_{datetime.now().strftime('%Y-%m-%d')}.txt"
    with open(log_filename, "a", encoding="utf-8") as log_file:
        log_file.write(log_msg + "\n")

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

        log_message("📧 Email alert sent!")
    except Exception as e:
        log_message(f"❌ Failed to send email: {e}")

def read_ip_list(file_path):
    try:
        with open(file_path, "r") as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        log_message(f"⚠ IP list file not found: {file_path}")
        return []

def is_telnet_successful(ip, port, timeout=5):
    try:
        with socket.create_connection((ip, int(port)), timeout=timeout):
            return True
    except Exception:
        return False

def start_monitoring(ip_list, sender, password, receiver):
    global monitoring_started
    receiver_list = [email.strip() for email in receiver.split(",")]

    def monitor(ip_port):
        try:
            ip, port = ip_port.split(":")
            port = int(port)
        except ValueError:
            log_message(f"⚠ Invalid IP:Port format: {ip_port}")
            return

        while monitoring_started:
            if is_telnet_successful(ip, port):
                log_message(f"✅ Telnet to {ip}:{port} successful.")
            else:
                log_message(f"❌ Telnet to {ip}:{port} FAILED.")
                subject = f"❌ Telnet to {ip}:{port} failed"
                body = f"{datetime.now()}: Telnet to {ip}:{port} failed."
                send_email(sender, password, receiver_list, subject, body)
            time.sleep(60)

    for ip_port in ip_list:
        thread = threading.Thread(target=monitor, args=(ip_port,), daemon=True)
        thread.start()

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

    log_message("🚀 Starting Telnet monitoring…")
    monitoring_started = True
    start_monitoring(ip_list, sender, password, receiver)

def on_stop():
    global monitoring_started
    monitoring_started = False
    log_message("🛑 Monitoring stopped.")

def browse_file():
    file_path = filedialog.askopenfilename(title="Select IP:Port List File", filetypes=[("Text Files", "*.txt")])
    if file_path:
        ip_file_path.set(file_path)

def on_closing():
    remove_lock_file()
    root.destroy()

# ---------------------- GUI Setup ----------------------

root.title("Telnet Monitor")
root.geometry("520x450")
ip_file_path = tk.StringVar()

tk.Label(root, text="Select IP:Port List File:").pack()
file_frame = tk.Frame(root)
file_frame.pack(pady=2)
tk.Entry(file_frame, textvariable=ip_file_path, width=40).pack(side=tk.LEFT)
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

log_box = tk.Listbox(root, width=70, height=12)
log_box.pack(pady=10)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
