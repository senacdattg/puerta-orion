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
from typing import Dict, Any, Optional, Tuple
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.models.base import db  
from src.models.personas.persona import Persona
from src.models.usuarios.usuario import Usuario
from src.models.roles_y_permisos.rol import Rol
from src.models.roles_y_permisos.usuario_rol import UsuarioRol
from src.models.deportistas.deportista import Deportista
from src.models.acudientes.acudiente import Acudiente
from src.utils.logger import obtener_registrador


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
        campos_requeridos = [
            'primer_nombre', 'primer_apellido', 'documento',
            'correo_electronico', 'direccion', 'telefono',
            'id_tipo_documento', 'id_sexo'
        ]
        
        campos_faltantes = [campo for campo in campos_requeridos if not datos.get(campo)]
        
        if campos_faltantes:
            raise UsuarioServiceError(f"Campos requeridos faltantes: {', '.join(campos_faltantes)}")
        
        # Validar formato de email básico
        email = datos.get('correo_electronico', '')
        if '@' not in email or '.' not in email.split('@')[-1]:
            raise UsuarioServiceError("Formato de email inválido")
        
        # Validar longitud de campos
        if len(datos.get('primer_nombre', '')) > 50:
            raise UsuarioServiceError("El primer nombre excede la longitud máxima (50 caracteres)")
        
        if len(datos.get('primer_apellido', '')) > 50:
            raise UsuarioServiceError("El primer apellido excede la longitud máxima (50 caracteres)")
    
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
        
        # Validar longitud de contraseña
        password = datos.get('password', '')
        if len(password) < 6:
            raise UsuarioServiceError("La contraseña debe tener al menos 6 caracteres")
        
        # Validar longitud de nombre de usuario
        usuario = datos.get('usuario', '')
        if len(usuario) < 3:
            raise UsuarioServiceError("El nombre de usuario debe tener al menos 3 caracteres")
        
        if len(usuario) > 200:
            raise UsuarioServiceError("El nombre de usuario excede la longitud máxima (200 caracteres)")
    
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
            # Crear persona
            persona = self._crear_persona(datos_persona)
            db.session.flush()  # Obtener ID sin hacer commit
            
            # Crear usuario asociado
            usuario = self._crear_usuario(persona.id_persona, datos_usuario)
            db.session.flush()
            
            # Asignar rol por defecto
            self._asignar_rol_por_defecto(usuario.id_usuario)
            
            # Si se especifica un rol, crear el registro correspondiente
            if rol_opcional and rol_opcional in ['deportista', 'acudiente']:
                self._crear_registro_rol(usuario.id_persona, rol_opcional, datos_rol)
                
                # Asignar rol específico además del rol por defecto
                rol_especifico = Rol.query.filter_by(nombre_rol=rol_opcional.capitalize()).first()
                if rol_especifico:
                    # Verificar si ya tiene el rol
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
            
            # Commit de la transacción
            db.session.commit()
            
            # Retornar datos del usuario (sin password)
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
            segundo_nombre=datos.get('segundo_nombre'),
            primer_apellido=datos['primer_apellido'],
            segundo_apellido=datos.get('segundo_apellido'),
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
    
    def _crear_registro_rol(self, id_persona: int, rol: str, datos: Dict[str, Any]) -> None:
        """
        Crea un registro de Deportista o Acudiente según el rol especificado.
        
        Args:
            id_persona (int): ID de la persona asociada
            rol (str): Tipo de rol ('deportista' o 'acudiente')
            datos (Dict): Datos adicionales para el rol (opcional)
            
        Raises:
            UsuarioServiceError: Si hay errores en la creación
        """
        from datetime import date
        
        try:
            if rol == 'deportista':
                # Verificar que no exista ya un deportista para esta persona
                deportista_existente = Deportista.query.filter_by(id_persona=id_persona).first()
                if deportista_existente:
                    raise UsuarioServiceError("Ya existe un registro de deportista para esta persona")
                
                # Validar que se proporcione id_categoria (obligatorio)
                if not datos or not datos.get('id_categoria'):
                    raise UsuarioServiceError("El campo 'id_categoria' es obligatorio para crear un deportista")
                
                # Procesar fecha de nacimiento - convertir string a date si es necesario
                fecha_nacimiento_date = None
                fecha_nacimiento_raw = datos.get('fecha_nacimiento')
                
                if fecha_nacimiento_raw:
                    from datetime import datetime
                    if isinstance(fecha_nacimiento_raw, str):
                        # Intentar parsear fecha ISO (YYYY-MM-DD)
                        try:
                            fecha_nacimiento_date = datetime.fromisoformat(fecha_nacimiento_raw).date()
                        except ValueError:
                            # Si falla, tratar como año solo (compatibilidad)
                            try:
                                año = int(fecha_nacimiento_raw)
                                fecha_nacimiento_date = date(año, 1, 1)
                            except ValueError:
                                raise UsuarioServiceError(f'Formato de fecha de nacimiento inválido: {fecha_nacimiento_raw}')
                    elif isinstance(fecha_nacimiento_raw, int):
                        # Compatibilidad con años antiguos
                        fecha_nacimiento_date = date(fecha_nacimiento_raw, 1, 1)
                    elif isinstance(fecha_nacimiento_raw, date):
                        fecha_nacimiento_date = fecha_nacimiento_raw
                
                deportista = Deportista(
                    id_persona=id_persona,
                    id_categoria=datos['id_categoria'],
                    peso=datos.get('peso'),
                    altura=datos.get('altura'),
                    fecha_ingreso=datos.get('fecha_ingreso', date.today()),
                    fecha_nacimiento=fecha_nacimiento_date,
                    id_tipo_sanguineo=datos.get('id_tipo_sanguineo'),
                    id_ciudad_recidencia=datos.get('id_ciudad_recidencia'),
                    id_mensualidad=datos.get('id_mensualidad'),
                    id_informacion_deportiva=datos.get('id_informacion_deportiva'),
                    id_eps=datos.get('id_eps')
                )
                db.session.add(deportista)
                self.logger.info(f"Registro de deportista creado para persona ID: {id_persona}")
            
            elif rol == 'acudiente':
                # Verificar que no exista ya un acudiente para esta persona
                acudiente_existente = Acudiente.query.filter_by(id_persona=id_persona).first()
                if acudiente_existente:
                    raise UsuarioServiceError("Ya existe un registro de acudiente para esta persona")
                
                acudiente = Acudiente(
                    id_persona=id_persona,
                    estado=datos.get('estado', True) if datos else True
                )
                db.session.add(acudiente)
                self.logger.info(f"Registro de acudiente creado para persona ID: {id_persona}")
            
            else:
                raise UsuarioServiceError(f"Rol inválido: {rol}")
                
        except UsuarioServiceError:
            raise
        except Exception as e:
            self.logger.error(f"Error al crear registro de {rol}: {str(e)}")
            raise UsuarioServiceError(f"Error al crear registro de {rol}: {str(e)}")
    
    def _asignar_rol_por_defecto(self, id_usuario: int) -> None:
        """
        Asigna el rol por defecto 'usuario' al usuario recién creado.
        
        Args:
            id_usuario (int): ID del usuario al que asignar el rol
            
        Raises:
            UsuarioServiceError: Si hay errores al asignar el rol
        """
        try:
            # Verificar si el usuario ya tiene roles asignados
            roles_existentes = UsuarioRol.query.filter_by(id_usuario=id_usuario).all()
            if roles_existentes:
                self.logger.info(f"Usuario {id_usuario} ya tiene roles asignados, omitiendo asignación de rol por defecto")
                return
            
            # Obtener o crear el rol por defecto
            rol_usuario = self._obtener_o_crear_rol_usuario()
            
            # Crear la relación usuario-rol
            usuario_rol = UsuarioRol(
                id_usuario=id_usuario,
                id_rol=rol_usuario.id_rol
            )
            
            db.session.add(usuario_rol)
            self.logger.info(f"Rol 'usuario' asignado al usuario ID: {id_usuario}")
            
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
        # Validar y actualizar nombre completo
        if 'primer_nombre' in datos:
            primer_nombre = datos['primer_nombre'].strip()
            if len(primer_nombre) > 50:
                raise UsuarioServiceError("El primer nombre excede la longitud máxima (50 caracteres)")
            if persona.primer_nombre != primer_nombre:
                persona.primer_nombre = primer_nombre
                campos_actualizados.append('primer_nombre')
        
        if 'segundo_nombre' in datos:
            segundo_nombre = datos.get('segundo_nombre', '').strip() if datos.get('segundo_nombre') else None
            if segundo_nombre and len(segundo_nombre) > 50:
                raise UsuarioServiceError("El segundo nombre excede la longitud máxima (50 caracteres)")
            if persona.segundo_nombre != segundo_nombre:
                persona.segundo_nombre = segundo_nombre
                campos_actualizados.append('segundo_nombre')
        
        if 'primer_apellido' in datos:
            primer_apellido = datos['primer_apellido'].strip()
            if len(primer_apellido) > 50:
                raise UsuarioServiceError("El primer apellido excede la longitud máxima (50 caracteres)")
            if persona.primer_apellido != primer_apellido:
                persona.primer_apellido = primer_apellido
                campos_actualizados.append('primer_apellido')
        
        if 'segundo_apellido' in datos:
            segundo_apellido = datos.get('segundo_apellido', '').strip() if datos.get('segundo_apellido') else None
            if segundo_apellido and len(segundo_apellido) > 50:
                raise UsuarioServiceError("El segundo apellido excede la longitud máxima (50 caracteres)")
            if persona.segundo_apellido != segundo_apellido:
                persona.segundo_apellido = segundo_apellido
                campos_actualizados.append('segundo_apellido')
        
        # Validar y actualizar documento
        if 'documento' in datos:
            documento = str(datos['documento']).strip()
            if len(documento) < 6:
                raise UsuarioServiceError("El documento debe tener al menos 6 dígitos")
            
            # Validar unicidad (excluyendo la persona actual)
            documento_existente = Persona.query.filter_by(documento=documento).filter(
                Persona.id_persona != id_persona
            ).first()
            
            if documento_existente:
                raise UsuarioServiceError(f"Ya existe una persona con el documento {documento}")
            
            if persona.documento != documento:
                persona.documento = documento
                campos_actualizados.append('documento')
        
        # Validar y actualizar correo electrónico
        if 'correo_electronico' in datos:
            email = datos['correo_electronico'].strip().lower()
            
            # Validar formato básico
            if '@' not in email or '.' not in email.split('@')[-1]:
                raise UsuarioServiceError("Formato de email inválido")
            
            # Validar unicidad (excluyendo la persona actual)
            email_existente = Persona.query.filter_by(correo_electronico=email).filter(
                Persona.id_persona != id_persona
            ).first()
            
            if email_existente:
                raise UsuarioServiceError(f"Ya existe una persona con el email {email}")
            
            if persona.correo_electronico != email:
                persona.correo_electronico = email
                campos_actualizados.append('correo_electronico')
        
        # Actualizar dirección
        if 'direccion' in datos:
            nueva_direccion = datos['direccion'].strip() if datos['direccion'] else None
            if persona.direccion != nueva_direccion:
                persona.direccion = nueva_direccion
                campos_actualizados.append('direccion')
        
        # Validar y actualizar teléfono
        if 'telefono' in datos:
            telefono = str(datos['telefono']).strip()
            if len(telefono) < 7 or len(telefono) > 20:
                raise UsuarioServiceError("El teléfono debe tener entre 7 y 20 caracteres")
            if persona.telefono != telefono:
                persona.telefono = telefono
                campos_actualizados.append('telefono')
        
        # Validar y actualizar relaciones
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
        
        # No permitir actualizar estado desde este endpoint
        if 'estado' in datos:
            raise UsuarioServiceError("El estado no se puede actualizar desde este endpoint. Use los endpoints dedicados para activar/desactivar personas")
        
        # Log de campos actualizados
        if campos_actualizados:
            self.logger.info(f"Campos de persona actualizados: {', '.join(campos_actualizados)}")
        else:
            self.logger.warning(f"No se actualizaron campos de persona (todos los valores son iguales a los existentes)")

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
            from src.models.deportistas.informacion_deportiva import InformacionDeportiva
            from src.models.salud.diagnostico_deportista import DiagnosticoDeportista
            from src.models.salud.diagnostico import Diagnostico
            from src.models.acudientes.deportista_acudiente import DeportistaAcudiente
            
            self.logger.info(f"[DETALLE] Buscando detalle completo para usuario ID: {id_usuario}")
            
            # Si se proporciona el objeto usuario directamente, usarlo
            if usuario_obj:
                self.logger.info(f"[DETALLE] Usando usuario proporcionado: {usuario_obj.usuario} (ID: {usuario_obj.id_usuario}, estado: {usuario_obj.estado})")
                usuario = usuario_obj
            else:
                # Primero buscar sin filtro de estado para ver si existe
                usuario_sin_filtro = Usuario.query.filter_by(id_usuario=id_usuario).first()
                if usuario_sin_filtro:
                    self.logger.info(f"[DETALLE] Usuario encontrado sin filtro de estado: {usuario_sin_filtro.usuario}, estado: {usuario_sin_filtro.estado}")
                
                # Buscar primero con estado activo
                usuario = Usuario.query.filter_by(id_usuario=id_usuario, estado=True).first()
                
                # Si no se encuentra activo pero existe, usar el inactivo (ya pasó autenticación)
                if not usuario and usuario_sin_filtro:
                    self.logger.warning(f"[DETALLE] Usuario ID {id_usuario} existe pero está inactivo, usando de todas formas (token válido)")
                    usuario = usuario_sin_filtro
                
                if not usuario:
                    self.logger.warning(f"[DETALLE] Usuario ID {id_usuario} no encontrado en la base de datos")
                    return None

            self.logger.info(f"[DETALLE] Usuario encontrado: {usuario.usuario} (ID: {usuario.id_usuario}, estado: {usuario.estado})")

            # Obtener persona completa
            persona = usuario.persona
            if not persona:
                self.logger.warning(f"[DETALLE] Usuario ID {id_usuario} no tiene persona asociada (id_persona: {usuario.id_persona})")
                # Retornar al menos la información básica del usuario
                return {
                    'usuario': {
                        'usuario': usuario.usuario
                    },
                    'persona': None,
                    'error': 'El usuario no tiene una persona asociada'
                }

            self.logger.info(f"[DETALLE] Persona encontrada: {persona.primer_nombre} {persona.primer_apellido} (ID: {persona.id_persona})")

            # Obtener fecha_nacimiento de deportista si existe, si no None
            fecha_nacimiento_persona = None
            deportista_temp = Deportista.query.filter_by(id_persona=persona.id_persona).first()
            if deportista_temp and deportista_temp.fecha_nacimiento:
                fecha_nacimiento_persona = deportista_temp.fecha_nacimiento

            # Construir resultado base con estructura solicitada
            resultado: Dict[str, Any] = {
                'persona': {
                    'primer_nombre': persona.primer_nombre,
                    'segundo_nombre': persona.segundo_nombre,
                    'primer_apellido': persona.primer_apellido,
                    'segundo_apellido': persona.segundo_apellido,
                    'documento': persona.documento,
                    'correo_electronico': persona.correo_electronico,
                    'direccion': persona.direccion,
                    'telefono': persona.telefono,
                    'fecha_nacimiento': fecha_nacimiento_persona,
                    'id_tipo_documento': persona.id_tipo_documento,
                    'id_sexo': persona.id_sexo
                },
                'usuario': {
                    'usuario': usuario.usuario
                }
            }

            # Deportista - información completa
            deportista = Deportista.query.filter_by(id_persona=persona.id_persona).first()
            if deportista:
                resultado['deportista'] = {
                    'id_deportista': deportista.id_deportista,
                    'fecha_nacimiento': deportista.fecha_nacimiento,
                    'id_tipo_sanguineo': deportista.id_tipo_sanguineo,
                    'id_ciudad_recidencia': deportista.id_ciudad_recidencia,
                    'id_eps': deportista.id_eps,
                    'peso': deportista.peso,
                    'altura': deportista.altura
                }

                # Información deportiva
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

                # Diagnósticos del deportista
                diagnosticos_deportista = DiagnosticoDeportista.query.filter_by(
                    id_deportista=deportista.id_deportista
                ).all()

                if diagnosticos_deportista:
                    # Obtener IDs de diagnósticos
                    ids_diagnosticos = [dd.id_diagnostico for dd in diagnosticos_deportista]
                    resultado['diagnostico'] = ids_diagnosticos

                    # Obtener tipo_enfermedad del primer diagnóstico
                    if ids_diagnosticos:
                        primer_diagnostico = Diagnostico.query.filter_by(
                            id_diagnostico=ids_diagnosticos[0]
                        ).first()
                        if primer_diagnostico:
                            resultado['tipo_enfermedad'] = primer_diagnostico.id_tipo_enfermedad

            # Acudiente - información completa
            acudiente = Acudiente.query.filter_by(id_persona=persona.id_persona).first()
            if acudiente:
                # Buscar relación DeportistaAcudiente para este acudiente
                relacion = DeportistaAcudiente.query.filter_by(
                    id_acudiente=acudiente.id_acudiente
                ).first()

                resultado['informacion_acudiente'] = {
                    'id_acudiente': acudiente.id_acudiente,
                    'es_respondable': relacion.es_responsable if relacion else False
                }

            self.logger.info(f"[DETALLE] Detalle completo obtenido exitosamente para usuario ID: {id_usuario}")
            return resultado

        except Exception as e:
            self.logger.error(f"[DETALLE] Error al obtener detalle completo de usuario ID {id_usuario}: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None


# Instancia global del servicio para uso en la aplicación
usuario_service = UsuarioService()
