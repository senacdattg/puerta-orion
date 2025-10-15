"""
Seeder para la tabla Categoria.
Inserta las categorías deportivas del sistema.
"""

from src.models.base import db
from src.models.categorias.categoria import Categoria


def run():
    """
    Ejecuta el seeder de categorías deportivas.
    Inserta los registros si no existen (idempotente).
    """
    print("🔄 Ejecutando seeder: Categoria...")
    
    categorias = [
        {
            'id_categoria': 1,
            'nombre_categoria': 'Pre-infantil',
            'codigo_categoria': 1,
            'edad_minima': 5,
            'edad_maxima': 7,
            'estado': True
        },
        {
            'id_categoria': 2,
            'nombre_categoria': 'Infantil',
            'codigo_categoria': 2,
            'edad_minima': 8,
            'edad_maxima': 10,
            'estado': True
        },
        {
            'id_categoria': 3,
            'nombre_categoria': 'Pre-juvenil',
            'codigo_categoria': 3,
            'edad_minima': 11,
            'edad_maxima': 13,
            'estado': True
        },
        {
            'id_categoria': 4,
            'nombre_categoria': 'Juvenil',
            'codigo_categoria': 4,
            'edad_minima': 14,
            'edad_maxima': 17,
            'estado': True
        },
        {
            'id_categoria': 5,
            'nombre_categoria': 'Mayores',
            'codigo_categoria': 5,
            'edad_minima': 18,
            'edad_maxima': 35,
            'estado': True
        },
        {
            'id_categoria': 6,
            'nombre_categoria': 'Sénior',
            'codigo_categoria': 6,
            'edad_minima': 36,
            'edad_maxima': 60,
            'estado': True
        },
        {
            'id_categoria': 7,
            'nombre_categoria': 'Máster',
            'codigo_categoria': 7,
            'edad_minima': 61,
            'edad_maxima': 99,
            'estado': True
        },
    ]
    
    insertados = 0
    existentes = 0
    
    for categoria_data in categorias:
        categoria_existente = Categoria.query.filter_by(
            id_categoria=categoria_data['id_categoria']
        ).first()
        
        if not categoria_existente:
            categoria = Categoria(**categoria_data)
            db.session.add(categoria)
            insertados += 1
            print(f"  ✅ Insertado: {categoria_data['nombre_categoria']} "
                f"({categoria_data['edad_minima']}-{categoria_data['edad_maxima']} años)")
        else:
            existentes += 1
            print(f"  ⏭️  Ya existe: {categoria_data['nombre_categoria']}")
    
    db.session.commit()
    print(f"✅ Seeder Categoria completado: {insertados} insertados, {existentes} ya existían.\n")


