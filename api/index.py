from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Make sure the root directory is on the path so grabber_fixed can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        body = json.dumps({
            "status": "ok",
            "message": "Service is running."
        })
        self.wfile.write(body.encode())

    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        body = json.dumps({
            "status": "ok",
            "message": "POST received."
        })
        self.wfile.write(body.encode())
