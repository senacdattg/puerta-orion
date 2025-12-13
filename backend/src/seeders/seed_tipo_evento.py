"""
Seeder para la tabla TipoEvento.
Inserta los tipos de eventos del sistema.
"""

from src.models.base import db
from src.models.eventos.tipo_evento import TipoEvento


def run():
    """
    Ejecuta el seeder de tipos de evento.
    Inserta los registros si no existen (idempotente).
    """
    print("🔄 Ejecutando seeder: TipoEvento...")
    
    tipos_evento = [
        {'id_tipo_evento': 1, 'nombre': 'Entrenamiento', 'descripcion': 'Sesión de entrenamiento regular'},
        {'id_tipo_evento': 2, 'nombre': 'Competencia', 'descripcion': 'Evento competitivo oficial'},
        {'id_tipo_evento': 3, 'nombre': 'Exhibición', 'descripcion': 'Demostración pública de habilidades'},
        {'id_tipo_evento': 4, 'nombre': 'Torneo', 'descripcion': 'Competencia con múltiples participantes'},
        {'id_tipo_evento': 5, 'nombre': 'Evaluación Médica', 'descripcion': 'Chequeo médico deportivo'},
    ]
    
    insertados = 0
    existentes = 0
    
    for tipo_data in tipos_evento:
        tipo_existente = TipoEvento.query.filter_by(
            id_tipo_evento=tipo_data['id_tipo_evento']
        ).first()
        
        if not tipo_existente:
            tipo = TipoEvento(**tipo_data)
            db.session.add(tipo)
            insertados += 1
            print(f"  ✅ Insertado: {tipo_data['nombre']}")
        else:
            existentes += 1
            print(f"  ⏭️  Ya existe: {tipo_data['nombre']}")
    
    db.session.commit()
    print(f"✅ Seeder TipoEvento completado: {insertados} insertados, {existentes} ya existían.\n")


