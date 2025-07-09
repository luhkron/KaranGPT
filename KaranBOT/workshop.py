from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import or_
from .models import WorkshopJob, Truck, Trailer
from . import db

bp = Blueprint('workshop', __name__, url_prefix='/workshop')

@bp.route('/')
def list_jobs():
    query = request.args.get('q')
    jobs_query = WorkshopJob.query.outerjoin(Truck).outerjoin(Trailer)

    if query:
        search_term = f"%{query}%"
        jobs_query = jobs_query.filter(
            or_(
                WorkshopJob.description.ilike(search_term),
                WorkshopJob.status.ilike(search_term),
                Truck.unit_number.ilike(search_term),
                Trailer.trailer_id.ilike(search_term)
            )
        )

    jobs = jobs_query.order_by(WorkshopJob.date_opened.desc()).all()
    return render_template('workshop/list.html', jobs=jobs)

@bp.route('/add', methods=['GET', 'POST'])
def add_job():
    trucks = Truck.query.order_by(Truck.unit_number).all()
    trailers = Trailer.query.order_by(Trailer.trailer_id).all()
    if request.method == 'POST':
        description = request.form['description']
        status = request.form['status']
        cost = request.form['cost'] or None
        truck_id = request.form.get('truck_id') or None
        trailer_id = request.form.get('trailer_id') or None
        job = WorkshopJob(description=description, status=status, cost=cost,
                          truck_id=truck_id, trailer_id=trailer_id)
        db.session.add(job)
        db.session.commit()
        flash('Workshop job added!')
        return redirect(url_for('workshop.list_jobs'))
    return render_template('workshop/add_edit.html', action='Add', trucks=trucks, trailers=trailers)

@bp.route('/edit/<int:job_id>', methods=['GET', 'POST'])
def edit_job(job_id):
    job = WorkshopJob.query.get_or_404(job_id)
    trucks = Truck.query.order_by(Truck.unit_number).all()
    trailers = Trailer.query.order_by(Trailer.trailer_id).all()
    if request.method == 'POST':
        job.description = request.form['description']
        job.status = request.form['status']
        job.cost = request.form['cost'] or None
        job.truck_id = request.form.get('truck_id') or None
        job.trailer_id = request.form.get('trailer_id') or None
        db.session.commit()
        flash('Workshop job updated!')
        return redirect(url_for('workshop.list_jobs'))
    return render_template('workshop/add_edit.html', action='Edit', job=job, trucks=trucks, trailers=trailers)

@bp.route('/delete/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    job = WorkshopJob.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    flash('Workshop job deleted!')
    return redirect(url_for('workshop.list_jobs'))
