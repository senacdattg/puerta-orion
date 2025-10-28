"""
Seeder para la tabla TipoDocumento.
Inserta los tipos de documento de identificación del sistema.
"""

from src.models.base import db
from src.models.catalogos.tipo_documento import TipoDocumento


def run():
    """
    Ejecuta el seeder de tipos de documento.
    Inserta los registros si no existen (idempotente).
    """
    print("🔄 Ejecutando seeder: TipoDocumento...")
    
    tipos_documento = [
        {'id_documento': 1, 'nombre_documento': 'Cédula de Ciudadanía'},
        {'id_documento': 2, 'nombre_documento': 'Tarjeta de Identidad'},
        {'id_documento': 3, 'nombre_documento': 'Cédula de Extranjería'},
        {'id_documento': 4, 'nombre_documento': 'Pasaporte'},
        {'id_documento': 5, 'nombre_documento': 'Registro Civil'},
    ]
    
    insertados = 0
    existentes = 0
    
    for tipo_data in tipos_documento:
        # Verificar si existe por ID o por nombre (para evitar duplicados)
        tipo_existente = TipoDocumento.query.filter_by(
            id_documento=tipo_data['id_documento']
        ).first()
        
        if not tipo_existente:
            # También verificar por nombre
            tipo_por_nombre = TipoDocumento.query.filter_by(
                nombre_documento=tipo_data['nombre_documento']
            ).first()
            
            if not tipo_por_nombre:
                tipo = TipoDocumento(**tipo_data)
                db.session.add(tipo)
                insertados += 1
                print(f"  ✅ Insertado: {tipo_data['nombre_documento']}")
            else:
                existentes += 1
                print(f"  ⏭️  Ya existe: {tipo_data['nombre_documento']}")
        else:
            existentes += 1
            print(f"  ⏭️  Ya existe: {tipo_data['nombre_documento']}")
    
    db.session.commit()
    print(f"✅ Seeder TipoDocumento completado: {insertados} insertados, {existentes} ya existían.\n")


