"""
Seeder para crear el super usuario del sistema.

Crea un usuario SuperAdmin con todos los permisos del sistema.
Este usuario es el administrador principal y tiene acceso total.

Credenciales por defecto:
- Usuario: superadmin
- Contraseña: Se obtiene de variable de entorno SEEDER_SUPERADMIN_PASSWORD
              o usa 'SuperAdmin2024!' por defecto

⚠️ IMPORTANTE: Cambiar la contraseña después del primer login.

Uso:
    python -m backend.src.seeders.seed_superadmin
    
    O con variable de entorno:
    SEEDER_SUPERADMIN_PASSWORD=MiPasswordSegura python -m backend.src.seeders.seed_superadmin
"""

from werkzeug.security import generate_password_hash
from src.models.base import db
from src.models.personas.persona import Persona
from src.models.usuarios.usuario import Usuario
from src.models.roles_y_permisos.rol import Rol
from src.models.roles_y_permisos.usuario_rol import UsuarioRol
from src.models.catalogos.tipo_documento import TipoDocumento
from src.models.categorias.sexo import Sexo
from src.config.seeder_config import get_superadmin_password


def run():
    """Ejecuta el seeder del super administrador."""
    print("  👑 Creando Super Administrador...")
    
    # Verificar si ya existe el super admin
    superadmin_existente = Usuario.query.filter_by(usuario='superadmin').first()
    
    if superadmin_existente:
        print("     ℹ️  Super Administrador ya existe")
        print("        Usuario: superadmin")
        print(f"        ID: {superadmin_existente.id_usuario}")
        return
    
    # Obtener tipo de documento CC (Cédula de Ciudadanía)
    tipo_doc = TipoDocumento.query.filter_by(nombre_documento='Cédula de Ciudadanía').first()
    if not tipo_doc:
        # Si no existe CC, buscar Tarjeta de Identidad
        tipo_doc = TipoDocumento.query.filter_by(nombre_documento='Tarjeta de Identidad').first()
    if not tipo_doc:
        # Si no existe, tomar el primero disponible
        tipo_doc = TipoDocumento.query.first()
        if not tipo_doc:
            print("     ❌ Error: No hay tipos de documento disponibles")
            print("        Ejecuta primero: seed_tipo_documento")
            return
    
    # Obtener sexo (tomar el primero disponible)
    sexo = Sexo.query.first()
    if not sexo:
        print("     ❌ Error: No hay sexos disponibles")
        print("        Ejecuta primero: seed_sexo")
        return
    
    # Obtener rol SuperAdmin
    rol_superadmin = Rol.query.filter_by(nombre_rol='SuperAdmin').first()
    if not rol_superadmin:
        print("     ❌ Error: Rol 'SuperAdmin' no encontrado")
        print("        Ejecuta primero: seed_roles")
        return
    
    try:
        # Crear persona para el super admin
        persona_superadmin = Persona(
            primer_nombre='Super',
            segundo_nombre='',
            primer_apellido='Admin',
            segundo_apellido='',
            documento='0000000000',
            correo_electronico='superadmin@puertaorion.com',
            direccion='Sistema',
            telefono='0000000000',
            id_tipo_documento=tipo_doc.id_documento,
            id_sexo=sexo.id_sexo,
            estado=True
        )
        
        db.session.add(persona_superadmin)
        db.session.flush()  # Para obtener el id_persona
        
        # Obtener password desde configuración
        superadmin_password = get_superadmin_password()
        
        # Crear usuario super admin
        usuario_superadmin = Usuario(
            id_persona=persona_superadmin.id_persona,
            usuario='superadmin',
            password=generate_password_hash(superadmin_password),
            estado=True
        )
        
        db.session.add(usuario_superadmin)
        db.session.flush()  # Para obtener el id_usuario
        
        # Asignar rol SuperAdmin al usuario
        usuario_rol = UsuarioRol(
            id_usuario=usuario_superadmin.id_usuario,
            id_rol=rol_superadmin.id_rol
        )
        
        db.session.add(usuario_rol)
        db.session.commit()
        
        print("     ✅ Super Administrador creado exitosamente")
        print("\n     🔑 CREDENCIALES DE ACCESO:")
        print("        Usuario: superadmin")
        print(f"        Contraseña: {superadmin_password}")
        print("        Rol: SuperAdmin")
        print("\n     ⚠️  IMPORTANTE: Cambia la contraseña después del primer login")
        
    except Exception as e:
        db.session.rollback()
        print(f"     ❌ Error al crear Super Administrador: {str(e)}")
        raise


if __name__ == '__main__':
    from backend.app import create_app
    app = create_app()
    with app.app_context():
        run()

