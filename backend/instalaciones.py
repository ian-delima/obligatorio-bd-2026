
from functools import wraps

from flask import Blueprint, request, session, redirect, url_for
from mysql.connector import IntegrityError, DataError

from db import conectar


instalaciones_bp = Blueprint("instalaciones", __name__)


def solo_admin(funcion):
    @wraps(funcion)
    def envoltura(*args, **kwargs):
        if "rol" not in session:
            return redirect(url_for("login"))

        if session["rol"] != "administrador":
            return {"error": "No tenés permiso"}, 403

        return funcion(*args, **kwargs)

    return envoltura


def consultar(sql, parametros=()):
    conexion = conectar("administrador")
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute(sql, parametros)
        return cursor.fetchall()
    finally:
        cursor.close()
        conexion.close()


def ejecutar(sql, parametros=()):
    conexion = conectar("administrador")
    cursor = conexion.cursor()

    try:
        cursor.execute(sql, parametros)
        filas = cursor.rowcount
        nuevo_id = cursor.lastrowid
        conexion.commit()
        return filas, nuevo_id
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def validar_texto(datos, campo, maximo):
    valor = datos.get(campo)

    if not isinstance(valor, str) or not valor.strip():
        return f"El campo {campo} es obligatorio"

    if len(valor) > maximo:
        return f"El campo {campo} supera los {maximo} caracteres"

    return None


def validar_complejo(datos):
    if not isinstance(datos, dict):
        return "Debés enviar un objeto JSON"

    campos = {
        "nombre": 100,
        "direccion": 150,
        "departamento": 30
    }

    for campo, maximo in campos.items():
        error = validar_texto(datos, campo, maximo)
        if error:
            return error

    return None


def validar_cancha(datos):
    if not isinstance(datos, dict):
        return "Debés enviar un objeto JSON"

    error = validar_texto(datos, "nombre_cancha", 50)
    if error:
        return error

    if type(datos.get("id_complejo")) is not int:
        return "El ID del complejo debe ser un entero"

    if datos["id_complejo"] <= 0:
        return "El ID del complejo debe ser positivo"

    if datos.get("superficie") not in ("sintetico", "parquet"):
        return "La superficie debe ser sintetico o parquet"

    if type(datos.get("techada")) is not bool:
        return "El campo techada debe ser true o false"

    return None


# ==========================================
# 7.3 - ABM DE COMPLEJOS
# ==========================================

@instalaciones_bp.route("/complejos", methods=["GET"])
@solo_admin
def listar_complejos():
    complejos = consultar(
        """
        SELECT id_complejo, nombre, direccion, departamento
        FROM complejo
        ORDER BY id_complejo
        """
    )
    return {"complejos": complejos}, 200


@instalaciones_bp.route("/complejos/nuevo", methods=["POST"])
@solo_admin
def crear_complejo():
    datos = request.get_json(silent=True)

    error = validar_complejo(datos)
    if error:
        return {"error": error}, 400

    try:
        _, nuevo_id = ejecutar(
            """
            INSERT INTO complejo (nombre, direccion, departamento)
            VALUES (%s, %s, %s)
            """,
            (
                datos["nombre"].strip(),
                datos["direccion"].strip(),
                datos["departamento"].strip()
            )
        )
    except (IntegrityError, DataError):
        return {"error": "No se pudo crear el complejo"}, 400

    return {
        "mensaje": "Complejo creado correctamente",
        "id_complejo": nuevo_id
    }, 201


@instalaciones_bp.route("/complejos/<int:id_complejo>", methods=["PUT"])
@solo_admin
def modificar_complejo(id_complejo):
    datos = request.get_json(silent=True)

    error = validar_complejo(datos)
    if error:
        return {"error": error}, 400

    existentes = consultar(
        "SELECT id_complejo FROM complejo WHERE id_complejo = %s",
        (id_complejo,)
    )

    if not existentes:
        return {"error": "No existe el complejo"}, 404

    try:
        ejecutar(
            """
            UPDATE complejo
            SET nombre = %s, direccion = %s, departamento = %s
            WHERE id_complejo = %s
            """,
            (
                datos["nombre"].strip(),
                datos["direccion"].strip(),
                datos["departamento"].strip(),
                id_complejo
            )
        )
    except (IntegrityError, DataError):
        return {"error": "No se pudo modificar el complejo"}, 400

    return {"mensaje": "Complejo modificado correctamente"}, 200


