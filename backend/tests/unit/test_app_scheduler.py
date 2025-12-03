"""
Tests adicionales para app.py - Scheduler initialization.
"""

import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
import sys

from app import _initialize_scheduler


@pytest.mark.unit
class TestInitializeScheduler:
    """Tests para _initialize_scheduler."""
    
    def test_initialize_scheduler_success(self):
        """Test: Inicializar scheduler exitosamente."""
        app = Flask(__name__)
        app.logger = MagicMock()
        
        mock_init_scheduler = MagicMock()
        
        # Patch the function where it's imported - need to patch at the point of import
        # Since the import is inside the function, we patch the module before it's imported
        original_module = sys.modules.get('src.utils.scheduler')
        
        try:
            # Remove from cache to force re-import
            if 'src.utils.scheduler' in sys.modules:
                del sys.modules['src.utils.scheduler']
            
            # Create mock module
            mock_module = MagicMock()
            mock_module.init_scheduler = mock_init_scheduler
            sys.modules['src.utils.scheduler'] = mock_module
            
            _initialize_scheduler(app)
            
            mock_init_scheduler.assert_called_once_with(app)
            app.logger.info.assert_called_once()
            assert 'Scheduler' in app.logger.info.call_args[0][0]
        finally:
            # Restore original module
            if original_module:
                sys.modules['src.utils.scheduler'] = original_module
            elif 'src.utils.scheduler' in sys.modules:
                del sys.modules['src.utils.scheduler']
    
    def test_initialize_scheduler_import_error(self):
        """Test: Manejar error de importación del scheduler."""
        app = Flask(__name__)
        app.logger = MagicMock()
        
        # Remove module from cache to simulate import error
        original_module = sys.modules.get('src.utils.scheduler')
        
        try:
            # Remove from cache
            if 'src.utils.scheduler' in sys.modules:
                del sys.modules['src.utils.scheduler']
            
            # Create module that raises ImportError on attribute access
            class ErrorModule:
                def __getattr__(self, name):
                    raise ImportError("Cannot import init_scheduler")
            
            sys.modules['src.utils.scheduler'] = ErrorModule()
            
            _initialize_scheduler(app)
            
            app.logger.warning.assert_called_once()
            warning_msg = app.logger.warning.call_args[0][0]
            assert 'scheduler' in warning_msg.lower()
        finally:
            # Restore original module
            if original_module:
                sys.modules['src.utils.scheduler'] = original_module
            elif 'src.utils.scheduler' in sys.modules:
                del sys.modules['src.utils.scheduler']
    
    def test_initialize_scheduler_general_exception(self):
        """Test: Manejar excepción general del scheduler."""
        app = Flask(__name__)
        app.logger = MagicMock()
        
        mock_init_scheduler = MagicMock(side_effect=Exception("General error"))
        
        original_module = sys.modules.get('src.utils.scheduler')
        
        try:
            mock_module = MagicMock()
            mock_module.init_scheduler = mock_init_scheduler
            sys.modules['src.utils.scheduler'] = mock_module
            
            _initialize_scheduler(app)
            
            app.logger.error.assert_called_once()
            assert 'Error inicializando scheduler' in app.logger.error.call_args[0][0]
        finally:
            # Restore original module
            if original_module:
                sys.modules['src.utils.scheduler'] = original_module
            elif 'src.utils.scheduler' in sys.modules:
                del sys.modules['src.utils.scheduler']

