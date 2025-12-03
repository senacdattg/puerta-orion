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
        # Verificar si la ciudad ya existe por nombre
        ciudad_existente = CiudadResidencia.query.filter_by(
            nombre_ciudad=ciudad_data['nombre_ciudad']
        ).first()
        
        if not ciudad_existente:
            ciudad = CiudadResidencia(**ciudad_data)
            db.session.add(ciudad)
            insertados += 1
        else:
            existentes += 1
    
    db.session.commit()
    
    print("✅ Seeder CiudadResidencia completado:")
    print(f"   - Ciudades insertadas: {insertados}")
    print(f"   - Ciudades existentes: {existentes}")
    print(f"   - Total procesadas: {len(ciudades)}")
    
    return insertados, existentes

