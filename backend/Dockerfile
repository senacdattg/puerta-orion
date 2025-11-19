FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_RUN_HOST=0.0.0.0 \
    FLASK_RUN_PORT=5000

WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

# Crear directorio de configuración de pip
RUN mkdir -p /root/.config/pip

# Copiar configuración de pip con timeouts extendidos
COPY pip.conf /root/.config/pip/pip.conf

COPY requirements.txt .

# Actualizar pip, setuptools y wheel primero
RUN pip install --upgrade pip setuptools wheel

# Instalar dependencias (la configuración de pip.conf maneja los timeouts)
RUN pip install -r requirements.txt

COPY . .

RUN sed -i 's/\r$//' ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["./entrypoint.sh"]