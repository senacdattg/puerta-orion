"""
Seeder para la tabla Deporte.
Inserta los deportes disponibles en el sistema.
"""

from src.models.base import db
from src.models.categorias.deporte import Deporte


def run():
    """
    Ejecuta el seeder de deportes.
    Inserta los registros si no existen (idempotente).
    """
    print("🔄 Ejecutando seeder: Deporte...")
    
    deportes = [
        {'id_deporte': 1, 'nombre': 'Fútbol'},
        {'id_deporte': 2, 'nombre': 'Atletismo'},
        {'id_deporte': 3, 'nombre': 'Baloncesto'},
        {'id_deporte': 4, 'nombre': 'Natación'},
        {'id_deporte': 5, 'nombre': 'Voleibol'},
        {'id_deporte': 6, 'nombre': 'Ciclismo'},
        {'id_deporte': 7, 'nombre': 'Patinaje'},
        {'id_deporte': 8, 'nombre': 'Taekwondo'},
    ]
    
    insertados = 0
    existentes = 0
    
    for deporte_data in deportes:
        deporte_existente = Deporte.query.filter_by(
            id_deporte=deporte_data['id_deporte']
        ).first()
        
        if not deporte_existente:
            deporte = Deporte(**deporte_data)
            db.session.add(deporte)
            insertados += 1
            print(f"  ✅ Insertado: {deporte_data['nombre']}")
        else:
            existentes += 1
            print(f"  ⏭️  Ya existe: {deporte_data['nombre']}")
    
    db.session.commit()
    print(f"✅ Seeder Deporte completado: {insertados} insertados, {existentes} ya existían.\n")


