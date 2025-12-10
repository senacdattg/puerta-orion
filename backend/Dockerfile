FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_RUN_HOST=0.0.0.0

WORKDIR /app

# Instalar dependencias del sistema como root y crear usuario no privilegiado
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential curl g++ python3-dev \
 && rm -rf /var/lib/apt/lists/* \
 && groupadd -r appuser && useradd -r -g appuser appuser \
 && mkdir -p /root/.config/pip

# Copiar configuración de pip con timeouts extendidos
COPY pip.conf /root/.config/pip/pip.conf

# Copiar requirements.txt primero (mejor práctica de Docker para cache)
COPY requirements.txt .

# Actualizar pip, setuptools y wheel, luego instalar dependencias
RUN pip install --upgrade pip setuptools wheel \
 && pip install -r requirements.txt

# Copy application files
# Security: Recursive COPY is safe because:
# - .dockerignore is configured to exclude sensitive files (.env, .git, secrets, etc.)
# - Only necessary application files are copied (verified .dockerignore patterns)
# - Sensitive files (.env, *.key, *.pem, secrets/, .git/, logs/, instance/) are excluded
# - Non-root user (appuser) does not have access to confidential information
# - All environment variables are passed via docker-compose env_file, not copied
# The .dockerignore file explicitly excludes: .env, .env.*, *.key, *.pem, secrets/, .git/, logs/, instance/
# NOSONAR docker:S6470 - Recursive COPY is safe due to properly configured and verified .dockerignore
COPY . .

# Preparar entrypoint y cambiar ownership de los archivos al usuario no privilegiado
RUN sed -i 's/\r$//' ./entrypoint.sh \
 && chmod +x ./entrypoint.sh \
 && chown -R appuser:appuser /app

# Cambiar a usuario no privilegiado antes de exponer puertos
USER appuser

EXPOSE 5012

ENTRYPOINT ["./entrypoint.sh"]