import os
os.environ['FLASK_APP'] = 'app.py'

from app import app
from src.database.database import db

with app.app_context():
    try:
        # Actualizar la tabla alembic_version para corregir el estado
        db.session.execute(db.text("UPDATE alembic_version SET version_num = '005_eliminar_diagnostico_persona'"))
        db.session.commit()
        print("✅ Estado de migración corregido exitosamente")
        
        # Verificar el estado actual
        result = db.session.execute(db.text("SELECT version_num FROM alembic_version"))
        version = result.fetchone()
        print(f"📋 Versión actual en BD: {version[0] if version else 'No encontrada'}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.session.rollback()