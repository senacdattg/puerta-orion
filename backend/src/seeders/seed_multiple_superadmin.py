"""
Seeder para crear múltiples super usuarios del sistema.

Permite crear varios usuarios SuperAdmin con todos los permisos del sistema.
Cada usuario tendrá acceso total al sistema.

Las passwords se obtienen de variables de entorno:
- SEEDER_SUPERADMIN_PASSWORD: Password para superadmin (default: 'SuperAdmin2024!')
- SEEDER_ADMIN2_PASSWORD: Password para admin2 (default: 'Admin2024!')
- SEEDER_ADMIN3_PASSWORD: Password para admin3 (default: 'Admin2024!')

Uso:
    python -m backend.src.seeders.seed_multiple_superadmin
    
    O con variables de entorno:
    SEEDER_SUPERADMIN_PASSWORD=MiPassword1 SEEDER_ADMIN2_PASSWORD=MiPassword2 python -m backend.src.seeders.seed_multiple_superadmin
"""

from werkzeug.security import generate_password_hash
from src.models.base import db
from src.models.personas.persona import Persona
from src.models.usuarios.usuario import Usuario
from src.models.roles_y_permisos.rol import Rol
from src.models.roles_y_permisos.usuario_rol import UsuarioRol
from src.models.catalogos.tipo_documento import TipoDocumento
from src.models.categorias.sexo import Sexo
from src.config.seeder_config import (
    get_superadmin_password,
    get_admin2_password,
    get_admin3_password
)


def run():
    """Ejecuta el seeder de múltiples super administradores."""
    print("  👑 Creando Múltiples Super Administradores...")
    
    # Obtener passwords desde configuración
    superadmin_password = get_superadmin_password()
    admin2_password = get_admin2_password()
    admin3_password = get_admin3_password()
    
    # Lista de super usuarios a crear
    super_usuarios = [
        {
            'usuario': 'superadmin',
            'password': superadmin_password,
            'primer_nombre': 'Super',
            'primer_apellido': 'Administrador',
            'documento': '0000000001',
            'email': 'superadmin@puertaorion.com',
            'telefono': '3000000001'
        },
        {
            'usuario': 'admin2',
            'password': admin2_password,
            'primer_nombre': 'Admin',
            'primer_apellido': 'Secundario',
            'documento': '0000000002',
            'email': 'admin2@puertaorion.com',
            'telefono': '3000000002'
        },
        {
            'usuario': 'admin3',
            'password': admin3_password,
            'primer_nombre': 'Admin',
            'primer_apellido': 'Terciario',
            'documento': '0000000003',
            'email': 'admin3@puertaorion.com',
            'telefono': '3000000003'
        }
        # Agrega más super usuarios aquí si necesitas
    ]
    
    try:
        # Obtener datos necesarios de catálogos
        tipo_documento = TipoDocumento.query.filter_by(nombre_documento='Cédula de Ciudadanía').first()
        if not tipo_documento:
            # Si no existe CC, buscar Tarjeta de Identidad
            tipo_documento = TipoDocumento.query.filter_by(nombre_documento='Tarjeta de Identidad').first()
        if not tipo_documento:
            # Si no existe, tomar el primero disponible
            tipo_documento = TipoDocumento.query.first()
            if not tipo_documento:
                print("  ❌ Error: No hay tipos de documento disponibles")
                return
        
        sexo = Sexo.query.first()
        if not sexo:
            print("  ❌ Error: No hay sexos disponibles")
            return
        
        # Obtener rol SuperAdmin
        rol_superadmin = Rol.query.filter_by(nombre_rol='SuperAdmin').first()
        if not rol_superadmin:
            print("  ❌ Error: Rol SuperAdmin no encontrado")
            return
        
        usuarios_creados = 0
        
        for datos_usuario in super_usuarios:
            # Verificar si ya existe el usuario
            usuario_existente = Usuario.query.filter_by(usuario=datos_usuario['usuario']).first()
            if usuario_existente:
                print(f"  ⚠️ Usuario {datos_usuario['usuario']} ya existe")
                continue
            
            # Crear persona
            persona = Persona(
                primer_nombre=datos_usuario['primer_nombre'],
                segundo_nombre='',
                primer_apellido=datos_usuario['primer_apellido'],
                segundo_apellido='',
                documento=datos_usuario['documento'],
                correo_electronico=datos_usuario['email'],
                direccion='Sistema',
                telefono=datos_usuario['telefono'],
                id_tipo_documento=tipo_documento.id_documento,
                id_sexo=sexo.id_sexo,
                estado=True
            )
            
            db.session.add(persona)
            db.session.flush()  # Para obtener el ID
            
            # Crear usuario
            usuario = Usuario(
                id_persona=persona.id_persona,
                usuario=datos_usuario['usuario'],
                password=generate_password_hash(datos_usuario['password']),
                estado=True
            )
            
            db.session.add(usuario)
            db.session.flush()  # Para obtener el ID
            
            # Asignar rol SuperAdmin
            usuario_rol = UsuarioRol(
                id_usuario=usuario.id_usuario,
                id_rol=rol_superadmin.id_rol
            )
            
            db.session.add(usuario_rol)
            usuarios_creados += 1
            
            print(f"  ✅ Super Usuario creado: {datos_usuario['usuario']}")
        
        db.session.commit()
        
        print(f"\n  🎉 Total de Super Usuarios creados: {usuarios_creados}")
        print("  📋 CREDENCIALES DE ACCESO:")
        print("  " + "="*50)
        
        for datos_usuario in super_usuarios:
            print(f"     Usuario: {datos_usuario['usuario']}")
            print(f"     Contraseña: {datos_usuario['password']}")
            print(f"     Email: {datos_usuario['email']}")
            print("     " + "-"*30)
        
        print(f"\n  ⚠️  IMPORTANTE: Cambia las contraseñas después del primer login")
        
    except Exception as e:
        db.session.rollback()
        print(f"  ❌ Error al crear Super Usuarios: {str(e)}")
        raise


if __name__ == '__main__':
    from backend.app import create_app
    app = create_app()
    with app.app_context():
        run()
