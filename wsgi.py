from app import create_app, db

app = create_app()

# Initialize the database with the app
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
