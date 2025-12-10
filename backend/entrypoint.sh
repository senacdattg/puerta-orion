#!/bin/sh
set -e

echo "Esperando a la base de datos..."
until python - <<'PY'
import os
import pymysql

host = os.environ.get("DB_HOST", os.environ.get("MYSQL_HOST", "db"))
user = os.environ.get("DB_USER") or os.environ.get("MYSQL_USER") or os.environ.get("MYSQL_ROOT_USER") or "root"
password = os.environ.get("DB_PASSWORD") or os.environ.get("MYSQL_PASSWORD") or os.environ.get("MYSQL_ROOT_PASSWORD") or "123456"
database = os.environ.get("DB_NAME") or os.environ.get("MYSQL_DATABASE", "puerta_orion")

try:
    conn = pymysql.connect(host=host, user=user, password=password, database=database, connect_timeout=3)
except Exception as exc:
    raise SystemExit(1)
else:
    conn.close()
PY
do
  echo "La base de datos aún no está lista. Reintentando en 3s..."
  sleep 3
done

echo "Aplicando migraciones..."
if ! flask db upgrade; then
    echo "Error aplicando migraciones. Intentando continuar..."
    # En desarrollo, permitimos continuar aunque haya errores de migración
    if [ "${FLASK_ENV}" = "development" ]; then
        echo "Modo desarrollo: continuando a pesar del error de migraciones"
    else
        echo "Error crítico en migraciones. Deteniendo..."
        exit 1
    fi
fi

if [ "${RUN_SEEDERS:-true}" = "true" ]; then
  echo "Ejecutando seeders..."
  python run_seeders.py
fi

echo "Arrancando el servidor..."
PORT=${PORT:-5000}
if [ "${FLASK_ENV}" = "development" ]; then
  exec flask run --host=0.0.0.0 --port=${PORT} --reload
else
  exec gunicorn aplicacion:app --bind 0.0.0.0:${PORT}
fi
