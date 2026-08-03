"""add_ticket_resolution_photo

Revision ID: c7e2a4d1f6b3
Revises: a1c3e5f7b9d2
Create Date: 2026-08-03 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c7e2a4d1f6b3'
down_revision = 'a1c3e5f7b9d2'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('tickets', sa.Column('resolution_photo_path', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('tickets', 'resolution_photo_path')
