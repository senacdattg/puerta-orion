# 🧪 Guía para Ejecutar Tests

Esta guía te mostrará cómo ejecutar todos los tests del backend y frontend del proyecto Puerta Orion.

## 📋 Tabla de Contenidos

- [Tests del Backend](#tests-del-backend)
- [Tests del Frontend](#tests-del-frontend)
- [Ejecutar Tests con Cobertura](#ejecutar-tests-con-cobertura)
- [Comandos Rápidos](#comandos-rápidos)

---

## 🔧 Tests del Backend

### Requisitos Previos

Asegúrate de estar en el directorio del backend:

```powershell
cd backend
```

### Ejecutar Todos los Tests del Backend

```powershell
# Opción 1: Comando básico (desde el directorio backend) - RECOMENDADO
python -m pytest

# Opción 2: Con más detalle (verbose)
python -m pytest -v

# Opción 3: Con aún más detalle
python -m pytest -vv

# Nota: Si tienes problemas con rutas del venv, usa siempre "python -m pytest"
# en lugar de solo "pytest"
```

### Ejecutar Tests por Categoría

```powershell
# Solo tests unitarios
python -m pytest tests/unit/

# Solo tests de integración
python -m pytest tests/integration/

# Solo tests de servicios
python -m pytest tests/unit/services/

# Solo tests de rutas
python -m pytest tests/integration/routes/
```

### Ejecutar Tests por Marcadores

```powershell
# Tests de autenticación
python -m pytest -m auth

# Tests de eventos
python -m pytest -m eventos

# Tests de deportistas
python -m pytest -m deportistas

# Tests de usuarios
python -m pytest -m usuarios

# Tests de mensualidades
python -m pytest -m mensualidades

# Excluir tests lentos
python -m pytest -m "not slow"
```

### Ejecutar un Archivo Específico

```powershell
# Archivo específico
python -m pytest tests/unit/services/auth/test_auth_service.py

# Una clase específica
python -m pytest tests/unit/services/auth/test_auth_service.py::TestAuthService

# Un test específico
python -m pytest tests/unit/services/auth/test_auth_service.py::TestAuthService::test_login_success
```

### Ejecutar Tests con Cobertura (Backend)

```powershell
# Cobertura en terminal
python -m pytest --cov=src --cov-report=term-missing

# Cobertura con reporte HTML (se genera en htmlcov/index.html)
python -m pytest --cov=src --cov-report=html

# Cobertura con ambos reportes
python -m pytest --cov=src --cov-report=term-missing --cov-report=html
```

---

## 🎨 Tests del Frontend

### Requisitos Previos

Asegúrate de estar en el directorio del frontend:

```powershell
cd frontend
```

### Ejecutar Todos los Tests del Frontend

```powershell
# Opción 1: Comando básico (desde el directorio frontend)
npm test

# Opción 2: Ejecutar una sola vez
npm test -- --run

# Opción 3: Modo watch (se ejecuta automáticamente al cambiar archivos)
npm run test:watch

# Opción 4: Interfaz gráfica (UI)
npm run test:ui
```

### Ejecutar Tests por Categoría (Frontend)

```powershell
# Solo tests de servicios
npm test -- --run tests/unit/services/

# Solo tests de composables
npm test -- --run tests/unit/composables/

# Solo tests de componentes
npm test -- --run tests/unit/components/

# Solo tests de stores
npm test -- --run tests/unit/stores/

# Solo tests de views
npm test -- --run tests/unit/views/
```

### Ejecutar un Archivo Específico (Frontend)

```powershell
# Un archivo específico
npm test -- --run tests/unit/composables/useFetch.test.js

# Múltiples archivos
npm test -- --run tests/unit/services/authService.test.js tests/unit/services/usuarioService.test.js
```

### Ejecutar Tests con Cobertura (Frontend)

```powershell
# Cobertura completa
npm run test:coverage

# Esto genera:
# - Reporte en terminal
# - Reporte HTML en frontend/coverage/index.html
# - Reporte XML en frontend/coverage/test-results.xml
```

---

## 📊 Ejecutar Tests con Cobertura

### Backend con Cobertura

```powershell
cd backend
python -m pytest --cov=src --cov-report=html --cov-report=term-missing
```

El reporte HTML se generará en: `backend/htmlcov/index.html`

### Frontend con Cobertura

```powershell
cd frontend
npm run test:coverage
```

El reporte HTML se generará en: `frontend/coverage/index.html`

---

## ⚡ Comandos Rápidos

### Desde la Raíz del Proyecto

#### Backend (desde raíz)

```powershell
# Ejecutar todos los tests del backend
cd backend && python -m pytest && cd ..

# O en una sola línea
cd backend; python -m pytest
```

#### Frontend (desde raíz)

```powershell
# Ejecutar todos los tests del frontend
cd frontend && npm test -- --run && cd ..

# O en una sola línea (si npm está disponible desde raíz)
cd frontend; npm test -- --run
```

### Scripts de Ejecución Rápida

Puedes crear scripts `.bat` o `.ps1` para Windows:

#### `run_backend_tests.bat`

```batch
@echo off
echo Ejecutando tests del backend...
cd backend
pytest -v
cd ..
pause
```

#### `run_frontend_tests.bat`

```batch
@echo off
echo Ejecutando tests del frontend...
cd frontend
npm test -- --run
cd ..
pause
```

#### `run_all_tests.bat`

```batch
@echo off
echo ============================================
echo Ejecutando TODOS los tests
echo ============================================
echo.
echo --- Backend Tests ---
cd backend
pytest -v
cd ..
echo.
echo --- Frontend Tests ---
cd frontend
npm test -- --run
cd ..
echo.
echo ============================================
echo Tests completados
echo ============================================
pause
```

---

## 📝 Notas Importantes

### Backend
- Los tests del backend usan **pytest**
- La configuración está en `backend/pytest.ini`
- Los tests se ejecutan con SQLite en memoria
- Los marcadores permiten filtrar tests por categoría

### Frontend
- Los tests del frontend usan **Vitest**
- La configuración está en `frontend/vitest.config.js`
- Los tests usan Vue Test Utils para componentes
- Los tests se ejecutan con jsdom para simular el navegador

### Estado Actual
- **Backend**: ✅ Tests configurados y funcionando
- **Frontend**: ✅ Tests configurados y funcionando (360/363 pasando)

---

## 🐛 Troubleshooting

### Backend

Si encuentras problemas:

```powershell
# Verificar que pytest esté instalado
pip list | findstr pytest

# Instalar dependencias si falta
pip install -r requirements.txt

# Ejecutar con más información de debug
python -m pytest -vv --tb=long

# Si tienes problemas con rutas del venv, usar siempre:
python -m pytest
# en lugar de solo:
# pytest
```

### Frontend

Si encuentras problemas:

```powershell
# Verificar que node_modules esté instalado
cd frontend
npm install

# Limpiar cache y reinstalar
rm -r node_modules
npm install

# Ejecutar con más información
npm test -- --run --reporter=verbose
```

---

## 📚 Referencias

- [Documentación de Pytest](https://docs.pytest.org/)
- [Documentación de Vitest](https://vitest.dev/)
- [Documentación de Vue Test Utils](https://test-utils.vuejs.org/)

