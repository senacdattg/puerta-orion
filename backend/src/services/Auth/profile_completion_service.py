"""
Servicio unificado para completar el perfil de usuario (Deportista o Acudiente).

Responsabilidad:
- Gestionar el flujo completo de completar perfil
- Validar datos según el tipo de perfil
- Crear entidades relacionadas (deportista/acudiente)
- Asignar roles automáticamente
- Mantener consistencia de datos

Este módulo sigue los principios SRP, KISS, DRY y SOLID.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from src.models.base import db
from src.models.usuarios.usuario import Usuario
from src.models.deportistas.deportista import Deportista
from src.models.acudientes.acudiente import Acudiente
from src.models.roles_y_permisos.rol import Rol
from src.models.roles_y_permisos.usuario_rol import UsuarioRol
from src.utils.logger import obtener_registrador

# Logger simple para casos donde el gestor no está inicializado
import logging
logger = logging.getLogger(__name__)


class ProfileCompletionError(Exception):
    """Excepción personalizada para errores de completar perfil."""
    pass


@dataclass
class ProfileCompletionResult:
    """Resultado de completar perfil."""
    success: bool
    profile_type: str
    profile_id: int
    usuario_id: int
    role_assigned: str
    message: str
    data: Optional[Dict[str, Any]] = None


class ProfileValidator(ABC):
    """Interfaz para validadores de perfil."""

    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> None:
        """Valida los datos del perfil."""
        pass


class DeportistaValidator(ProfileValidator):
    """Validador para datos de deportista."""

    def validate(self, data: Dict[str, Any]) -> None:
        """Valida datos requeridos para deportista."""
        required_fields = ['id_categoria']

        missing_fields = [
            field for field in required_fields
            if field not in data or data[field] is None or data[field] == ''
        ]

        if missing_fields:
            raise ProfileCompletionError(
                f"Campos requeridos faltantes: {', '.join(missing_fields)}"
            )

        # Validaciones adicionales
        if 'peso' in data and data['peso'] is not None and data['peso'] != '':
            try:
                peso = float(data['peso'])
                if peso <= 0 or peso > 300:  # Rango razonable
                    raise ProfileCompletionError("El peso debe estar entre 1 y 300 kg")
            except (ValueError, TypeError):
                raise ProfileCompletionError("El peso debe ser un número válido")

        if 'altura' in data and data['altura'] is not None and data['altura'] != '':
            try:
                altura = float(data['altura'])
                if altura <= 0 or altura > 3:  # Rango razonable en metros
                    raise ProfileCompletionError("La altura debe estar entre 0.1 y 3 metros")
            except (ValueError, TypeError):
                raise ProfileCompletionError("La altura debe ser un número válido")

        if 'fecha_nacimiento' in data and data['fecha_nacimiento'] is not None and data['fecha_nacimiento'] != '':
            try:
                año = int(data['fecha_nacimiento'])
                año_actual = datetime.now().year
                if año < 1900 or año > año_actual:
                    raise ProfileCompletionError(f"El año de nacimiento debe estar entre 1900 y {año_actual}")
            except (ValueError, TypeError):
                raise ProfileCompletionError("El año de nacimiento debe ser un número válido")


class AcudienteValidator(ProfileValidator):
    """Validador para datos de acudiente."""

    def validate(self, data: Dict[str, Any]) -> None:
        """
        Valida datos para acudiente.
        
        Requiere que se proporcione información de asociación con deportista:
        - id_deportista (obligatorio)
        - id_parentesco (obligatorio)
        - es_responsable (obligatorio, bool)
        """
        required_fields = ['id_deportista', 'id_parentesco']
        
        missing_fields = [
            field for field in required_fields
            if field not in data or data[field] is None or data[field] == ''
        ]
        
        if missing_fields:
            raise ProfileCompletionError(
                f"Para completar el perfil como acudiente, debe asociarse con un deportista. "
                f"Campos requeridos faltantes: {', '.join(missing_fields)}"
            )
        
        # Validar que es_responsable esté definido (puede ser False, pero debe estar)
        if 'es_responsable' not in data:
            raise ProfileCompletionError(
                "Debe especificar si es responsable legal del deportista"
            )
        
        # Validar que el parentesco sea un número válido
        try:
            id_parentesco = int(data['id_parentesco'])
            if id_parentesco <= 0:
                raise ProfileCompletionError("El ID de parentesco debe ser un número positivo")
        except (ValueError, TypeError):
            raise ProfileCompletionError("El ID de parentesco debe ser un número válido")
        
        # Validar que el deportista sea un número válido
        try:
            id_deportista = int(data['id_deportista'])
            if id_deportista <= 0:
                raise ProfileCompletionError("El ID de deportista debe ser un número positivo")
        except (ValueError, TypeError):
            raise ProfileCompletionError("El ID de deportista debe ser un número válido")


class ProfileCreator(ABC):
    """Interfaz para creadores de perfil."""

    @abstractmethod
    def create(self, usuario_id: int, data: Dict[str, Any]) -> Any:
        """Crea el perfil específico."""
        pass

    @abstractmethod
    def get_profile_type(self) -> str:
        """Retorna el tipo de perfil."""
        pass


class DeportistaCreator(ProfileCreator):
    """Creador de perfil deportista."""

    def get_profile_type(self) -> str:
        return "deportista"

    def create(self, usuario_id: int, data: Dict[str, Any]) -> Deportista:
        """Crea un deportista con los datos proporcionados."""
        from datetime import date

        # Obtener usuario para acceder a id_persona
        usuario = Usuario.query.filter_by(id_usuario=usuario_id).first()
        if not usuario:
            raise ProfileCompletionError("Usuario no encontrado")

        deportista = Deportista(
            id_persona=usuario.id_persona,
            id_categoria=data['id_categoria'],
            peso=data.get('peso'),
            altura=data.get('altura'),
            fecha_ingreso=data.get('fecha_ingreso', date.today()),
            fecha_nacimiento=data.get('fecha_nacimiento'),
            id_tipo_sanguineo=data.get('id_tipo_sanguineo'),
            id_ciudad_recidencia=data.get('id_ciudad_recidencia'),
            id_mensualidad=data.get('id_mensualidad'),
            id_informacion_deportiva=data.get('id_informacion_deportiva'),
            id_eps=data.get('id_eps'),
            alergias=data.get('alergias', ''),
            medicamentos=data.get('medicamentos', ''),
            condiciones_medicas=data.get('condiciones_medicas', ''),
            institucion_educativa=data.get('institucion_educativa', ''),
            grado=data.get('grado', ''),
            jornada=data.get('jornada', '')
        )

        db.session.add(deportista)
        return deportista


class AcudienteCreator(ProfileCreator):
    """Creador de perfil acudiente."""

    def get_profile_type(self) -> str:
        return "acudiente"

    def create(self, usuario_id: int, data: Dict[str, Any]) -> Acudiente:
        """
        Crea un acudiente con los datos proporcionados.
        También crea la relación inicial con el deportista automáticamente.
        """
        from datetime import date
        from src.models.acudientes.deportista_acudiente import DeportistaAcudiente
        from src.models.deportistas.deportista import Deportista
        from src.models.acudientes.parentesco import Parentesco
        
        # Obtener usuario para acceder a id_persona
        usuario = Usuario.query.filter_by(id_usuario=usuario_id).first()
        if not usuario:
            raise ProfileCompletionError("Usuario no encontrado")
        
        # Crear el registro de acudiente (solo id_persona y estado)
        acudiente = Acudiente(
            id_persona=usuario.id_persona,
            estado=True
        )
        
        db.session.add(acudiente)
        db.session.flush()  # Para obtener el id_acudiente
        
        # Validar y crear relación con deportista (OBLIGATORIO)
        id_deportista = data.get('id_deportista')
        id_parentesco = data.get('id_parentesco')
        es_responsable = data.get('es_responsable', False)
        
        if not id_deportista or not id_parentesco:
            raise ProfileCompletionError(
                "Para completar el perfil como acudiente, debe asociarse con un deportista, "
                "indicar el parentesco y si es responsable"
            )
        
        # Validar que el deportista existe
        deportista = Deportista.query.filter_by(id_deportista=int(id_deportista)).first()
        if not deportista:
            raise ProfileCompletionError(f"El deportista con ID {id_deportista} no existe")
        
        # Validar que el parentesco existe
        parentesco = Parentesco.query.filter_by(id_parentesco=int(id_parentesco)).first()
        if not parentesco:
            raise ProfileCompletionError(f"El parentesco con ID {id_parentesco} no existe")
        
        # Validar que no exista ya esta relación
        relacion_existente = DeportistaAcudiente.query.filter_by(
            id_deportista=int(id_deportista),
            id_acudiente=acudiente.id_acudiente
        ).first()
        
        if relacion_existente:
            raise ProfileCompletionError(
                "Ya existe una relación entre este acudiente y este deportista"
            )
        
        # Crear la relación DeportistaAcudiente
        deportista_acudiente = DeportistaAcudiente(
            id_deportista=int(id_deportista),
            id_acudiente=acudiente.id_acudiente,
            id_parentesco=int(id_parentesco),
            es_responsable=bool(es_responsable),
            fecha_registro=date.today()
        )
        
        db.session.add(deportista_acudiente)
        
        return acudiente


class RoleAssigner:
    """Servicio para asignar roles a usuarios."""

    def __init__(self):
        # Usar logger simple por defecto para evitar problemas de inicialización
        self.logger = logger

    def assign_role(self, usuario_id: int, role_name: str) -> None:
        """
        Asigna un rol específico al usuario si no lo tiene ya.

        Args:
            usuario_id: ID del usuario
            role_name: Nombre del rol a asignar

        Raises:
            ProfileCompletionError: Si hay errores al asignar el rol
        """
        try:
            # Obtener rol por nombre
            rol = Rol.query.filter_by(nombre_rol=role_name).first()

            if not rol:
                raise ProfileCompletionError(f"Rol '{role_name}' no encontrado en el sistema")

            # Verificar si ya tiene el rol
            usuario_rol_existente = UsuarioRol.query.filter_by(
                id_usuario=usuario_id,
                id_rol=rol.id_rol
            ).first()

            if not usuario_rol_existente:
                # Crear la relación usuario-rol
                usuario_rol = UsuarioRol(
                    id_usuario=usuario_id,
                    id_rol=rol.id_rol
                )
                db.session.add(usuario_rol)
                self.logger.info(f"Rol '{role_name}' asignado al usuario ID: {usuario_id}")

        except ProfileCompletionError:
            raise
        except Exception as e:
            self.logger.error(f"Error al asignar rol {role_name}: {str(e)}")
            raise ProfileCompletionError(f"Error al asignar rol {role_name}: {str(e)}")


class ProfileCompletionService:
    """
    Servicio principal para completar perfiles de usuario.

    Coordina validación, creación de perfil y asignación de roles.
    """

    def __init__(self):
        # Usar logger simple por defecto para evitar problemas de inicialización
        self.logger = logger
        self.role_assigner = RoleAssigner()

        # Mapeo de tipos de perfil a sus componentes
        self.profile_components = {
            'deportista': {
                'validator': DeportistaValidator(),
                'creator': DeportistaCreator(),
                'role': 'Deportista'
            },
            'acudiente': {
                'validator': AcudienteValidator(),
                'creator': AcudienteCreator(),
                'role': 'Acudiente'
            }
        }

    def complete_profile(
        self,
        usuario_id: int,
        profile_type: str,
        profile_data: Optional[Dict[str, Any]] = None
    ) -> ProfileCompletionResult:
        """
        Completa el perfil del usuario según el tipo especificado.

        Args:
            usuario_id: ID del usuario
            profile_type: Tipo de perfil ('deportista' o 'acudiente')
            profile_data: Datos específicos del perfil

        Returns:
            ProfileCompletionResult: Resultado de la operación

        Raises:
            ProfileCompletionError: Si hay errores en el proceso
        """
        if profile_type not in self.profile_components:
            raise ProfileCompletionError(f"Tipo de perfil no válido: {profile_type}")

        components = self.profile_components[profile_type]
        profile_data = profile_data or {}

        try:
            # Verificar que el usuario existe y no tiene perfil completo
            self._validate_user_can_complete_profile(usuario_id, profile_type)

            # Validar datos del perfil
            components['validator'].validate(profile_data)

            # Crear el perfil
            profile_entity = components['creator'].create(usuario_id, profile_data)
            db.session.flush()

            # Asignar rol correspondiente
            self.role_assigner.assign_role(usuario_id, components['role'])

            # Commit de la transacción
            db.session.commit()

            self.logger.info(
                f"Perfil {profile_type} completado exitosamente para usuario {usuario_id}"
            )

            return ProfileCompletionResult(
                success=True,
                profile_type=profile_type,
                profile_id=getattr(profile_entity, f'id_{profile_type}'),
                usuario_id=usuario_id,
                role_assigned=components['role'],
                message=f"Perfil completado como {profile_type} exitosamente",
                data={
                    f'id_{profile_type}': getattr(profile_entity, f'id_{profile_type}'),
                    'id_persona': profile_entity.id_persona
                }
            )

        except ProfileCompletionError:
            db.session.rollback()
            raise
        except IntegrityError as e:
            db.session.rollback()
            self.logger.error(f"Error de integridad al completar perfil: {str(e)}")
            raise ProfileCompletionError("Error de duplicación de datos")
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error inesperado al completar perfil: {str(e)}")
            raise ProfileCompletionError(f"Error al completar perfil: {str(e)}")

    def check_profile_status(self, usuario_id: int) -> Dict[str, Any]:
        """
        Verifica el estado del perfil del usuario.

        Args:
            usuario_id: ID del usuario

        Returns:
            Dict con información del estado del perfil
        """
        try:
            usuario = Usuario.query.filter_by(id_usuario=usuario_id).first()

            if not usuario:
                raise ProfileCompletionError("Usuario no encontrado")

            # Verificar perfiles existentes
            deportista = Deportista.query.filter_by(id_persona=usuario.id_persona).first()
            acudiente = Acudiente.query.filter_by(id_persona=usuario.id_persona).first()

            # Obtener roles del usuario
            roles = [rol.nombre_rol for rol in usuario.roles]

            return {
                'id_usuario': usuario.id_usuario,
                'id_persona': usuario.id_persona,
                'es_deportista': deportista is not None,
                'es_acudiente': acudiente is not None,
                'id_deportista': deportista.id_deportista if deportista else None,
                'id_acudiente': acudiente.id_acudiente if acudiente else None,
                'roles': roles,
                'perfil_completo': deportista is not None or acudiente is not None,
                'puede_completar_deportista': deportista is None,
                'puede_completar_acudiente': acudiente is None
            }

        except Exception as e:
            self.logger.error(f"Error al verificar estado del perfil: {str(e)}")
            raise ProfileCompletionError(f"Error al verificar estado del perfil: {str(e)}")

    def _validate_user_can_complete_profile(self, usuario_id: int, profile_type: str) -> None:
        """
        Valida que el usuario pueda completar el perfil especificado.

        Args:
            usuario_id: ID del usuario
            profile_type: Tipo de perfil a validar

        Raises:
            ProfileCompletionError: Si no puede completar el perfil
        """
        from datetime import date
        
        usuario = Usuario.query.filter_by(id_usuario=usuario_id).first()

        if not usuario:
            raise ProfileCompletionError("Usuario no encontrado")

        # Verificar que no esté intentando completar el mismo tipo que ya tiene
        deportista = Deportista.query.filter_by(id_persona=usuario.id_persona).first()
        acudiente = Acudiente.query.filter_by(id_persona=usuario.id_persona).first()

        if profile_type == 'deportista' and deportista:
            raise ProfileCompletionError("El usuario ya está registrado como deportista")
        elif profile_type == 'acudiente' and acudiente:
            raise ProfileCompletionError("El usuario ya está registrado como acudiente")
        
        # Validación específica para acudientes: deben ser mayores de 18 años
        if profile_type == 'acudiente':
            # Buscar fecha de nacimiento
            fecha_nacimiento = None
            
            # Intentar obtener de la persona si tiene deportista
            if deportista and deportista.fecha_nacimiento:
                fecha_nacimiento = deportista.fecha_nacimiento
            # TODO: Si no, buscar en otra fuente de datos
            
            if fecha_nacimiento:
                año_actual = date.today().year
                edad = año_actual - fecha_nacimiento
                
                if edad < 18:
                    raise ProfileCompletionError(
                        f"Para ser acudiente debe ser mayor de edad. Su edad actual es {edad} años"
                    )
                self.logger.info(f"Validación de edad para acudiente: {edad} años (OK)")
            else:
                # Si no hay fecha de nacimiento registrada, no validamos por seguridad
                self.logger.warning("No se pudo validar edad del usuario para acudiente")


# Instancia global del servicio para uso en la aplicación
profile_completion_service = ProfileCompletionService()