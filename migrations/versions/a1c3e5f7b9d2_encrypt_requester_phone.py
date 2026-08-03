"""encrypt_requester_phone

Revision ID: a1c3e5f7b9d2
Revises: 5f2a9c1b7e21
Create Date: 2026-08-02 21:00:00.000000

"""
import os

from alembic import op
import sqlalchemy as sa
from cryptography.fernet import Fernet, InvalidToken


# revision identifiers, used by Alembic.
revision = 'a1c3e5f7b9d2'
down_revision = '5f2a9c1b7e21'
branch_labels = None
depends_on = None


def upgrade():
    # String(20) no alcanza para un token Fernet (~base64 de ~100+ bytes).
    op.alter_column(
        'requesters', 'phone',
        existing_type=sa.String(length=20),
        type_=sa.Text(),
        existing_nullable=True,
    )

    key = os.environ.get('ENCRYPTION_KEY')
    if not key:
        # Sin ENCRYPTION_KEY no se pueden cifrar los teléfonos existentes en
        # este paso; la columna ya quedó ensanchada, pero los valores
        # preexistentes seguirán en texto plano hasta correr el backfill
        # manualmente (ver README/runbook) una vez definida la clave.
        return

    fernet = Fernet(key)
    conn = op.get_bind()
    rows = conn.execute(sa.text("SELECT id, phone FROM requesters WHERE phone IS NOT NULL AND phone <> ''")).fetchall()
    for row in rows:
        raw = row.phone
        try:
            # Ya cifrado (ej. re-ejecución de la migración): no lo vuelvas a cifrar.
            fernet.decrypt(raw.encode('utf-8'))
            continue
        except InvalidToken:
            pass
        encrypted = fernet.encrypt(raw.encode('utf-8')).decode('utf-8')
        conn.execute(
            sa.text("UPDATE requesters SET phone = :phone WHERE id = :id"),
            {"phone": encrypted, "id": row.id},
        )


def downgrade():
    key = os.environ.get('ENCRYPTION_KEY')
    if key:
        fernet = Fernet(key)
        conn = op.get_bind()
        rows = conn.execute(sa.text("SELECT id, phone FROM requesters WHERE phone IS NOT NULL AND phone <> ''")).fetchall()
        for row in rows:
            try:
                decrypted = fernet.decrypt(row.phone.encode('utf-8')).decode('utf-8')
            except InvalidToken:
                continue
            conn.execute(
                sa.text("UPDATE requesters SET phone = :phone WHERE id = :id"),
                {"phone": decrypted, "id": row.id},
            )

    op.alter_column(
        'requesters', 'phone',
        existing_type=sa.Text(),
        type_=sa.String(length=20),
        existing_nullable=True,
    )
