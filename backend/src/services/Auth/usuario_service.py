"""
Servicio para gestión de usuarios del sistema Puerta Orion.

Responsabilidad:
- Registrar nuevas personas y usuarios
- Validar unicidad de datos críticos
- Manejar hashing de contraseñas
- Gestionar transacciones de base de datos

Este módulo sigue los principios SRP, KISS, DRY y SOLID.
"""

from datetime import date
from typing import Dict, Any, Optional, Tuple, List

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash, generate_password_hash

from src.models.acudientes.acudiente import Acudiente
from src.models.base import db
from src.models.deportistas.deportista import Deportista
from src.models.personas.persona import Persona
from src.models.roles_y_permisos.rol import Rol
from src.models.roles_y_permisos.usuario_rol import UsuarioRol
from src.models.usuarios.usuario import Usuario
from src.utils.logger import obtener_registrador
from .role_permission_service import puede_registrarse_como_acudiente
from src.utils.validations import (
    ValidationError,
    sanitize_address,
    sanitize_free_text,
    validate_document,
    validate_email,
    validate_name,
    validate_phone,
)


class UsuarioServiceError(Exception):
    """Excepción personalizada para errores del servicio de usuario."""
    pass


class UsuarioService:
    """
    Servicio para gestión de usuarios.
    
    Encapsula toda la lógica de negocio relacionada con el registro
    y gestión de usuarios, siguiendo el principio de responsabilidad única.
    """
    
    def __init__(self):
        """Inicializa el servicio con el logger configurado."""
        self.logger = obtener_registrador('aplicacion')
    
    def registrar_usuario_completo(
        self, 
        datos_persona: Dict[str, Any], 
        datos_usuario: Dict[str, Any],
        rol_opcional: str = None,
        datos_rol: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Registra una persona y crea su usuario asociado, opcionalmente creando
        registro de Deportista o Acudiente si se especifica el rol.
        
        Args:
            datos_persona (Dict): Datos de la persona a registrar
            datos_usuario (Dict): Datos del usuario a crear
            rol_opcional (str): Rol opcional ('deportista' o 'acudiente')
            datos_rol (Dict): Datos adicionales para el rol (opcional)
            
        Returns:
            Dict: Información del usuario creado (sin password)
            
        Raises:
            UsuarioServiceError: Si hay errores de validación o duplicación
        """
        try:
            # Validar datos de entrada
            self._validar_datos_persona(datos_persona)
            self._validar_datos_usuario(datos_usuario)
            
            # Validar unicidad antes de crear
            self._validar_unicidad(datos_persona, datos_usuario)
            
            # Crear persona y usuario en una transacción
            usuario_creado = self._crear_persona_y_usuario(
                datos_persona, 
                datos_usuario, 
                rol_opcional,
                datos_rol
            )
            
            self.logger.info(f"Usuario registrado exitosamente: {usuario_creado['usuario']}")
            
            return usuario_creado
            
        except UsuarioServiceError:
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado al registrar usuario: {str(e)}")
            raise UsuarioServiceError(f"Error interno del servidor: {str(e)}")
    
    def _validar_datos_persona(self, datos: Dict[str, Any]) -> None:
        """
        Valida los datos requeridos para crear una persona.
        
        Args:
            datos (Dict): Datos de la persona
            
        Raises:
            UsuarioServiceError: Si faltan campos requeridos
        """
        try:
            datos['primer_nombre'] = validate_name('primer_nombre', datos.get('primer_nombre'))
            datos['segundo_nombre'] = validate_name('segundo_nombre', datos.get('segundo_nombre'), required=False)
            datos['primer_apellido'] = validate_name('primer_apellido', datos.get('primer_apellido'))
            datos['segundo_apellido'] = validate_name('segundo_apellido', datos.get('segundo_apellido'), required=False)

            datos['documento'] = validate_document('documento', datos.get('documento'))
            telefono_normalizado = validate_phone('telefono', datos.get('telefono'), required=False)
            datos['telefono'] = telefono_normalizado or None
            datos['correo_electronico'] = validate_email('correo_electronico', datos.get('correo_electronico'))
            direccion_normalizada = sanitize_address('direccion', datos.get('direccion'), required=False)
            datos['direccion'] = direccion_normalizada or None

            # Normalizar observaciones u otros campos textuales si vienen
            if 'observaciones' in datos:
                datos['observaciones'] = sanitize_free_text('observaciones', datos.get('observaciones'))

            # Campos requeridos numéricos
            faltantes_ids = [
                campo for campo in ('id_tipo_documento', 'id_sexo') if not datos.get(campo)
            ]
            if faltantes_ids:
                raise UsuarioServiceError(
                    f"Campos requeridos faltantes: {', '.join(faltantes_ids)}"
                )

            # Ajustar opcionales a None si quedan vacíos
            if not datos['segundo_nombre']:
                datos['segundo_nombre'] = None
            if not datos['segundo_apellido']:
                datos['segundo_apellido'] = None

        except ValidationError as error:
            raise UsuarioServiceError(str(error))
    
    def _validar_datos_usuario(self, datos: Dict[str, Any]) -> None:
        """
        Valida los datos requeridos para crear un usuario.
        
        Args:
            datos (Dict): Datos del usuario
            
        Raises:
            UsuarioServiceError: Si faltan campos requeridos o son inválidos
        """
        campos_requeridos = ['usuario', 'password']
        campos_faltantes = [campo for campo in campos_requeridos if not datos.get(campo)]

        if campos_faltantes:
            raise UsuarioServiceError(f"Campos de usuario requeridos faltantes: {', '.join(campos_faltantes)}")

        password = str(datos.get('password', '')).strip()
        if len(password) < 6:
            raise UsuarioServiceError("La contraseña debe tener al menos 6 caracteres")

        usuario = str(datos.get('usuario', '')).strip()
        if len(usuario) < 3:
            raise UsuarioServiceError("El nombre de usuario debe tener al menos 3 caracteres")

        if len(usuario) > 200:
            raise UsuarioServiceError("El nombre de usuario excede la longitud máxima (200 caracteres)")

        datos['usuario'] = usuario.lower()
        datos['password'] = password
    
    def _validar_unicidad(self, datos_persona: Dict[str, Any], datos_usuario: Dict[str, Any]) -> None:
        """
        Valida que no existan duplicados en campos únicos.
        
        Args:
            datos_persona (Dict): Datos de la persona
            datos_usuario (Dict): Datos del usuario
            
        Raises:
            UsuarioServiceError: Si se encuentran duplicados
        """
        documento = datos_persona.get('documento')
        email = datos_persona.get('correo_electronico')
        username = datos_usuario.get('usuario')
        
        # Verificar documento único
        if Persona.query.filter_by(documento=documento).first():
            raise UsuarioServiceError(f"Ya existe una persona con el documento {documento}")
        
        # Verificar email único
        if Persona.query.filter_by(correo_electronico=email).first():
            raise UsuarioServiceError(f"Ya existe una persona con el email {email}")
        
        # Verificar username único
        if Usuario.query.filter_by(usuario=username).first():
            raise UsuarioServiceError(f"Ya existe un usuario con el nombre {username}")
    
    def _asignar_rol_especifico(self, usuario: Usuario, rol_opcional: str, rol_por_defecto: Optional[Rol]) -> None:
        """Asigna un rol específico al usuario si se proporciona."""
        rol_especifico = Rol.query.filter_by(nombre_rol=rol_opcional.capitalize()).first()
        if rol_especifico:
            rol_existente = UsuarioRol.query.filter_by(
                id_usuario=usuario.id_usuario,
                id_rol=rol_especifico.id_rol
            ).first()
            
            if not rol_existente:
                usuario_rol = UsuarioRol(
                    id_usuario=usuario.id_usuario,
                    id_rol=rol_especifico.id_rol
                )
                db.session.add(usuario_rol)
                usuario.set_rol_activo(rol_especifico)
        elif rol_por_defecto:
            usuario.set_rol_activo(rol_por_defecto)

    def _procesar_rol_opcional(self, usuario: Usuario, rol_opcional: str, datos_rol: Optional[Dict[str, Any]], rol_por_defecto: Optional[Rol]) -> None:
        """Procesa el rol opcional si se especifica."""
        if not rol_opcional or rol_opcional not in ['deportista', 'acudiente']:
            if rol_por_defecto:
                usuario.set_rol_activo(rol_por_defecto)
            return
        
        self._crear_registro_rol(usuario, rol_opcional, datos_rol)
        self._asignar_rol_especifico(usuario, rol_opcional, rol_por_defecto)

    def _crear_persona_y_usuario(
        self, 
        datos_persona: Dict[str, Any], 
        datos_usuario: Dict[str, Any],
        rol_opcional: str = None,
        datos_rol: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Crea la persona, el usuario y opcionalmente Deportista o Acudiente en una transacción atómica.
        
        Args:
            datos_persona (Dict): Datos de la persona
            datos_usuario (Dict): Datos del usuario
            rol_opcional (str): Rol opcional ('deportista' o 'acudiente')
            datos_rol (Dict): Datos adicionales para el rol
            
        Returns:
            Dict: Información del usuario creado
            
        Raises:
            UsuarioServiceError: Si hay errores en la creación
        """
        try:
            persona = self._crear_persona(datos_persona)
            db.session.flush()
            
            usuario = self._crear_usuario(persona.id_persona, datos_usuario)
            db.session.flush()
            
            rol_por_defecto = self._asignar_rol_por_defecto(usuario)
            self._procesar_rol_opcional(usuario, rol_opcional, datos_rol, rol_por_defecto)
            
            db.session.commit()
            return self._serializar_usuario(usuario)
            
        except IntegrityError as e:
            db.session.rollback()
            self.logger.error(f"Error de integridad al crear usuario: {str(e)}")
            raise UsuarioServiceError("Error de duplicación de datos")
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error al crear usuario: {str(e)}")
            raise UsuarioServiceError(f"Error al crear usuario: {str(e)}")
    
    def _crear_persona(self, datos: Dict[str, Any]) -> Persona:
        """
        Crea una nueva persona en la base de datos.
        
        Args:
            datos (Dict): Datos de la persona
            
        Returns:
            Persona: Instancia de la persona creada
        """
        persona = Persona(
            primer_nombre=datos['primer_nombre'],
            segundo_nombre=datos.get('segundo_nombre') or None,
            primer_apellido=datos['primer_apellido'],
            segundo_apellido=datos.get('segundo_apellido') or None,
            documento=datos['documento'],
            correo_electronico=datos['correo_electronico'],
            direccion=datos['direccion'],
            telefono=datos['telefono'],
            estado=True,
            fecha_registro=date.today(),
            id_tipo_documento=datos['id_tipo_documento'],
            id_sexo=datos['id_sexo']
        )
        
        db.session.add(persona)
        return persona
    
    def _crear_usuario(self, id_persona: int, datos: Dict[str, Any]) -> Usuario:
        """
        Crea un nuevo usuario asociado a una persona.
        
        Args:
            id_persona (int): ID de la persona asociada
            datos (Dict): Datos del usuario
            
        Returns:
            Usuario: Instancia del usuario creado
        """
        # Hashear contraseña
        password_hash = generate_password_hash(datos['password'])
        
        usuario = Usuario(
            id_persona=id_persona,
            usuario=datos['usuario'],
            password=password_hash,
            estado=True
        )
        
        db.session.add(usuario)
        return usuario
    
    def _procesar_fecha_nacimiento_deportista(self, fecha_nacimiento_raw: Any) -> Optional[date]:
        """Procesa y convierte la fecha de nacimiento para deportista."""
        if not fecha_nacimiento_raw:
            return None
        
        from datetime import datetime
        
        if isinstance(fecha_nacimiento_raw, date):
            return fecha_nacimiento_raw
        
        if isinstance(fecha_nacimiento_raw, int):
            return date(fecha_nacimiento_raw, 1, 1)
        
        if isinstance(fecha_nacimiento_raw, str):
            try:
                return datetime.fromisoformat(fecha_nacimiento_raw).date()
            except ValueError:
                try:
                    anio = int(fecha_nacimiento_raw)
                    return date(anio, 1, 1)
                except ValueError:
                    raise UsuarioServiceError(f'Formato de fecha de nacimiento inválido: {fecha_nacimiento_raw}')
        
        return None

    def _crear_deportista_registro(self, id_persona: int, datos: Dict[str, Any]) -> None:
        """Crea un registro de deportista."""
        deportista_existente = Deportista.query.filter_by(id_persona=id_persona).first()
        if deportista_existente:
            raise UsuarioServiceError("Ya existe un registro de deportista para esta persona")
        
        if not datos or not datos.get('id_categoria'):
            raise UsuarioServiceError("El campo 'id_categoria' es obligatorio para crear un deportista")
        
        fecha_nacimiento_date = self._procesar_fecha_nacimiento_deportista(datos.get('fecha_nacimiento'))
        
        deportista = Deportista(
            id_persona=id_persona,
            id_categoria=datos['id_categoria'],
            peso=datos.get('peso'),
            altura=datos.get('altura'),
            fecha_ingreso=datos.get('fecha_ingreso', date.today()),
            fecha_nacimiento=fecha_nacimiento_date,
            id_tipo_sanguineo=datos.get('id_tipo_sanguineo'),
            id_ciudad_recidencia=datos.get('id_ciudad_recidencia'),
            id_informacion_deportiva=datos.get('id_informacion_deportiva'),
            id_eps=datos.get('id_eps')
        )
        db.session.add(deportista)
        self.logger.info(f"Registro de deportista creado para persona ID: {id_persona}")

    def _crear_acudiente_registro(self, id_persona: int, usuario: Usuario, datos: Optional[Dict[str, Any]]) -> None:
        """Crea un registro de acudiente."""
        acudiente_existente = Acudiente.query.filter_by(id_persona=id_persona).first()
        if acudiente_existente:
            raise UsuarioServiceError("Ya existe un registro de acudiente para esta persona")

        if not puede_registrarse_como_acudiente(usuario):
            raise UsuarioServiceError(
                "Para registrarse como acudiente debe cumplir la mayoría de edad o no ser deportista activo"
            )
        
        acudiente = Acudiente(
            id_persona=id_persona,
            estado=datos.get('estado', True) if datos else True
        )
        db.session.add(acudiente)
        self.logger.info(f"Registro de acudiente creado para persona ID: {id_persona}")

    def _crear_registro_rol(self, usuario: Usuario, rol: str, datos: Dict[str, Any]) -> None:
        """
        Crea un registro de Deportista o Acudiente según el rol especificado.
        
        Args:
            usuario (Usuario): Usuario asociado
            rol (str): Tipo de rol ('deportista' o 'acudiente')
            datos (Dict): Datos adicionales para el rol (opcional)
            
        Raises:
            UsuarioServiceError: Si hay errores en la creación
        """
        try:
            id_persona = usuario.id_persona

            if rol == 'deportista':
                self._crear_deportista_registro(id_persona, datos)
            elif rol == 'acudiente':
                self._crear_acudiente_registro(id_persona, usuario, datos)
            else:
                raise UsuarioServiceError(f"Rol inválido: {rol}")
                
        except UsuarioServiceError:
            raise
        except Exception as e:
            self.logger.error(f"Error al crear registro de {rol}: {str(e)}")
            raise UsuarioServiceError(f"Error al crear registro de {rol}: {str(e)}")
    
    def _asignar_rol_por_defecto(self, usuario: Usuario) -> Rol:
        """
        Asigna el rol por defecto 'usuario' al usuario recién creado.
        
        Args:
            usuario (Usuario): Usuario al que asignar el rol
            
        Raises:
            UsuarioServiceError: Si hay errores al asignar el rol
        """
        try:
            # Verificar si el usuario ya tiene roles asignados
            roles_existentes = UsuarioRol.query.filter_by(id_usuario=usuario.id_usuario).all()
            if roles_existentes:
                self.logger.info(
                    f"Usuario {usuario.id_usuario} ya tiene roles asignados, omitiendo asignación de rol por defecto"
                )
                rol_usuario = Rol.query.filter_by(nombre_rol='usuario').first()
                if rol_usuario and any(rel.id_rol == rol_usuario.id_rol for rel in roles_existentes):
                    return rol_usuario
                primer_rol = Rol.query.get(roles_existentes[0].id_rol)
                return primer_rol
            
            # Obtener o crear el rol por defecto
            rol_usuario = self._obtener_o_crear_rol_usuario()
            
            # Crear la relación usuario-rol
            usuario_rol = UsuarioRol(
                id_usuario=usuario.id_usuario,
                id_rol=rol_usuario.id_rol
            )
            
            db.session.add(usuario_rol)
            self.logger.info(f"Rol 'usuario' asignado al usuario ID: {usuario.id_usuario}")
            return rol_usuario
            
        except Exception as e:
            self.logger.error(f"Error al asignar rol por defecto: {str(e)}")
            raise UsuarioServiceError(f"Error al asignar rol por defecto: {str(e)}")
    
    def _obtener_o_crear_rol_usuario(self) -> Rol:
        """
        Obtiene el rol 'usuario' o lo crea si no existe.
        
        Returns:
            Rol: Instancia del rol 'usuario'
            
        Raises:
            UsuarioServiceError: Si hay errores al crear el rol
        """
        try:
            # Buscar el rol 'usuario'
            rol_usuario = Rol.query.filter_by(nombre_rol='usuario').first()
            
            if not rol_usuario:
                # Crear el rol 'usuario' si no existe
                rol_usuario = Rol(
                    nombre_rol='usuario',
                    descripcion='Rol por defecto para usuarios del sistema'
                )
                
                db.session.add(rol_usuario)
                db.session.flush()  # Obtener ID sin hacer commit
                
                self.logger.info("Rol 'usuario' creado automáticamente")
            
            return rol_usuario
            
        except Exception as e:
            self.logger.error(f"Error al obtener/crear rol usuario: {str(e)}")
            raise UsuarioServiceError(f"Error al gestionar rol usuario: {str(e)}")
    
    def _serializar_usuario(self, usuario: Usuario) -> Dict[str, Any]:
        """
        Serializa un usuario para retorno (sin exponer password).
        
        Args:
            usuario (Usuario): Instancia del usuario
            
        Returns:
            Dict: Datos del usuario serializados
        """
        # Obtener roles del usuario
        roles_usuario = []
        if hasattr(usuario, 'roles') and usuario.roles:
            roles_usuario = [rol.to_dict() for rol in usuario.roles]
        
        # Serializar datos de persona solo si existe
        datos_persona = None
        if usuario.persona:
            datos_persona = {
                'nombre_completo': usuario.persona.nombre_completo,
                'correo_electronico': usuario.persona.correo_electronico,
                'documento': usuario.persona.documento,
                'telefono': usuario.persona.telefono
            }
        
        return {
            'id_usuario': usuario.id_usuario,
            'id_persona': usuario.id_persona,
            'usuario': usuario.usuario,
            'estado': usuario.estado,
            'roles': roles_usuario,
            'persona': datos_persona,
            'fecha_creacion': usuario.created_at.isoformat() if usuario.created_at else None
        }
    
    def verificar_credenciales(self, usuario: str, password: str) -> Optional[Usuario]:
        """
        Verifica las credenciales de un usuario.
        
        Args:
            usuario (str): Nombre de usuario
            password (str): Contraseña en texto plano
            
        Returns:
            Usuario: Usuario si las credenciales son válidas, None en caso contrario
        """
        try:
            usuario_obj = Usuario.query.filter_by(usuario=usuario, estado=True).first()
            
            if usuario_obj and check_password_hash(usuario_obj.password, password):
                return usuario_obj
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error al verificar credenciales: {str(e)}")
            return None
    
    def obtener_usuario_por_id(self, id_usuario: int) -> Optional[Usuario]:
        """
        Obtiene un usuario por su ID.
        
        Args:
            id_usuario (int): ID del usuario
            
        Returns:
            Usuario: Usuario encontrado o None
        """
        try:
            return Usuario.query.filter_by(id_usuario=id_usuario, estado=True).first()
        except Exception as e:
            self.logger.error(f"Error al obtener usuario por ID: {str(e)}")
            return None
    
    def obtener_usuario_con_roles(self, id_usuario: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un usuario por su ID con información de roles.
        
        Args:
            id_usuario (int): ID del usuario
            
        Returns:
            Dict: Usuario con roles o None
        """
        try:
            usuario = Usuario.query.filter_by(id_usuario=id_usuario, estado=True).first()
            if usuario:
                return self._serializar_usuario(usuario)
            return None
        except Exception as e:
            self.logger.error(f"Error al obtener usuario con roles: {str(e)}")
            return None

    def actualizar_usuario(
        self, 
        id_usuario: int, 
        datos_persona: Dict[str, Any] = None,
        datos_usuario: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Actualiza los datos de un usuario existente.
        
        Permite actualizar tanto datos de la persona como datos del usuario.
        La contraseña NO se puede actualizar desde este método.
        Aplica validaciones de unicidad y formato antes de actualizar.
        
        Args:
            id_usuario (int): ID del usuario a actualizar
            datos_persona (Dict): Datos de la persona a actualizar (opcional)
            datos_usuario (Dict): Datos del usuario a actualizar (opcional, sin contraseña)
            
        Returns:
            Dict: Respuesta con el resultado de la operación
            
        Raises:
            UsuarioServiceError: Si hay errores de validación o el usuario no existe
        """
        try:
            # Verificar que el usuario existe
            usuario = Usuario.query.filter_by(id_usuario=id_usuario).first()
            if not usuario:
                raise UsuarioServiceError(f"Usuario con ID {id_usuario} no encontrado")
            
            # Verificar que el usuario esté activo
            if not usuario.estado:
                raise UsuarioServiceError(f"Usuario con ID {id_usuario} está inactivo")
            
            # Validar y actualizar datos de persona SOLO si se proporcionan
            if datos_persona:
                # Cargar la persona directamente desde la sesión para asegurar que esté en el contexto de SQLAlchemy
                from src.models.personas.persona import Persona
                persona = Persona.query.get(usuario.id_persona)
                if not persona:
                    raise UsuarioServiceError(f"Persona con ID {usuario.id_persona} no encontrada para el usuario {id_usuario}")
                
                self.logger.info(f"Actualizando datos de persona ID: {persona.id_persona} (antes: {persona.primer_nombre} {persona.primer_apellido})")
                self._validar_y_actualizar_persona(persona, datos_persona, persona.id_persona)
                self.logger.info(f"Datos de persona actualizados: {persona.primer_nombre} {persona.primer_apellido}")
                
                # Asegurar que SQLAlchemy detecte los cambios en el objeto persona
                db.session.add(persona)
            
            # Validar y actualizar datos de usuario SOLO si se proporcionan
            if datos_usuario:
                self._validar_y_actualizar_usuario(usuario, datos_usuario, id_usuario)
            
            # Verificar que se haya actualizado al menos un campo
            if not datos_persona and not datos_usuario:
                raise UsuarioServiceError("Debe proporcionar al menos datos_persona o datos_usuario para actualizar")
            
            # Asegurar que los objetos estén marcados como modificados
            db.session.flush()
            
            # Guardar cambios
            db.session.commit()
            
            # Refrescar los objetos para obtener los valores actualizados
            db.session.refresh(usuario)
            if datos_persona and usuario.persona:
                db.session.refresh(usuario.persona)
            
            self.logger.info(f"Usuario actualizado exitosamente: ID {id_usuario}")
            
            # Retornar datos actualizados
            return {
                'success': True,
                'message': 'Usuario actualizado exitosamente',
                'data': self._serializar_usuario(usuario),
                'status_code': 200
            }
            
        except UsuarioServiceError:
            db.session.rollback()
            raise
        except IntegrityError as e:
            db.session.rollback()
            self.logger.error(f"Error de integridad al actualizar usuario: {str(e)}")
            raise UsuarioServiceError("Error de duplicación de datos")
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error inesperado al actualizar usuario: {str(e)}")
            raise UsuarioServiceError(f"Error interno del servidor: {str(e)}")
    
    def _validar_y_actualizar_usuario(
        self, 
        usuario: Usuario, 
        datos: Dict[str, Any],
        id_usuario: int
    ) -> None:
        """
        Valida y actualiza los datos del usuario.
        
        Nota: La contraseña NO se actualiza desde este método.
        Para cambiar la contraseña, debe usarse un endpoint dedicado.
        
        Args:
            usuario (Usuario): Objeto Usuario a actualizar
            datos (Dict): Datos a actualizar
            id_usuario (int): ID del usuario (para validaciones de unicidad)
            
        Raises:
            UsuarioServiceError: Si hay errores de validación
        """
        # Validar nombre de usuario si se proporciona
        if 'usuario' in datos:
            nuevo_usuario = datos['usuario'].strip()
            
            # Validar longitud
            if len(nuevo_usuario) < 3:
                raise UsuarioServiceError("El nombre de usuario debe tener al menos 3 caracteres")
            
            if len(nuevo_usuario) > 200:
                raise UsuarioServiceError("El nombre de usuario excede la longitud máxima (200 caracteres)")
            
            # Validar unicidad (excluyendo el usuario actual)
            usuario_existente = Usuario.query.filter_by(usuario=nuevo_usuario).filter(
                Usuario.id_usuario != id_usuario
            ).first()
            
            if usuario_existente:
                raise UsuarioServiceError(f"Ya existe un usuario con el nombre {nuevo_usuario}")
            
            usuario.usuario = nuevo_usuario
        
        # No permitir actualizar contraseña desde este endpoint
        if 'password' in datos:
            raise UsuarioServiceError("La contraseña no se puede actualizar desde este endpoint. Use el endpoint dedicado para cambio de contraseña")
        
        # No permitir actualizar estado desde este endpoint
        if 'estado' in datos:
            raise UsuarioServiceError("El estado no se puede actualizar desde este endpoint. Use los endpoints dedicados para activar/desactivar usuarios")
    
    def _actualizar_campo_nombre(self, persona: Persona, datos: Dict[str, Any], campo: str, campos_actualizados: List[str]) -> None:
        """Actualiza un campo de nombre de la persona."""
        if campo not in datos:
            return
        
        es_segundo = campo in ['segundo_nombre', 'segundo_apellido']
        valor_validado = validate_name(campo, datos.get(campo), required=not es_segundo)
        valor_db = valor_validado or None if es_segundo else valor_validado
        
        if getattr(persona, campo) != valor_db:
            setattr(persona, campo, valor_db)
            campos_actualizados.append(campo)

    def _actualizar_documento(self, persona: Persona, datos: Dict[str, Any], id_persona: int, campos_actualizados: List[str]) -> None:
        """Valida y actualiza el documento de la persona."""
        if 'documento' not in datos:
            return
        
        documento = validate_document('documento', datos['documento'])
        documento_existente = (
            Persona.query.filter_by(documento=documento)
            .filter(Persona.id_persona != id_persona)
            .first()
        )
        
        if documento_existente:
            raise UsuarioServiceError(f"Ya existe una persona con el documento {documento}")
        
        if persona.documento != documento:
            persona.documento = documento
            campos_actualizados.append('documento')

    def _actualizar_email(self, persona: Persona, datos: Dict[str, Any], id_persona: int, campos_actualizados: List[str]) -> None:
        """Valida y actualiza el correo electrónico de la persona."""
        if 'correo_electronico' not in datos:
            return
        
        email = validate_email('correo_electronico', datos['correo_electronico'])
        email_existente = (
            Persona.query.filter_by(correo_electronico=email)
            .filter(Persona.id_persona != id_persona)
            .first()
        )
        
        if email_existente:
            raise UsuarioServiceError(f"Ya existe una persona con el email {email}")
        
        if persona.correo_electronico != email:
            persona.correo_electronico = email
            campos_actualizados.append('correo_electronico')

    def _actualizar_direccion(self, persona: Persona, datos: Dict[str, Any], campos_actualizados: List[str]) -> None:
        """Actualiza la dirección de la persona."""
        if 'direccion' not in datos:
            return
        
        nueva_direccion = sanitize_address('direccion', datos.get('direccion'), required=False)
        nueva_direccion_db = nueva_direccion or None
        if persona.direccion != nueva_direccion_db:
            persona.direccion = nueva_direccion_db
            campos_actualizados.append('direccion')

    def _actualizar_telefono(self, persona: Persona, datos: Dict[str, Any], campos_actualizados: List[str]) -> None:
        """Valida y actualiza el teléfono de la persona."""
        if 'telefono' not in datos:
            return
        
        telefono = validate_phone('telefono', datos['telefono'])
        if persona.telefono != telefono:
            persona.telefono = telefono
            campos_actualizados.append('telefono')

    def _actualizar_relaciones_persona(self, persona: Persona, datos: Dict[str, Any], campos_actualizados: List[str]) -> None:
        """Valida y actualiza las relaciones de la persona (tipo_documento, sexo)."""
        if 'id_tipo_documento' in datos:
            from src.models.catalogos.tipo_documento import TipoDocumento
            tipo_doc = TipoDocumento.query.get(datos['id_tipo_documento'])
            if not tipo_doc:
                raise UsuarioServiceError(f"Tipo de documento con ID {datos['id_tipo_documento']} no encontrado")
            if persona.id_tipo_documento != datos['id_tipo_documento']:
                persona.id_tipo_documento = datos['id_tipo_documento']
                campos_actualizados.append('id_tipo_documento')
        
        if 'id_sexo' in datos:
            from src.models.categorias.sexo import Sexo
            sexo = Sexo.query.get(datos['id_sexo'])
            if not sexo:
                raise UsuarioServiceError(f"Sexo con ID {datos['id_sexo']} no encontrado")
            if persona.id_sexo != datos['id_sexo']:
                persona.id_sexo = datos['id_sexo']
                campos_actualizados.append('id_sexo')

    def _validar_y_actualizar_persona(
        self, 
        persona: Persona, 
        datos: Dict[str, Any],
        id_persona: int
    ) -> None:
        """
        Valida y actualiza los datos de la persona.
        
        Args:
            persona (Persona): Objeto Persona a actualizar
            datos (Dict): Datos a actualizar
            id_persona (int): ID de la persona (para validaciones de unicidad)
            
        Raises:
            UsuarioServiceError: Si hay errores de validación
        """
        campos_actualizados = []
        
        try:
            self._actualizar_campo_nombre(persona, datos, 'primer_nombre', campos_actualizados)
            self._actualizar_campo_nombre(persona, datos, 'segundo_nombre', campos_actualizados)
            self._actualizar_campo_nombre(persona, datos, 'primer_apellido', campos_actualizados)
            self._actualizar_campo_nombre(persona, datos, 'segundo_apellido', campos_actualizados)
            
            self._actualizar_documento(persona, datos, id_persona, campos_actualizados)
            self._actualizar_email(persona, datos, id_persona, campos_actualizados)
            self._actualizar_direccion(persona, datos, campos_actualizados)
            self._actualizar_telefono(persona, datos, campos_actualizados)
            
        except ValidationError as error:
            raise UsuarioServiceError(str(error))
        
        self._actualizar_relaciones_persona(persona, datos, campos_actualizados)
        
        if 'estado' in datos:
            raise UsuarioServiceError("El estado no se puede actualizar desde este endpoint. Use los endpoints dedicados para activar/desactivar personas")
        
        if campos_actualizados:
            self.logger.info(f"Campos de persona actualizados: {', '.join(campos_actualizados)}")
        else:
            self.logger.warning("No se actualizaron campos de persona (todos los valores son iguales a los existentes)")

    def _obtener_usuario_para_detalle(self, id_usuario: int, usuario_obj: Optional[Usuario]) -> Optional[Usuario]:
        """Obtiene el usuario para el detalle completo."""
        if usuario_obj:
            self.logger.info(f"[DETALLE] Usando usuario proporcionado: {usuario_obj.usuario} (ID: {usuario_obj.id_usuario}, estado: {usuario_obj.estado})")
            return usuario_obj
        
        usuario_sin_filtro = Usuario.query.filter_by(id_usuario=id_usuario).first()
        if usuario_sin_filtro:
            self.logger.info(f"[DETALLE] Usuario encontrado sin filtro de estado: {usuario_sin_filtro.usuario}, estado: {usuario_sin_filtro.estado}")
        
        usuario = Usuario.query.filter_by(id_usuario=id_usuario, estado=True).first()
        
        if not usuario and usuario_sin_filtro:
            self.logger.warning(f"[DETALLE] Usuario ID {id_usuario} existe pero está inactivo, usando de todas formas (token válido)")
            usuario = usuario_sin_filtro
        
        if not usuario:
            self.logger.warning(f"[DETALLE] Usuario ID {id_usuario} no encontrado en la base de datos")
            return None
        
        self.logger.info(f"[DETALLE] Usuario encontrado: {usuario.usuario} (ID: {usuario.id_usuario}, estado: {usuario.estado})")
        return usuario

    def _obtener_fecha_nacimiento_persona(self, id_persona: int) -> Optional[date]:
        """Obtiene la fecha de nacimiento del deportista si existe."""
        deportista_temp = Deportista.query.filter_by(id_persona=id_persona).first()
        if deportista_temp and deportista_temp.fecha_nacimiento:
            return deportista_temp.fecha_nacimiento
        return None

    def _obtener_roles_usuario(self, usuario: Usuario) -> List[Dict[str, Any]]:
        """Obtiene los roles del usuario en formato de lista."""
        if not hasattr(usuario, 'roles') or not usuario.roles:
            return []
        
        return [{
            'id_rol': rol.id_rol,
            'nombre_rol': rol.nombre_rol,
            'descripcion': rol.descripcion
        } for rol in usuario.roles]

    def _construir_datos_persona(self, persona: Persona, fecha_nacimiento: Optional[date]) -> Dict[str, Any]:
        """Construye el diccionario de datos de la persona."""
        return {
            'primer_nombre': persona.primer_nombre,
            'segundo_nombre': persona.segundo_nombre,
            'primer_apellido': persona.primer_apellido,
            'segundo_apellido': persona.segundo_apellido,
            'documento': persona.documento,
            'correo_electronico': persona.correo_electronico,
            'direccion': persona.direccion,
            'telefono': persona.telefono,
            'fecha_nacimiento': fecha_nacimiento,
            'id_tipo_documento': persona.id_tipo_documento,
            'id_sexo': persona.id_sexo,
            'nombre_completo': persona.nombre_completo
        }

    def _agregar_info_deportista(self, resultado: Dict[str, Any], deportista: Deportista) -> None:
        """Agrega información del deportista al resultado."""
        from src.models.deportistas.informacion_deportiva import InformacionDeportiva
        from src.models.salud.diagnostico_deportista import DiagnosticoDeportista
        from src.models.salud.diagnostico import Diagnostico
        
        resultado['deportista'] = {
            'id_deportista': deportista.id_deportista,
            'fecha_nacimiento': deportista.fecha_nacimiento,
            'id_tipo_sanguineo': deportista.id_tipo_sanguineo,
            'id_ciudad_recidencia': deportista.id_ciudad_recidencia,
            'id_eps': deportista.id_eps,
            'peso': deportista.peso,
            'altura': deportista.altura
        }

        if deportista.id_informacion_deportiva:
            info_deportiva = InformacionDeportiva.query.filter_by(
                id_informacion_deportiva=deportista.id_informacion_deportiva
            ).first()
            if info_deportiva:
                resultado['informacion_deportiva'] = {
                    'practica_otro_deporte': info_deportiva.practica_otro_deporte,
                    'participa_escuela': info_deportiva.participa_escuela,
                    'recomendacion_medica': info_deportiva.recomendacion_medica,
                    'descripcion_recomendacion': info_deportiva.descripcion_recomendacion,
                    'id_escuela': info_deportiva.id_escuela,
                    'id_deporte': info_deportiva.id_deporte,
                    'id_institucion_registro': info_deportiva.id_institucion_registro,
                    'id_categoria': deportista.id_categoria
                }

        diagnosticos_deportista = DiagnosticoDeportista.query.filter_by(
            id_deportista=deportista.id_deportista
        ).all()

        if diagnosticos_deportista:
            ids_diagnosticos = [dd.id_diagnostico for dd in diagnosticos_deportista]
            resultado['diagnostico'] = ids_diagnosticos

            if ids_diagnosticos:
                primer_diagnostico = Diagnostico.query.filter_by(
                    id_diagnostico=ids_diagnosticos[0]
                ).first()
                if primer_diagnostico:
                    resultado['tipo_enfermedad'] = primer_diagnostico.id_tipo_enfermedad

    def _agregar_info_acudiente(self, resultado: Dict[str, Any], acudiente: Acudiente) -> None:
        """Agrega información del acudiente al resultado."""
        from src.models.acudientes.deportista_acudiente import DeportistaAcudiente
        
        relacion = DeportistaAcudiente.query.filter_by(
            id_acudiente=acudiente.id_acudiente
        ).first()

        resultado['informacion_acudiente'] = {
            'id_acudiente': acudiente.id_acudiente,
            'es_respondable': relacion.es_responsable if relacion else False
        }

    def obtener_detalle_completo_usuario(self, id_usuario: int, usuario_obj: Optional[Usuario] = None) -> Optional[Dict[str, Any]]:
        """
        Obtiene la información completa de un usuario, incluyendo:
        - Datos básicos del usuario y su persona
        - Roles asignados
        - Información específica por rol (Deportista, Acudiente, etc.)

        Args:
            id_usuario (int): ID del usuario
            usuario_obj (Usuario, optional): Objeto Usuario ya obtenido. Si se proporciona, se usa directamente.

        Returns:
            Dict: Estructura con la información completa o None si no existe
        """
        try:
            self.logger.info(f"[DETALLE] Buscando detalle completo para usuario ID: {id_usuario}")
            
            usuario = self._obtener_usuario_para_detalle(id_usuario, usuario_obj)
            if not usuario:
                return None

            persona = usuario.persona
            if not persona:
                self.logger.warning(f"[DETALLE] Usuario ID {id_usuario} no tiene persona asociada (id_persona: {usuario.id_persona})")
                return {
                    'usuario': {'usuario': usuario.usuario},
                    'persona': None,
                    'error': 'El usuario no tiene una persona asociada'
                }

            self.logger.info(f"[DETALLE] Persona encontrada: {persona.primer_nombre} {persona.primer_apellido} (ID: {persona.id_persona})")

            fecha_nacimiento_persona = self._obtener_fecha_nacimiento_persona(persona.id_persona)
            roles_usuario = self._obtener_roles_usuario(usuario)

            resultado: Dict[str, Any] = {
                'persona': self._construir_datos_persona(persona, fecha_nacimiento_persona),
                'usuario': {
                    'id_usuario': usuario.id_usuario,
                    'usuario': usuario.usuario,
                    'estado': usuario.estado,
                    'id_persona': usuario.id_persona
                },
                'roles': roles_usuario
            }

            deportista = Deportista.query.filter_by(id_persona=persona.id_persona).first()
            if deportista:
                self._agregar_info_deportista(resultado, deportista)

            acudiente = Acudiente.query.filter_by(id_persona=persona.id_persona).first()
            if acudiente:
                self._agregar_info_acudiente(resultado, acudiente)

            self.logger.info(f"[DETALLE] Detalle completo obtenido exitosamente para usuario ID: {id_usuario}")
            return resultado

        except Exception as e:
            self.logger.error(f"[DETALLE] Error al obtener detalle completo de usuario ID {id_usuario}: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None


# Instancia global del servicio para uso en la aplicación
usuario_service = UsuarioService()
