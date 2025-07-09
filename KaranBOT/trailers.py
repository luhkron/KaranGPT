from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import or_
from .models import Trailer
from . import db

bp = Blueprint('trailers', __name__, url_prefix='/trailers')

@bp.route('/')
def list_trailers():
    query = request.args.get('q')
    if query:
        search_term = f"%{query}%"
        trailers_query = Trailer.query.filter(
            or_(
                Trailer.trailer_id.ilike(search_term),
                Trailer.type.ilike(search_term),
                Trailer.rego.ilike(search_term)
            )
        )
    else:
        trailers_query = Trailer.query

    trailers = trailers_query.order_by(Trailer.trailer_id).all()
    return render_template('trailers/list.html', trailers=trailers)

@bp.route('/add', methods=['GET', 'POST'])
def add_trailer():
    if request.method == 'POST':
        trailer_id = request.form['trailer_id']
        type_ = request.form['type']
        rego = request.form['rego']
        capacity_tonnes = request.form['capacity_tonnes']
        if not trailer_id:
            flash('Trailer ID is required.')
        else:
            trailer = Trailer(trailer_id=trailer_id, type=type_, rego=rego, capacity_tonnes=capacity_tonnes or None)
            db.session.add(trailer)
            db.session.commit()
            flash('Trailer added!')
            return redirect(url_for('trailers.list_trailers'))
    return render_template('trailers/add_edit.html', action='Add')

@bp.route('/edit/<int:trailer_id>', methods=['GET', 'POST'])
def edit_trailer(trailer_id):
    trailer = Trailer.query.get_or_404(trailer_id)
    if request.method == 'POST':
        trailer.trailer_id = request.form['trailer_id']
        trailer.type = request.form['type']
        trailer.rego = request.form['rego']
        trailer.capacity_tonnes = request.form['capacity_tonnes'] or None
        db.session.commit()
        flash('Trailer updated!')
        return redirect(url_for('trailers.list_trailers'))
    return render_template('trailers/add_edit.html', action='Edit', trailer=trailer)

@bp.route('/delete/<int:trailer_id>', methods=['POST'])
def delete_trailer(trailer_id):
    trailer = Trailer.query.get_or_404(trailer_id)
    db.session.delete(trailer)
    db.session.commit()
    flash('Trailer deleted!')
    return redirect(url_for('trailers.list_trailers'))
