"""
Seeder para la tabla Sexo.
Inserta los tipos de sexo del sistema.
"""

from src.models.base import db
from src.models.categorias.sexo import Sexo


def run():
    """
    Ejecuta el seeder de sexos.
    Inserta los registros si no existen (idempotente).
    """
    print("🔄 Ejecutando seeder: Sexo...")
    
    sexos = [
        {'id_sexo': 1, 'nombre': 'Masculino'},
        {'id_sexo': 2, 'nombre': 'Femenino'},
        {'id_sexo': 3, 'nombre': 'Otro'},
    ]
    
    insertados = 0
    existentes = 0
    
    for sexo_data in sexos:
        sexo_existente = Sexo.query.filter_by(
            id_sexo=sexo_data['id_sexo']
        ).first()
        
        if not sexo_existente:
            sexo = Sexo(**sexo_data)
            db.session.add(sexo)
            insertados += 1
            print(f"  ✅ Insertado: {sexo_data['nombre']}")
        else:
            existentes += 1
            print(f"  ⏭️  Ya existe: {sexo_data['nombre']}")
    
    db.session.commit()
    print(f"✅ Seeder Sexo completado: {insertados} insertados, {existentes} ya existían.\n")


