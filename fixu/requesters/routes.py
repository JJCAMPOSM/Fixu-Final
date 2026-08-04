from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from . import bp
from .forms import RequesterForm
from ..extensions import db
from ..models import Requester, Ticket, User


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
        if not form.password.data:
            flash('La contraseña es requerida al crear un solicitante.', 'danger')
            return render_template('requesters/form.html', form=form, mode='create')

        email = form.email.data.strip().lower()

        if Requester.query.filter_by(email=email).first():
            flash('Ya existe un solicitante con este correo.', 'danger')
            return render_template('requesters/form.html', form=form, mode='create')
        if User.query.filter_by(email=email).first():
            flash('Este correo ya está registrado como usuario.', 'danger')
            return render_template('requesters/form.html', form=form, mode='create')

        name = form.name.data.strip()
        req = Requester(name=name, email=email, phone=form.phone.data.strip())
        db.session.add(req)

        user = User(name=name, email=email, role='requester')
        user.set_password(form.password.data)
        db.session.add(user)

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
        new_email = form.email.data.strip().lower()
        old_email = req.email

        if new_email != old_email and Requester.query.filter(Requester.email == new_email, Requester.id != req_id).first():
            flash('Ya existe un solicitante con este correo.', 'danger')
            return render_template('requesters/form.html', form=form, mode='edit', requester=req)

        linked_user = User.query.filter_by(email=old_email, role='requester').first()
        other_user = User.query.filter(User.email == new_email).first()
        if new_email != old_email and other_user and (not linked_user or other_user.id != linked_user.id):
            flash('Este correo ya está registrado como usuario.', 'danger')
            return render_template('requesters/form.html', form=form, mode='edit', requester=req)

        name = form.name.data.strip()
        req.name = name
        req.email = new_email
        req.phone = form.phone.data.strip()

        if linked_user:
            linked_user.name = name
            linked_user.email = new_email
            if form.password.data:
                linked_user.set_password(form.password.data)
        elif form.password.data:
            # Solicitante creado antes de que existiera este campo: todavía no
            # tenía cuenta de acceso. La creamos ahora con la contraseña dada.
            new_user = User(name=name, email=new_email, role='requester')
            new_user.set_password(form.password.data)
            db.session.add(new_user)

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
