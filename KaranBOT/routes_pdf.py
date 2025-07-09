import os
from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploaded_pdfs')
ALLOWED_EXTENSIONS = {'pdf'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

pdf_bp = Blueprint('pdf', __name__)

@pdf_bp.route('/upload_pdf', methods=['GET', 'POST'])
def upload_pdf():
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['pdf_file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and file.filename.lower().endswith('.pdf'):
            filename = secure_filename(file.filename)
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(save_path)
            flash('PDF uploaded successfully!')

            # --- Extract data from PDF and insert into DB ---
            import pdfplumber
            import pandas as pd
            from KaranBOT import db
            from KaranBOT.models import Driver, Truck, Trailer, WorkshopJob  # Adjust as needed
            extracted_rows = 0
            with pdfplumber.open(save_path) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        # Assume first row is header
                        headers = [str(h).strip() for h in table[0]]
                        for row in table[1:]:
                            row_dict = {headers[i]: (row[i] if i < len(row) else None) for i in range(len(headers))}
                            # Example: Parse and insert data
                            driver_name = str(row_dict.get("Driver", "")).strip()
                            truck_name = str(row_dict.get("Truck", "")).strip()
                            trailer_name = str(row_dict.get("Trailer", "")).strip()
                            # Add more fields as needed

                            # Insert Driver
                            if driver_name:
                                driver = Driver.query.filter_by(name=driver_name).first()
                                if not driver:
                                    driver = Driver(name=driver_name)
                                    db.session.add(driver)
                            # Insert Truck
                            if truck_name:
                                truck = Truck.query.filter_by(name=truck_name).first()
                                if not truck:
                                    truck = Truck(name=truck_name)
                                    db.session.add(truck)
                            # Insert Trailer
                            if trailer_name:
                                trailer = Trailer.query.filter_by(name=trailer_name).first()
                                if not trailer:
                                    trailer = Trailer(name=trailer_name)
                                    db.session.add(trailer)
                            # Add more logic for jobs, etc.
                            extracted_rows += 1
            db.session.commit()
            flash(f'Imported {extracted_rows} rows from PDF into the database!')
            return redirect(url_for('pdf.list_pdfs'))
        else:
            flash('Invalid file type. Only PDF allowed.')
            return redirect(request.url)
    return render_template('upload_pdf.html')

@pdf_bp.route('/pdfs')
def list_pdfs():
    files = os.listdir(UPLOAD_FOLDER)
    files = [f for f in files if f.lower().endswith('.pdf')]
    return render_template('list_pdfs.html', files=files)

@pdf_bp.route('/pdfs/<filename>')
def serve_pdf(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
