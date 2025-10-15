"""
Seeder para la tabla TipoEnfermedad.
Inserta los tipos/clasificaciones de enfermedades del sistema.
"""

from src.models.base import db
from src.models.salud.tipo_enfermedad import TipoEnfermedad


def run():
    """
    Ejecuta el seeder de tipos de enfermedad.
    Inserta los registros si no existen (idempotente).
    """
    print("🔄 Ejecutando seeder: TipoEnfermedad...")
    
    tipos_enfermedad = [
        {'id_tipo_enfermedad': 1, 'nombre': 'Crónica'},
        {'id_tipo_enfermedad': 2, 'nombre': 'Aguda'},
        {'id_tipo_enfermedad': 3, 'nombre': 'Congénita'},
        {'id_tipo_enfermedad': 4, 'nombre': 'Infecciosa'},
        {'id_tipo_enfermedad': 5, 'nombre': 'Mental'},
    ]
    
    insertados = 0
    existentes = 0
    
    for tipo_data in tipos_enfermedad:
        tipo_existente = TipoEnfermedad.query.filter_by(
            id_tipo_enfermedad=tipo_data['id_tipo_enfermedad']
        ).first()
        
        if not tipo_existente:
            tipo = TipoEnfermedad(**tipo_data)
            db.session.add(tipo)
            insertados += 1
            print(f"  ✅ Insertado: {tipo_data['nombre']}")
        else:
            existentes += 1
            print(f"  ⏭️  Ya existe: {tipo_data['nombre']}")
    
    db.session.commit()
    print(f"✅ Seeder TipoEnfermedad completado: {insertados} insertados, {existentes} ya existían.\n")


