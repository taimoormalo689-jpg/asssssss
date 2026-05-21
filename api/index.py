import threading
import json

# Import the grabber script; it will start the server when imported.
# The script already starts its threads at import time, so we just import it.
import grabber_fixed

_started = False

def handler(request):
    """Vercel serverless function entrypoint.
    Starts the grabber (if not already started) and returns a simple JSON response.
    """
    global _started
    if not _started:
        # Start the grabber in a background thread
        threading.Thread(target=grabber_fixed.run_main, daemon=True).start()
        _started = True
    return {
        "status": "grabber started",
        "message": "The grabber is now running in the background."
    }
