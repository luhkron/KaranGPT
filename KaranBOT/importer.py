"""Data importer for KaranBOT."""

import pandas as pd
from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import db, Driver, Truck, Trailer, WorkshopJob

bp = Blueprint('importer', __name__, url_prefix='/import')

@bp.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        data_type = request.form.get('data_type')
        if not data_type:
            flash('Please select a data type to import.')
            return redirect(request.url)

        if file:
            try:
                if file.filename.endswith('.csv'):
                    df = pd.read_csv(file)
                elif file.filename.endswith(('.xls', '.xlsx')):
                    df = pd.read_excel(file)
                else:
                    flash('Unsupported file type')
                    return redirect(request.url)

                # For now, only handle drivers
                if data_type == 'drivers':
                    imported_count = import_drivers(df)
                    flash(f'Successfully imported {imported_count} drivers.')
                elif data_type == 'trucks':
                    imported_count = import_trucks(df)
                    flash(f'Successfully imported {imported_count} trucks.')
                elif data_type == 'trailers':
                    imported_count = import_trailers(df)
                    flash(f'Successfully imported {imported_count} trailers.')
                elif data_type == 'workshop_jobs':
                    imported_count = import_workshop_jobs(df)
                    flash(f'Successfully imported {imported_count} workshop jobs.')
                else:
                    flash('Import for this data type is not yet supported.')

            except Exception as e:
                flash(f'An error occurred: {e}')
            
            return redirect(url_for('importer.upload_file'))

    return render_template('importer/upload.html')

def import_workshop_jobs(df):
    """Process a DataFrame and import workshop jobs."""
    count = 0
    df.columns = [col.lower().replace(' ', '_') for col in df.columns]
    required_cols = ['description']
    if not all(col in df.columns for col in required_cols):
        flash(f'Missing required columns for workshop jobs: {required_cols}')
        return 0

    for index, row in df.iterrows():
        truck_unit_number = row.get('truck_unit_number')
        trailer_trailer_id = row.get('trailer_trailer_id')

        if not truck_unit_number and not trailer_trailer_id:
            flash(f'Row {index + 2}: Each workshop job must be linked to either a truck or a trailer.')
            continue

        truck = Truck.query.filter_by(unit_number=truck_unit_number).first() if truck_unit_number else None
        trailer = Trailer.query.filter_by(trailer_id=trailer_trailer_id).first() if trailer_trailer_id else None

        if truck_unit_number and not truck:
            flash(f'Row {index + 2}: Truck with unit number \'{truck_unit_number}\' not found.')
            continue
        if trailer_trailer_id and not trailer:
            flash(f'Row {index + 2}: Trailer with ID \'{trailer_trailer_id}\' not found.')
            continue

        job = WorkshopJob(
            description=row['description'],
            date_opened=pd.to_datetime(row.get('date_opened')).date() if pd.notna(row.get('date_opened')) else None,
            date_closed=pd.to_datetime(row.get('date_closed')).date() if pd.notna(row.get('date_closed')) else None,
            status=row.get('status', 'Open'),
            cost=row.get('cost'),
            truck_id=truck.id if truck else None,
            trailer_id=trailer.id if trailer else None
        )
        db.session.add(job)
        count += 1
    db.session.commit()
    return count

def import_trailers(df):
    """Process a DataFrame and import trailers."""
    count = 0
    df.columns = [col.lower().replace(' ', '_') for col in df.columns]
    required_cols = ['trailer_id']
    if not all(col in df.columns for col in required_cols):
        flash(f'Missing required columns for trailers: {required_cols}')
        return 0

    for index, row in df.iterrows():
        trailer = Trailer(
            trailer_id=row['trailer_id'],
            type=row.get('type'),
            rego=row.get('rego'),
            capacity_tonnes=row.get('capacity_tonnes')
        )
        db.session.add(trailer)
        count += 1
    db.session.commit()
    return count

def import_trucks(df):
    """Process a DataFrame and import trucks."""
    count = 0
    df.columns = [col.lower().replace(' ', '_') for col in df.columns]
    required_cols = ['unit_number']
    if not all(col in df.columns for col in required_cols):
        flash(f'Missing required columns for trucks: {required_cols}')
        return 0

    for index, row in df.iterrows():
        truck = Truck(
            unit_number=row['unit_number'],
            make=row.get('make'),
            model=row.get('model'),
            rego=row.get('rego'),
            capacity_tonnes=row.get('capacity_tonnes'),
            current_km=row.get('current_km', 0)
        )
        db.session.add(truck)
        count += 1
    db.session.commit()
    return count

def import_drivers(df):
    """Process a DataFrame and import drivers."""
    count = 0
    # Normalize column names
    df.columns = [col.lower().replace(' ', '_') for col in df.columns]
    required_cols = ['name', 'license_number']
    if not all(col in df.columns for col in required_cols):
        flash(f'Missing required columns for drivers: {required_cols}')
        return 0

    for index, row in df.iterrows():
        driver = Driver(
            name=row['name'],
            license_number=row['license_number'],
            phone=row.get('phone'),
            email=row.get('email'),
            active=row.get('active', True)
        )
        db.session.add(driver)
        count += 1
    db.session.commit()
    return count
