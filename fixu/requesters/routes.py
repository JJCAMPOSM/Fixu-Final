from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from . import bp
from .forms import RequesterForm
from ..extensions import db
from ..models import Requester, Ticket


@bp.route('/')
@login_required
def index():
    if current_user.role != 'admin':
        flash('No autorizado. Solo administradores pueden acceder a esta sección.', 'danger')
        return redirect(url_for('tickets.index'))

    query = Requester.query.order_by(Requester.created_at.desc())
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=10)

    return render_template('requesters/index.html', pagination=pagination, requesters=pagination.items)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if current_user.role != 'admin':
        flash('No autorizado. Solo administradores pueden acceder a esta sección.', 'danger')
        return redirect(url_for('tickets.index'))

    form = RequesterForm()
    if form.validate_on_submit():
        req = Requester(name=form.name.data.strip(), email=form.email.data.strip().lower(), phone=form.phone.data.strip() if form.phone.data else None)
        db.session.add(req)
        db.session.commit()
        flash('Solicitante creado.', 'success')
        return redirect(url_for('requesters.index'))
    return render_template('requesters/form.html', form=form, mode='create')


@bp.route('/<int:req_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(req_id):
    if current_user.role != 'admin':
        flash('No autorizado. Solo administradores pueden acceder a esta sección.', 'danger')
        return redirect(url_for('tickets.index'))

    req = Requester.query.get_or_404(req_id)
    form = RequesterForm(obj=req)
    if form.validate_on_submit():
        req.name = form.name.data.strip()
        req.email = form.email.data.strip().lower()
        req.phone = form.phone.data.strip() if form.phone.data else None
        db.session.commit()
        flash('Solicitante actualizado.', 'success')
        return redirect(url_for('requesters.index'))
    return render_template('requesters/form.html', form=form, mode='edit', requester=req)


@bp.route('/<int:req_id>/delete', methods=['POST'])
@login_required
def delete(req_id):
    if current_user.role != 'admin':
        flash('No autorizado. Solo administradores pueden acceder a esta sección.', 'danger')
        return redirect(url_for('tickets.index'))

    req = Requester.query.get_or_404(req_id)

    # Eliminar todos los tickets asociados con este requester antes de borrarlo
    Ticket.query.filter_by(requester_id=req_id).delete()

    db.session.delete(req)
    db.session.commit()
    flash('Solicitante eliminado.', 'warning')
    return redirect(url_for('requesters.index'))
