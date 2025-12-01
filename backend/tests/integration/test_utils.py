"""
Utilidades compartidas para tests de integración.

Este módulo centraliza funciones auxiliares y fixtures comunes
para reducir la duplicidad de código en los tests de integración.
"""

from datetime import date
from unittest.mock import MagicMock
from typing import Any, Dict


def create_mock_mensualidad(
    id_mensualidad: int = 1,
    id_persona: int = 1,
    monto_pago: float = 50000.0,
    saldo_pendiente: float = 50000.0,
    fecha_vencimiento: date = None,
    estado: bool = False,
    id_metodo_pago: int = 1,
    to_dict_data: Dict[str, Any] = None
) -> MagicMock:
    """
    Crea un mock de Mensualidad con valores por defecto configurables.
    
    Args:
        id_mensualidad: ID de la mensualidad
        id_persona: ID de la persona
        monto_pago: Monto del pago
        saldo_pendiente: Saldo pendiente
        fecha_vencimiento: Fecha de vencimiento
        estado: Estado de la mensualidad
        id_metodo_pago: ID del método de pago
        to_dict_data: Datos para el método to_dict
    
    Returns:
        MagicMock configurado como Mensualidad
    """
    if fecha_vencimiento is None:
        fecha_vencimiento = date(2024, 12, 31)
    
    if to_dict_data is None:
        to_dict_data = {
            'id_mensualidad': id_mensualidad,
            'fecha_vencimiento': fecha_vencimiento.isoformat(),
            'monto': monto_pago
        }
    
    mock_mensualidad = MagicMock()
    mock_mensualidad.id_mensualidad = id_mensualidad
    mock_mensualidad.id_persona = id_persona
    mock_mensualidad.monto_pago = monto_pago
    mock_mensualidad.saldo_pendiente = saldo_pendiente
    mock_mensualidad.fecha_vencimiento = fecha_vencimiento
    mock_mensualidad.estado = estado
    mock_mensualidad.fecha_pago = None
    mock_mensualidad.id_metodo_pago = id_metodo_pago
    mock_mensualidad.persona = None
    mock_mensualidad.created_at = None
    mock_mensualidad.activo = True
    mock_mensualidad.to_dict.return_value = to_dict_data
    
    return mock_mensualidad


def create_mock_persona(
    id_persona: int = 1,
    nombre_completo: str = 'Juan Pérez',
    documento: str = '12345678',
    correo_electronico: str = 'usuario@example.com'
) -> Any:
    """
    Crea un mock de Persona con valores por defecto configurables.
    
    Args:
        id_persona: ID de la persona
        nombre_completo: Nombre completo
        documento: Número de documento
        correo_electronico: Correo electrónico
    
    Returns:
        Objeto mock de Persona
    """
    # Crear MagicMock para permitir asignación de to_dict.return_value
    mock_persona = MagicMock()
    mock_persona.id_persona = id_persona
    mock_persona.nombre_completo = nombre_completo
    mock_persona.documento = documento
    mock_persona.correo_electronico = correo_electronico
    # Atributos adicionales requeridos por _serializar_persona
    mock_persona.primer_nombre = nombre_completo.split()[0] if nombre_completo else 'Juan'
    mock_persona.primer_apellido = nombre_completo.split()[-1] if len(nombre_completo.split()) > 1 else 'Pérez'
    mock_persona.telefono = '3001234567'
    mock_persona.estado = True
    
    # Configurar to_dict con valores por defecto
    default_dict = {
        'id_persona': id_persona,
        'nombre_completo': nombre_completo,
        'primer_nombre': mock_persona.primer_nombre,
        'primer_apellido': mock_persona.primer_apellido,
        'documento': documento,
        'correo_electronico': correo_electronico,
        'telefono': mock_persona.telefono
    }
    mock_persona.to_dict.return_value = default_dict
    
    return mock_persona


def create_mock_usuario(
    id_usuario: int = 1,
    usuario: str = 'testuser',
    estado: bool = True,
    id_persona: int = 1,
    persona: Any = None
) -> MagicMock:
    """
    Crea un mock de Usuario con valores por defecto configurables.
    
    Args:
        id_usuario: ID del usuario
        usuario: Nombre de usuario
        estado: Estado del usuario
        id_persona: ID de la persona asociada
        persona: Objeto persona mock (opcional)
    
    Returns:
        MagicMock configurado como Usuario
    """
    if persona is None:
        persona = create_mock_persona(id_persona=id_persona)
    
    mock_usuario = MagicMock()
    mock_usuario.id_usuario = id_usuario
    mock_usuario.usuario = usuario
    mock_usuario.estado = estado
    mock_usuario.roles = []
    mock_usuario.persona = persona
    
    # Configurar atributos de persona si es un MagicMock
    if isinstance(persona, MagicMock):
        persona.id_persona = id_persona
        persona.nombre_completo = persona.nombre_completo or 'Test User'
        persona.primer_nombre = persona.primer_nombre or 'Test'
        persona.primer_apellido = persona.primer_apellido or 'User'
        persona.correo_electronico = persona.correo_electronico or 'test@example.com'
        persona.documento = persona.documento or 12345678
        persona.telefono = persona.telefono or '3001234567'
    
    return mock_usuario


def create_mock_pagination(
    items: list,
    page: int = 1,
    per_page: int = 20,
    total: int = 1,
    pages: int = 1
) -> MagicMock:
    """
    Crea un mock de objeto de paginación.
    
    Args:
        items: Lista de items
        page: Página actual
        per_page: Items por página
        total: Total de items
        pages: Total de páginas
    
    Returns:
        MagicMock configurado como objeto de paginación
    """
    mock_pagination = MagicMock()
    mock_pagination.items = items
    mock_pagination.page = page
    mock_pagination.per_page = per_page
    mock_pagination.total = total
    mock_pagination.pages = pages
    
    return mock_pagination


