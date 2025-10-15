"""
Script auxiliar para ejecutar los seeders desde la raíz del proyecto.

Uso:
    python run_seeders.py
"""

from src.seeders.seed import run_all_seeders

if __name__ == '__main__':
    run_all_seeders()


