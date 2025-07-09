from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import or_
from .models import Truck
from . import db

bp = Blueprint('trucks', __name__, url_prefix='/trucks')

@bp.route('/')
def list_trucks():
    query = request.args.get('q')
    if query:
        search_term = f"%{query}%"
        trucks_query = Truck.query.filter(
            or_(
                Truck.unit_number.ilike(search_term),
                Truck.make.ilike(search_term),
                Truck.model.ilike(search_term),
                Truck.rego.ilike(search_term)
            )
        )
    else:
        trucks_query = Truck.query

    trucks = trucks_query.order_by(Truck.unit_number).all()
    return render_template('trucks/list.html', trucks=trucks)

@bp.route('/add', methods=['GET', 'POST'])
def add_truck():
    if request.method == 'POST':
        unit_number = request.form['unit_number']
        make = request.form['make']
        model = request.form['model']
        rego = request.form['rego']
        capacity_tonnes = request.form['capacity_tonnes']
        current_km = request.form['current_km']
        if not unit_number:
            flash('Unit number is required.')
        else:
            truck = Truck(unit_number=unit_number, make=make, model=model, rego=rego,
                          capacity_tonnes=capacity_tonnes or None, current_km=current_km or 0)
            db.session.add(truck)
            db.session.commit()
            flash('Truck added!')
            return redirect(url_for('trucks.list_trucks'))
    return render_template('trucks/add_edit.html', action='Add')

@bp.route('/edit/<int:truck_id>', methods=['GET', 'POST'])
def edit_truck(truck_id):
    truck = Truck.query.get_or_404(truck_id)
    if request.method == 'POST':
        truck.unit_number = request.form['unit_number']
        truck.make = request.form['make']
        truck.model = request.form['model']
        truck.rego = request.form['rego']
        truck.capacity_tonnes = request.form['capacity_tonnes'] or None
        truck.current_km = request.form['current_km'] or 0
        db.session.commit()
        flash('Truck updated!')
        return redirect(url_for('trucks.list_trucks'))
    return render_template('trucks/add_edit.html', action='Edit', truck=truck)

@bp.route('/delete/<int:truck_id>', methods=['POST'])
def delete_truck(truck_id):
    truck = Truck.query.get_or_404(truck_id)
    db.session.delete(truck)
    db.session.commit()
    flash('Truck deleted!')
    return redirect(url_for('trucks.list_trucks'))
