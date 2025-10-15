"""
Script para poblar la base de datos con datos fijos iniciales.
Ejecutar con: python seeders.py
Ejecutar con force: python seeders.py --force
"""

from app import create_app, db
from src.models import (
    TipoDocumento, 
    Sexo, 
    GrupoSanguineo,
    Categoria,
    MetodoPago
)


def seed_tipo_documento(force=False):
    """Seed para TipoDocumento"""
    print("\n📄 Iniciando seed de TipoDocumento...")
    
    datos = [
        {'nombre_documento': 'Cédula de Ciudadanía'},
        {'nombre_documento': 'Cédula de Extranjería'},
        {'nombre_documento': 'Tarjeta de Identidad'},
        {'nombre_documento': 'Pasaporte'},
        {'nombre_documento': 'Registro Civil'},
    ]
    
    insertados = 0
    for dato in datos:
        # Verificar si ya existe
        existe = TipoDocumento.query.filter_by(nombre_documento=dato['nombre_documento']).first()
        if not existe:
            tipo_doc = TipoDocumento(**dato)
            db.session.add(tipo_doc)
            insertados += 1
        else:
            print(f"   ⏭️  {dato['nombre_documento']} ya existe, saltando...")
    
    db.session.commit()
    print(f"✅ TipoDocumento seed completado: {insertados} nuevos registros insertados")


def seed_sexo(force=False):
    """Seed para Sexo"""
    print("\n👤 Iniciando seed de Sexo...")
    
    datos = [
        {'nombre': 'Masculino'},
        {'nombre': 'Femenino'},
        {'nombre': 'Otro'},
    ]
    
    insertados = 0
    for dato in datos:
        # Verificar si ya existe
        existe = Sexo.query.filter_by(nombre=dato['nombre']).first()
        if not existe:
            sexo = Sexo(**dato)
            db.session.add(sexo)
            insertados += 1
        else:
            print(f"   ⏭️  {dato['nombre']} ya existe, saltando...")
    
    db.session.commit()
    print(f"✅ Sexo seed completado: {insertados} nuevos registros insertados")


def seed_grupo_sanguineo(force=False):
    """Seed para GrupoSanguineo"""
    print("\n🩸 Iniciando seed de GrupoSanguineo...")
    
    datos = [
        {'tipo_sangre': 'O+'},
        {'tipo_sangre': 'O-'},
        {'tipo_sangre': 'A+'},
        {'tipo_sangre': 'A-'},
        {'tipo_sangre': 'B+'},
        {'tipo_sangre': 'B-'},
        {'tipo_sangre': 'AB+'},
        {'tipo_sangre': 'AB-'},
    ]
    
    insertados = 0
    for dato in datos:
        # Verificar si ya existe
        existe = GrupoSanguineo.query.filter_by(tipo_sangre=dato['tipo_sangre']).first()
        if not existe:
            grupo = GrupoSanguineo(**dato)
            db.session.add(grupo)
            insertados += 1
        else:
            print(f"   ⏭️  {dato['tipo_sangre']} ya existe, saltando...")
    
    db.session.commit()
    print(f"✅ GrupoSanguineo seed completado: {insertados} nuevos registros insertados")


def seed_categoria(force=False):
    """Seed para Categoria"""
    print("\n🏆 Iniciando seed de Categoria...")
    
    datos = [
        {
            'codigo_categoria': 1,
            'nombre_categoria': 'Mini',
            'edad_minima': 6,
            'edad_maxima': 9,
            'estado': True
        },
        {
            'codigo_categoria': 2,
            'nombre_categoria': 'Infantil',
            'edad_minima': 10,
            'edad_maxima': 12,
            'estado': True
        },
        {
            'codigo_categoria': 3,
            'nombre_categoria': 'Prejuvenil',
            'edad_minima': 13,
            'edad_maxima': 14,
            'estado': True
        },
        {
            'codigo_categoria': 4,
            'nombre_categoria': 'Juvenil',
            'edad_minima': 15,
            'edad_maxima': 17,
            'estado': True
        },
        {
            'codigo_categoria': 5,
            'nombre_categoria': 'Mayores',
            'edad_minima': 18,
            'edad_maxima': 100,
            'estado': True
        },
    ]
    
    insertados = 0
    for dato in datos:
        # Verificar si ya existe
        existe = Categoria.query.filter_by(codigo_categoria=dato['codigo_categoria']).first()
        if not existe:
            categoria = Categoria(**dato)
            db.session.add(categoria)
            insertados += 1
        else:
            print(f"   ⏭️  {dato['nombre_categoria']} ya existe, saltando...")
    
    db.session.commit()
    print(f"✅ Categoria seed completado: {insertados} nuevos registros insertados")


def seed_metodo_pago(force=False):
    """Seed para MetodoPago"""
    print("\n💳 Iniciando seed de MetodoPago...")
    
    datos = [
        {'nombre_metodo': 'Efectivo', 'estado': True},
        {'nombre_metodo': 'Transferencia', 'estado': True},
        {'nombre_metodo': 'Mercado Pago', 'estado': True},
        {'nombre_metodo': 'Tarjeta', 'estado': True},
    ]
    
    insertados = 0
    for dato in datos:
        # Verificar si ya existe
        existe = MetodoPago.query.filter_by(nombre_metodo=dato['nombre_metodo']).first()
        if not existe:
            metodo = MetodoPago(**dato)
            db.session.add(metodo)
            insertados += 1
        else:
            print(f"   ⏭️  {dato['nombre_metodo']} ya existe, saltando...")
    
    db.session.commit()
    print(f"✅ MetodoPago seed completado: {insertados} nuevos registros insertados")


def run_all_seeds(force=False):
    """Ejecuta todos los seeds"""
    print("\n" + "="*60)
    print("🌱 INICIANDO SEED DE DATOS FIJOS")
    print("="*60)
    
    try:
        seed_tipo_documento(force=force)
        seed_sexo(force=force)
        seed_grupo_sanguineo(force=force)
        seed_categoria(force=force)
        seed_metodo_pago(force=force)
        
        print("\n" + "="*60)
        print("✅ SEED COMPLETADO EXITOSAMENTE")
        print("="*60)
        
    except Exception as e:
        print("\n" + "="*60)
        print(f"❌ ERROR EN SEED: {str(e)}")
        print("="*60)
        db.session.rollback()
        raise


if __name__ == '__main__':
    import sys
    
    # Verificar si se pasó el argumento --force
    force = '--force' in sys.argv
    
    app = create_app()
    with app.app_context():
        if force:
            print("⚠️  Modo FORCE activado - Se insertarán datos incluso si ya existen")
            run_all_seeds(force=True)
        else:
            run_all_seeds(force=False)

