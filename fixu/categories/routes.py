from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from . import bp
from .forms import CategoryForm
from ..extensions import db
from ..models import Category


def is_admin():
    return current_user.is_authenticated and current_user.role == 'admin'


@bp.route('/')
@login_required
def index():
    if not is_admin():
        flash('No autorizado. Solo administradores pueden acceder a esta sección.', 'danger')
        return redirect(url_for('tickets.index'))

    query = Category.query.order_by(Category.name)
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=15, error_out=False)

    return render_template('categories/index.html', pagination=pagination, categories=pagination.items)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if not is_admin():
        flash('No autorizado. Solo administradores pueden acceder a esta sección.', 'danger')
        return redirect(url_for('tickets.index'))

    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(
            name=form.name.data.strip(),
            description=form.description.data.strip() if form.description.data else None,
            color=form.color.data.strip() if form.color.data else '#6366f1'
        )
        db.session.add(category)
        db.session.commit()
        flash('Categoría creada con éxito.', 'success')
        return redirect(url_for('categories.index'))

    return render_template('categories/form.html', form=form, mode='create')


@bp.route('/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(category_id):
    if not is_admin():
        flash('No autorizado. Solo administradores pueden acceder a esta sección.', 'danger')
        return redirect(url_for('tickets.index'))

    category = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=category)

    if form.validate_on_submit():
        category.name = form.name.data.strip()
        category.description = form.description.data.strip() if form.description.data else None
        category.color = form.color.data.strip() if form.color.data else '#6366f1'
        db.session.commit()
        flash('Categoría actualizada con éxito.', 'success')
        return redirect(url_for('categories.index'))

    return render_template('categories/form.html', form=form, mode='edit', category=category)


@bp.route('/<int:category_id>/delete', methods=['POST'])
@login_required
def delete(category_id):
    if not is_admin():
        flash('No autorizado. Solo administradores pueden acceder a esta sección.', 'danger')
        return redirect(url_for('tickets.index'))

    category = Category.query.get_or_404(category_id)

    # Verificar si hay tickets asociados
    if category.tickets:
        flash(f'No se puede eliminar. Hay {len(category.tickets)} ticket(s) asociados a esta categoría.', 'danger')
        return redirect(url_for('categories.index'))

    db.session.delete(category)
    db.session.commit()
    flash('Categoría eliminada.', 'warning')
    return redirect(url_for('categories.index'))
