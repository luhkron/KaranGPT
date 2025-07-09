from flask import Flask, render_template, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path
import os
from dotenv import load_dotenv

# ----------------------------------------------------
# KaranBOT – Fleet Management Assistant
# Package init: exposes create_app() for external use.
# ----------------------------------------------------

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    load_dotenv()  # Load environment variables from .env file

    # Configure SQLite DB inside project directory
    base_dir = Path(__file__).resolve().parent.parent
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{base_dir / 'karanbot.db'}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # Set secret key for session and flashing
    app.secret_key = 'karanbot-secret-key'  # You can change this to any random string

    # Import models so that SQLAlchemy registers tables
    from .models import Driver, Truck, Trailer, WorkshopJob

    # Register blueprints
    from .drivers import bp as drivers_bp
    from .trucks import bp as trucks_bp
    from .trailers import bp as trailers_bp
    from .workshop import bp as workshop_bp
    from .chatbot import chatbot_bp
    from .importer import bp as importer_bp
    app.register_blueprint(drivers_bp)
    app.register_blueprint(trucks_bp)
    app.register_blueprint(trailers_bp)
    app.register_blueprint(workshop_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(importer_bp)

    # Register PDF upload blueprint
    from .routes_pdf import pdf_bp
    app.register_blueprint(pdf_bp)
    from .routes_excel import excel_bp
    app.register_blueprint(excel_bp)


    @app.route("/")
    def index():
        """Homepage showing quick stats."""
        counts = {
            "drivers": Driver.query.count(),
            "trucks": Truck.query.count(),
            "trailers": Trailer.query.count(),
            "workshop_jobs": WorkshopJob.query.count(),
        }
        return render_template("index.html", **counts)

    # Ensure DB exists
    with app.app_context():
        db.create_all()

    return app
