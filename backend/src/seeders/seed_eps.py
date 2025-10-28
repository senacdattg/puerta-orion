"""
Seeder para la tabla EPS (Entidades Promotoras de Salud).
Inserta las principales EPS de Colombia.
"""

from src.models.base import db
from src.models.catalogos.eps import EPS


def run():
    """
    Ejecuta el seeder de EPS.
    Inserta las principales EPS de Colombia (idempotente).
    """
    print("🔄 Ejecutando seeder: EPS...")
    
    eps_list = [
        {'id_eps': 1, 'nombre_eps': 'Sura', 'codigo_eps': 1234},
        {'id_eps': 2, 'nombre_eps': 'Nueva EPS', 'codigo_eps': 5678},
        {'id_eps': 3, 'nombre_eps': 'Sanitas', 'codigo_eps': 9012},
        {'id_eps': 4, 'nombre_eps': 'Compensar', 'codigo_eps': 3456},
        {'id_eps': 5, 'nombre_eps': 'Cruz Blanca', 'codigo_eps': 7890},
        {'id_eps': 6, 'nombre_eps': 'Salud Total', 'codigo_eps': 2345},
        {'id_eps': 7, 'nombre_eps': 'Medimás', 'codigo_eps': 6789},
        {'id_eps': 8, 'nombre_eps': 'Cafesalud', 'codigo_eps': 123},
        {'id_eps': 9, 'nombre_eps': 'Coomeva', 'codigo_eps': 4567},
        {'id_eps': 10, 'nombre_eps': 'Asmet Salud', 'codigo_eps': 8901},
    ]
    
    insertados = 0
    existentes = 0
    
    for eps_data in eps_list:
        eps_existente = EPS.query.filter_by(
            id_eps=eps_data['id_eps']
        ).first()
        
        if not eps_existente:
            eps = EPS(**eps_data)
            db.session.add(eps)
            insertados += 1
            print(f"  ✅ Insertado: {eps_data['nombre_eps']}")
        else:
            existentes += 1
            print(f"  ⏭️  Ya existe: {eps_data['nombre_eps']}")
    
    db.session.commit()
    print(f"✅ Seeder EPS completado: {insertados} insertados, {existentes} ya existían.\n")


