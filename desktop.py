"""Desktop wrapper for KaranBOT using pywebview.

Launches the Flask app in a background thread, then opens a native
window that loads the local web page. Build into a single executable
with PyInstaller:

    pyinstaller --noconfirm --noconsole --add-data "templates;templates" \
                --add-data "KaranBOT/static;KaranBOT/static" desktop.py

Run `python desktop.py` for local testing.
"""

import threading
import time
import webbrowser
from pathlib import Path

import webview
from KaranBOT import create_app

_FLASK_PORT = 5000
_URL = f"http://127.0.0.1:{_FLASK_PORT}/teletrac_navman"


def _start_flask():
    """Run Flask app (production settings: no reloader)."""
    app = create_app()
    # Disable Flask reloader; use a threaded server so it doesn't block.
    app.run(host="127.0.0.1", port=_FLASK_PORT, debug=False, use_reloader=False, threaded=True)


def launch_desktop():
    # Start Flask in background thread
    flask_thread = threading.Thread(target=_start_flask, daemon=True)
    flask_thread.start()

    # Wait briefly for server to start
    for _ in range(20):
        try:
            import requests
            requests.get(f"http://127.0.0.1:{_FLASK_PORT}")
            break
        except Exception:
            time.sleep(0.3)

    # Create webview window
    webview.create_window("KaranBOT", _URL, width=1280, height=800)
    webview.start(debug=False)


if __name__ == "__main__":
    launch_desktop()
