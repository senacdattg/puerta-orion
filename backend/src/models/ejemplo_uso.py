"""
Ejemplo de uso de los modelos ORM.
Muestra cómo utilizar los modelos para operaciones CRUD básicas.
"""

from flask import Flask
from . import (
    init_database, create_tables, db,
    Persona, Usuario, Rol, Permiso,
    TipoDocumento, CiudadResidencia, GrupoSanguineo,
    MetodoPago, Categoria, Cuota, Mensualidad
)

def ejemplo_uso_modelos():
    """
    Ejemplo de cómo usar los modelos ORM para operaciones básicas.
    """
    
    # Inicializar la aplicación Flask
    app = Flask(__name__)
    
    # Inicializar la base de datos
    init_database(app)
    
    with app.app_context():
        # Crear todas las tablas
        create_tables(app)
        
        # Ejemplo 1: Crear un tipo de documento
        tipo_doc = TipoDocumento(nombre_documento="Cédula de Ciudadanía")
        db.session.add(tipo_doc)
        db.session.commit()
        
        # Ejemplo 2: Crear una ciudad
        ciudad = CiudadResidencia(nombre_ciudad="Bogotá")
        db.session.add(ciudad)
        db.session.commit()
        
        # Ejemplo 3: Crear un grupo sanguíneo
        grupo_sangre = GrupoSanguineo(tipo_sangre="O+")
        db.session.add(grupo_sangre)
        db.session.commit()
        
        # Ejemplo 4: Crear una persona
        persona = Persona(
            doc_identificacion="12345678",
            primer_nombre="Juan",
            primer_apellido="Pérez",
            correo_electronico="juan.perez@email.com",
            telefono="3001234567",
            fecha_nacimiento="1990-01-15",
            id_documento=tipo_doc.id_documento,
            id_ciudad=ciudad.id_ciudad,
            id_tipo_sangre=grupo_sangre.id_tipo_sangre,
            # ... otros campos requeridos
        )
        db.session.add(persona)
        db.session.commit()
        
        # Ejemplo 5: Crear un rol
        rol_admin = Rol(nombre_rol="Administrador", descripcion="Rol de administrador del sistema")
        db.session.add(rol_admin)
        db.session.commit()
        
        # Ejemplo 6: Crear un usuario
        usuario = Usuario(
            id_persona=persona.id_persona,
            usuario="jperez",
            password="password123",
            estado=True
        )
        db.session.add(usuario)
        db.session.commit()
        
        # Ejemplo 7: Asignar rol al usuario
        usuario.roles.append(rol_admin)
        db.session.commit()
        
        # Ejemplo 8: Consultar datos
        personas = Persona.query.all()
        print(f"Total de personas: {len(personas)}")
        
        # Ejemplo 9: Consultar con filtros
        persona_especifica = Persona.query.filter_by(doc_identificacion="12345678").first()
        if persona_especifica:
            print(f"Persona encontrada: {persona_especifica.nombre_completo}")
            print(f"Edad: {persona_especifica.edad}")
        
        # Ejemplo 10: Actualizar datos
        if persona_especifica:
            persona_especifica.telefono = "3009876543"
            db.session.commit()
        
        # Ejemplo 11: Eliminar datos
        # db.session.delete(persona_especifica)
        # db.session.commit()

if __name__ == "__main__":
    ejemplo_uso_modelos()



