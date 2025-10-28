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
        {'id_tipo_enfermedad': 1, 'nombre': 'Lesión Muscular'},
        {'id_tipo_enfermedad': 2, 'nombre': 'Lesión Ósea'},
        {'id_tipo_enfermedad': 3, 'nombre': 'Lesión Articular'},
        {'id_tipo_enfermedad': 4, 'nombre': 'Enfermedad Respiratoria'},
        {'id_tipo_enfermedad': 5, 'nombre': 'Enfermedad Cardiovascular'},
        {'id_tipo_enfermedad': 6, 'nombre': 'Condición Crónica'},
        {'id_tipo_enfermedad': 7, 'nombre': 'Enfermedad Infecciosa'},
        {'id_tipo_enfermedad': 8, 'nombre': 'Trastorno Mental'},
        {'id_tipo_enfermedad': 9, 'nombre': 'Alergia'},
        {'id_tipo_enfermedad': 10, 'nombre': 'Otro'},
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


