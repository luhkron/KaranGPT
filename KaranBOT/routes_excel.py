import os
import traceback
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
import pandas as pd
from KaranBOT import db
from KaranBOT.models import Driver, Truck, Trailer

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploaded_excels')
ALLOWED_EXTENSIONS = {'xlsx'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

excel_bp = Blueprint('excel', __name__)

@excel_bp.route('/upload_excel', methods=['GET', 'POST'])
def upload_excel():
    if request.method == 'POST':
        try:
            if 'excel_file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            
            file = request.files['excel_file']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            
            if not file.filename.lower().endswith(('.xlsx', '.xls')):
                flash('Invalid file type. Only .xlsx or .xls allowed.')
                return redirect(request.url)
            
            filename = secure_filename(file.filename)
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            try:
                file.save(save_path)
                current_app.logger.info(f"File saved to {save_path}")
            except Exception as e:
                flash(f'Error saving file: {str(e)}')
                current_app.logger.error(f'Error saving file: {str(e)}')
                return redirect(request.url)
            
            try:
                # Try reading with openpyxl first
                df = pd.read_excel(save_path, engine='openpyxl')
                current_app.logger.info("Successfully read Excel file with openpyxl")
            except Exception as e:
                current_app.logger.error(f"Error reading with openpyxl: {str(e)}")
                try:
                    # Fall back to xlrd for older .xls files
                    df = pd.read_excel(save_path, engine='xlrd')
                    current_app.logger.info("Successfully read Excel file with xlrd")
                except Exception as e2:
                    current_app.logger.error(f"Error reading with xlrd: {str(e2)}")
                    flash(f'Error reading Excel file. Please ensure it is a valid Excel file. Error: {str(e)}')
                    return redirect(request.url)
            
            # Log the columns in the uploaded file for debugging
            current_app.logger.info(f"Columns in uploaded file: {df.columns.tolist()}")
            
            drivers_added = set()
            trucks_added = set()
            trailers_added = set()
            
            # Try to find the correct column names (case-insensitive)
            df_columns_lower = [str(col).lower() for col in df.columns]
            driver_col = next((col for col in df.columns if 'driver' in str(col).lower()), None)
            truck_col = next((col for col in df.columns if 'truck' in str(col).lower()), None)
            trailer_col = next((col for col in df.columns if 'trailer' in str(col).lower()), None)
            
            if not (driver_col or truck_col or trailer_col):
                flash('Could not find expected columns (Driver, Truck, or Trailer) in the Excel file.')
                current_app.logger.error('Could not find expected columns in the Excel file')
                return redirect(request.url)
            
            for idx, row in df.iterrows():
                try:
                    driver_name = str(row.get(driver_col, '')).strip() if driver_col else ''
                    truck_name = str(row.get(truck_col, '')).strip() if truck_col else ''
                    trailer_name = str(row.get(trailer_col, '')).strip() if trailer_col else ''
                    
                    if driver_name and driver_name.lower() not in ['', 'nan', 'none']:
                        driver = Driver.query.filter_by(name=driver_name).first()
                        if not driver:
                            driver = Driver(name=driver_name)
                            db.session.add(driver)
                            drivers_added.add(driver_name)
                    
                    if truck_name and truck_name.lower() not in ['', 'nan', 'none']:
                        truck = Truck.query.filter_by(name=truck_name).first()
                        if not truck:
                            truck = Truck(name=truck_name)
                            db.session.add(truck)
                            trucks_added.add(truck_name)
                    
                    if trailer_name and trailer_name.lower() not in ['', 'nan', 'none']:
                        trailer = Trailer.query.filter_by(name=trailer_name).first()
                        if not trailer:
                            trailer = Trailer(name=trailer_name)
                            db.session.add(trailer)
                            trailers_added.add(trailer_name)
                            
                except Exception as e:
                    current_app.logger.error(f"Error processing row {idx}: {str(e)}"
                                         f"\nRow data: {row.to_dict()}")
            
            try:
                db.session.commit()
                flash(f"Imported {len(drivers_added)} drivers, {len(trucks_added)} trucks, and {len(trailers_added)} trailers from Excel!")
                current_app.logger.info(f"Successfully imported data: {len(drivers_added)} drivers, {len(trucks_added)} trucks, {len(trailers_added)} trailers")
            except Exception as e:
                db.session.rollback()
                flash(f'Error saving to database: {str(e)}')
                current_app.logger.error(f'Database error: {str(e)}')
                return redirect(request.url)
                
            return redirect(url_for('excel.upload_excel'))
            
        except Exception as e:
            error_msg = f'An unexpected error occurred: {str(e)}'
            current_app.logger.error(f"Unexpected error in upload_excel: {str(e)}\n{traceback.format_exc()}")
            flash(error_msg)
            return redirect(request.url)
    return render_template('upload_excel.html')
