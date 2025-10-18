-"""Script temporal para verificar catálogos."""
from src.models.base import db
from src.models.catalogos.tipo_documento import TipoDocumento
from src.models.categorias.sexo import Sexo
from app import app

with app.app_context():
    tipos_doc = TipoDocumento.query.all()
    sexos = Sexo.query.all()
    
    print("=== TIPOS DE DOCUMENTO ===")
    for tipo in tipos_doc:
        print(f"ID: {tipo.id_documento}, Nombre: {tipo.nombre_documento}")
    
    print("\n=== SEXOS ===")
    for sexo in sexos:
        print(f"ID: {sexo.id_sexo}, Nombre: {sexo.nombre}")



