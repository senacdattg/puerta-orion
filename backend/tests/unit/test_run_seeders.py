"""
Tests para run_seeders.py.
"""

import pytest
from unittest.mock import patch, MagicMock, call
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


@pytest.mark.unit
class TestRunSeeders:
    """Tests para run_seeders.py."""
    
    def test_run_seeders_file_exists(self):
        """Test: Verificar que el archivo run_seeders.py existe."""
        import os
        
        # Get backend directory
        backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
        run_seeders_path = os.path.join(backend_dir, 'run_seeders.py')
        
        assert os.path.exists(run_seeders_path), f"run_seeders.py should exist at {run_seeders_path}"
    
    def test_run_seeders_imports_seed_function(self):
        """Test: Verificar que run_seeders.py importa run_all_seeders."""
        import os
        import sys
        
        # Get backend directory
        backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
        
        # Add to path temporarily
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)
        
        try:
            # Read the file content to verify it imports correctly
            run_seeders_path = os.path.join(backend_dir, 'run_seeders.py')
            with open(run_seeders_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert 'from src.seeders.seed import run_all_seeders' in content
                assert 'run_all_seeders' in content
        finally:
            # Clean up path
            if backend_dir in sys.path:
                sys.path.remove(backend_dir)


@pytest.mark.integration
class TestRunSeedersIntegration:
    """Tests de integración para run_seeders.py."""
    
    def test_run_all_seeders_main_execution(self, app):
        """Test: Ejecutar run_all_seeders en contexto de aplicación."""
        from src.seeders.seed import run_all_seeders
        
        with patch('src.seeders.seed.seed_tipo_documento') as mock_tipo_doc:
            with patch('src.seeders.seed.seed_sexo') as mock_sexo:
                with patch('src.seeders.seed.seed_grupo_sanguineo') as mock_grupo:
                    with patch('src.seeders.seed.seed_categoria') as mock_categoria:
                        with patch('src.seeders.seed.seed_deporte') as mock_deporte:
                            with patch('src.seeders.seed.seed_tipo_evento') as mock_tipo_evento:
                                with patch('src.seeders.seed.seed_metodo_pago') as mock_metodo_pago:
                                    with patch('src.seeders.seed.seed_parentesco') as mock_parentesco:
                                        with patch('src.seeders.seed.seed_ciudad_residencia') as mock_ciudad:
                                            with patch('src.seeders.seed.seed_escuela') as mock_escuela:
                                                with patch('src.seeders.seed.seed_institucion_registro') as mock_institucion:
                                                    with patch('src.seeders.seed.seed_eps') as mock_eps:
                                                        with patch('src.seeders.seed.seed_tipo_enfermedad') as mock_tipo_enfermedad:
                                                            with patch('src.seeders.seed.seed_diagnostico') as mock_diagnostico:
                                                                with patch('src.seeders.seed.seed_permisos') as mock_permisos:
                                                                    with patch('src.seeders.seed.seed_roles') as mock_roles:
                                                                        with patch('src.seeders.seed.seed_superadmin') as mock_superadmin:
                                                                            # Mock all run functions
                                                                            mock_tipo_doc.run = MagicMock()
                                                                            mock_sexo.run = MagicMock()
                                                                            mock_grupo.run = MagicMock()
                                                                            mock_categoria.run = MagicMock()
                                                                            mock_deporte.run = MagicMock()
                                                                            mock_tipo_evento.run = MagicMock()
                                                                            mock_metodo_pago.run = MagicMock()
                                                                            mock_parentesco.run = MagicMock()
                                                                            mock_ciudad.run = MagicMock()
                                                                            mock_escuela.run = MagicMock()
                                                                            mock_institucion.run = MagicMock()
                                                                            mock_eps.run = MagicMock()
                                                                            mock_tipo_enfermedad.run = MagicMock()
                                                                            mock_diagnostico.run = MagicMock()
                                                                            mock_permisos.run = MagicMock()
                                                                            mock_roles.run = MagicMock()
                                                                            mock_superadmin.run = MagicMock()
                                                                            
                                                                            # Mock inspector
                                                                            mock_inspector = MagicMock()
                                                                            mock_inspector.get_table_names.return_value = []
                                                                            
                                                                            with patch('src.seeders.seed.inspect') as mock_inspect:
                                                                                with patch('src.seeders.seed.db') as mock_db:
                                                                                    mock_inspect.return_value = mock_inspector
                                                                                    mock_db.engine = MagicMock()
                                                                                    
                                                                                    with app.app_context():
                                                                                        run_all_seeders()
                                                                                        
                                                                                        # Verify all seeders were called
                                                                                        mock_tipo_doc.run.assert_called_once()
                                                                                        mock_sexo.run.assert_called_once()
                                                                                        mock_grupo.run.assert_called_once()
                                                                                        mock_categoria.run.assert_called_once()
                                                                                        mock_deporte.run.assert_called_once()
                                                                                        mock_tipo_evento.run.assert_called_once()
                                                                                        mock_metodo_pago.run.assert_called_once()
                                                                                        mock_parentesco.run.assert_called_once()
                                                                                        mock_ciudad.run.assert_called_once()
                                                                                        mock_escuela.run.assert_called_once()
                                                                                        mock_institucion.run.assert_called_once()
                                                                                        mock_eps.run.assert_called_once()
                                                                                        mock_tipo_enfermedad.run.assert_called_once()
                                                                                        mock_diagnostico.run.assert_called_once()
                                                                                        mock_permisos.run.assert_called_once()
                                                                                        mock_roles.run.assert_called_once()
                                                                                        mock_superadmin.run.assert_called_once()
    
    def test_run_all_seeders_error_handling(self, app):
        """Test: Manejar errores durante la ejecución de seeders."""
        from src.seeders.seed import run_all_seeders
        
        mock_inspector = MagicMock()
        mock_inspector.get_table_names.return_value = []
        
        with patch('src.seeders.seed.inspect') as mock_inspect:
            with patch('src.seeders.seed.db') as mock_db:
                with patch('src.seeders.seed.seed_tipo_documento') as mock_tipo_doc:
                    mock_inspect.return_value = mock_inspector
                    mock_db.engine = MagicMock()
                    mock_db.session.rollback = MagicMock()
                    
                    mock_tipo_doc.run = MagicMock(side_effect=Exception("Seeder error"))
                    
                    with app.app_context():
                        with pytest.raises(Exception) as exc_info:
                            run_all_seeders()
                        
                        assert "Seeder error" in str(exc_info.value)
                        mock_db.session.rollback.assert_called_once()

