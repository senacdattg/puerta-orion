"""
Seeder para la tabla Escuela.
Inserta las escuelas deportivas del sistema.
"""

from src.models.base import db
from src.models.categorias.escuela import Escuela


def run():
    """
    Ejecuta el seeder de escuelas deportivas.
    Inserta las escuelas si no existen (idempotente).
    """
    print("🔄 Ejecutando seeder: Escuela...")
    
    escuelas = [
        {'id_escuela': 1, 'nombre': 'Escuela de Fútbol Nacional'},
        {'id_escuela': 2, 'nombre': 'Club Deportivo Juvenil'},
        {'id_escuela': 3, 'nombre': 'Academia de Baloncesto Colombia'},
        {'id_escuela': 4, 'nombre': 'Instituto de Deportes de Alto Rendimiento'},
        {'id_escuela': 5, 'nombre': 'Centro Deportivo Municipal'},
        {'id_escuela': 6, 'nombre': 'Escuela de Atletismo Olímpico'},
        {'id_escuela': 7, 'nombre': 'Club de Natación Los Pinos'},
        {'id_escuela': 8, 'nombre': 'Academia de Artes Marciales'},
        {'id_escuela': 9, 'nombre': 'Escuela de Voleibol Regional'},
        {'id_escuela': 10, 'nombre': 'Centro de Entrenamiento Puerta Orion'},
    ]
    
    insertados = 0
    existentes = 0
    
    for escuela_data in escuelas:
        escuela_existente = Escuela.query.filter_by(
            id_escuela=escuela_data['id_escuela']
        ).first()
        
        if not escuela_existente:
            escuela = Escuela(**escuela_data)
            db.session.add(escuela)
            insertados += 1
            print(f"  ✅ Insertado: {escuela_data['nombre']}")
        else:
            existentes += 1
            print(f"  ⏭️  Ya existe: {escuela_data['nombre']}")
    
    db.session.commit()
    print(f"✅ Seeder Escuela completado: {insertados} insertados, {existentes} ya existían.\n")


