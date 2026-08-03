"""ticket_status_workflow

Revision ID: d3e5a7c9b1f2
Revises: b2d4f6a8c0e1
Create Date: 2026-08-03 00:00:00.000000

Rediseña el flujo de estados del ticket para alinearlo con la rúbrica:
Pendiente -> Asignado -> En proceso / En espera / Cancelado / Resuelto.

Mapeo de datos existentes (mejor esfuerzo, no hay forma de recuperar el
significado exacto de cada estado viejo):
  open   -> assigned si ya tiene agente asignado, si no pending
  pending -> in_progress (el viejo 'pending' representaba trabajo en curso)
  solved -> resolved
  closed -> resolved
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd3e5a7c9b1f2'
down_revision = 'b2d4f6a8c0e1'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('tickets', sa.Column('resolved_at', sa.DateTime(), nullable=True))

    tickets = sa.table(
        'tickets',
        sa.column('id', sa.Integer),
        sa.column('status', sa.String),
        sa.column('assignee_team_member_id', sa.Integer),
        sa.column('updated_at', sa.DateTime),
        sa.column('resolved_at', sa.DateTime),
    )

    conn = op.get_bind()
    # Ojo con el orden: 'pending' (viejo) se convierte a 'in_progress' ANTES
    # de tocar 'open', porque 'open' sin asignar pasará a valer 'pending'
    # (nuevo significado) y no debe volver a caer en esta conversión.
    conn.execute(
        tickets.update()
        .where(tickets.c.status == 'pending')
        .values(status='in_progress')
    )
    conn.execute(
        tickets.update()
        .where(tickets.c.status.in_(['solved', 'closed']))
        .values(status='resolved')
    )
    conn.execute(
        tickets.update()
        .where(tickets.c.status == 'open')
        .where(tickets.c.assignee_team_member_id.isnot(None))
        .values(status='assigned')
    )
    conn.execute(
        tickets.update()
        .where(tickets.c.status == 'open')
        .where(tickets.c.assignee_team_member_id.is_(None))
        .values(status='pending')
    )
    # Para los que quedaron resueltos, usar updated_at como fecha de cierre aproximada.
    conn.execute(
        tickets.update()
        .where(tickets.c.status == 'resolved')
        .values(resolved_at=tickets.c.updated_at)
    )


def downgrade():
    tickets = sa.table(
        'tickets',
        sa.column('id', sa.Integer),
        sa.column('status', sa.String),
    )
    conn = op.get_bind()
    conn.execute(
        tickets.update()
        .where(tickets.c.status.in_(['assigned', 'pending']))
        .values(status='open')
    )
    conn.execute(
        tickets.update()
        .where(tickets.c.status.in_(['in_progress', 'on_hold', 'cancelled']))
        .values(status='pending')
    )
    conn.execute(
        tickets.update()
        .where(tickets.c.status == 'resolved')
        .values(status='closed')
    )
    op.drop_column('tickets', 'resolved_at')
