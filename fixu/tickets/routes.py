from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload

from . import bp
from .forms import TicketForm, CommentForm
from ..extensions import db
from ..models import Ticket, Requester, Team, TeamMember, Comment, TicketEvent, Category, SatisfactionTicket, User
from ..services.bridge_client import get_bridge_client


def is_admin_or_agent():
    return current_user.is_authenticated and current_user.role in ('admin', 'agent')


@bp.route('/')
@login_required
def index():
    query = Ticket.query.options(
        joinedload(Ticket.requester),
        joinedload(Ticket.team),
        joinedload(Ticket.assignee).joinedload(TeamMember.user)
    ).order_by(Ticket.created_at.desc())

    status = request.args.get('status', type=str)
    priority = request.args.get('priority', type=str)
    team_id = request.args.get('team_id', type=int)
    assignee_id = request.args.get('assignee_id', type=int)

    if status:
        query = query.filter(Ticket.status == status)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if team_id:
        query = query.filter(Ticket.team_id == team_id)
    if assignee_id:
        query = query.filter(Ticket.assignee_team_member_id == assignee_id)

    if current_user.role == 'requester':
        requester = Requester.query.filter_by(email=current_user.email).first()
        if requester:
            query = query.filter(Ticket.requester_id == requester.id)
        else:
            query = query.filter(False)

    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=10, error_out=False)

    teams = Team.query.order_by(Team.name).all() if is_admin_or_agent() else []

    return render_template('tickets/index.html', pagination=pagination, tickets=pagination.items, teams=teams)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = TicketForm()

    # Solo admins y agentes necesitan ver las opciones de solicitantes y equipos
    if is_admin_or_agent():
        requesters = Requester.query.order_by(Requester.name).all()
        form.requester_id.choices = [(r.id, f"{r.name} <{r.email}>") for r in requesters]

        categories = Category.query.order_by(Category.name).all()
        form.category_id.choices = [(0, '— Ninguna —')] + [(c.id, c.name) for c in categories]

        teams = Team.query.order_by(Team.name).all()
        form.team_id.choices = [(0, '— Ninguno —')] + [(t.id, t.name) for t in teams]
        
        # Show all team members from all teams
        all_members = TeamMember.query.join(User).order_by(User.name).all()
        form.assignee_team_member_id.choices = [(0, '— Ninguno —')] + [
            (m.id, f"{m.user.name} ({m.team.name})") for m in all_members
        ]
    else:
        # Para solicitantes, establecer valores dummy (no se usarán)
        form.requester_id.choices = [(0, '')]
        form.category_id.choices = [(0, '')]
        form.team_id.choices = [(0, '')]
        form.assignee_team_member_id.choices = [(0, '')]

    if not is_admin_or_agent() and current_user.role != 'requester':
        flash('No autorizado.', 'danger')
        return redirect(url_for('tickets.index'))

    if form.validate_on_submit():
        # Si es solicitante, forzar valores específicos
        if current_user.role == 'requester':
            req = Requester.query.filter_by(email=current_user.email).first()
            if not req:
                flash('Error: No se encontró perfil de solicitante.', 'danger')
                return redirect(url_for('tickets.index'))

            ticket = Ticket(
                title=form.title.data.strip(),
                body=form.body.data.strip(),
                requester_id=req.id,
                category_id=None,
                team_id=None,
                assignee_team_member_id=None,
                status='open',
                priority=form.priority.data
            )
        else:
            # Para admins y agentes, validar campos requeridos
            if not form.requester_id.data or form.requester_id.data == 0:
                flash('Debe seleccionar un solicitante.', 'danger')
                return render_template('tickets/form.html', form=form, mode='create')

            if not form.status.data:
                flash('Debe seleccionar un estado.', 'danger')
                return render_template('tickets/form.html', form=form, mode='create')

            if not form.priority.data:
                flash('Debe seleccionar una prioridad.', 'danger')
                return render_template('tickets/form.html', form=form, mode='create')

            # Usar los valores del formulario
            assignee_value = form.assignee_team_member_id.data or 0
            team_value = form.team_id.data or 0
            category_value = form.category_id.data or 0
            ticket = Ticket(
                title=form.title.data.strip(),
                body=form.body.data.strip(),
                requester_id=form.requester_id.data,
                category_id=category_value if category_value != 0 else None,
                team_id=team_value if team_value != 0 else None,
                assignee_team_member_id=assignee_value if assignee_value != 0 else None,
                status=form.status.data,
                priority=form.priority.data
            )

        db.session.add(ticket)
        db.session.flush()
        db.session.add(TicketEvent(ticket_id=ticket.id, user_id=current_user.id, body='Ticket creado'))
        db.session.commit()
        
        # Sincronizar con Laravel a través del Bridge API
        try:
            bridge = get_bridge_client()
            ticket_data = {
                'id': ticket.id,
                'title': ticket.title,
                'body': ticket.body,
                'requester_id': ticket.requester_id,
                'team_id': ticket.team_id,
                'assignee_team_member_id': ticket.assignee_team_member_id,
                'category_id': ticket.category_id,
                'status': ticket.status,
                'priority': ticket.priority,
                'created_at': ticket.created_at.isoformat() if ticket.created_at else None,
            }
            result = bridge.sync_ticket('create', ticket_data, source='flask')
            if not result.get('success'):
                current_app.logger.warning(f"Sync ticket to bridge failed: {result}")
        except Exception as e:
            current_app.logger.error(f"Error syncing ticket to bridge: {e}")
        
        flash('Ticket creado con éxito.', 'success')
        return redirect(url_for('tickets.show', ticket_id=ticket.id))

    return render_template('tickets/form.html', form=form, mode='create')