def setup_mock_db_session_get(mock_db: MagicMock, personas: Dict[int, Any]) -> None:
    """
    Configura mock_db.session.get para retornar personas por ID.
    
    Args:
        mock_db: Mock de db
        personas: Diccionario con id_persona como clave y objeto persona como valor
    """
    def mock_get(model, id_value):
        return personas.get(id_value)
    
    mock_db.session.get = mock_get


def create_mock_abono(
    id_abono: int = 1,
    id_mensualidad: int = 1,
    monto: float = 30000.0,
    fecha_abono: date = None,
    id_metodo_pago: int = 1,
    to_dict_data: Dict[str, Any] = None
) -> MagicMock:
    """
    Crea un mock de AbonoMensualidad con valores por defecto configurables.
    
    Args:
        id_abono: ID del abono
        id_mensualidad: ID de la mensualidad
        monto: Monto del abono
        fecha_abono: Fecha del abono
        id_metodo_pago: ID del método de pago
        to_dict_data: Datos para el método to_dict
    
    Returns:
        MagicMock configurado como AbonoMensualidad
    """
    if fecha_abono is None:
        fecha_abono = date.today()
    
    if to_dict_data is None:
        to_dict_data = {
            'id_abono': id_abono,
            'id_mensualidad': id_mensualidad,
            'monto': monto,
            'fecha_abono': fecha_abono.isoformat(),
            'id_metodo_pago': id_metodo_pago
        }
    
    mock_abono = MagicMock()
    mock_abono.id_abono = id_abono
    mock_abono.id_mensualidad = id_mensualidad
    mock_abono.monto = monto
    mock_abono.fecha_abono = fecha_abono
    mock_abono.id_metodo_pago = id_metodo_pago
    mock_abono.to_dict.return_value = to_dict_data
    
    return mock_abono


def create_mock_serialized_mensualidad(
    id_mensualidad: int = 1,
    saldo_pendiente: float = 50000.0,
    monto_pago: float = 50000.0,
    estado: bool = False,
    estado_texto: str = 'Pendiente'
) -> Dict[str, Any]:
    """
    Crea un diccionario serializado de mensualidad para mocks.
    
    Args:
        id_mensualidad: ID de la mensualidad
        saldo_pendiente: Saldo pendiente
        monto_pago: Monto del pago
        estado: Estado de la mensualidad
        estado_texto: Texto del estado
    
    Returns:
        Diccionario con datos serializados de mensualidad
    """
    return {
        'id_mensualidad': id_mensualidad,
        'saldo_pendiente': saldo_pendiente,
        'monto_pago': monto_pago,
        'estado': estado,
        'estado_texto': estado_texto
    }


def setup_forgot_password_mocks(
    mock_persona: Any = None,
    mock_usuario: Any = None,
    mock_token_exists: bool = False,
    mock_enviar_correo_side_effect: Exception = None
) -> Dict[str, Any]:
    """
    Configura todos los mocks necesarios para tests de forgot_password.
    
    Args:
        mock_persona: Mock de persona
        mock_usuario: Mock de usuario
        mock_token_exists: Si existe un token previo
        mock_enviar_correo_side_effect: Excepción para lanzar al enviar correo
    
    Returns:
        Diccionario con los patches configurados
    """
    from unittest.mock import patch
    
    if mock_persona is None:
        mock_persona = create_mock_persona()
    
    if mock_usuario is None:
        mock_usuario = create_mock_usuario(persona=mock_persona)
    
    patches = {}
    
    # Patch de validación de configuración email
    patches['validar_config'] = patch('src.routes.auth_reset._validar_configuracion_email', return_value=None)
    
    # Patch de queries
    mock_persona_query = MagicMock()
    mock_persona_query.filter_by.return_value.first.return_value = mock_persona
    patches['persona_query'] = patch('src.routes.auth_reset.Persona.query', mock_persona_query)
    
    mock_usuario_query = MagicMock()
    mock_usuario_query.filter_by.return_value.first.return_value = mock_usuario
    patches['usuario_query'] = patch('src.routes.auth_reset.Usuario.query', mock_usuario_query)
    
    # Patch de token - necesita soportar .all() y .first()
    mock_token_filter = MagicMock()
    if mock_token_exists:
        mock_token_filter.first.return_value = MagicMock()
        mock_token_filter.all.return_value = [MagicMock()]
    else:
        mock_token_filter.first.return_value = None
        mock_token_filter.all.return_value = []
    
    mock_token_query = MagicMock()
    mock_token_query.filter_by.return_value = mock_token_filter
    patches['token_query'] = patch('src.routes.auth_reset.PasswordResetToken.query', mock_token_query)
    
    # Patch de creación de token
    mock_token_class = MagicMock()
    mock_token_instance = MagicMock()
    mock_token_instance.id_token = 1
    mock_token_instance.token = 'test-token-123'
    mock_token_class.return_value = mock_token_instance
    mock_token_class.query = mock_token_query
    patches['token_class'] = patch('src.routes.auth_reset.PasswordResetToken', mock_token_class)
    
    mock_db = MagicMock()
    mock_db.session.add = MagicMock()
    mock_db.session.commit = MagicMock()
    patches['db'] = patch('src.routes.auth_reset.db', mock_db)
    
    # Patch de envío de correo
    if mock_enviar_correo_side_effect:
        patches['enviar_correo'] = patch(
            'src.routes.auth_reset._enviar_correo_reset',
            side_effect=mock_enviar_correo_side_effect
        )
    else:
        patches['enviar_correo'] = patch('src.routes.auth_reset._enviar_correo_reset', return_value=None)
    
    return patches

