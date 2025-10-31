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
                
                deportista = Deportista(
                    id_persona=id_persona,
                    id_categoria=datos['id_categoria'],
                    peso=datos.get('peso'),
                    altura=datos.get('altura'),
                    fecha_ingreso=datos.get('fecha_ingreso', date.today()),
                    fecha_nacimiento=datos.get('fecha_nacimiento'),
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
        
        return {
            'id_usuario': usuario.id_usuario,
            'id_persona': usuario.id_persona,
            'usuario': usuario.usuario,
            'estado': usuario.estado,
            'roles': roles_usuario,
            'persona': {
                'nombre_completo': usuario.persona.nombre_completo,
                'correo_electronico': usuario.persona.correo_electronico,
                'documento': usuario.persona.documento,
                'telefono': usuario.persona.telefono
            },
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
