"""
Tests unitarios para el módulo scheduler.py.

Cubre todas las funciones y ramas para alcanzar 100% de cobertura.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

from src.utils.scheduler import (
    init_scheduler,
    shutdown_scheduler,
    reset_scheduler,
    get_scheduler,
    get_scheduler_status
)


@pytest.mark.unit
class TestInitScheduler:
    """Tests para init_scheduler."""
    
    def test_init_scheduler_skips_when_testing(self):
        """Test: No inicializar scheduler en modo testing."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        # Reset scheduler antes del test
        reset_scheduler()
        
        # Llamar init_scheduler
        init_scheduler(app)
        
        # Verificar que scheduler sigue siendo None
        assert get_scheduler() is None
    
    def test_init_scheduler_when_already_initialized(self):
        """Test: Warning cuando scheduler ya está inicializado."""
        app = Flask(__name__)
        app.config['TESTING'] = False
        
        # Crear un mock scheduler
        mock_scheduler = MagicMock(spec=BackgroundScheduler)
        mock_scheduler.running = True
        
        # Inyectar scheduler directamente (usando el módulo)
        import src.utils.scheduler as scheduler_module
        scheduler_module.scheduler = mock_scheduler
        
        with patch.object(scheduler_module.logger, 'warning') as mock_warning:
            init_scheduler(app)
            mock_warning.assert_called_once()
            assert 'Scheduler ya está inicializado' in mock_warning.call_args[0][0]
        
        # Limpiar
        reset_scheduler()
    
    def test_init_scheduler_success(self):
        """Test: Inicializar scheduler exitosamente."""
        app = Flask(__name__)
        app.config['TESTING'] = False
        
        # Reset scheduler antes del test
        reset_scheduler()
        
        with patch('src.utils.scheduler.BackgroundScheduler') as mock_scheduler_class:
            mock_scheduler_instance = MagicMock()
            mock_scheduler_instance.running = True
            mock_scheduler_class.return_value = mock_scheduler_instance
            
            with patch('src.utils.scheduler._configure_scheduled_tasks') as mock_configure:
                with patch.object(app, 'app_context', return_value=MagicMock(__enter__=MagicMock(), __exit__=MagicMock())):
                    init_scheduler(app)
                    
                    # Verificar que se creó y empezó el scheduler
                    mock_scheduler_class.assert_called_once()
                    mock_scheduler_instance.start.assert_called_once()
                    mock_configure.assert_called_once_with(app)
        
        # Limpiar
        reset_scheduler()


@pytest.mark.unit
class TestConfigureScheduledTasks:
    """Tests para _configure_scheduled_tasks."""
    
    def test_configure_scheduled_tasks_adds_job(self):
        """Test: Configurar tareas programadas."""
        app = Flask(__name__)
        
        # Reset scheduler
        reset_scheduler()
        
        # Crear mock scheduler
        mock_scheduler = MagicMock(spec=BackgroundScheduler)
        mock_job = MagicMock()
        mock_job.id = 'renovar_mensualidades'
        mock_job.name = 'Renovación automática de mensualidades'
        mock_scheduler.get_jobs.return_value = [mock_job]
        
        # Inyectar scheduler
        import src.utils.scheduler as scheduler_module
        scheduler_module.scheduler = mock_scheduler
        
        # Importar función privada
        from src.utils.scheduler import _configure_scheduled_tasks
        
        with patch('src.utils.scheduler.CronTrigger') as mock_cron:
            with patch.object(scheduler_module.logger, 'info') as mock_info:
                _configure_scheduled_tasks(app)
                
                # Verificar que se agregó el job
                mock_scheduler.add_job.assert_called_once()
                mock_info.assert_called_once()
        
        # Limpiar
        reset_scheduler()


@pytest.mark.unit
class TestRenovarMensualidadesAutomaticamente:
    """Tests para _renovar_mensualidades_automaticamente."""
    
    def test_renovar_mensualidades_success(self):
        """Test: Renovar mensualidades exitosamente."""
        app = Flask(__name__)
        
        mock_resultado = {
            'success': True,
            'renovadas': 5,
            'bloqueadas': 2
        }
        
        # Mock la función importada dentro de _renovar_mensualidades_automaticamente
        with patch('src.routes.mensualidades_routes._renovar_mensualidades_automaticamente', return_value=mock_resultado) as mock_imported_func:
            import src.utils.scheduler as scheduler_module
            
            with app.app_context():
                with patch.object(scheduler_module.logger, 'info') as mock_info:
                    scheduler_module._renovar_mensualidades_automaticamente(app)
                    
                    # Verificar logs
                    assert mock_info.call_count >= 2
                    # Verificar que se llamó la función importada
                    mock_imported_func.assert_called_once()
    
    def test_renovar_mensualidades_with_error_result(self):
        """Test: Renovar mensualidades con resultado de error."""
        app = Flask(__name__)
        
        mock_resultado = {
            'success': False,
            'error': 'Error de prueba'
        }
        
        # Mock la función importada dentro de _renovar_mensualidades_automaticamente
        with patch('src.routes.mensualidades_routes._renovar_mensualidades_automaticamente', return_value=mock_resultado):
            import src.utils.scheduler as scheduler_module
            
            with app.app_context():
                with patch.object(scheduler_module.logger, 'error') as mock_error:
                    scheduler_module._renovar_mensualidades_automaticamente(app)
                    
                    # Verificar que se registró el error (línea 88-90)
                    assert mock_error.call_count >= 1
                    # Verificar que el mensaje de error contiene el error del resultado
                    call_args = mock_error.call_args[0]
                    assert 'Error en renovación automática' in call_args[0] or 'Error de prueba' in str(call_args)
    
    def test_renovar_mensualidades_with_exception(self):
        """Test: Renovar mensualidades con excepción."""
        app = Flask(__name__)
        
        # Mock la función importada para que lance excepción
        with patch('src.routes.mensualidades_routes._renovar_mensualidades_automaticamente', side_effect=Exception('Error de prueba')):
            import src.utils.scheduler as scheduler_module
            
            with app.app_context():
                with patch.object(scheduler_module.logger, 'error') as mock_error:
                    scheduler_module._renovar_mensualidades_automaticamente(app)
                    
                    # Verificar que se registró el error (línea 93)
                    assert mock_error.call_count >= 1


