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
        # Lesiones Musculares (id_tipo_enfermedad: 1)
        {'id_diagnostico': 1, 'nombre': 'Esguince de tobillo', 'id_tipo_enfermedad': 1},
        {'id_diagnostico': 2, 'nombre': 'Desgarro muscular', 'id_tipo_enfermedad': 1},
        {'id_diagnostico': 3, 'nombre': 'Contractura muscular', 'id_tipo_enfermedad': 1},
        {'id_diagnostico': 4, 'nombre': 'Calambre muscular', 'id_tipo_enfermedad': 1},
        {'id_diagnostico': 5, 'nombre': 'Distensión muscular', 'id_tipo_enfermedad': 1},
        
        # Lesiones Óseas (id_tipo_enfermedad: 2)
        {'id_diagnostico': 6, 'nombre': 'Fractura de pierna', 'id_tipo_enfermedad': 2},
        {'id_diagnostico': 7, 'nombre': 'Fractura de brazo', 'id_tipo_enfermedad': 2},
        {'id_diagnostico': 8, 'nombre': 'Fractura de pie', 'id_tipo_enfermedad': 2},
        {'id_diagnostico': 9, 'nombre': 'Contusión ósea', 'id_tipo_enfermedad': 2},
        {'id_diagnostico': 10, 'nombre': 'Fisura ósea', 'id_tipo_enfermedad': 2},
        
        # Lesiones Articulares (id_tipo_enfermedad: 3)
        {'id_diagnostico': 11, 'nombre': 'Luxación de hombro', 'id_tipo_enfermedad': 3},
        {'id_diagnostico': 12, 'nombre': 'Bursitis', 'id_tipo_enfermedad': 3},
        {'id_diagnostico': 13, 'nombre': 'Tendinitis', 'id_tipo_enfermedad': 3},
        {'id_diagnostico': 14, 'nombre': 'Síndrome del túnel carpiano', 'id_tipo_enfermedad': 3},
        {'id_diagnostico': 15, 'nombre': 'Artritis', 'id_tipo_enfermedad': 3},
        
        # Enfermedades Respiratorias (id_tipo_enfermedad: 4)
        {'id_diagnostico': 16, 'nombre': 'Asma', 'id_tipo_enfermedad': 4},
        {'id_diagnostico': 17, 'nombre': 'Bronquitis', 'id_tipo_enfermedad': 4},
        {'id_diagnostico': 18, 'nombre': 'Gripe', 'id_tipo_enfermedad': 4},
        {'id_diagnostico': 19, 'nombre': 'Sinusitis', 'id_tipo_enfermedad': 4},
        {'id_diagnostico': 20, 'nombre': 'Rinitis', 'id_tipo_enfermedad': 4},
        
        # Enfermedades Cardiovasculares (id_tipo_enfermedad: 5)
        {'id_diagnostico': 21, 'nombre': 'Hipertensión arterial', 'id_tipo_enfermedad': 5},
        {'id_diagnostico': 22, 'nombre': 'Arritmia cardíaca', 'id_tipo_enfermedad': 5},
        {'id_diagnostico': 23, 'nombre': 'Taquicardia', 'id_tipo_enfermedad': 5},
        {'id_diagnostico': 24, 'nombre': 'Bradicardia', 'id_tipo_enfermedad': 5},
        
        # Condiciones Crónicas (id_tipo_enfermedad: 6)
        {'id_diagnostico': 25, 'nombre': 'Diabetes mellitus', 'id_tipo_enfermedad': 6},
        {'id_diagnostico': 26, 'nombre': 'Obesidad', 'id_tipo_enfermedad': 6},
        {'id_diagnostico': 27, 'nombre': 'Hipertensión crónica', 'id_tipo_enfermedad': 6},
        {'id_diagnostico': 28, 'nombre': 'Artritis crónica', 'id_tipo_enfermedad': 6},
        
        # Enfermedades Infecciosas (id_tipo_enfermedad: 7)
        {'id_diagnostico': 29, 'nombre': 'Infección viral', 'id_tipo_enfermedad': 7},
        {'id_diagnostico': 30, 'nombre': 'Infección bacteriana', 'id_tipo_enfermedad': 7},
        {'id_diagnostico': 31, 'nombre': 'Dengue', 'id_tipo_enfermedad': 7},
        {'id_diagnostico': 32, 'nombre': 'COVID-19', 'id_tipo_enfermedad': 7},
        
        # Trastornos Mentales (id_tipo_enfermedad: 8)
        {'id_diagnostico': 33, 'nombre': 'Ansiedad', 'id_tipo_enfermedad': 8},
        {'id_diagnostico': 34, 'nombre': 'Depresión', 'id_tipo_enfermedad': 8},
        {'id_diagnostico': 35, 'nombre': 'Estrés', 'id_tipo_enfermedad': 8},
        {'id_diagnostico': 36, 'nombre': 'Insomnio', 'id_tipo_enfermedad': 8},
        
        # Alergias (id_tipo_enfermedad: 9)
        {'id_diagnostico': 37, 'nombre': 'Alergia alimentaria', 'id_tipo_enfermedad': 9},
        {'id_diagnostico': 38, 'nombre': 'Alergia al polen', 'id_tipo_enfermedad': 9},
        {'id_diagnostico': 39, 'nombre': 'Dermatitis alérgica', 'id_tipo_enfermedad': 9},
        {'id_diagnostico': 40, 'nombre': 'Alergia a medicamentos', 'id_tipo_enfermedad': 9},
        
        # Otros (id_tipo_enfermedad: 10)
        {'id_diagnostico': 41, 'nombre': 'Condición física temporal', 'id_tipo_enfermedad': 10},
        {'id_diagnostico': 42, 'nombre': 'Fatiga muscular', 'id_tipo_enfermedad': 10},
        {'id_diagnostico': 43, 'nombre': 'Dolor post-entrenamiento', 'id_tipo_enfermedad': 10},
        {'id_diagnostico': 44, 'nombre': 'Malestar general', 'id_tipo_enfermedad': 10},
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