@bp.route('/<int:ticket_id>')
@login_required
def show(ticket_id):
    ticket = Ticket.query.options(
        joinedload(Ticket.requester),
        joinedload(Ticket.team),
        joinedload(Ticket.assignee).joinedload(TeamMember.user),
        joinedload(Ticket.comments).joinedload(Comment.team_member).joinedload(TeamMember.user),
        joinedload(Ticket.events)
    ).get_or_404(ticket_id)

    if current_user.role == 'requester':
        req = Requester.query.filter_by(email=current_user.email).first()
        if not req or ticket.requester_id != req.id:
            flash('No autorizado.', 'danger')
            return redirect(url_for('tickets.index'))

    comment_form = CommentForm()
    has_feedback = SatisfactionTicket.query.filter_by(ticket_id=ticket_id).first() is not None
    return render_template('tickets/show.html', ticket=ticket, comment_form=comment_form, has_feedback=has_feedback)


@bp.route('/<int:ticket_id>/comment', methods=['POST'])
@login_required
def add_comment(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    form = CommentForm()
    if form.validate_on_submit():
        if not is_admin_or_agent():
            flash('Solo agentes o admins pueden comentar.', 'danger')
            return redirect(url_for('tickets.show', ticket_id=ticket.id))
        tm = TeamMember.query.filter_by(user_id=current_user.id).first()
        if not tm:
            flash('No estás asignado a un equipo.', 'danger')
            return redirect(url_for('tickets.show', ticket_id=ticket.id))
        comment = Comment(ticket_id=ticket.id, team_member_id=tm.id, private=bool(form.private.data), body=form.body.data.strip())
        db.session.add(comment)
        db.session.add(TicketEvent(ticket_id=ticket.id, user_id=current_user.id, body='Comentario agregado'))
        db.session.commit()
        flash('Comentario agregado.', 'success')
    else:
        flash('Error al agregar comentario.', 'danger')
    return redirect(url_for('tickets.show', ticket_id=ticket.id))


@bp.route('/<int:ticket_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    if not is_admin_or_agent():
        flash('No autorizado.', 'danger')
        return redirect(url_for('tickets.show', ticket_id=ticket.id))

    form = TicketForm(obj=ticket)

    requesters = Requester.query.order_by(Requester.name).all()
    form.requester_id.choices = [(r.id, f"{r.name} <{r.email}>") for r in requesters]

    categories = Category.query.order_by(Category.name).all()
    form.category_id.choices = [(0, '— Ninguna —')] + [(c.id, c.name) for c in categories]

    teams = Team.query.order_by(Team.name).all()
    form.team_id.choices = [(0, '— Ninguno —')] + [(t.id, t.name) for t in teams]

    # Populate assignee dropdown
    members = []
    if ticket.team_id:
        # If ticket has a team, show only members from that team
        members = TeamMember.query.filter_by(team_id=ticket.team_id).all()
    else:
        # If no team assigned, show ALL team members from ALL teams
        members = TeamMember.query.join(User).order_by(User.name).all()
    
    form.assignee_team_member_id.choices = [(0, '— Ninguno —')] + [
        (m.id, f"{m.user.name} ({m.team.name})") for m in members
    ]

    # Pre-validación: sincronizar opciones de assignee con el team_id seleccionado en el POST
    if request.method == 'POST' and form.team_id.data:
        team_id_from_form = form.team_id.data
        if team_id_from_form and team_id_from_form != 0:
            # Recargar los miembros del equipo seleccionado en el formulario
            members_from_selected_team = TeamMember.query.filter_by(team_id=team_id_from_form).all()
            form.assignee_team_member_id.choices = [(0, '— Ninguno —')] + [
                (m.id, f"{m.user.name} ({m.team.name})") for m in members_from_selected_team
            ]
        else:
            # Si no hay equipo seleccionado, mostrar TODOS los miembros de TODOS los equipos
            all_members = TeamMember.query.join(User).order_by(User.name).all()
            form.assignee_team_member_id.choices = [(0, '— Ninguno —')] + [
                (m.id, f"{m.user.name} ({m.team.name})") for m in all_members
            ]

    if form.validate_on_submit():
        assignee_value = form.assignee_team_member_id.data or 0
        team_value = form.team_id.data or 0
        category_value = form.category_id.data or 0
        ticket.title = form.title.data.strip()
        ticket.body = form.body.data.strip()
        ticket.requester_id = form.requester_id.data
        ticket.category_id = category_value if category_value != 0 else None
        ticket.team_id = team_value if team_value != 0 else None
        ticket.assignee_team_member_id = assignee_value if assignee_value != 0 else None
        ticket.status = form.status.data
        ticket.priority = form.priority.data
        db.session.add(TicketEvent(ticket_id=ticket.id, user_id=current_user.id, body='Ticket actualizado'))
        db.session.commit()
        flash('Ticket actualizado.', 'success')
        return redirect(url_for('tickets.show', ticket_id=ticket.id))

    return render_template('tickets/form.html', form=form, mode='edit', ticket=ticket)


@bp.route('/<int:ticket_id>/delete', methods=['POST'])
@login_required
def delete(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if not is_admin_or_agent():
        flash('No autorizado.', 'danger')
        return redirect(url_for('tickets.show', ticket_id=ticket.id))
    db.session.delete(ticket)
    db.session.commit()
    flash('Ticket eliminado.', 'warning')
    return redirect(url_for('tickets.index'))
