"""
Seeder para permisos del sistema.

Crea todos los permisos necesarios para el funcionamiento del sistema Puerta Orion.
Los permisos siguen la convención: acción_recurso

Uso:
    python -m backend.src.seeders.seed_permisos
"""

from src.models.base import db
from src.models.roles_y_permisos.permiso import Permiso


def run():
    """Ejecuta el seeder de permisos."""
    print("  🔑 Insertando permisos del sistema...")
    
    # Lista de permisos del sistema
    permisos = [
        # Permisos de deportistas
        {"nombre": "crear_deportista", "descripcion": "Permite crear deportistas"},
        {"nombre": "ver_deportista", "descripcion": "Permite ver información de deportistas"},
        {"nombre": "editar_deportista", "descripcion": "Permite editar información de deportistas"},
        {"nombre": "eliminar_deportista", "descripcion": "Permite eliminar deportistas"},
        {"nombre": "listar_deportistas", "descripcion": "Permite listar todos los deportistas"},
        
        # Permisos de usuarios
        {"nombre": "crear_usuario", "descripcion": "Permite crear usuarios"},
        {"nombre": "ver_usuario", "descripcion": "Permite ver información de usuarios"},
        {"nombre": "editar_usuario", "descripcion": "Permite editar información de usuarios"},
        {"nombre": "eliminar_usuario", "descripcion": "Permite eliminar usuarios"},
        {"nombre": "listar_usuarios", "descripcion": "Permite listar todos los usuarios"},
        {"nombre": "gestionar_usuarios", "descripcion": "Permite gestión completa de usuarios"},
        
        # Permisos de roles y permisos
        {"nombre": "crear_rol", "descripcion": "Permite crear roles"},
        {"nombre": "ver_rol", "descripcion": "Permite ver información de roles"},
        {"nombre": "editar_rol", "descripcion": "Permite editar roles"},
        {"nombre": "eliminar_rol", "descripcion": "Permite eliminar roles"},
        {"nombre": "asignar_permisos", "descripcion": "Permite asignar permisos a roles"},
        {"nombre": "asignar_roles", "descripcion": "Permite asignar roles a usuarios"},
        
        # Permisos de eventos
        {"nombre": "crear_evento", "descripcion": "Permite crear eventos"},
        {"nombre": "ver_evento", "descripcion": "Permite ver información de eventos"},
        {"nombre": "editar_evento", "descripcion": "Permite editar eventos"},
        {"nombre": "eliminar_evento", "descripcion": "Permite eliminar eventos"},
        {"nombre": "listar_eventos", "descripcion": "Permite listar todos los eventos"},
        {"nombre": "gestionar_eventos", "descripcion": "Permite gestión completa de eventos"},
        
        # Permisos de pagos
        {"nombre": "crear_pago", "descripcion": "Permite crear pagos"},
        {"nombre": "ver_pago", "descripcion": "Permite ver información de pagos"},
        {"nombre": "editar_pago", "descripcion": "Permite editar pagos"},
        {"nombre": "eliminar_pago", "descripcion": "Permite eliminar pagos"},
        {"nombre": "listar_pagos", "descripcion": "Permite listar todos los pagos"},
        {"nombre": "gestionar_pagos", "descripcion": "Permite gestión completa de pagos"},
        {"nombre": "procesar_pago", "descripcion": "Permite procesar pagos"},
        
        # Permisos de acudientes
        {"nombre": "crear_acudiente", "descripcion": "Permite crear acudientes"},
        {"nombre": "ver_acudiente", "descripcion": "Permite ver información de acudientes"},
        {"nombre": "editar_acudiente", "descripcion": "Permite editar acudientes"},
        {"nombre": "eliminar_acudiente", "descripcion": "Permite eliminar acudientes"},
        {"nombre": "listar_acudientes", "descripcion": "Permite listar todos los acudientes"},
        
        # Permisos de salud
        {"nombre": "ver_diagnostico", "descripcion": "Permite ver diagnósticos médicos"},
        {"nombre": "crear_diagnostico", "descripcion": "Permite crear diagnósticos médicos"},
        {"nombre": "editar_diagnostico", "descripcion": "Permite editar diagnósticos médicos"},
        {"nombre": "eliminar_diagnostico", "descripcion": "Permite eliminar diagnósticos médicos"},
        
        # Permisos de reportes
        {"nombre": "ver_reportes", "descripcion": "Permite ver reportes del sistema"},
        {"nombre": "generar_reportes", "descripcion": "Permite generar reportes personalizados"},
        {"nombre": "exportar_reportes", "descripcion": "Permite exportar reportes"},
        
        # Permisos de catálogos
        {"nombre": "gestionar_catalogos", "descripcion": "Permite gestionar catálogos del sistema"},
        {"nombre": "ver_catalogos", "descripcion": "Permite ver catálogos del sistema"},
        
        # Permisos de galería
        {"nombre": "ver_galeria", "descripcion": "Permite ver galería de fotos"},
        {"nombre": "subir_foto", "descripcion": "Permite subir fotos a la galería"},
        {"nombre": "eliminar_foto", "descripcion": "Permite eliminar fotos de la galería"},
        {"nombre": "gestionar_galeria", "descripcion": "Permite gestión completa de la galería"},
        
        # Permisos de calendario
        {"nombre": "ver_calendario", "descripcion": "Permite ver el calendario"},
        {"nombre": "gestionar_calendario", "descripcion": "Permite gestionar el calendario"},
        
        # Permisos administrativos
        {"nombre": "acceso_panel_admin", "descripcion": "Permite acceder al panel de administración"},
        {"nombre": "ver_logs", "descripcion": "Permite ver logs del sistema"},
        {"nombre": "gestionar_configuracion", "descripcion": "Permite gestionar configuración del sistema"},
        {"nombre": "acceso_total", "descripcion": "Acceso total al sistema sin restricciones"},
    ]
    
    permisos_creados = 0
    permisos_existentes = 0
    
    for permiso_data in permisos:
        # Verificar si el permiso ya existe
        permiso_existente = Permiso.query.filter_by(nombre=permiso_data['nombre']).first()
        
        if not permiso_existente:
            # Crear nuevo permiso
            nuevo_permiso = Permiso(
                nombre=permiso_data['nombre'],
                descripcion=permiso_data['descripcion']
            )
            db.session.add(nuevo_permiso)
            permisos_creados += 1
        else:
            permisos_existentes += 1
    
    # Guardar cambios
    try:
        db.session.commit()
        print(f"     ✅ {permisos_creados} permisos creados exitosamente")
        if permisos_existentes > 0:
            print(f"     ℹ️  {permisos_existentes} permisos ya existían")
    except Exception as e:
        db.session.rollback()
        print(f"     ❌ Error al crear permisos: {str(e)}")
        raise


if __name__ == '__main__':
    from backend.app import create_app
    app = create_app()
    with app.app_context():
        run()

