from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import or_
from .models import Driver
from . import db

bp = Blueprint('drivers', __name__, url_prefix='/drivers')

@bp.route('/')
def list_drivers():
    query = request.args.get('q')
    if query:
        search_term = f"%{query}%"
        drivers_query = Driver.query.filter(
            or_(
                Driver.name.ilike(search_term),
                Driver.license_number.ilike(search_term),
                Driver.phone.ilike(search_term),
                Driver.email.ilike(search_term)
            )
        )
    else:
        drivers_query = Driver.query

    drivers = drivers_query.order_by(Driver.name).all()
    return render_template('drivers/list.html', drivers=drivers)

@bp.route('/add', methods=['GET', 'POST'])
def add_driver():
    if request.method == 'POST':
        name = request.form['name']
        license_number = request.form['license_number']
        phone = request.form['phone']
        email = request.form['email']
        active = 'active' in request.form
        if not name or not license_number:
            flash('Name and license number are required.')
        else:
            driver = Driver(name=name, license_number=license_number, phone=phone, email=email, active=active)
            db.session.add(driver)
            db.session.commit()
            flash('Driver added!')
            return redirect(url_for('drivers.list_drivers'))
    return render_template('drivers/add_edit.html', action='Add')

@bp.route('/edit/<int:driver_id>', methods=['GET', 'POST'])
def edit_driver(driver_id):
    driver = Driver.query.get_or_404(driver_id)
    if request.method == 'POST':
        driver.name = request.form['name']
        driver.license_number = request.form['license_number']
        driver.phone = request.form['phone']
        driver.email = request.form['email']
        driver.active = 'active' in request.form
        db.session.commit()
        flash('Driver updated!')
        return redirect(url_for('drivers.list_drivers'))
    return render_template('drivers/add_edit.html', action='Edit', driver=driver)

@bp.route('/delete/<int:driver_id>', methods=['POST'])
def delete_driver(driver_id):
    driver = Driver.query.get_or_404(driver_id)
    db.session.delete(driver)
    db.session.commit()
    flash('Driver deleted!')
    return redirect(url_for('drivers.list_drivers'))
