"""
Seeder para la tabla InstitucionRegistro.
Inserta las instituciones de registro del sistema.
"""

from src.models.base import db
from src.models.categorias.institucion_registro import InstitucionRegistro


def run():
    """
    Ejecuta el seeder de instituciones de registro.
    Inserta las instituciones si no existen (idempotente).
    """
    print("🔄 Ejecutando seeder: InstitucionRegistro...")
    
    instituciones = [
        {'id_institucion': 1, 'nombre_institucion': 'Coldeportes - Instituto Colombiano del Deporte'},
        {'id_institucion': 2, 'nombre_institucion': 'COLDEPORTES Antioquia'},
        {'id_institucion': 3, 'nombre_institucion': 'INDER Medellín'},
        {'id_institucion': 4, 'nombre_institucion': 'IDRD Bogotá'},
        {'id_institucion': 5, 'nombre_institucion': 'Secretaría de Deporte Municipal'},
        {'id_institucion': 6, 'nombre_institucion': 'Liga Antioqueña de Fútbol'},
        {'id_institucion': 7, 'nombre_institucion': 'Federación Colombiana de Atletismo'},
        {'id_institucion': 8, 'nombre_institucion': 'Federación Colombiana de Natación'},
        {'id_institucion': 9, 'nombre_institucion': 'Comité Olímpico Colombiano'},
        {'id_institucion': 10, 'nombre_institucion': 'Club Deportivo Local'},
    ]
    
    insertados = 0
    existentes = 0
    
    for inst_data in instituciones:
        inst_existente = InstitucionRegistro.query.filter_by(
            id_institucion=inst_data['id_institucion']
        ).first()
        
        if not inst_existente:
            institucion = InstitucionRegistro(**inst_data)
            db.session.add(institucion)
            insertados += 1
            print(f"  ✅ Insertado: {inst_data['nombre_institucion']}")
        else:
            existentes += 1
            print(f"  ⏭️  Ya existe: {inst_data['nombre_institucion']}")
    
    db.session.commit()
    print(f"✅ Seeder InstitucionRegistro completado: {insertados} insertados, {existentes} ya existían.\n")


