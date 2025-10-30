"""
Seeder para la tabla MetodoPago.
Inserta los métodos de pago disponibles en el sistema.
"""

from src.models.base import db
from src.models.pagos.metodo_pago import MetodoPago


def run():
    """
    Ejecuta el seeder de métodos de pago.
    Inserta los registros si no existen (idempotente).
    """
    print("🔄 Ejecutando seeder: MetodoPago...")
    
    metodos_pago = [
        {'id_metodo_pago': 7, 'nombre_metodo': 'Mercado Pago', 'estado': True},
        {'id_metodo_pago': 8, 'nombre_metodo': 'Ninguno', 'estado': True},
        {'id_metodo_pago': 1, 'nombre_metodo': 'Efectivo', 'estado': True},
        {'id_metodo_pago': 2, 'nombre_metodo': 'Transferencia Bancaria', 'estado': True},
        {'id_metodo_pago': 3, 'nombre_metodo': 'Tarjeta Débito/Crédito', 'estado': True},
        {'id_metodo_pago': 4, 'nombre_metodo': 'Nequi', 'estado': True},
        {'id_metodo_pago': 5, 'nombre_metodo': 'Daviplata', 'estado': True},
        {'id_metodo_pago': 6, 'nombre_metodo': 'PSE', 'estado': True},
    ]
    
    insertados = 0
    existentes = 0
    
    for metodo_data in metodos_pago:
        # Evitar duplicados por nombre (clave única) o por ID
        existente_por_nombre = MetodoPago.query.filter_by(
            nombre_metodo=metodo_data['nombre_metodo']
        ).first()
        existente_por_id = MetodoPago.query.filter_by(
            id_metodo_pago=metodo_data['id_metodo_pago']
        ).first()

        if existente_por_nombre or existente_por_id:
            existentes += 1
            print(f"  ⏭️  Ya existe: {metodo_data['nombre_metodo']}")
            continue

        metodo = MetodoPago(**metodo_data)
        db.session.add(metodo)
        insertados += 1
        print(f"  ✅ Insertado: {metodo_data['nombre_metodo']}")
    
    db.session.commit()
    print(f"✅ Seeder MetodoPago completado: {insertados} insertados, {existentes} ya existían.\n")


