
# 📡 Ping & Telnet Email Monitor

A Python desktop application that monitors network availability using **Ping** and **Telnet** protocols. It sends **email alerts** when a server or IP becomes unreachable.

---

## 📁 Project Structure

```
ping_telnet_email/
├── ping/
│   └── ping_monitor.py
├── telnet/
│   └── telnet_monitor.py
├── requirements.txt
└── README.md
```

---

## ✅ Features

- 🔒 Prevents multiple instances using a lock file
- ✉️ Sends email alerts via Gmail
- 💾 Logs failures/success to daily log files
- 🔁 Monitors multiple IPs or IP:Port pairs
- 🧵 Threaded monitoring for scalability
- 🖥️ GUI built with Tkinter

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/bekelemulugeta/ping_telnet_email.git
cd ping_telnet_email
```

### 2. Set up a virtual environment (optional but recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install the dependencies

```bash
pip install -r requirements.txt
```

---

## 📥 Input File Format

### For `ping_monitor.py` (inside `ping/`)

Plain `.txt` file with one **IP or hostname per line**:

```
8.8.8.8
192.168.0.1
example.com
```

---

### For `telnet_monitor.py` (inside `telnet/`)

Plain `.txt` file with one **IP:Port** pair per line:

```
192.168.0.1:22
example.com:80
```

---

## 📧 Email Configuration

- Use **Gmail** address for the sender.
- Use an **App Password** (not your Gmail password) for authentication.  
  [How to generate one →](https://support.google.com/accounts/answer/185833)

---

## 📝 How to Run

### Ping Monitor

```bash
cd ping
python ping_monitor.py
```

### Telnet Monitor

```bash
cd telnet
python telnet_monitor.py
```

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 🤝 Contributing

Pull requests and issues are welcome! Please fork the repository and submit changes via PR.

---

## 👨‍💻 Author

**Bekele Mulugeta**  
🔗 [GitHub Profile](https://github.com/bekelemulugeta)

---

## 🗂️ Example Logs

Logs are saved daily as:

- `ping_monitor_YYYY-MM-DD.txt`
- `telnet_monitor_YYYY-MM-DD.txt`

Each line includes timestamps and connection status.