@pytest.mark.unit
class TestShutdownScheduler:
    """Tests para shutdown_scheduler."""
    
    def test_shutdown_scheduler_when_none(self):
        """Test: shutdown_scheduler cuando scheduler es None."""
        reset_scheduler()
        
        # No debería lanzar excepción
        shutdown_scheduler()
        
        assert get_scheduler() is None
    
    def test_shutdown_scheduler_success(self):
        """Test: Detener scheduler exitosamente."""
        # Crear mock scheduler
        mock_scheduler = MagicMock(spec=BackgroundScheduler)
        
        # Inyectar scheduler
        import src.utils.scheduler as scheduler_module
        scheduler_module.scheduler = mock_scheduler
        
        shutdown_scheduler()
        
        # Verificar que se llamó shutdown
        mock_scheduler.shutdown.assert_called_once()
        assert get_scheduler() is None
    
    def test_shutdown_scheduler_with_exception(self):
        """Test: shutdown_scheduler maneja excepciones."""
        # Crear mock scheduler que lanza excepción
        mock_scheduler = MagicMock(spec=BackgroundScheduler)
        mock_scheduler.shutdown.side_effect = Exception('Error al cerrar')
        
        # Inyectar scheduler
        import src.utils.scheduler as scheduler_module
        scheduler_module.scheduler = mock_scheduler
        
        # No debería lanzar excepción
        shutdown_scheduler()
        
        # Verificar que scheduler se reseteó a pesar del error
        assert get_scheduler() is None


@pytest.mark.unit
class TestResetScheduler:
    """Tests para reset_scheduler."""
    
    def test_reset_scheduler(self):
        """Test: Resetear scheduler."""
        # Crear un scheduler mock
        mock_scheduler = MagicMock()
        import src.utils.scheduler as scheduler_module
        scheduler_module.scheduler = mock_scheduler
        
        reset_scheduler()
        
        assert get_scheduler() is None


@pytest.mark.unit
class TestGetScheduler:
    """Tests para get_scheduler."""
    
    def test_get_scheduler_when_none(self):
        """Test: Obtener scheduler cuando es None."""
        reset_scheduler()
        
        assert get_scheduler() is None
    
    def test_get_scheduler_when_initialized(self):
        """Test: Obtener scheduler cuando está inicializado."""
        mock_scheduler = MagicMock(spec=BackgroundScheduler)
        
        import src.utils.scheduler as scheduler_module
        scheduler_module.scheduler = mock_scheduler
        
        assert get_scheduler() == mock_scheduler
        
        # Limpiar
        reset_scheduler()


@pytest.mark.unit
class TestGetSchedulerStatus:
    """Tests para get_scheduler_status."""
    
    def test_get_scheduler_status_when_none(self):
        """Test: Estado del scheduler cuando es None."""
        reset_scheduler()
        
        status = get_scheduler_status()
        
        assert status['activo'] is False
        assert status['tareas'] == []
        assert 'mensaje' in status
        assert 'Scheduler no inicializado' in status['mensaje']
    
    def test_get_scheduler_status_when_initialized_with_jobs(self):
        """Test: Estado del scheduler cuando está inicializado con jobs."""
        # Crear mock scheduler con jobs
        mock_scheduler = MagicMock(spec=BackgroundScheduler)
        mock_scheduler.running = True
        
        # Crear mock jobs
        mock_job1 = MagicMock()
        mock_job1.id = 'job1'
        mock_job1.name = 'Tarea 1'
        mock_job1.next_run_time = MagicMock()
        mock_job1.next_run_time.isoformat.return_value = '2025-01-01T00:00:00'
        
        mock_job2 = MagicMock()
        mock_job2.id = 'job2'
        mock_job2.name = 'Tarea 2'
        mock_job2.next_run_time = None
        
        mock_scheduler.get_jobs.return_value = [mock_job1, mock_job2]
        
        # Inyectar scheduler
        import src.utils.scheduler as scheduler_module
        scheduler_module.scheduler = mock_scheduler
        
        status = get_scheduler_status()
        
        assert status['activo'] is True
        assert len(status['tareas']) == 2
        assert status['total_tareas'] == 2
        assert status['tareas'][0]['id'] == 'job1'
        assert status['tareas'][0]['activo'] is True
        assert status['tareas'][1]['id'] == 'job2'
        assert status['tareas'][1]['activo'] is False
        assert status['tareas'][1]['proxima_ejecucion'] is None
        
        # Limpiar
        reset_scheduler()
    
    def test_get_scheduler_status_when_initialized_no_jobs(self):
        """Test: Estado del scheduler cuando está inicializado sin jobs."""
        # Crear mock scheduler sin jobs
        mock_scheduler = MagicMock(spec=BackgroundScheduler)
        mock_scheduler.running = False
        mock_scheduler.get_jobs.return_value = []
        
        # Inyectar scheduler
        import src.utils.scheduler as scheduler_module
        scheduler_module.scheduler = mock_scheduler
        
        status = get_scheduler_status()
        
        assert status['activo'] is False
        assert status['tareas'] == []
        assert status['total_tareas'] == 0
        
        # Limpiar
        reset_scheduler()

