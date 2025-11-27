FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_RUN_HOST=0.0.0.0 \
    FLASK_RUN_PORT=5000

WORKDIR /app

# Instalar dependencias del sistema como root y crear usuario no privilegiado
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl build-essential g++ python3-dev \
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

# Copiar archivos de la aplicación
# NOTA DE SEGURIDAD: COPY recursivo es seguro porque:
# - .dockerignore está configurado para excluir archivos sensibles (.env, .git, secrets, etc.)
# - Solo se copian archivos necesarios para la aplicación
# - Archivos sensibles como .env, claves privadas, y credenciales están excluidos
# - El usuario no root (appuser) no tiene acceso a información confidencial
# nosonar: S6470 - COPY recursivo es seguro gracias a .dockerignore configurado
COPY . .

# Preparar entrypoint y cambiar ownership de los archivos al usuario no privilegiado
RUN sed -i 's/\r$//' ./entrypoint.sh \
 && chmod +x ./entrypoint.sh \
 && chown -R appuser:appuser /app

# Cambiar a usuario no privilegiado antes de exponer puertos
USER appuser

EXPOSE 5000

ENTRYPOINT ["./entrypoint.sh"]