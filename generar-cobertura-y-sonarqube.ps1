# ==================================================
# SCRIPT PARA GENERAR COBERTURA Y EJECUTAR SONARQUBE
# ==================================================
# Este script:
# 1. Genera los reportes de cobertura del backend (coverage.xml)
# 2. Genera los reportes de cobertura del frontend (lcov.info)
# 3. Ejecuta SonarQube scanner con los reportes disponibles
# ==================================================

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "GENERANDO REPORTES DE COBERTURA" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Función para verificar si un comando existe
function Test-Command {
    param($command)
    $null = Get-Command $command -ErrorAction SilentlyContinue
    return $?
}

# ==================================================
# 1. GENERAR COBERTURA DEL BACKEND
# ==================================================
Write-Host "`n[1/3] Generando cobertura del Backend (Python)..." -ForegroundColor Yellow

Push-Location backend

# Verificar que pytest-cov está instalado
if (-not (Test-Command "python")) {
    Write-Host "❌ ERROR: Python no está instalado o no está en el PATH" -ForegroundColor Red
    Pop-Location
    exit 1
}

# Ejecutar tests con cobertura
Write-Host "Ejecutando tests del backend con cobertura..." -ForegroundColor Gray
python -m pytest tests/ --cov=src --cov-report=xml --cov-report=term --tb=short -q

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  ADVERTENCIA: Algunos tests fallaron, pero continuando..." -ForegroundColor Yellow
}

# Verificar que se generó el archivo
if (Test-Path "coverage.xml") {
    $fileSize = (Get-Item "coverage.xml").Length
    Write-Host "✅ Backend coverage.xml generado correctamente ($([math]::Round($fileSize/1KB, 2)) KB)" -ForegroundColor Green
} else {
    Write-Host "❌ ERROR: No se pudo generar backend/coverage.xml" -ForegroundColor Red
    Pop-Location
    exit 1
}

Pop-Location

# ==================================================
# 2. GENERAR COBERTURA DEL FRONTEND
# ==================================================
Write-Host "`n[2/3] Generando cobertura del Frontend (JavaScript/Vue)..." -ForegroundColor Yellow

Push-Location frontend

# Verificar que node está instalado
if (-not (Test-Command "node")) {
    Write-Host "⚠️  ADVERTENCIA: Node.js no está instalado o no está en el PATH" -ForegroundColor Yellow
    Write-Host "   Omitiendo cobertura del frontend..." -ForegroundColor Yellow
    Pop-Location
} else {
    # Verificar que existe package.json
    if (-not (Test-Path "package.json")) {
        Write-Host "⚠️  ADVERTENCIA: No se encontró package.json en frontend/" -ForegroundColor Yellow
        Write-Host "   Omitiendo cobertura del frontend..." -ForegroundColor Yellow
        Pop-Location
    } else {
        # Verificar que node_modules existe, si no, instalar dependencias
        if (-not (Test-Path "node_modules")) {
            Write-Host "Instalando dependencias de npm..." -ForegroundColor Gray
            if (Test-Command "npm") {
                npm install
                if ($LASTEXITCODE -ne 0) {
                    Write-Host "⚠️  ADVERTENCIA: Error al instalar dependencias" -ForegroundColor Yellow
                }
            } elseif (Test-Command "yarn") {
                yarn install
                if ($LASTEXITCODE -ne 0) {
                    Write-Host "⚠️  ADVERTENCIA: Error al instalar dependencias" -ForegroundColor Yellow
                }
            } else {
                Write-Host "⚠️  ADVERTENCIA: npm o yarn no están disponibles" -ForegroundColor Yellow
                Write-Host "   Omitiendo cobertura del frontend..." -ForegroundColor Yellow
                Pop-Location
                # Continuar con el siguiente paso (SonarQube)
            }
        }
        
        # Crear directorio de cobertura si no existe
        if (-not (Test-Path "coverage")) {
            New-Item -ItemType Directory -Path "coverage" | Out-Null
        }
        
        # Intentar ejecutar tests con cobertura usando npm run
        Write-Host "Ejecutando tests del frontend con cobertura..." -ForegroundColor Gray
        $coverageGenerated = $false
        
        # Opción 1: Usar npm run test:coverage
        if (Test-Command "npm") {
            try {
                npm run test:coverage 2>&1 | Out-Null
                if ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq $null) {
                    if (Test-Path "coverage/lcov.info") {
                        $coverageGenerated = $true
                    }
                }
            } catch {
                Write-Host "   Error con npm run, intentando con npx..." -ForegroundColor Gray
            }
        }
        
        # Opción 2: Usar npx vitest directamente si npm run falló
        if (-not $coverageGenerated) {
            if (Test-Command "npx") {
                Write-Host "   Ejecutando vitest con npx..." -ForegroundColor Gray
                try {
                    npx vitest run --coverage 2>&1 | Out-Null
                    if (Test-Path "coverage/lcov.info") {
                        $coverageGenerated = $true
                    }
                } catch {
                    Write-Host "   Error con npx vitest..." -ForegroundColor Gray
                }
            }
        }
        
        # Verificar que se generó el archivo
        if (Test-Path "coverage/lcov.info") {
            $fileSize = (Get-Item "coverage/lcov.info").Length
            Write-Host "✅ Frontend lcov.info generado correctamente ($([math]::Round($fileSize/1KB, 2)) KB)" -ForegroundColor Green
        } else {
            Write-Host "⚠️  ADVERTENCIA: No se pudo generar frontend/coverage/lcov.info" -ForegroundColor Yellow
            Write-Host "   Continuando sin cobertura del frontend..." -ForegroundColor Yellow
            Write-Host "   Para generar manualmente, ejecuta: cd frontend && npm run test:coverage" -ForegroundColor Gray
        }
        
        Pop-Location
    }
}

# ==================================================
# 3. EJECUTAR SONARQUBE SCANNER
# ==================================================
Write-Host "`n[3/3] Ejecutando SonarQube Scanner..." -ForegroundColor Yellow

# Verificar que sonar-scanner existe
if (-not (Test-Command "sonar-scanner")) {
    Write-Host "❌ ERROR: sonar-scanner no está instalado o no está en el PATH" -ForegroundColor Red
    Write-Host "   Instala sonar-scanner o usa Docker:" -ForegroundColor Yellow
    Write-Host "   docker run --rm -v `"${PWD}:/usr/src`" -w /usr/src sonarsource/sonar-scanner-cli -Dproject.settings=sonar-project.properties" -ForegroundColor Gray
    exit 1
}

# Verificar que existe sonar-project.properties
if (-not (Test-Path "sonar-project.properties")) {
    Write-Host "❌ ERROR: No se encontró sonar-project.properties en la raíz del proyecto" -ForegroundColor Red
    exit 1
}

# Ejecutar sonar-scanner
Write-Host "Iniciando análisis con SonarQube..." -ForegroundColor Gray
# SonarQube Scanner busca automáticamente sonar-project.properties en el directorio actual
# Si el archivo está en otra ubicación, usar: sonar-scanner -Dproject.settings=<ruta>
sonar-scanner

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ SonarQube Scanner ejecutado correctamente" -ForegroundColor Green
    Write-Host "   Revisa los resultados en: http://sonarqube.dataguaviare.com.co" -ForegroundColor Cyan
} else {
    Write-Host "`n❌ ERROR: SonarQube Scanner falló" -ForegroundColor Red
    exit 1
}

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "PROCESO COMPLETADO" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

