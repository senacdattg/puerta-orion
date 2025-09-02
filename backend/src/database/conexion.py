import os
import mysql.connector
from mysql.connector import Error
import time

class ConexionDB:
    """
    Clase para gestionar la conexión a la base de datos MySQL.

    Uso:
        db = ConexionDB()
        conexion = db.conectar()
        cursor = db.obtener_cursor()
        # ... operaciones ...
        db.cerrar()

    Variables de entorno requeridas:
        - DB_HOST: Host de la base de datos (por defecto 'localhost')
        - DB_USER: Usuario de la base de datos (por defecto 'root')
        - DB_PASSWORD: Contraseña de la base de datos (por defecto '')
        - DB_NAME: Nombre de la base de datos (por defecto 'mi_base')
    """

    def __init__(self):
        """
        Inicializa los parámetros de conexión utilizando variables de entorno.
        """
        self.host = os.environ.get('DB_HOST', 'localhost')
        self.user = os.environ.get('DB_USER', 'root')
        self.password = os.environ.get('DB_PASSWORD', '')
        self.database = os.environ.get('DB_NAME', 'mi_base')
        self.conexion = None

    def conectar(self):
        """
        Establece la conexión con la base de datos MySQL.

        Returns:
            conexion (mysql.connector.connection.MySQLConnection): Objeto de conexión si es exitosa, None si falla.
        """
        try:
            self.conexion = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return self.conexion
        except Error as e:
            print(f"Error al conectar a la base de datos: {e}")
            print("error/conexion-bd")
            return None

    def cerrar(self):
        """
        Cierra la conexión activa con la base de datos.
        """
        if self.conexion and self.conexion.is_connected():
            self.conexion.close()

    def obtener_cursor(self):
        """
        Devuelve un cursor de la base de datos si la conexión está activa.

        Returns:
            cursor (mysql.connector.cursor.MySQLCursorDict): Cursor para ejecutar consultas, None si no hay conexión.

        Nota:
            En proyectos grandes, centralizar la obtención del cursor ayuda a mantener el código limpio,
            facilita el manejo de errores y promueve la reutilización, siguiendo los principios SRP y DRY.
        """
        if not self.conexion or not self.conexion.is_connected():
            print("No hay conexión activa.")
            return None
        return self.conexion.cursor(dictionary=True)
