# Solución para Timeouts de Pip en Docker

## Problema

Durante el build de Docker, pip no puede descargar paquetes de PyPI debido a timeouts de red:
```
ReadTimeoutError: HTTPSConnectionPool(host='files.pythonhosted.org', port=443): Read timed out.
```

## Soluciones Aplicadas

### 1. Configuración de Pip con Timeouts Extendidos

Se ha creado `backend/pip.conf` con configuración que aumenta:
- **Timeout**: 300 segundos (5 minutos) por paquete
- **Reintentos**: 10 intentos antes de fallar
- **Trusted hosts**: PyPI y files.pythonhosted.org

### 2. Dockerfile Optimizado

El Dockerfile ahora:
- Configura pip antes de instalar dependencias
- Usa timeouts extendidos automáticamente
- Actualiza pip, setuptools y wheel primero

## Si el Problema Persiste

### Opción 1: Usar un Mirror de PyPI

Si estás en una región con problemas de conectividad a PyPI, puedes usar un mirror:

**Modificar `backend/pip.conf`:**
```ini
[global]
timeout = 300
retries = 10
index-url = https://pypi.douban.com/simple/  # Mirror en China
# O
# index-url = https://pypi.tuna.tsinghua.edu.cn/simple/  # Mirror de Tsinghua
trusted-host = pypi.douban.com
               files.pythonhosted.org
```

### Opción 2: Usar Docker BuildKit con Caché

Ejecutar con BuildKit para mejor manejo de caché:
```bash
DOCKER_BUILDKIT=1 docker compose build --progress=plain
```

### Opción 3: Construir sin Caché (para debugging)

Si hay problemas de caché corrupta:
```bash
docker compose build --no-cache backend
```

### Opción 4: Instalar Dependencias en el Host Primero

Si Docker sigue fallando, instalar dependencias localmente:
```bash
cd backend
pip install -r requirements.txt
```

Luego usar un volumen en Docker para usar las dependencias instaladas.

### Opción 5: Usar un Proxy

Si estás detrás de un proxy corporativo, configurar Docker:

**Crear `~/.docker/config.json`:**
```json
{
  "proxies": {
    "default": {
      "httpProxy": "http://proxy.example.com:8080",
      "httpsProxy": "http://proxy.example.com:8080",
      "noProxy": "localhost,127.0.0.1"
    }
  }
}
```

**O en el Dockerfile:**
```dockerfile
ENV http_proxy=http://proxy.example.com:8080
ENV https_proxy=http://proxy.example.com:8080
ENV no_proxy=localhost,127.0.0.1
```

### Opción 6: Verificar Conectividad

Verificar que puedes acceder a PyPI desde tu máquina:
```bash
curl -I https://pypi.org/simple/
curl -I https://files.pythonhosted.org/
```

Si estos comandos fallan, el problema es de conectividad de red.

### Opción 7: Usar un VPN o Cambiar de Red

Si estás en una red con restricciones:
- Conectar a una red diferente (móvil, WiFi, etc.)
- Usar un VPN
- Verificar firewall/proxy corporativo

## Verificación

Después de aplicar las soluciones, verificar el build:
```bash
docker compose build backend
```

Si el build es exitoso, continuar con:
```bash
docker compose up
```

## Archivos Modificados

1. **backend/Dockerfile**: Actualizado con configuración de pip
2. **backend/pip.conf**: Nuevo archivo de configuración de pip

## Notas

- Los timeouts extendidos pueden hacer que el build tarde más tiempo
- Si la conexión es muy lenta, considerar usar un mirror de PyPI
- El problema puede ser temporal debido a problemas de red de PyPI
- Verificar logs de Docker para identificar qué paquete está causando el timeout



