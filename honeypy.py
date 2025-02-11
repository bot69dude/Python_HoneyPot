import argparse
import logging
from ssh_honeypot import SSHHoneypot

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():

    parser = argparse.ArgumentParser(description="Honeypot Controller")

    parser.add_argument('-a', '--address', type=str, required=True, help="IP address to bind the honeypot")
    parser.add_argument('-p', '--port', type=int, required=True, help="Port number to run the honeypot on")

    honeypot_group = parser.add_mutually_exclusive_group(required=True)
    honeypot_group.add_argument('-s', '--ssh', action="store_true", help="Run SSH Honeypot")
    honeypot_group.add_argument('-wh', '--http', action="store_true", help="Run HTTP Honeypot")

    parser.add_argument('-u', '--username', type=str, default="admin", help="Username for HTTP honeypot (default: admin)")
    parser.add_argument('-w', '--password', type=str, default="deeboodah", help="Password for HTTP honeypot (default: deeboodah)")
    parser.add_argument('-t', '--tarpit', action="store_true", help="Enable tarpit mode (SSH only)")

    args = parser.parse_args()

    try:
        if args.ssh:
            logging.info(f"Starting SSH Honeypot on {args.address}:{args.port} (Tarpit: {'Enabled' if args.tarpit else 'Disabled'})")
            honeypot = SSHHoneypot(args.address, args.port)
            honeypot.run()

        elif args.http:
            logging.info(f"Starting HTTP Honeypot on port {args.port} with credentials {args.username}/{args.password}")

    except KeyboardInterrupt:
        logging.warning("Honeypot stopped by user.")
    except Exception as e:
        logging.error(f"Error starting honeypot: {e}", exc_info=True)

if __name__ == "__main__":
    main()
