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
flask db upgrade

if [ "${RUN_SEEDERS:-true}" = "true" ]; then
  echo "Ejecutando seeders..."
  python run_seeders.py
fi

echo "Arrancando el servidor..."
if [ "${FLASK_ENV}" = "development" ]; then
  exec flask run --host=0.0.0.0 --port=5000
else
  exec gunicorn aplicacion:app --bind 0.0.0.0:5000
fi