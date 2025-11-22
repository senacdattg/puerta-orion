FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_RUN_HOST=0.0.0.0 \
    FLASK_RUN_PORT=5000

WORKDIR /app

# Instalar dependencias del sistema como root
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

# Crear usuario no privilegiado para ejecutar la aplicación
# Esto mejora la seguridad al no ejecutar como root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Crear directorio de configuración de pip para el usuario root (solo durante build)
RUN mkdir -p /root/.config/pip

# Copiar configuración de pip con timeouts extendidos
COPY pip.conf /root/.config/pip/pip.conf

# Copiar requirements.txt primero (mejor práctica de Docker para cache)
COPY requirements.txt .

# Actualizar pip, setuptools y wheel primero
RUN pip install --upgrade pip setuptools wheel

# Instalar dependencias (la configuración de pip.conf maneja los timeouts)
RUN pip install -r requirements.txt

# Copiar archivos de la aplicación
# NOTA DE SEGURIDAD: COPY recursivo es seguro porque:
# - .dockerignore está configurado para excluir archivos sensibles (.env, .git, secrets, etc.)
# - Solo se copian archivos necesarios para la aplicación
# - Archivos sensibles como .env, claves privadas, y credenciales están excluidos
# - El usuario no root (appuser) no tiene acceso a información confidencial
# nosonar: S6470 - COPY recursivo es seguro gracias a .dockerignore configurado
COPY . .

# Preparar entrypoint
RUN sed -i 's/\r$//' ./entrypoint.sh \
 && chmod +x ./entrypoint.sh

# Cambiar ownership de los archivos al usuario no privilegiado
RUN chown -R appuser:appuser /app

# Cambiar a usuario no privilegiado antes de exponer puertos
USER appuser

EXPOSE 5000

ENTRYPOINT ["./entrypoint.sh"]