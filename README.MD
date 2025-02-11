# SSH & HTTP Honeypot

## Overview
This project is a **honeypot** that mimics an SSH and HTTP server to log and analyze unauthorized access attempts. It provides:

- A **fake SSH server** using Paramiko to capture login attempts and commands executed by attackers.
- A **web honeypot** simulating a vulnerable WordPress login page.
- A **dashboard** for real-time monitoring of attack data.

---

## Features
- **SSH Honeypot**
  - Logs usernames, passwords, and commands used by attackers.
  - Fake interactive shell with realistic responses.
  - Supports tarpit mode to slow down brute-force attacks.
- **HTTP Honeypot**
  - Simulates a fake WordPress login page.
  - Captures credentials entered by attackers.
- **Logging & Monitoring**
  - Stores login attempts and commands in log files.
  - Web-based dashboard for real-time analysis.
- **Scalability**
  - Uses multithreading and thread pooling for handling large numbers of connections.
  
---

## Installation
### **1. Clone the Repository**
```bash
git clone https://github.com/yourusername/honeypot-project.git
cd honeypot-project
```

### **2. Install Dependencies**
Ensure Python 3.8+ is installed, then run:
```bash
pip install -r requirements.txt
```

### **3. Generate SSH Key (If Needed)**
```bash
ssh-keygen -t rsa -b 2048 -f ssh_honeypy/static/server.key -N ""
```

---

## Usage
### **Running the SSH Honeypot**
```bash
python honeypy.py -a 0.0.0.0 -p 2222 -s
```
- The SSH honeypot will listen on **port 2222**.

### **Running the HTTP Honeypot**
```bash
python honeypy.py -a 0.0.0.0 -p 8080 -wh
```
- The HTTP honeypot will start on **port 8080**.

### **Accessing the Dashboard**
```bash
python web_app.py
```
- Open your browser and go to `http://localhost:5000`.

---

## Testing
To test the SSH honeypot, open a new terminal and run:
```bash
ssh -p 2222 someuser@localhost
```
For the HTTP honeypot, visit:
```bash
http://localhost:8080
```

---

## Logs & Data
- **SSH Credentials & Commands**: Stored in `logs/creds_audit.log` & `logs/cmd_audit.log`
- **Web Login Attempts**: Stored in `logs/web_honeypot.log`

---

## Contributing
Feel free to submit pull requests or report issues on GitHub.

---

## License
MIT License. See `LICENSE` file for details.