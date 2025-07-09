from flask import Flask, render_template, redirect, url_for, jsonify, abort, request
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path

# ----------------------------------------------------
# KaranBOT – Fleet Management Assistant
# ----------------------------------------------------
# Entry point of the Flask application. Creates the app,
# initialises the database, and wires up the blueprints.
# ----------------------------------------------------

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Configure SQLite DB in the project root
    base_dir = Path(__file__).resolve().parent
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{base_dir / 'kronbot.db'}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # Import models so that SQLAlchemy is aware of them
    from . import models  # noqa: F401

    @app.route("/")
    def index():
        """Homepage with quick stats and navigation."""
        from .models import Driver, Truck, Trailer, WorkshopJob

        counts = {
            "drivers": Driver.query.count(),
            "trucks": Truck.query.count(),
            "trailers": Trailer.query.count(),
            "workshop_jobs": WorkshopJob.query.count(),
        }
        return render_template("index.html", **counts)

    # Create database tables if they don't exist yet
    with app.app_context():
        db.create_all()

    # --- Teletrac Navman Integration ---
    from . import teletrac_navman

    # Dummy user check (replace with real authentication if needed)
    def is_current_user():
        # TODO: Replace with real authentication logic
        return True  # Only you can see this page

    @app.route("/teletrac_navman")
    def teletrac_navman_dashboard():
        if not is_current_user():
            abort(403)
        return render_template("teletrac_navman.html")

    @app.route("/teletrac_navman/trip_history")
    def teletrac_trip_history():
        if not is_current_user():
            abort(403)
        # Example: Get all vehicles and aggregate trip histories
        vehicles = teletrac_navman.get_vehicles().get("vehicles", [])
        trips = []
        for v in vehicles:
            try:
                v_trips = teletrac_navman.get_trip_history(v["id"]).get("trips", [])
                for trip in v_trips:
                    trips.append({
                        "vehicleName": v["name"],
                        "startTime": trip.get("startTime"),
                        "endTime": trip.get("endTime")
                    })
            except Exception:
                continue
        return jsonify(trips)

    @app.route("/teletrac_navman/alerts")
    def teletrac_alerts():
        if not is_current_user():
            abort(403)
        alerts = teletrac_navman.get_alerts().get("alerts", [])
        # Simplify for frontend
        return jsonify([
            {"type": a.get("type"), "description": a.get("description")} for a in alerts
        ])

    @app.route("/teletrac_navman/vehicles")
    def teletrac_vehicles():
        if not is_current_user():
            abort(403)
        vehicles = teletrac_navman.get_vehicles().get("vehicles", [])
        # Simplify for frontend: id, name, lat, lon
        return jsonify([
            {
                "id": v["id"],
                "name": v["name"],
                "lat": v.get("lastKnownPosition", {}).get("latitude", -33.8688),
                "lon": v.get("lastKnownPosition", {}).get("longitude", 151.2093)
            } for v in vehicles
        ])

    return app


# Create the application instance
app = create_app()

if __name__ == "__main__":
    # Debug mode for development; disable in production.
    app.run(debug=True)
