"""
Seeder para la tabla CiudadResidencia.
Carga las principales ciudades de Colombia.
"""

from src.models.base import db
from src.models.categorias.ciudad_residencia import CiudadResidencia


def run():
    """
    Ejecuta el seeder de ciudades de residencia.
    Inserta las principales ciudades de Colombia (idempotente).
    """
    print("🔄 Ejecutando seeder: CiudadResidencia...")
    
    ciudades = [
        # Región Caribe
        {"id_ciudad": 1, "nombre_ciudad": "Barranquilla"},
        {"id_ciudad": 2, "nombre_ciudad": "Cartagena"},
        {"id_ciudad": 3, "nombre_ciudad": "Santa Marta"},
        {"id_ciudad": 4, "nombre_ciudad": "Montería"},
        {"id_ciudad": 5, "nombre_ciudad": "Sincelejo"},
        {"id_ciudad": 6, "nombre_ciudad": "Valledupar"},
        
        # Región Pacífica
        {"id_ciudad": 7, "nombre_ciudad": "Cali"},
        {"id_ciudad": 8, "nombre_ciudad": "Buenaventura"},
        {"id_ciudad": 9, "nombre_ciudad": "Pasto"},
        {"id_ciudad": 10, "nombre_ciudad": "Popayán"},
        {"id_ciudad": 11, "nombre_ciudad": "Quibdó"},
        {"id_ciudad": 12, "nombre_ciudad": "Tumaco"},
        
        # Región Andina - Centro
        {"id_ciudad": 13, "nombre_ciudad": "Bogotá"},
        {"id_ciudad": 14, "nombre_ciudad": "Soacha"},
        {"id_ciudad": 15, "nombre_ciudad": "Chía"},
        {"id_ciudad": 16, "nombre_ciudad": "Facatativá"},
        {"id_ciudad": 17, "nombre_ciudad": "Girardot"},
        {"id_ciudad": 18, "nombre_ciudad": "Zipaquirá"},
        {"id_ciudad": 19, "nombre_ciudad": "Cajicá"},
        {"id_ciudad": 20, "nombre_ciudad": "Madrid"},
        
        # Región Andina - Antioquia
        {"id_ciudad": 21, "nombre_ciudad": "Medellín"},
        {"id_ciudad": 22, "nombre_ciudad": "Bello"},
        {"id_ciudad": 23, "nombre_ciudad": "Itagüí"},
        {"id_ciudad": 24, "nombre_ciudad": "Envigado"},
        {"id_ciudad": 25, "nombre_ciudad": "Sabaneta"},
        {"id_ciudad": 26, "nombre_ciudad": "La Estrella"},
        
        # Región Andina - Valle del Cauca
        {"id_ciudad": 27, "nombre_ciudad": "Yumbo"},
        {"id_ciudad": 28, "nombre_ciudad": "Palmira"},
        {"id_ciudad": 29, "nombre_ciudad": "Buga"},
        {"id_ciudad": 30, "nombre_ciudad": "Tuluá"},
        {"id_ciudad": 31, "nombre_ciudad": "Cartago"},
        
        # Región Andina - Santander
        {"id_ciudad": 32, "nombre_ciudad": "Bucaramanga"},
        {"id_ciudad": 33, "nombre_ciudad": "Floridablanca"},
        {"id_ciudad": 34, "nombre_ciudad": "Girón"},
        {"id_ciudad": 35, "nombre_ciudad": "Piedecuesta"},
        {"id_ciudad": 36, "nombre_ciudad": "Barrancabermeja"},
        
        # Región Andina - Boyacá
        {"id_ciudad": 37, "nombre_ciudad": "Tunja"},
        {"id_ciudad": 38, "nombre_ciudad": "Duitama"},
        {"id_ciudad": 39, "nombre_ciudad": "Sogamoso"},
        {"id_ciudad": 40, "nombre_ciudad": "Villa de Leyva"},
        
        # Región Andina - Tolima
        {"id_ciudad": 41, "nombre_ciudad": "Ibagué"},
        {"id_ciudad": 42, "nombre_ciudad": "Espinal"},
        {"id_ciudad": 43, "nombre_ciudad": "Melgar"},
        
        # Región Andina - Huila
        {"id_ciudad": 44, "nombre_ciudad": "Neiva"},
        {"id_ciudad": 45, "nombre_ciudad": "Pitalito"},
        
        # Región Andina - Norte de Santander
        {"id_ciudad": 46, "nombre_ciudad": "Cúcuta"},
        {"id_ciudad": 47, "nombre_ciudad": "Villa del Rosario"},
        
        # Región Andina - Eje Cafetero
        {"id_ciudad": 48, "nombre_ciudad": "Pereira"},
        {"id_ciudad": 49, "nombre_ciudad": "Manizales"},
        {"id_ciudad": 50, "nombre_ciudad": "Armenia"},
        {"id_ciudad": 51, "nombre_ciudad": "Dosquebradas"},
        {"id_ciudad": 52, "nombre_ciudad": "La Virginia"},
        
        # Región Orinoquía
        {"id_ciudad": 53, "nombre_ciudad": "Villavicencio"},
        {"id_ciudad": 54, "nombre_ciudad": "Yopal"},
        {"id_ciudad": 55, "nombre_ciudad": "Arauca"},
        
        # Región Amazonía
        {"id_ciudad": 56, "nombre_ciudad": "Leticia"},
        {"id_ciudad": 57, "nombre_ciudad": "Florencia"},
        {"id_ciudad": 58, "nombre_ciudad": "Mocoa"},
        
        # Región Caribe - Atlántico (Adicionales)
        {"id_ciudad": 59, "nombre_ciudad": "Soledad"},
        {"id_ciudad": 60, "nombre_ciudad": "Malambo"},
        {"id_ciudad": 61, "nombre_ciudad": "Sabanalarga"},
        
        # Región Caribe - Bolívar
        {"id_ciudad": 62, "nombre_ciudad": "Magangué"},
        
        # Región Andina - Risaralda
        {"id_ciudad": 63, "nombre_ciudad": "Chinchiná"},
        
        # Región Andina - Quindío
        {"id_ciudad": 64, "nombre_ciudad": "Montenegro"},
        {"id_ciudad": 65, "nombre_ciudad": "Quimbaya"},
        
        # Región Andina - Caldas
        {"id_ciudad": 66, "nombre_ciudad": "Riosucio"},
        
        # Región Andina - Valle del Cauca
        {"id_ciudad": 67, "nombre_ciudad": "Florida"},
        
        # Región Caribe - Cesar
        {"id_ciudad": 68, "nombre_ciudad": "La Paz"},
        
        # Región Andina - Cauca
        {"id_ciudad": 69, "nombre_ciudad": "Santiago de Cali"},
        
        # Región Caribe - Sucre
        {"id_ciudad": 70, "nombre_ciudad": "Corozal"}
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
    
    print(f"✅ Seeder CiudadResidencia completado:")
    print(f"   - Ciudades insertadas: {insertados}")
    print(f"   - Ciudades existentes: {existentes}")
    print(f"   - Total procesadas: {len(ciudades)}")
    
    return insertados, existentes

