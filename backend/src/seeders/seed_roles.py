"""
Seeder para roles del sistema.

Crea los roles básicos del sistema y les asigna sus permisos correspondientes.

Roles:
- SuperAdmin: Acceso total al sistema (todos los permisos)
- Administrador: Gestión general del sistema
- Entrenador: Gestión de deportistas y eventos
- Deportista: Acceso limitado (solo lectura)
- Acudiente: Acceso limitado (solo lectura)

Uso:
    python -m backend.src.seeders.seed_roles
"""

from src.models.base import db
from src.models.roles_y_permisos.rol import Rol
from src.models.roles_y_permisos.permiso import Permiso
from src.models.roles_y_permisos.rol_permiso import RolPermiso


def run():
    """Ejecuta el seeder de roles."""
    print("  👥 Insertando roles del sistema...")
    
    # Definición de roles con sus permisos
    roles_config = {
        "SuperAdmin": {
            "descripcion": "Super Administrador con acceso total al sistema",
            "permisos": "ALL"  # Todos los permisos
        },
        "Administrador": {
            "descripcion": "Administrador del sistema con permisos de gestión",
            "permisos": [
                # Deportistas
                "crear_deportista", "ver_deportista", "editar_deportista", "eliminar_deportista", "listar_deportistas",
                # Usuarios
                "crear_usuario", "ver_usuario", "editar_usuario", "listar_usuarios", "gestionar_usuarios",
                # Roles
                "ver_rol", "asignar_roles",
                # Eventos
                "crear_evento", "ver_evento", "editar_evento", "eliminar_evento", "listar_eventos", "gestionar_eventos",
                # Mensualidades
                "crear_mensualidad", "ver_mensualidad", "editar_mensualidad", "abonar_mensualidad",
                "editar_abono_mensualidad", "eliminar_abono_mensualidad",
                "desactivar_mensualidad", "reactivar_mensualidad",
                # Acudientes
                "crear_acudiente", "ver_acudiente", "editar_acudiente", "listar_acudientes",
                # Salud
                "ver_diagnostico", "crear_diagnostico", "editar_diagnostico",
                # Reportes
                "ver_reportes", "generar_reportes", "exportar_reportes",
                # Catálogos
                "gestionar_catalogos", "ver_catalogos",
                # Galería
                "ver_galeria", "crear_foto", "editar_foto", "eliminar_foto", "subir_foto", "gestionar_galeria",
                # Calendario
                "ver_calendario", "gestionar_calendario",
                # Admin
                "acceso_panel_admin"
            ]
        },
        "Entrenador": {
            "descripcion": "Entrenador con permisos para gestionar deportistas y eventos",
            "permisos": [
                # Deportistas
                "crear_deportista", "ver_deportista", "editar_deportista", "listar_deportistas",
                # Eventos
                "crear_evento", "ver_evento", "editar_evento", "listar_eventos",
                # Acudientes
                "ver_acudiente", "listar_acudientes",
                # Salud
                "ver_diagnostico",
                # Catálogos
                "ver_catalogos",
                # Galería
                "ver_galeria", "crear_foto", "editar_foto", "subir_foto",
                # Calendario
                "ver_calendario",
                # Reportes básicos
                "ver_reportes",
                # Mensualidades (solo lectura)
                "ver_mensualidad"
            ]
        },
        "Deportista": {
            "descripcion": "Deportista con acceso de lectura limitado",
            "permisos": [
                # Solo lectura
                "ver_deportista",
                "ver_evento",
                "listar_eventos",
                # Mensualidades (solo lectura)
                "ver_mensualidad",
                "ver_galeria",
                "ver_calendario"
            ]
        },
        "Acudiente": {
            "descripcion": "Acudiente con acceso de lectura limitado",
            "permisos": [
                # Solo lectura
                "ver_deportista",
                "ver_evento",
                "listar_eventos",
                # Mensualidades (solo lectura)
                "ver_mensualidad",
                "ver_diagnostico",
                "ver_galeria",
                "ver_calendario"
            ]
        }
        ,
        "Usuario": {
            "descripcion": "Usuario básico con acceso solo a información pública de calendario y galería",
            "permisos": [
                "ver_calendario",
                "ver_galeria"
            ]
        }
    }
    
    roles_creados = 0
    roles_existentes = 0
    permisos_asignados = 0
    
    for nombre_rol, config in roles_config.items():
        # Verificar si el rol ya existe
        rol = Rol.query.filter_by(nombre_rol=nombre_rol).first()
        
        if not rol:
            # Crear nuevo rol
            rol = Rol(
                nombre_rol=nombre_rol,
                descripcion=config['descripcion']
            )
            db.session.add(rol)
            db.session.flush()  # Para obtener el ID del rol
            roles_creados += 1
            print(f"     ✅ Rol '{nombre_rol}' creado")
        else:
            roles_existentes += 1
            print(f"     ℹ️  Rol '{nombre_rol}' ya existe")
        
        # Asignar permisos al rol
        if config['permisos'] == "ALL":
            # SuperAdmin: obtener todos los permisos
            todos_permisos = Permiso.query.all()
            for permiso in todos_permisos:
                # Verificar si ya tiene el permiso
                rol_permiso_existente = RolPermiso.query.filter_by(
                    id_rol=rol.id_rol,
                    id_permiso=permiso.id_permiso
                ).first()
                
                if not rol_permiso_existente:
                    rol_permiso = RolPermiso(
                        id_rol=rol.id_rol,
                        id_permiso=permiso.id_permiso
                    )
                    db.session.add(rol_permiso)
                    permisos_asignados += 1
            
            print(f"        🔑 {len(todos_permisos)} permisos asignados a '{nombre_rol}'")
        else:
            # Asignar permisos específicos
            contador_permisos_rol = 0
            for nombre_permiso in config['permisos']:
                permiso = Permiso.query.filter_by(nombre=nombre_permiso).first()
                
                if permiso:
                    # Verificar si ya tiene el permiso
                    rol_permiso_existente = RolPermiso.query.filter_by(
                        id_rol=rol.id_rol,
                        id_permiso=permiso.id_permiso
                    ).first()
                    
                    if not rol_permiso_existente:
                        rol_permiso = RolPermiso(
                            id_rol=rol.id_rol,
                            id_permiso=permiso.id_permiso
                        )
                        db.session.add(rol_permiso)
                        permisos_asignados += 1
                        contador_permisos_rol += 1
                else:
                    print(f"        ⚠️  Permiso '{nombre_permiso}' no encontrado")
            
            if contador_permisos_rol > 0:
                print(f"        🔑 {contador_permisos_rol} permisos asignados a '{nombre_rol}'")

            # Sincronizar: remover permisos que el rol ya tenía pero no están en la configuración (excepto SuperAdmin)
            try:
                if nombre_rol != "SuperAdmin":
                    permisos_config = set(config['permisos'])
                    permisos_actuales = RolPermiso.query.filter_by(id_rol=rol.id_rol).all()
                    removidos = 0
                    for rp in permisos_actuales:
                        permiso_obj = Permiso.query.get(rp.id_permiso)
                        if permiso_obj and permiso_obj.nombre not in permisos_config:
                            db.session.delete(rp)
                            removidos += 1
                    if removidos:
                        print(f"        🧹 {removidos} permisos removidos de '{nombre_rol}' para sincronizar")
            except Exception as e:
                print(f"        ⚠️  No se pudo sincronizar permisos de '{nombre_rol}': {str(e)}")
    
    # Guardar cambios
    try:
        db.session.commit()
        print(f"\n     ✅ Roles creados: {roles_creados}")
        if roles_existentes > 0:
            print(f"     ℹ️  Roles existentes: {roles_existentes}")
        print(f"     🔑 Total de permisos asignados: {permisos_asignados}")
    except Exception as e:
        db.session.rollback()
        print(f"     ❌ Error al crear roles: {str(e)}")
        raise


if __name__ == '__main__':
    from backend.app import create_app
    app = create_app()
    with app.app_context():
        run()

