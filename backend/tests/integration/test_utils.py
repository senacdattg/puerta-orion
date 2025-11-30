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
    class MockPersona:
        """Mock simple de Persona para evitar problemas de serialización."""
        def __init__(self):
            self.id_persona = id_persona
            self.nombre_completo = nombre_completo
            self.documento = documento
            self.correo_electronico = correo_electronico
    
    return MockPersona()


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

