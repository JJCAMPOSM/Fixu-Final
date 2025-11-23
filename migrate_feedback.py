"""
Script de migración para agregar soporte de Feedback de Tickets.

Este script crea la tabla 'satisfaccion_tickets' si no existe.
"""

import sys
import os

# Agregar el directorio al path para importar fixu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fixu import create_app
from fixu.extensions import db
from sqlalchemy import text, inspect


def check_table_exists(table_name):
    """Verifica si una tabla existe."""
    inspector = inspect(db.engine)
    return table_name in inspector.get_table_names()


def migrate():
    """Ejecuta la migración de la base de datos."""
    app = create_app()

    with app.app_context():
        print("Iniciando migracion para feedback de tickets...")
        print()

        # Crear tabla satisfaccion_tickets si no existe
        if not check_table_exists('satisfaccion_tickets'):
            print("Creando tabla 'satisfaccion_tickets'...")
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS satisfaccion_tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    calificacion INTEGER NOT NULL,
                    comentario TEXT,
                    fecha_envio DATETIME NOT NULL,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    FOREIGN KEY (ticket_id) REFERENCES tickets (id),
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE (ticket_id)
                )
            
            """)
            )
            print("[OK] Tabla 'satisfaccion_tickets' creada exitosamente.")
        else:
            print("[INFO] La tabla 'satisfaccion_tickets' ya existe.")

        db.session.commit()
        print("\nMigracion completada exitosamente!")


if __name__ == '__main__':
    try:
        migrate()
    except Exception as e:
        print(f"[ERROR] Error durante la migracion: {e}")
        sys.exit(1)
