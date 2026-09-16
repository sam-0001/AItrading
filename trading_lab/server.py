import http.server
import socketserver
import threading
import logging
from pathlib import Path

from trading_lab.services import LabService
from trading_lab.store import SqliteStore
from trading_lab.dashboard import DashboardGenerator

logger = logging.getLogger(__name__)

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Re-initialize connection to read current state
            # Note: Hardcoded to local db for simplicity in standalone server
            db_path = Path("test.db") if Path("test.db").exists() else Path("data/lab.db")
            store = SqliteStore(db_path)
            lab = LabService(store)
            dashboard = DashboardGenerator(lab)
            
            html_content = dashboard.generate_html()
            self.wfile.write(html_content.encode('utf-8'))
        elif self.path == '/favicon.ico':
            self.send_response(204) # No Content
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()


def start_server(port=8080):
    handler = DashboardHandler
    # Allow port reuse
    socketserver.TCPServer.allow_reuse_address = True
    
    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            logger.info(f"Dashboard web server started on port {port}")
            httpd.serve_forever()
    except Exception as e:
        logger.error(f"Failed to start dashboard server: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_server()
