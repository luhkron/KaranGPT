"""Database models for KaranBOT Fleet Management Assistant."""

from datetime import date
from . import db


class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    license_number = db.Column(db.String(64), unique=True, nullable=False)
    phone = db.Column(db.String(32))
    email = db.Column(db.String(120))
    active = db.Column(db.Boolean, default=True)
    # relationships
    trips = db.relationship("Trip", back_populates="driver")

    def __repr__(self):
        return f"<Driver {self.name}>"


class Truck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unit_number = db.Column(db.String(32), unique=True, nullable=False)
    make = db.Column(db.String(64))
    model = db.Column(db.String(64))
    rego = db.Column(db.String(32))
    capacity_tonnes = db.Column(db.Float)
    current_km = db.Column(db.Integer, default=0)
    # relationships
    trips = db.relationship("Trip", back_populates="truck")
    workshop_jobs = db.relationship("WorkshopJob", back_populates="truck")

    def __repr__(self):
        return f"<Truck {self.unit_number}>"


class Trailer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trailer_id = db.Column(db.String(32), unique=True, nullable=False)
    type = db.Column(db.String(64))
    rego = db.Column(db.String(32))
    capacity_tonnes = db.Column(db.Float)
    # relationships
    trips = db.relationship("Trip", back_populates="trailer")
    workshop_jobs = db.relationship("WorkshopJob", back_populates="trailer")

    def __repr__(self):
        return f"<Trailer {self.trailer_id}>"


class WorkshopJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    date_opened = db.Column(db.Date, default=date.today)
    date_closed = db.Column(db.Date)
    status = db.Column(db.String(32), default="Open")  # Open, In Progress, Closed
    cost = db.Column(db.Float)

    # FK to either truck or trailer
    truck_id = db.Column(db.Integer, db.ForeignKey("truck.id"))
    trailer_id = db.Column(db.Integer, db.ForeignKey("trailer.id"))

    # relationships
    truck = db.relationship("Truck", back_populates="workshop_jobs")
    trailer = db.relationship("Trailer", back_populates="workshop_jobs")

    def __repr__(self):
        return f"<WorkshopJob {self.id} - {self.status}>"


class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    origin = db.Column(db.String(120), nullable=False)
    destination = db.Column(db.String(120), nullable=False)
    date_start = db.Column(db.Date, default=date.today)
    date_end = db.Column(db.Date)

    # foreign keys
    driver_id = db.Column(db.Integer, db.ForeignKey("driver.id"), nullable=False)
    truck_id = db.Column(db.Integer, db.ForeignKey("truck.id"), nullable=False)
    trailer_id = db.Column(db.Integer, db.ForeignKey("trailer.id"))

    # relationships
    driver = db.relationship("Driver", back_populates="trips")
    truck = db.relationship("Truck", back_populates="trips")
    trailer = db.relationship("Trailer", back_populates="trips")

    def __repr__(self):
        return f"<Trip {self.id} {self.origin}->{self.destination}>"
