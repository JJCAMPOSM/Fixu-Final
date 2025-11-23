"""
Script de migración manual para agregar soporte de Categorías.

Este script:
1. Crea la tabla 'categories' si no existe
2. Agrega la columna 'category_id' a la tabla 'tickets' si no existe
3. Opcionalmente, crea categorías de ejemplo

Ejecutar con: python migrate_db.py
"""

import sys
import os

# Agregar el directorio al path para importar fixu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fixu import create_app
from fixu.extensions import db
from fixu.models import Category
from sqlalchemy import text, inspect


def check_column_exists(table_name, column_name):
    """Verifica si una columna existe en una tabla."""
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def check_table_exists(table_name):
    """Verifica si una tabla existe."""
    inspector = inspect(db.engine)
    return table_name in inspector.get_table_names()


def migrate():
    """Ejecuta la migración de la base de datos."""
    app = create_app()

    with app.app_context():
        print("🔄 Iniciando migración de base de datos...")
        print()

        # 1. Crear tabla categories si no existe
        if not check_table_exists('categories'):
            print("✨ Creando tabla 'categories'...")
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(120) UNIQUE NOT NULL,
                    description TEXT,
                    color VARCHAR(7) DEFAULT '#6366f1',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
                )
            """))
            db.session.commit()
            print("✅ Tabla 'categories' creada exitosamente")
            print()
        else:
            print("ℹ️  Tabla 'categories' ya existe")
            print()

        # 2. Agregar columna category_id a tickets si no existe
        if not check_column_exists('tickets', 'category_id'):
            print("✨ Agregando columna 'category_id' a tabla 'tickets'...")
            db.session.execute(text("""
                ALTER TABLE tickets ADD COLUMN category_id INTEGER REFERENCES categories(id)
            """))
            db.session.commit()
            print("✅ Columna 'category_id' agregada exitosamente")
            print()
        else:
            print("ℹ️  Columna 'category_id' ya existe en 'tickets'")
            print()

        # 3. Crear categorías de ejemplo si no existen
        if Category.query.count() == 0:
            print("✨ Creando categorías de ejemplo...")
            example_categories = [
                Category(name='Soporte Técnico', description='Problemas técnicos y errores del sistema', color='#ef4444'),
                Category(name='Consulta', description='Preguntas generales y consultas', color='#3b82f6'),
                Category(name='Solicitud de Acceso', description='Permisos y accesos al sistema', color='#10b981'),
                Category(name='Mejora', description='Sugerencias y mejoras del sistema', color='#f59e0b'),
                Category(name='Incidente', description='Incidentes críticos que requieren atención inmediata', color='#dc2626'),
            ]
            for cat in example_categories:
                db.session.add(cat)

            db.session.commit()
            print(f"✅ {len(example_categories)} categorías de ejemplo creadas")
            print()
        else:
            print(f"ℹ️  Ya existen {Category.query.count()} categoría(s) en la base de datos")
            print()

        print("✅ Migración completada exitosamente!")
        print()
        print("📝 Cambios realizados:")
        print("   - Tabla 'categories' verificada/creada")
        print("   - Columna 'category_id' agregada a 'tickets'")
        print("   - Categorías de ejemplo creadas (si no existían)")
        print()
        print("🚀 El sistema está listo para usar las nuevas funcionalidades:")
        print("   - CRUD de Categorías (Admin)")
        print("   - CRUD de Agentes (Admin)")
        print("   - Selector de categoría en formulario de Tickets")


if __name__ == '__main__':
    try:
        migrate()
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
