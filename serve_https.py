"""
Serveur HTTPS local pour GRYB Meetings PWA.
Nécessaire pour que les notifications fonctionnent sur Chrome.

Usage: python serve_https.py
"""
import http.server
import ssl
import os
import socket
import webbrowser
import threading

PORT = 8443
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
CERTFILE = os.path.join(DIRECTORY, "cert.pem")
KEYFILE = os.path.join(DIRECTORY, "key.pem")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def log_message(self, format, *args):
        pass  # Suppress logs


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


if __name__ == '__main__':
    if not os.path.exists(CERTFILE) or not os.path.exists(KEYFILE):
        print("Generating SSL certificate...")
        import gen_cert  # noqa

    local_ip = get_local_ip()

    server = http.server.HTTPServer(("0.0.0.0", PORT), Handler)

    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(CERTFILE, KEYFILE)
    server.socket = ctx.wrap_socket(server.socket, server_side=True)

    print(f"\n  GRYB Meetings - Serveur HTTPS")
    print(f"  PC:     https://localhost:{PORT}")
    print(f"  Mobile: https://{local_ip}:{PORT}")
    print(f"  Chrome: Avance > Continuer pour acceder")
    print(f"  Ctrl+C pour arreter\n")

    threading.Timer(1, lambda: webbrowser.open(f'https://localhost:{PORT}')).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServeur arrêté.")
        server.server_close()
