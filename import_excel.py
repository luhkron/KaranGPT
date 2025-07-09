import pandas as pd
from KaranBOT import create_app, db
from KaranBOT.models import Driver, Truck, Trailer, WorkshopJob  # Adjust as needed
from datetime import datetime

# Path to your Excel file
EXCEL_PATH = r"C:\Users\kshot\CascadeProjects\KaranBOT\Transport Daybook 2024.xlsx"

# Read the Excel file
df = pd.read_excel(EXCEL_PATH)

app = create_app()

with app.app_context():
    for idx, row in df.iterrows():
        # Example: Insert/update Driver
        driver_name = str(row.get("Driver", "")).strip()
        truck_name = str(row.get("Truck", "")).strip()
        trailer_name = str(row.get("Trailer", "")).strip()
        route = str(row.get("Route", "")).strip()
        date_str = str(row.get("Date", "")).strip()
        from_location = str(row.get("From", "")).strip()
        to_location = str(row.get("To", "")).strip()
        customer = str(row.get("Customer", "")).strip()
        details = str(row.get("Details", "")).strip()
        # Add more fields as needed

        # Example: Parse date
        try:
            date = pd.to_datetime(date_str, errors='coerce')
        except Exception:
            date = None

        # Only add static data: drivers, trucks, trailers
        if driver_name:
            driver = Driver.query.filter_by(name=driver_name).first()
            if not driver:
                driver = Driver(name=driver_name)
                db.session.add(driver)

        if truck_name:
            truck = Truck.query.filter_by(name=truck_name).first()
            if not truck:
                truck = Truck(name=truck_name)
                db.session.add(truck)

        if trailer_name:
            trailer = Trailer.query.filter_by(name=trailer_name).first()
            if not trailer:
                trailer = Trailer(name=trailer_name)
                db.session.add(trailer)
        # Do NOT import jobs or load numbers during this one-time import

    db.session.commit()

print("Static data import complete! Only drivers, trucks, and trailers were added.")
