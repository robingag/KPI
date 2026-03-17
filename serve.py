"""
Serveur local pour GRYB Meetings PWA.
Lance le serveur puis ouvre l'app dans le navigateur.

Usage: python serve.py
"""
import http.server
import os
import socket
import webbrowser
import threading

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def log_message(self, format, *args):
        pass  # Suppress logs


def get_local_ip():
    """Get LAN IP so phone can connect."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


if __name__ == '__main__':
    # Generate icons first
    print("Generating icons...")
    import generate_icons  # noqa
    generate_icons

    local_ip = get_local_ip()

    server = http.server.HTTPServer(("0.0.0.0", PORT), Handler)

    print(f"""
╔══════════════════════════════════════════════════╗
║          GRYB Meetings - Serveur Local           ║
╠══════════════════════════════════════════════════╣
║                                                  ║
║  PC:       http://localhost:{PORT}                ║
║  Mobile:   http://{local_ip}:{PORT}       ║
║                                                  ║
║  Sur ton cell Android:                           ║
║  1. Ouvre le lien Mobile dans Chrome              ║
║  2. Menu ⋮ → "Ajouter à l'écran d'accueil"      ║
║  3. Clique "Activer" pour les notifications      ║
║                                                  ║
║  Ctrl+C pour arrêter                             ║
╚══════════════════════════════════════════════════╝
    """)

    # Open in browser
    threading.Timer(1, lambda: webbrowser.open(f'http://localhost:{PORT}')).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServeur arrêté.")
        server.server_close()
