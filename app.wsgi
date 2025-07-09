import os
import sys

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

from app import create_app, db

app = create_app()

# Initialize the database with the app
with app.app_context():
    db.create_all()
