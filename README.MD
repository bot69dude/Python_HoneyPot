# SSH & Web Honeypot

This project is a honeypot that mimics an SSH and WordPress login system to capture attacker activity.

## Features
- Fake SSH server that logs login attempts and commands executed by attackers.
- Fake WordPress login page that logs username and password attempts.
- Logs all activity to rotating log files.
- Rate-limiting to prevent excessive connection attempts.
- Simulates a realistic Linux system for attackers to interact with.

## Project Structure
```
D:.
│   .env                  # Stores environment variables
│   .gitignore            # Specifies ignored files for version control
│   honeypy.py            # Main script to run the honeypot
│   README.MD             # Documentation for the project
│   requirements.txt      # Lists dependencies
│   ssh_honeypot.py       # SSH honeypot implementation
│   web_honeypot.py       # Web honeypot (WordPress login page)
│
├───logs
│       cmd_audit.log     # Logs SSH commands executed by attackers
│       creds_audit.log   # Logs SSH login attempts
│       funnel.log        # Logs general honeypot activity
│
├───ssh_honeypy
│   └───static
│           server.key       # SSH private key
│           server.key.pub   # SSH public key
│
├───templates
│       dashboard.html    # Web dashboard UI (if implemented)
│       index.html        # Main page for the honeypot
│       wp-admin.html     # Fake WordPress login page
│
└───__pycache__           # Compiled Python files
```

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/bot69dude/Python_HoneyPot.git
   cd Honey_pot
   ```

2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Linux/macOS
   venv\Scripts\activate     # On Windows
   ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory and add the following:
   ```sh
   SSH_KEY_PASSPHRASE=""
   ```

## Usage

### Running the SSH Honeypot
```sh
python honeypy.py -a 0.0.0.0 -p 2222 -s
```
This starts the SSH honeypot on port 2222.

### Running the Web Honeypot
```sh
python honeypy.py -a 0.0.0.0 -p 8080 -wh
```
This starts the web honeypot on port 8080.

## Logs
- All logs are stored in the `logs/` directory.
- SSH login attempts are recorded in `creds_audit.log`.
- Commands executed in the SSH honeypot are stored in `cmd_audit.log`.
- General honeypot activity is logged in `funnel.log`.

## Security Notice
This project is for research and educational purposes only. Running a honeypot may expose your system to potential risks. Ensure it is run in an isolated environment.

## License
MIT License