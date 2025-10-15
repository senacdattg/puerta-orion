"""
Seeder para la tabla Diagnostico.
Inserta los diagnósticos médicos del sistema.
IMPORTANTE: Este seeder depende de TipoEnfermedad, ejecutarlo después.
"""

from src.models.base import db
from src.models.salud.diagnostico import Diagnostico


def run():
    """
    Ejecuta el seeder de diagnósticos.
    Inserta los registros si no existen (idempotente).
    """
    print("🔄 Ejecutando seeder: Diagnostico...")
    
    diagnosticos = [
        # Crónicas (id_tipo_enfermedad: 1)
        {'id_diagnostico': 1, 'nombre': 'Asma', 'id_tipo_enfermedad': 1},
        {'id_diagnostico': 2, 'nombre': 'Diabetes Mellitus', 'id_tipo_enfermedad': 1},
        {'id_diagnostico': 3, 'nombre': 'Hipertensión Arterial', 'id_tipo_enfermedad': 1},
        
        # Agudas (id_tipo_enfermedad: 2)
        {'id_diagnostico': 4, 'nombre': 'Gripe', 'id_tipo_enfermedad': 2},
        {'id_diagnostico': 5, 'nombre': 'Bronquitis', 'id_tipo_enfermedad': 2},
        
        # Congénitas (id_tipo_enfermedad: 3)
        {'id_diagnostico': 6, 'nombre': 'Síndrome de Down', 'id_tipo_enfermedad': 3},
        {'id_diagnostico': 7, 'nombre': 'Cardiopatía Congénita', 'id_tipo_enfermedad': 3},
        
        # Infecciosas (id_tipo_enfermedad: 4)
        {'id_diagnostico': 8, 'nombre': 'Varicela', 'id_tipo_enfermedad': 4},
        {'id_diagnostico': 9, 'nombre': 'Dengue', 'id_tipo_enfermedad': 4},
        
        # Mental (id_tipo_enfermedad: 5)
        {'id_diagnostico': 10, 'nombre': 'Ansiedad', 'id_tipo_enfermedad': 5},
        {'id_diagnostico': 11, 'nombre': 'Depresión', 'id_tipo_enfermedad': 5},
    ]
    
    insertados = 0
    existentes = 0
    
    for diagnostico_data in diagnosticos:
        diagnostico_existente = Diagnostico.query.filter_by(
            id_diagnostico=diagnostico_data['id_diagnostico']
        ).first()
        
        if not diagnostico_existente:
            diagnostico = Diagnostico(**diagnostico_data)
            db.session.add(diagnostico)
            insertados += 1
            print(f"  ✅ Insertado: {diagnostico_data['nombre']} "
                  f"(Tipo: {diagnostico_data['id_tipo_enfermedad']})")
        else:
            existentes += 1
            print(f"  ⏭️  Ya existe: {diagnostico_data['nombre']}")
    
    db.session.commit()
    print(f"✅ Seeder Diagnostico completado: {insertados} insertados, {existentes} ya existían.\n")


