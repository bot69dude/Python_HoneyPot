from flask import Flask, request, render_template
import logging
import os
from logging.handlers import RotatingFileHandler

# Configuration
LOGS_PATH = "logs"
os.makedirs(LOGS_PATH, exist_ok=True)
LOG_FILE = os.path.join(LOGS_PATH, "creds_audit.log")

# Setup logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("web_honeypot")
handler = RotatingFileHandler(LOG_FILE, maxBytes=100000, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Initialize Flask app
app = Flask(__name__, template_folder="templates")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/wp-admin', methods=['GET', 'POST'])
def wp_admin():
    if request.method == 'POST':
        username = request.form.get('log', '')
        password = request.form.get('pwd', '')
        ip = request.remote_addr
        
        logger.info(f"WordPress Login Attempt - User: {username}, Password: {password}, IP: {ip}")
        
        return render_template('wp-admin.html', error="Invalid username or password")
    
    return render_template('wp-admin.html')


def run_app(port=8080, username="admin", password="password"):
    logging.info(f"[+] Web Honeypot running on port {port}, default username: {username}, default password: {password}")
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    run_app()