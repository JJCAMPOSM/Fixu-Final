"""add_ticket_location_fields

Revision ID: b2d4f6a8c0e1
Revises: f3b8d9e1a4c7
Create Date: 2026-08-03 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2d4f6a8c0e1'
down_revision = 'f3b8d9e1a4c7'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('tickets', sa.Column('building', sa.String(length=80), nullable=True))
    op.add_column('tickets', sa.Column('classroom', sa.String(length=80), nullable=True))
    op.add_column('tickets', sa.Column('equipment_type', sa.String(length=80), nullable=True))


def downgrade():
    op.drop_column('tickets', 'equipment_type')
    op.drop_column('tickets', 'classroom')
    op.drop_column('tickets', 'building')
