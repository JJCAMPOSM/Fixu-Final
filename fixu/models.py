from datetime import datetime
from flask_login import UserMixin
import bcrypt

from .extensions import db
from .crypto import EncryptedString


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class User(UserMixin, db.Model, TimestampMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin|agent|requester
    avatar = db.Column(db.String(255), nullable=True)

    team_members = db.relationship('TeamMember', back_populates='user', cascade='all, delete-orphan')
    ticket_events = db.relationship('TicketEvent', back_populates='user', cascade='all, delete-orphan')

    def set_password(self, password: str):
        # Laravel usa hashes bcrypt estándar
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
        except ValueError:
            return False


class Team(db.Model, TimestampMixin):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

    members = db.relationship('TeamMember', back_populates='team', cascade='all, delete-orphan')
    tickets = db.relationship('Ticket', back_populates='team')


class TeamMember(db.Model, TimestampMixin):
    __tablename__ = 'team_members'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)

    user = db.relationship('User', back_populates='team_members')
    team = db.relationship('Team', back_populates='members')
    comments = db.relationship('Comment', back_populates='team_member')

    __table_args__ = (db.UniqueConstraint('user_id', 'team_id', name='uq_team_member'),)


class Requester(db.Model, TimestampMixin):
    __tablename__ = 'requesters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    # Cifrado en reposo (Fernet, ver crypto.py): dato personal (PII) que solo
    # se usa para mostrarlo/contactar, nunca para filtrar/buscar en BD.
    phone = db.Column(EncryptedString, nullable=True)

    tickets = db.relationship('Ticket', back_populates='requester')


class Category(db.Model, TimestampMixin):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    color = db.Column(db.String(7), nullable=True, default='#6366f1')  # Hex color for UI

    tickets = db.relationship('Ticket', back_populates='category')


class Ticket(db.Model, TimestampMixin):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    requester_id = db.Column(db.Integer, db.ForeignKey('requesters.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)
    assignee_team_member_id = db.Column(db.Integer, db.ForeignKey('team_members.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending|assigned|in_progress|on_hold|cancelled|resolved
    resolved_at = db.Column(db.DateTime, nullable=True)  # fecha de cierre, se fija al pasar a 'resolved'
    priority = db.Column(db.String(20), nullable=False, default='medium')  # low|medium|high
    rating = db.Column(db.Integer, nullable=False, default=0)
    building = db.Column(db.String(80), nullable=True)  # edificio donde está el equipo (reportado por el solicitante)
    classroom = db.Column(db.String(80), nullable=True)  # aula/salón
    equipment_type = db.Column(db.String(80), nullable=True)  # tipo de equipo (proyector, computadora, etc.)
    photo_path = db.Column(db.String(255), nullable=True)  # foto adjunta desde la App Móvil
    resolution_photo_path = db.Column(db.String(255), nullable=True)  # foto de resolución subida por agente/admin desde la web
    source = db.Column(db.String(20), nullable=False, default='web')  # web|mobile

    requester = db.relationship('Requester', back_populates='tickets')
    team = db.relationship('Team', back_populates='tickets')
    assignee = db.relationship('TeamMember')
    category = db.relationship('Category', back_populates='tickets')
    comments = db.relationship('Comment', back_populates='ticket', cascade='all, delete-orphan')
    events = db.relationship('TicketEvent', back_populates='ticket', cascade='all, delete-orphan')

    @staticmethod
    def _photo_web_url(photo_path):
        """URL relativa (mismo origen) para servir una foto vía la ruta
        autenticada /uploads/tickets/<archivo>. A diferencia de
        _public_photo_url (usado por la App Móvil, que necesita una URL
        absoluta con PUBLIC_BASE_URL), la web puede usar una ruta relativa
        normal porque el navegador ya está en el mismo origen."""
        if not photo_path:
            return None
        from flask import url_for
        filename = photo_path.rsplit('/', 1)[-1]
        return url_for('api.ticket_photo', filename=filename)

    @property
    def photo_url(self):
        return self._photo_web_url(self.photo_path)

    @property
    def resolution_photo_url(self):
        return self._photo_web_url(self.resolution_photo_path)


class Comment(db.Model, TimestampMixin):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    team_member_id = db.Column(db.Integer, db.ForeignKey('team_members.id'), nullable=False)
    private = db.Column(db.Boolean, nullable=False, default=False)
    body = db.Column(db.Text, nullable=False)

    ticket = db.relationship('Ticket', back_populates='comments')
    team_member = db.relationship('TeamMember', back_populates='comments')


class TicketEvent(db.Model, TimestampMixin):
    __tablename__ = 'ticket_events'
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    body = db.Column(db.Text, nullable=False)

    ticket = db.relationship('Ticket', back_populates='events')
    user = db.relationship('User', back_populates='ticket_events')


class MaintenanceTask(db.Model, TimestampMixin):
    __tablename__ = 'maintenance_tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(200), nullable=True)
    assignee_team_member_id = db.Column(db.Integer, db.ForeignKey('team_members.id'), nullable=False)
    scheduled_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending|done

    assignee = db.relationship('TeamMember')
    checklist_items = db.relationship(
        'ChecklistItem', back_populates='maintenance_task',
        cascade='all, delete-orphan', order_by='ChecklistItem.id',
    )


class ChecklistItem(db.Model, TimestampMixin):
    __tablename__ = 'checklist_items'
    id = db.Column(db.Integer, primary_key=True)
    maintenance_task_id = db.Column(db.Integer, db.ForeignKey('maintenance_tasks.id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    is_done = db.Column(db.Boolean, nullable=False, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    maintenance_task = db.relationship('MaintenanceTask', back_populates='checklist_items')


class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # Se guarda el hash del token, nunca el token en claro (mismo criterio
    # que password_hash): si la BD se filtra, no alcanza para resetear cuentas.
    token_hash = db.Column(db.String(255), nullable=False, unique=True, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User')


class SatisfactionTicket(db.Model, TimestampMixin):
    __tablename__ = 'satisfaccion_tickets'
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    calificacion = db.Column(db.Integer, nullable=False)
    comentario = db.Column(db.Text, nullable=True)
    fecha_envio = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    ticket = db.relationship('Ticket')
    user = db.relationship('User')
    
    __table_args__ = (
        db.UniqueConstraint('ticket_id', name='uq_satisfaccion_ticket'),
    )
