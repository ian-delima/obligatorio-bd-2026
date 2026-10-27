import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def conectar(rol):
    if rol == "administrador":
        usuario = os.getenv("DB_ADMIN_USER")
        contrasena = os.getenv("DB_ADMIN_PASS")
    else:
        usuario = os.getenv("DB_PLANILLERO_USER")
        contrasena = os.getenv("DB_PLANILLERO_PASS")

    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        database=os.getenv("DB_NAME"),
        user=usuario,
        password=contrasena,
    )