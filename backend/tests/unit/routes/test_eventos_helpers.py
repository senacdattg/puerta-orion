"""
Tests unitarios para funciones helper de eventos_routes.py.

Cubre funciones auxiliares que no están en otros archivos de test para aumentar cobertura.
Aplicando principios de Clean Code: DRY, SRP, nombres descriptivos, tests aislados.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import date, time, datetime

from src.routes import eventos_routes
from src.routes.eventos_routes import (
    validar_fecha,
    validar_hora,
    validar_lugar,
    validar_solapamiento_horario,
    obtener_categorias_permitidas_usuario,
)


@pytest.mark.unit
@pytest.mark.eventos
class TestParseDate:
    """Tests para la función _parse_date."""

    def test_parse_date_success(self):
        """Test: Parsear fecha válida."""
        result = eventos_routes._parse_date('2024-12-31')
        
        assert result is not None
        assert isinstance(result, date)
        assert result.year == 2024
        assert result.month == 12
        assert result.day == 31

    def test_parse_date_invalida(self):
        """Test: Parsear fecha inválida."""
        result = eventos_routes._parse_date('invalid-date')
        
        assert result is None

    def test_parse_date_formato_incorrecto(self):
        """Test: Parsear fecha con formato incorrecto."""
        result = eventos_routes._parse_date('31-12-2024')
        
        assert result is None

    def test_parse_date_none(self):
        """Test: Parsear None."""
        result = eventos_routes._parse_date(None)
        
        assert result is None


@pytest.mark.unit
@pytest.mark.eventos
class TestParseTime:
    """Tests para la función _parse_time."""

    def test_parse_time_hh_mm(self):
        """Test: Parsear hora en formato HH:MM."""
        result = eventos_routes._parse_time('14:30')
        
        assert result is not None
        assert isinstance(result, time)
        assert result.hour == 14
        assert result.minute == 30

    def test_parse_time_hh_mm_ss(self):
        """Test: Parsear hora en formato HH:MM:SS."""
        result = eventos_routes._parse_time('14:30:45')
        
        assert result is not None
        assert isinstance(result, time)
        assert result.hour == 14
        assert result.minute == 30
        assert result.second == 45

    def test_parse_time_invalida(self):
        """Test: Parsear hora inválida."""
        result = eventos_routes._parse_time('invalid-time')
        
        assert result is None

    def test_parse_time_none(self):
        """Test: Parsear None."""
        result = eventos_routes._parse_time(None)
        
        assert result is None


@pytest.mark.unit
@pytest.mark.eventos
class TestValidarLugar:
    """Tests para la función _validar_lugar."""

    def test_validar_lugar_valido(self):
        """Test: Validar lugar válido."""
        result = eventos_routes._validar_lugar('Estadio Central')
        
        assert result is True

    def test_validar_lugar_muy_corto(self):
        """Test: Validar lugar muy corto."""
        result = eventos_routes._validar_lugar('AB')
        
        assert result is False

    def test_validar_lugar_vacio(self):
        """Test: Validar lugar vacío."""
        result = eventos_routes._validar_lugar('')
        
        assert result is False

    def test_validar_lugar_solo_espacios(self):
        """Test: Validar lugar con solo espacios."""
        result = eventos_routes._validar_lugar('   ')
        
        assert result is False


@pytest.mark.unit
@pytest.mark.eventos
class TestObtenerCategoriaTodos:
    """Tests para la función _obtener_categoria_todos."""

    def test_obtener_categoria_todos_existe(self, app):
        """Test: Obtener categoría 'Todos' cuando existe."""
        with app.app_context():
            mock_categoria = MagicMock()
            mock_categoria.id_categoria = 1
            
            with patch('src.routes.eventos_routes.Categoria') as mock_categoria_class:
                mock_query = MagicMock()
                mock_query.filter_by.return_value.first.return_value = mock_categoria
                mock_categoria_class.query = mock_query
                
                result = eventos_routes._obtener_categoria_todos()
                
                assert result == 1

    def test_obtener_categoria_todos_no_existe(self, app):
        """Test: Obtener categoría 'Todos' cuando no existe."""
        with app.app_context():
            with patch('src.routes.eventos_routes.Categoria') as mock_categoria_class:
                mock_query = MagicMock()
                mock_query.filter_by.return_value.first.return_value = None
                mock_categoria_class.query = mock_query
                
                result = eventos_routes._obtener_categoria_todos()
                
                assert result is None


@pytest.mark.unit
@pytest.mark.eventos
class TestValidarSolapamientoHorario:
    """Tests para la función _validar_solapamiento_horario."""

    def test_validar_solapamiento_sin_solapamiento(self, app):
        """Test: Validar solapamiento cuando no hay solapamiento."""
        with app.app_context():
            fecha = date(2024, 12, 31)
            hora_inicio = time(10, 0)
            hora_fin = time(12, 0)
            
            with patch('src.routes.eventos_routes.Evento') as mock_evento_class:
                mock_query = MagicMock()
                mock_query.filter_by.return_value = mock_query
                mock_query.all.return_value = []
                mock_evento_class.query = mock_query
                
                result, mensaje = eventos_routes._validar_solapamiento_horario(
                    fecha, hora_inicio, hora_fin
                )
                
                assert result is True
                assert mensaje is None

    def test_validar_solapamiento_con_solapamiento(self, app):
        """Test: Validar solapamiento cuando hay solapamiento."""
        with app.app_context():
            fecha = date(2024, 12, 31)
            hora_inicio = time(10, 0)
            hora_fin = time(12, 0)
            
            mock_evento_existente = MagicMock()
            mock_evento_existente.id_evento = 1
            mock_evento_existente.nombre = 'Evento Existente'
            mock_evento_existente.hora_inicio = time(11, 0)
            mock_evento_existente.hora_fin = time(13, 0)
            
            with patch('src.routes.eventos_routes.Evento') as mock_evento_class:
                mock_query = MagicMock()
                mock_query.filter_by.return_value = mock_query
                mock_query.all.return_value = [mock_evento_existente]
                mock_evento_class.query = mock_query
                
                result, mensaje = eventos_routes._validar_solapamiento_horario(
                    fecha, hora_inicio, hora_fin
                )
                
                assert result is False
                assert mensaje is not None
                assert 'solapa' in mensaje.lower()

    def test_validar_solapamiento_excluir_evento(self, app):
        """Test: Validar solapamiento excluyendo un evento."""
        with app.app_context():
            fecha = date(2024, 12, 31)
            hora_inicio = time(10, 0)
            hora_fin = time(12, 0)
            
            mock_evento_existente = MagicMock()
            mock_evento_existente.id_evento = 1
            mock_evento_existente.hora_inicio = time(11, 0)
            mock_evento_existente.hora_fin = time(13, 0)
            
            with patch('src.routes.eventos_routes.Evento') as mock_evento_class:
                mock_query = MagicMock()
                mock_query.filter_by.return_value = mock_query
                mock_query.all.return_value = [mock_evento_existente]
                mock_evento_class.query = mock_query
                
                result, _ = eventos_routes._validar_solapamiento_horario(
                    fecha, hora_inicio, hora_fin,
                    id_evento_excluir=1
                )
                
                # No debe haber solapamiento porque se excluye el evento
                assert result is True


@pytest.mark.unit
@pytest.mark.eventos
class TestConstruirMensajeSolapamiento:
    """Tests para la función _construir_mensaje_solapamiento."""

    def test_construir_mensaje_solapamiento_inicio_antes(self):
        """Test: Construir mensaje cuando el inicio es antes."""
        mock_evento = MagicMock()
        mock_evento.nombre = 'Evento Existente'
        mock_evento.hora_inicio = time(12, 0)
        
        hora_inicio_nueva = time(10, 0)
        hora_fin_nueva = time(11, 30)
        
        mensaje = eventos_routes._construir_mensaje_solapamiento(
            evento_existente=mock_evento,
            hora_inicio_nueva=hora_inicio_nueva,
            hora_fin_nueva=hora_fin_nueva
        )
        
        assert 'solapa' in mensaje.lower()
        assert 'Evento Existente' in mensaje

    def test_construir_mensaje_solapamiento_dentro(self):
        """Test: Construir mensaje cuando está completamente dentro."""
        mock_evento = MagicMock()
        mock_evento.nombre = 'Evento Existente'
        mock_evento.hora_inicio = time(10, 0)
        mock_evento.hora_fin = time(14, 0)
        
        hora_inicio_nueva = time(11, 0)
        hora_fin_nueva = time(13, 0)
        
        mensaje = eventos_routes._construir_mensaje_solapamiento(
            evento_existente=mock_evento,
            hora_inicio_nueva=hora_inicio_nueva,
            hora_fin_nueva=hora_fin_nueva
        )
        
        assert 'completamente dentro' in mensaje.lower()

    def test_construir_mensaje_solapamiento_inicio_despues(self):
        """Test: Construir mensaje cuando el inicio es después."""
        mock_evento = MagicMock()
        mock_evento.nombre = 'Evento Existente'
        mock_evento.hora_inicio = time(10, 0)
        mock_evento.hora_fin = time(12, 0)
        
        hora_inicio_nueva = time(11, 0)
        hora_fin_nueva = time(13, 0)
        
        mensaje = eventos_routes._construir_mensaje_solapamiento(
            evento_existente=mock_evento,
            hora_inicio_nueva=hora_inicio_nueva,
            hora_fin_nueva=hora_fin_nueva
        )
        
        assert 'solapa' in mensaje.lower()


@pytest.mark.unit
@pytest.mark.eventos
class TestEsUsuarioAdmin:
    """Tests para la función _es_usuario_admin."""

    def test_es_usuario_admin_superadmin(self):
        """Test: Usuario es SuperAdmin."""
        roles = ['SuperAdmin']
        result = eventos_routes._es_usuario_admin(roles)
        
        assert result is True

    def test_es_usuario_admin_administrador(self):
        """Test: Usuario es Administrador."""
        roles = ['Administrador']
        result = eventos_routes._es_usuario_admin(roles)
        
        assert result is True

    def test_es_usuario_admin_entrenador(self):
        """Test: Usuario es Entrenador."""
        roles = ['Entrenador']
        result = eventos_routes._es_usuario_admin(roles)
        
        assert result is True

    def test_es_usuario_admin_no_admin(self):
        """Test: Usuario no es admin."""
        roles = ['Deportista', 'Acudiente']
        result = eventos_routes._es_usuario_admin(roles)
        
        assert result is False


@pytest.mark.unit
@pytest.mark.eventos
class TestObtenerCategoriasDeportista:
    """Tests para la función _obtener_categorias_deportista."""

    def test_obtener_categorias_deportista_success(self, app):
        """Test: Obtener categorías de deportista exitosamente."""
        with app.app_context():
            mock_deportista = MagicMock()
            mock_deportista.id_categoria = 1
            
            with patch('src.routes.eventos_routes.Deportista') as mock_deportista_class:
                mock_query = MagicMock()
                mock_query.filter_by.return_value.first.return_value = mock_deportista
                mock_deportista_class.query = mock_query
                
                result = eventos_routes._obtener_categorias_deportista(1)
                
                assert isinstance(result, set)
                assert 1 in result

    def test_obtener_categorias_deportista_no_existe(self, app):
        """Test: Obtener categorías cuando el deportista no existe."""
        with app.app_context():
            with patch('src.routes.eventos_routes.Deportista') as mock_deportista_class:
                mock_query = MagicMock()
                mock_query.filter_by.return_value.first.return_value = None
                mock_deportista_class.query = mock_query
                
                result = eventos_routes._obtener_categorias_deportista(999)
                
                assert isinstance(result, set)
                assert len(result) == 0

    def test_obtener_categorias_deportista_sin_categoria(self, app):
        """Test: Obtener categorías cuando el deportista no tiene categoría."""
        with app.app_context():
            mock_deportista = MagicMock()
            mock_deportista.id_categoria = None
            
            with patch('src.routes.eventos_routes.Deportista') as mock_deportista_class:
                mock_query = MagicMock()
                mock_query.filter_by.return_value.first.return_value = mock_deportista
                mock_deportista_class.query = mock_query
                
                result = eventos_routes._obtener_categorias_deportista(1)
                
                assert isinstance(result, set)
                assert len(result) == 0


@pytest.mark.unit
@pytest.mark.eventos
class TestObtenerCategoriasAcudiente:
    """Tests para la función _obtener_categorias_acudiente."""

    def test_obtener_categorias_acudiente_success(self, app):
        """Test: Obtener categorías de acudiente exitosamente."""
        with app.app_context():
            mock_acudiente = MagicMock()
            mock_acudiente.id_acudiente = 1
            
            mock_relacion = MagicMock()
            mock_relacion.id_deportista = 1
            
            mock_deportista = MagicMock()
            mock_deportista.id_categoria = 2
            
            with patch('src.routes.eventos_routes.Acudiente') as mock_acudiente_class, \
                 patch('src.routes.eventos_routes.DeportistaAcudiente') as mock_relacion_class, \
                 patch('src.routes.eventos_routes.Deportista') as mock_deportista_class:
                
                mock_acudiente_query = MagicMock()
                mock_acudiente_query.filter_by.return_value.first.return_value = mock_acudiente
                mock_acudiente_class.query = mock_acudiente_query
                
                mock_relacion_query = MagicMock()
                mock_relacion_query.filter_by.return_value.all.return_value = [mock_relacion]
                mock_relacion_class.query = mock_relacion_query
                
                mock_deportista_query = MagicMock()
                mock_deportista_query.get.return_value = mock_deportista
                mock_deportista_class.query = mock_deportista_query
                
                result = eventos_routes._obtener_categorias_acudiente(1)
                
                assert isinstance(result, set)
                assert 2 in result

    def test_obtener_categorias_acudiente_no_existe(self, app):
        """Test: Obtener categorías cuando el acudiente no existe."""
        with app.app_context():
            with patch('src.routes.eventos_routes.Acudiente') as mock_acudiente_class:
                mock_query = MagicMock()
                mock_query.filter_by.return_value.first.return_value = None
                mock_acudiente_class.query = mock_query
                
                result = eventos_routes._obtener_categorias_acudiente(999)
                
                assert isinstance(result, set)
                assert len(result) == 0


@pytest.mark.unit
@pytest.mark.eventos
class TestObtenerCategoriasPermitidasUsuario:
    """Tests para la función obtener_categorias_permitidas_usuario."""

    def test_obtener_categorias_permitidas_sin_usuario(self, app):
        """Test: Obtener categorías cuando no hay usuario."""
        with app.app_context():
            with patch('src.routes.eventos_routes.get_current_user', return_value=None):
                result = obtener_categorias_permitidas_usuario()
                
                assert result == []

    def test_obtener_categorias_permitidas_rol_activo_deportista(self, app):
        """Test: Obtener categorías con rol activo Deportista."""
        with app.app_context():
            usuario_data = {
                'roles': [{'nombre_rol': 'Deportista'}],
                'rol_activo': 'Deportista',
                'persona': {'id_persona': 1}
            }
            
            with patch('src.routes.eventos_routes.get_current_user', return_value=usuario_data), \
                 patch('src.routes.eventos_routes._obtener_categorias_deportista', return_value={1, 2}):
                
                result = obtener_categorias_permitidas_usuario()
                
                assert isinstance(result, list)
                assert 1 in result
                assert 2 in result

    def test_obtener_categorias_permitidas_rol_activo_acudiente(self, app):
        """Test: Obtener categorías con rol activo Acudiente."""
        with app.app_context():
            usuario_data = {
                'roles': [{'nombre_rol': 'Acudiente'}],
                'rol_activo': 'Acudiente',
                'persona': {'id_persona': 1}
            }
            
            with patch('src.routes.eventos_routes.get_current_user', return_value=usuario_data), \
                 patch('src.routes.eventos_routes._obtener_categorias_acudiente', return_value={3, 4}):
                
                result = obtener_categorias_permitidas_usuario()
                
                assert isinstance(result, list)
                assert 3 in result
                assert 4 in result

    def test_obtener_categorias_permitidas_admin(self, app):
        """Test: Obtener categorías para admin (retorna None)."""
        with app.app_context():
            usuario_data = {
                'roles': [{'nombre_rol': 'Administrador'}],
                'rol_activo': 'Administrador',
                'persona': {'id_persona': 1}
            }
            
            with patch('src.routes.eventos_routes.get_current_user', return_value=usuario_data), \
                 patch('src.routes.eventos_routes._es_usuario_admin', return_value=True):
                
                result = obtener_categorias_permitidas_usuario()
                
                assert result is None


@pytest.mark.unit
@pytest.mark.eventos
class TestValidacionesPublicas:
    """Tests para funciones de validación públicas."""

    def test_validar_fecha_success(self):
        """Test: Validar fecha válida."""
        result = validar_fecha('2024-12-31')
        
        assert result is not None
        assert isinstance(result, date)

    def test_validar_fecha_invalida(self):
        """Test: Validar fecha inválida."""
        result = validar_fecha('invalid')
        
        assert result is None

    def test_validar_hora_success(self):
        """Test: Validar hora válida."""
        result = validar_hora('14:30')
        
        assert result is not None
        assert isinstance(result, time)

    def test_validar_hora_invalida(self):
        """Test: Validar hora inválida."""
        result = validar_hora('invalid')
        
        assert result is None

    def test_validar_lugar_success(self):
        """Test: Validar lugar válido."""
        result = validar_lugar('Estadio Central')
        
        assert result is True

    def test_validar_lugar_invalido(self):
        """Test: Validar lugar inválido."""
        result = validar_lugar('AB')
        
        assert result is False

    def test_validar_solapamiento_horario_success(self, app):
        """Test: Validar solapamiento horario sin solapamiento."""
        with app.app_context():
            from datetime import date, time
            fecha = date(2024, 12, 31)
            hora_inicio = time(10, 0)
            hora_fin = time(12, 0)
            
            with patch('src.routes.eventos_routes._validar_solapamiento_horario', return_value=(True, None)):
                result, _ = validar_solapamiento_horario(
                    fecha, hora_inicio, hora_fin, id_categoria=1
                )
                
                assert result is True

    def test_validar_solapamiento_horario_con_solapamiento(self, app):
        """Test: Validar solapamiento horario con solapamiento."""
        with app.app_context():
            from datetime import date, time
            fecha = date(2024, 12, 31)
            hora_inicio = time(10, 0)
            hora_fin = time(12, 0)
            
            with patch('src.routes.eventos_routes._validar_solapamiento_horario', 
                      return_value=(False, 'Hay solapamiento')):
                result, _ = validar_solapamiento_horario(
                    fecha, hora_inicio, hora_fin, id_categoria=1
                )
                
                assert result is False


@pytest.mark.unit
@pytest.mark.eventos
class TestSerializarEvento:
    """Tests para la función _serializar_evento."""

    def test_serializar_evento_completo(self, app):
        """Test: Serializar evento con todas las relaciones."""
        with app.app_context():
            mock_evento = MagicMock()
            mock_evento.id_evento = 1
            mock_evento.nombre = 'Torneo'
            mock_evento.fecha_evento = date(2024, 12, 31)
            mock_evento.hora_inicio = time(10, 0)
            mock_evento.hora_fin = time(12, 0)
            mock_evento.lugar = 'Estadio'
            mock_evento.descripcion = 'Descripción'
            mock_evento.id_categoria = 1
            mock_evento.id_tipo_evento = 1
            mock_evento.id_sesion = 1
            
            mock_categoria = MagicMock()
            mock_categoria.to_dict.return_value = {'id_categoria': 1, 'nombre': 'Sub-15'}
            mock_evento.categoria = mock_categoria
            
            mock_tipo = MagicMock()
            mock_tipo.to_dict.return_value = {'id_tipo_evento': 1, 'nombre': 'Competencia'}
            mock_evento.tipo_evento = mock_tipo
            
            mock_sesion = MagicMock()
            mock_sesion.to_dict.return_value = {'id_sesion': 1, 'nombre': 'Sesión 1'}
            mock_evento.sesion = mock_sesion
            
            mock_evento.to_dict.return_value = {
                'id_evento': 1,
                'nombre': 'Torneo'
            }
            
            with patch('src.routes.eventos_routes._agregar_categoria_serializada') as mock_cat, \
                 patch('src.routes.eventos_routes._agregar_tipo_evento_serializado') as mock_tipo, \
                 patch('src.routes.eventos_routes._agregar_sesion_serializada') as mock_ses:
                
                result = eventos_routes._serializar_evento(mock_evento)
                
                assert isinstance(result, dict)
                assert result['id_evento'] == 1
                mock_cat.assert_called_once()
                mock_tipo.assert_called_once()
                mock_ses.assert_called_once()


@pytest.mark.unit
@pytest.mark.eventos
class TestObtenerNombreRequerido:
    """Tests para la función _obtener_nombre_requerido."""

    def test_obtener_nombre_requerido_existe(self):
        """Test: Obtener nombre cuando existe."""
        data = {'nombre': 'Torneo de Fútbol'}
        result = eventos_routes._obtener_nombre_requerido(data)
        
        assert result == 'Torneo de Fútbol'

    def test_obtener_nombre_requerido_no_existe(self):
        """Test: Obtener nombre cuando no existe."""
        data = {}
        
        # La función lanza RequestValidationError cuando falta el campo
        from src.utils.request_validators import RequestValidationError
        with pytest.raises(RequestValidationError):
            eventos_routes._obtener_nombre_requerido(data)

