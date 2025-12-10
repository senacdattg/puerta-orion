"""
Seeder para la tabla CiudadResidencia.
Carga la ciudad de Guaviare.
"""

from src.models.base import db
from src.models.categorias.ciudad_residencia import CiudadResidencia


def run():
    """
    Ejecuta el seeder de ciudades de residencia.
    Inserta Guaviare (idempotente).
    """
    print("🔄 Ejecutando seeder: CiudadResidencia...")
    
    ciudades = [
        {"id_ciudad": 1, "nombre_ciudad": "Guaviare"}
    ]
    
    insertados = 0
    existentes = 0
    
    for ciudad_data in ciudades:
        # Verificar si existe por ID o por nombre (para evitar duplicados)
        ciudad_existente = CiudadResidencia.query.filter_by(
            id_ciudad=ciudad_data['id_ciudad']
        ).first()
        
        if not ciudad_existente:
            # También verificar por nombre
            ciudad_por_nombre = CiudadResidencia.query.filter_by(
                nombre_ciudad=ciudad_data['nombre_ciudad']
            ).first()
            
            if not ciudad_por_nombre:
                ciudad = CiudadResidencia(**ciudad_data)
                db.session.add(ciudad)
                insertados += 1
                print(f"  ✅ Insertado: {ciudad_data['nombre_ciudad']}")
            else:
                existentes += 1
                print(f"  ⏭️  Ya existe: {ciudad_data['nombre_ciudad']}")
        else:
            existentes += 1
            print(f"  ⏭️  Ya existe: {ciudad_data['nombre_ciudad']}")
    
    db.session.commit()
    print(f"✅ Seeder CiudadResidencia completado: {insertados} insertados, {existentes} ya existían.\n")
    
    return insertados, existentes

