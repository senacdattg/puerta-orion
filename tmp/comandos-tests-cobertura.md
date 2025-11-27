# Comandos Exactos - Tests y Cobertura
## Proyecto Puerta de Orión

---

## BACKEND (Flask/Python)

### 1. Instalar Dependencias de Test

```bash
cd backend
pip install -r requirements.txt
```

**Verificar instalación:**
```bash
pip list | grep pytest
```

Debe mostrar:
- pytest==8.3.4
- pytest-cov==6.0.0
- pytest-flask==1.3.0
- pytest-mock==3.14.0

### 2. Ejecutar Tests

**Todos los tests:**
```bash
cd backend
pytest
```

**Tests con salida detallada:**
```bash
pytest -v
```

**Tests por categoría:**
```bash
# Solo tests unitarios
pytest -m unit

# Solo tests de integración
pytest -m integration

# Solo tests de rutas
pytest -m routes

# Solo tests de autenticación
pytest -m auth
```

**Tests específicos:**
```bash
# Un archivo específico
pytest tests/integration/routes/test_auth_routes.py

# Una función específica
pytest tests/integration/routes/test_auth_routes.py::test_login_success
```

**Tests con salida corta:**
```bash
pytest --tb=short
```

**Tests sin mostrar output:**
```bash
pytest -q
```

### 3. Generar coverage.xml

**Generar cobertura (automático con pytest.ini):**
```bash
cd backend
pytest --cov=src --cov-report=xml
```

**Generar cobertura con reporte HTML:**
```bash
pytest --cov=src --cov-report=html --cov-report=xml
```

**Verificar que se generó coverage.xml:**
```bash
ls -la backend/coverage.xml
```

**Ver cobertura en navegador (HTML):**
```bash
# Abrir en navegador
start backend/htmlcov/index.html  # Windows
open backend/htmlcov/index.html   # macOS
xdg-open backend/htmlcov/index.html  # Linux
```

### 4. Verificar Cobertura

**Ver porcentaje de cobertura:**
```bash
pytest --cov=src --cov-report=term-missing
```

**Verificar que coverage.xml existe y tiene contenido:**
```bash
# Windows PowerShell
Test-Path backend/coverage.xml
Get-Content backend/coverage.xml | Select-Object -First 10

# Linux/macOS
test -f backend/coverage.xml && echo "Existe" || echo "No existe"
head -n 10 backend/coverage.xml
```

**Ver resumen de cobertura:**
```bash
pytest --cov=src --cov-report=term
```

### 5. Enviar Resultados a SonarQube

**Opción 1: Usando sonar-scanner (recomendado)**

```bash
# Desde la raíz del proyecto
sonar-scanner -Dproject.settings=sonar-project.properties
```

**Opción 2: Usando Docker (si SonarQube está en Docker)**

```bash
docker run --rm \
  -v "%cd%":/usr/src \
  -w /usr/src \
  sonarsource/sonar-scanner-cli \
  -Dproject.settings=sonar-project.properties
```

**Opción 3: Verificar configuración antes de enviar**

```bash
# Verificar que sonar-project.properties tiene las rutas correctas
cat sonar-project.properties | grep coverage
```

Debe mostrar:
```
sonar.python.coverage.reportPaths=backend/coverage.xml
```

---

## VERIFICACIÓN FINAL

### Verificar Archivos de Cobertura

**Backend:**
```bash
# Verificar que existe
test -f backend/coverage.xml && echo "✅ Backend coverage.xml existe" || echo "❌ Backend coverage.xml NO existe"

# Ver tamaño (debe ser > 0)
ls -lh backend/coverage.xml
```

### Verificar Configuración SonarQube

```bash
# Verificar rutas de cobertura
grep -E "coverage" sonar-project.properties
```

Debe mostrar:
```
sonar.python.coverage.reportPaths=backend/coverage.xml
```

---

## SOLUCIÓN DE PROBLEMAS

### Backend: coverage.xml no se genera

```bash
# Verificar que pytest-cov está instalado
pip show pytest-cov

# Ejecutar con flags explícitos
pytest --cov=src --cov-report=xml --cov-report=term

# Verificar permisos de escritura
ls -la backend/ | grep coverage
```

### SonarQube: No lee cobertura

```bash
# Verificar que las rutas en sonar-project.properties son correctas
cat sonar-project.properties | grep -E "coverage|lcov"

# Verificar que el archivo existe antes de ejecutar sonar-scanner
test -f backend/coverage.xml && echo "✅ Archivo OK" || echo "❌ Falta archivo"

# Ver logs de sonar-scanner
sonar-scanner -Dproject.settings=sonar-project.properties -X
```

---

## NOTAS IMPORTANTES

1. **Backend**: `coverage.xml` se genera automáticamente con `pytest.ini` configurado
2. **SonarQube**: Requiere que el archivo de cobertura exista antes de ejecutar `sonar-scanner`
3. **Rutas**: Todas las rutas en `sonar-project.properties` son relativas a la raíz del proyecto

