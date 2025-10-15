"""
Seeder para la tabla Parentesco.
Inserta los tipos de parentesco del sistema.
"""

from src.models.base import db
from src.models.acudientes.parentesco import Parentesco


def run():
    """
    Ejecuta el seeder de parentescos.
    Inserta los registros si no existen (idempotente).
    """
    print("🔄 Ejecutando seeder: Parentesco...")
    
    parentescos = [
        {'id_parentesco': 1, 'nombre': 'Padre'},
        {'id_parentesco': 2, 'nombre': 'Madre'},
        {'id_parentesco': 3, 'nombre': 'Hermano/a'},
        {'id_parentesco': 4, 'nombre': 'Abuelo/a'},
        {'id_parentesco': 5, 'nombre': 'Tío/a'},
        {'id_parentesco': 6, 'nombre': 'Tutor Legal'},
        {'id_parentesco': 7, 'nombre': 'Otro'},
    ]
    
    insertados = 0
    existentes = 0
    
    for parentesco_data in parentescos:
        parentesco_existente = Parentesco.query.filter_by(
            id_parentesco=parentesco_data['id_parentesco']
        ).first()
        
        if not parentesco_existente:
            parentesco = Parentesco(**parentesco_data)
            db.session.add(parentesco)
            insertados += 1
            print(f"  ✅ Insertado: {parentesco_data['nombre']}")
        else:
            existentes += 1
            print(f"  ⏭️  Ya existe: {parentesco_data['nombre']}")
    
    db.session.commit()
    print(f"✅ Seeder Parentesco completado: {insertados} insertados, {existentes} ya existían.\n")


