"""Convenience runner for KaranBOT.
Usage: python run.py
"""

from KaranBOT import create_app

app = create_app()

if __name__ == "__main__":
    # Bind to 0.0.0.0 so Browsers preview can access
    app.run(host="0.0.0.0", port=5000, debug=True)
