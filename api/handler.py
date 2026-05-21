import threading
import grabber_fixed

_started = False

def handler(request):
    """Vercel entrypoint: start grabber if not already started and return status JSON."""
    global _started
    if not _started:
        threading.Thread(target=grabber_fixed.run_main, daemon=True).start()
        _started = True
    return {
        "status": "grabber started",
        "message": "The grabber is now running in the background."
    }
