from datetime import datetime
from flask_login import UserMixin
import bcrypt

from .extensions import db


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
    phone = db.Column(db.String(20), nullable=True)

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
    status = db.Column(db.String(20), nullable=False, default='open')  # open|pending|solved|closed
    priority = db.Column(db.String(20), nullable=False, default='medium')  # low|medium|high
    rating = db.Column(db.Integer, nullable=False, default=0)
    photo_path = db.Column(db.String(255), nullable=True)  # foto adjunta desde la App Móvil
    source = db.Column(db.String(20), nullable=False, default='web')  # web|mobile

    requester = db.relationship('Requester', back_populates='tickets')
    team = db.relationship('Team', back_populates='tickets')
    assignee = db.relationship('TeamMember')
    category = db.relationship('Category', back_populates='tickets')
    comments = db.relationship('Comment', back_populates='ticket', cascade='all, delete-orphan')
    events = db.relationship('TicketEvent', back_populates='ticket', cascade='all, delete-orphan')


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
