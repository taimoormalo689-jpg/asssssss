import sys
print("START TEST")

# Test imports
try:
    import http.server
    print("http.server OK")
except Exception as e:
    print(f"http.server ERROR: {e}")

try:
    import socketserver
    print("socketserver OK")
except Exception as e:
    print(f"socketserver ERROR: {e}")

try:
    import threading
    print("threading OK")
except Exception as e:
    print(f"threading ERROR: {e}")

try:
    import webbrowser
    print("webbrowser OK")
except Exception as e:
    print(f"webbrowser ERROR: {e}")

try:
    import requests
    print("requests OK")
except Exception as e:
    print(f"requests ERROR: {e}")

try:
    import json
    print("json OK")
except Exception as e:
    print(f"json ERROR: {e}")

try:
    import time
    print("time OK")
except Exception as e:
    print(f"time ERROR: {e}")

try:
    import base64
    print("base64 OK")
except Exception as e:
    print(f"base64 ERROR: {e}")

try:
    import os
    print("os OK")
except Exception as e:
    print(f"os ERROR: {e}")

try:
    from pyngrok import ngrok, conf
    print("pyngrok OK")
except Exception as e:
    print(f"pyngrok ERROR: {e}")

try:
    from datetime import datetime
    print("datetime OK")
except Exception as e:
    print(f"datetime ERROR: {e}")

try:
    import urllib.parse
    print("urllib.parse OK")
except Exception as e:
    print(f"urllib.parse ERROR: {e}")

print("ALL IMPORTS DONE")
