import os
import logging
import time
import socket
import paramiko
import threading
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

# Load environment variables from .env file
load_dotenv()

# Configuration
HOST = "0.0.0.0"
PORT = 2222
KEY_PATH = "ssh_honeypy/static/server.key"
PASSPHRASE = os.getenv("SSH_KEY_PASSPHRASE")
MAX_CONNECTIONS = 500
RATE_LIMIT_SECONDS = 2

connection_tracker = defaultdict(float)

# Setup Logging
def setup_logging():
    logs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(logs_path, exist_ok=True)
    
    def create_logger(name, filename):
        handler = RotatingFileHandler(os.path.join(logs_path, filename), maxBytes=100000, backupCount=5)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        return logger
    
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
    return (
        create_logger("creds_audit", "creds_audit.log"), 
        create_logger("cmd_audit", "cmd_audit.log"),
        create_logger("funnel", "funnel.log")
    )

creds_logger, cmd_logger, funnel_logger = setup_logging()

def load_ssh_key():
    try:
        key_path = os.path.abspath(KEY_PATH)
        logging.info(f"Loading SSH key from: {key_path}")
        if not os.path.exists(key_path):
            logging.error(f"SSH key file not found at: {key_path}")
            return None
        return paramiko.RSAKey(filename=key_path, password=PASSPHRASE)
    except Exception as e:
        logging.error(f"Failed to load SSH key: {str(e)}", exc_info=True)
        return None

class SSHServerHandler(paramiko.ServerInterface):
    def __init__(self, client_addr):
        self.client_addr = client_addr
        self.event = threading.Event()

    def check_auth_password(self, username, password):
        creds_logger.info(f"Login attempt - User: {username}, Password: {password}, IP: {self.client_addr[0]}")
        return paramiko.AUTH_SUCCESSFUL

    def get_allowed_auths(self, username):
        return "password"

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

