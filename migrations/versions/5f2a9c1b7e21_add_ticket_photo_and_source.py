"""add_ticket_photo_and_source

Revision ID: 5f2a9c1b7e21
Revises: 88faf14a8b88
Create Date: 2026-08-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5f2a9c1b7e21'
down_revision = '88faf14a8b88'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('tickets', sa.Column('photo_path', sa.String(length=255), nullable=True))
    op.add_column('tickets', sa.Column('source', sa.String(length=20), nullable=False, server_default='web'))


def downgrade():
    op.drop_column('tickets', 'source')
    op.drop_column('tickets', 'photo_path')
