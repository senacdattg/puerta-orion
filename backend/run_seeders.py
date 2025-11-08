"""
Script auxiliar para ejecutar los seeders desde la raíz del proyecto.

Uso:
    python run_seeders.py
"""

import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # ruta al directorio backend
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))  # raíz del repo (si existe)

for path in (CURRENT_DIR, PARENT_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

from src.seeders.seed import run_all_seeders

if __name__ == '__main__':
    run_all_seeders()