class SSHHoneypot:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.key = load_ssh_key()
        if not self.key:
            raise Exception("Failed to load SSH key")
        self.socket = None
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=MAX_CONNECTIONS)

    def handle_shell(self, channel, addr):
        try:
            # Send initial prompt
            channel.send(b"corporate-jumpbox2$ ")
            
            current_dir = "/usr/local"
            hostname = "corporate-jumpbox2"
            username = "corpuser1"
            
            buf = b""
            while True:
                char = channel.recv(1)
                if not char:
                    break
                
                # Handle backspace
                if char == b"\x7f":
                    if buf:
                        buf = buf[:-1]
                        channel.send(b"\b \b")
                    continue
                
                # Handle Ctrl+C (SIGINT)
                if char == b"\x03":
                    channel.send(b"^C\n")
                    channel.send(f"{hostname}$ ".encode())
                    buf = b""
                    continue
                
                # Echo the character back
                channel.send(char)
                
                # Append typed character
                buf += char
                
                # Handle Enter (process command)
                if char == b"\r":
                    channel.send(b"\n")  # Send newline
                    
                    cmd_full = buf.strip(b"\r\n").decode('utf-8', 'ignore')
                    cmd_parts = cmd_full.split()
                    cmd = cmd_parts[0] if cmd_parts else ""
                    args = cmd_parts[1:] if len(cmd_parts) > 1 else []
                    
                    funnel_logger.info(f"Command executed: {cmd_full} from {addr[0]}")
                    
                    # Fake responses for commands
                    responses = {
                        "exit": lambda: b"\nlogout\nConnection closed.\n",
                        "pwd": lambda: current_dir.encode() + b"\n",
                        "whoami": lambda: username.encode() + b"\n",
                        "hostname": lambda: hostname.encode() + b"\n",
                        "uname": lambda: b"Linux corporate-jumpbox2 5.15.0-91-generic #101-Ubuntu SMP x86_64 GNU/Linux\n",
                        "id": lambda: b"uid=1000(corpuser1) gid=1000(corpuser1) groups=1000(corpuser1),4(adm),24(cdrom),27(sudo)\n",
                        "uptime": lambda: b" 16:42:13 up 8 days, 23:27, 1 user, load average: 0.08, 0.03, 0.01\n",
                        "df": lambda: b"Filesystem     1K-blocks      Used Available Use% Mounted on\n/dev/sda1      41251136  12164412  27033340  32% /\n",
                        "free": lambda: b"               total        used        free      shared  buff/cache   available\nMem:        16280908     4521432     8944072      322160     2815404    11139656\n",
                        "ps": lambda: b"    PID TTY          TIME CMD\n   3264 pts/0    00:00:00 bash\n   3349 pts/0    00:00:00 ps\n",
                    }
                    
                    # Handle commands
                    if cmd in responses:
                        response = responses[cmd]()
                    elif cmd == "ls":
                        response = b"file1.txt  file2.log  directory/\n"
                    elif cmd == "cd":
                        if args and args[0] == "..":
                            current_dir = "/"
                        elif args:
                            current_dir += f"/{args[0]}"
                        response = b""
                    elif cmd == "cat":
                        if args and args[0] == "file1.txt":
                            response = b"This is a fake honeypot file.\n"
                        else:
                            response = b"cat: No such file or directory\n"
                    elif cmd:
                        response = f"bash: {cmd}: command not found\n".encode()
                    else:
                        response = b""
                    
                    # Send response
                    channel.send(response)
                    if cmd == "exit":
                        break
                        
                    # Send new prompt on a fresh line
                    channel.send(f"{hostname}$ ".encode())
                    
                    # Reset buffer
                    buf = b""
                    
        except Exception as e:
            logging.error(f"Shell error for {addr[0]}: {str(e)}", exc_info=True)
        finally:
            channel.close()


    def handle_client(self, client_sock, addr):
        """Handle individual client connection."""
        try:
            transport = paramiko.Transport(client_sock)
            transport.add_server_key(self.key)
            transport.set_gss_host(socket.getfqdn(""))
            
            server = SSHServerHandler(addr)
            try:
                transport.start_server(server=server)
            except paramiko.SSHException:
                logging.error(f"SSH negotiation failed for {addr[0]}")
                return
            
            channel = transport.accept(20)
            if channel is None:
                logging.error(f"No channel opened for {addr[0]}")
                return
            
            self.handle_shell(channel, addr)
            
        except Exception as e:
            logging.error(f"Error handling client {addr[0]}: {str(e)}", exc_info=True)
        finally:
            try:
                transport.close()
            except:
                pass
            try:
                client_sock.close()
            except:
                pass

    def run(self):
        """Run the SSH honeypot server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            logging.info(f"SSH Honeypot listening on {self.host}:{self.port}")
            
            self.running = True
            while self.running:
                try:
                    client, addr = self.socket.accept()
                    logging.info(f"New connection from {addr[0]}")
                    
                    if time.time() - connection_tracker[addr[0]] < RATE_LIMIT_SECONDS:
                        logging.warning(f"Rate limited connection from {addr[0]}")
                        client.close()
                        continue
                        
                    connection_tracker[addr[0]] = time.time()
                    self.executor.submit(self.handle_client, client, addr)
                    
                except Exception as e:
                    if self.running:
                        logging.error(f"Error accepting connection: {str(e)}", exc_info=True)
                    
        except Exception as e:
            logging.error(f"Server error: {str(e)}", exc_info=True)
        finally:
            self.cleanup()

    def cleanup(self):
        """Cleanup resources."""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.executor.shutdown(wait=False)

def main():
    honeypot = SSHHoneypot(HOST, PORT)
    try:
        honeypot.run()
    except KeyboardInterrupt:
        logging.info("SSH Honeypot stopped by user")
    finally:
        honeypot.cleanup()

if __name__ == "__main__":
    main()