@instalaciones_bp.route("/complejos/<int:id_complejo>", methods=["DELETE"])
@solo_admin
def eliminar_complejo(id_complejo):
    try:
        filas, _ = ejecutar(
            "DELETE FROM complejo WHERE id_complejo = %s",
            (id_complejo,)
        )
    except IntegrityError as error:
        if error.errno == 1451:
            return {
                "error": "No se puede eliminar: el complejo tiene registros relacionados"
            }, 409

        return {"error": "No se pudo eliminar el complejo"}, 400

    if filas == 0:
        return {"error": "No existe el complejo"}, 404

    return {"mensaje": "Complejo eliminado correctamente"}, 200


# ==========================================
# 7.4 - ABM DE CANCHAS
# ==========================================

@instalaciones_bp.route("/canchas", methods=["GET"])
@solo_admin
def listar_canchas():
    canchas = consultar(
        """
        SELECT
            c.nombre_cancha,
            c.id_complejo,
            co.nombre AS nombre_complejo,
            c.superficie,
            c.techada
        FROM cancha c
        JOIN complejo co ON c.id_complejo = co.id_complejo
        ORDER BY c.id_complejo, c.nombre_cancha
        """
    )
    return {"canchas": canchas}, 200


@instalaciones_bp.route("/canchas/nueva", methods=["POST"])
@solo_admin
def crear_cancha():
    datos = request.get_json(silent=True)

    error = validar_cancha(datos)
    if error:
        return {"error": error}, 400

    try:
        ejecutar(
            """
            INSERT INTO cancha
            (nombre_cancha, id_complejo, superficie, techada)
            VALUES (%s, %s, %s, %s)
            """,
            (
                datos["nombre_cancha"].strip(),
                datos["id_complejo"],
                datos["superficie"],
                datos["techada"]
            )
        )
    except IntegrityError as error:
        if error.errno == 1062:
            return {"error": "Ya existe esa cancha en el complejo"}, 409

        if error.errno == 1452:
            return {"error": "El complejo indicado no existe"}, 400

        return {"error": "No se pudo crear la cancha"}, 400
    except DataError:
        return {"error": "Datos inválidos"}, 400

    return {"mensaje": "Cancha creada correctamente"}, 201


@instalaciones_bp.route(
    "/canchas/<int:id_complejo>/<string:nombre_cancha>",
    methods=["PUT"]
)
@solo_admin
def modificar_cancha(id_complejo, nombre_cancha):
    datos = request.get_json(silent=True)

    error = validar_cancha(datos)
    if error:
        return {"error": error}, 400

    existentes = consultar(
        """
        SELECT nombre_cancha
        FROM cancha
        WHERE id_complejo = %s AND nombre_cancha = %s
        """,
        (id_complejo, nombre_cancha)
    )

    if not existentes:
        return {"error": "No existe la cancha"}, 404

    try:
        ejecutar(
            """
            UPDATE cancha
            SET nombre_cancha = %s,
                id_complejo = %s,
                superficie = %s,
                techada = %s
            WHERE id_complejo = %s AND nombre_cancha = %s
            """,
            (
                datos["nombre_cancha"].strip(),
                datos["id_complejo"],
                datos["superficie"],
                datos["techada"],
                id_complejo,
                nombre_cancha
            )
        )
    except IntegrityError as error:
        if error.errno == 1062:
            return {"error": "Ya existe una cancha con ese nombre en el complejo"}, 409

        if error.errno == 1451:
            return {"error": "No se puede cambiar la cancha porque tiene partidos relacionados"}, 409

        if error.errno == 1452:
            return {"error": "El complejo indicado no existe"}, 400

        return {"error": "No se pudo modificar la cancha"}, 400
    except DataError:
        return {"error": "Datos inválidos"}, 400

    return {"mensaje": "Cancha modificada correctamente"}, 200


@instalaciones_bp.route(
    "/canchas/<int:id_complejo>/<string:nombre_cancha>",
    methods=["DELETE"]
)
@solo_admin
def eliminar_cancha(id_complejo, nombre_cancha):
    try:
        filas, _ = ejecutar(
            """
            DELETE FROM cancha
            WHERE id_complejo = %s AND nombre_cancha = %s
            """,
            (id_complejo, nombre_cancha)
        )
    except IntegrityError as error:
        if error.errno == 1451:
            return {
                "error": "No se puede eliminar la cancha porque tiene partidos relacionados"
            }, 409

        return {"error": "No se pudo eliminar la cancha"}, 400

    if filas == 0:
        return {"error": "No existe la cancha"}, 404

    return {"mensaje": "Cancha eliminada correctamente"}, 200
