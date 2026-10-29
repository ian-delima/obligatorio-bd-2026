from db import conectar


def listar_jugadores():
    conexion = conectar("administrador")
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT ci, nombre, apellido, email, fecha_nacimiento, id_facultad, tipo FROM jugador"
        )
        jugadores = cursor.fetchall()
        return jugadores
    finally:
        cursor.close()
        conexion.close()

def crear_jugador(ci, nombre, apellido, email, fecha_nacimiento, id_facultad, tipo):
    conexion = conectar("administrador")
    cursor = conexion.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO jugador
            (ci, nombre, apellido, email, fecha_nacimiento, id_facultad, tipo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (ci, nombre, apellido, email, fecha_nacimiento, id_facultad, tipo)
        )

        conexion.commit()
        return True

    finally:
        cursor.close()
        conexion.close()

def modificar_jugador(ci, nombre, apellido, email, fecha_nacimiento, id_facultad, tipo):
    conexion = conectar("administrador")
    cursor = conexion.cursor()

    try:
        cursor.execute(
            """
            UPDATE jugador
            SET nombre = %s,
                apellido = %s,
                email = %s,
                fecha_nacimiento = %s,
                id_facultad = %s,
                tipo = %s
            WHERE ci = %s
            """,
            (nombre, apellido, email, fecha_nacimiento, id_facultad, tipo, ci)
        )

        conexion.commit()
        return cursor.rowcount

    finally:
        cursor.close()
        conexion.close()

def eliminar_jugador(ci):
    conexion = conectar("administrador")
    cursor = conexion.cursor()

    try:
        cursor.execute(
            "DELETE FROM jugador WHERE ci = %s",
            (ci,)
        )

        filas = cursor.rowcount
        conexion.commit()
        return filas

    finally:
        cursor.close()
        conexion.close()

def existe_jugador(ci):
    conexion = conectar("administrador")
    cursor = conexion.cursor()

    try:
        cursor.execute(
            "SELECT 1 FROM jugador WHERE ci = %s",
            (ci,)
        )
        return cursor.fetchone() is not None

    finally:
        cursor.close()
        conexion.close()