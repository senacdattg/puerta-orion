"""
Seeder para la tabla GrupoSanguineo.
Inserta los tipos sanguíneos del sistema.
"""

from src.models.base import db
from src.models.categorias.grupo_sanguineo import GrupoSanguineo


def run():
    """
    Ejecuta el seeder de grupos sanguíneos.
    Inserta los registros si no existen (idempotente).
    """
    print("🔄 Ejecutando seeder: GrupoSanguineo...")
    
    grupos_sanguineos = [
        {'id_tipo_sangre': 1, 'tipo_sangre': 'A+'},
        {'id_tipo_sangre': 2, 'tipo_sangre': 'A-'},
        {'id_tipo_sangre': 3, 'tipo_sangre': 'B+'},
        {'id_tipo_sangre': 4, 'tipo_sangre': 'B-'},
        {'id_tipo_sangre': 5, 'tipo_sangre': 'AB+'},
        {'id_tipo_sangre': 6, 'tipo_sangre': 'AB-'},
        {'id_tipo_sangre': 7, 'tipo_sangre': 'O+'},
        {'id_tipo_sangre': 8, 'tipo_sangre': 'O-'},
    ]
    
    insertados = 0
    existentes = 0
    
    for grupo_data in grupos_sanguineos:
        grupo_existente = GrupoSanguineo.query.filter_by(
            id_tipo_sangre=grupo_data['id_tipo_sangre']
        ).first()
        
        if not grupo_existente:
            grupo = GrupoSanguineo(**grupo_data)
            db.session.add(grupo)
            insertados += 1
            print(f"  ✅ Insertado: {grupo_data['tipo_sangre']}")
        else:
            existentes += 1
            print(f"  ⏭️  Ya existe: {grupo_data['tipo_sangre']}")
    
    db.session.commit()
    print(f"✅ Seeder GrupoSanguineo completado: {insertados} insertados, {existentes} ya existían.\n")


