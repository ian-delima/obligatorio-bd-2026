import os
from datetime import date
from functools import wraps
from partidos import partidos_bp

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash
from mysql.connector import IntegrityError
from torneos_equipos import te_bp
from sanciones import sanciones_bp
from instalaciones import instalaciones_bp
from planillas import planillas_bp
from partidos import partidos_bp

from db import conectar
from jugadores import (
    listar_jugadores,
    crear_jugador,
    modificar_jugador,
    eliminar_jugador,
    existe_jugador
)


app = Flask(__name__)
app.register_blueprint(te_bp)
app.register_blueprint(sanciones_bp)
app.register_blueprint(instalaciones_bp)
app.register_blueprint(partidos_bp)
app.register_blueprint(planillas_bp)
app.secret_key = os.getenv("SECRET_KEY")


def requiere_rol(*roles):
    def decorador(funcion):
        @wraps(funcion)
        def envoltura(*args, **kwargs):
            if "rol" not in session:
                return redirect(url_for("login"))

            if session["rol"] not in roles:
                return "No tenés permiso para entrar acá", 403

            return funcion(*args, **kwargs)

        return envoltura

    return decorador


def validar_datos_jugador(datos, incluir_ci=False):
    if incluir_ci:
        ci = datos.get("ci")

        if type(ci) is not int or ci <= 0 or ci > 2147483647:
            return "La cédula debe ser un número entero positivo válido"

    id_facultad = datos.get("id_facultad")

    if type(id_facultad) is not int or id_facultad <= 0:
        return "El ID de facultad debe ser un número entero positivo"

    fecha = datos.get("fecha_nacimiento")

    if not isinstance(fecha, str):
        return "La fecha de nacimiento debe ser un texto con formato AAAA-MM-DD"

    try:
        if len(fecha) != 10 or fecha[4] != "-" or fecha[7] != "-":
            return "La fecha debe tener formato AAAA-MM-DD"

        nacimiento = date.fromisoformat(fecha)

        if nacimiento > date.today():
            return "La fecha de nacimiento no puede ser futura"

    except ValueError:
        return "La fecha de nacimiento no es válida"

    return None


def validar_textos_jugador(datos):
    nombre = datos.get("nombre")
    apellido = datos.get("apellido")
    email = datos.get("email")

    if not isinstance(nombre, str) or not nombre.strip():
        return "El nombre debe ser un texto no vacío"

    if len(nombre) > 50:
        return "El nombre no puede superar los 50 caracteres"

    if not isinstance(apellido, str) or not apellido.strip():
        return "El apellido debe ser un texto no vacío"

    if len(apellido) > 50:
        return "El apellido no puede superar los 50 caracteres"

    if email is not None:
        if not isinstance(email, str):
            return "El correo debe ser un texto"

        if len(email) > 100:
            return "El correo no puede superar los 100 caracteres"

        if "@" not in email or "." not in email.split("@")[-1]:
            return "El correo no tiene un formato válido"

    return None


@app.route("/")
@requiere_rol("administrador", "planillero")
def inicio():
    return (
        f"Hola {session['correo']}, entraste como {session['rol']}. "
        "<a href='/logout'>Salir</a>"
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        correo = request.form["correo"]
        contrasena = request.form["contrasena"]

        conexion = conectar("planillero")
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute(
                "SELECT contrasena, rol FROM login WHERE correo = %s",
                (correo,)
            )
            usuario = cursor.fetchone()
        finally:
            cursor.close()
            conexion.close()

        if usuario and check_password_hash(usuario["contrasena"], contrasena):
            session["correo"] = correo
            session["rol"] = usuario["rol"]
            return redirect(url_for("inicio"))

        error = "Correo o contraseña incorrectos"

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/prueba-admin")
@requiere_rol("administrador")
def prueba_admin():
    return "Si ves esto, sos admin"


@app.route("/jugadores")
@requiere_rol("administrador")
def ver_jugadores():
    jugadores = listar_jugadores()
    return {"jugadores": jugadores}


@app.route("/jugadores/nuevo", methods=["POST"])
@requiere_rol("administrador")
def nuevo_jugador():
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return {"error": "Debés enviar los datos del jugador"}, 400

    campos = [
        "ci",
        "nombre",
        "apellido",
        "fecha_nacimiento",
        "id_facultad",
        "tipo"
    ]

    if any(campo not in datos or datos[campo] is None for campo in campos):
        return {"error": "Faltan campos obligatorios"}, 400

    error = validar_datos_jugador(datos, incluir_ci=True)
    if error:
        return {"error": error}, 400

    error = validar_textos_jugador(datos)
    if error:
        return {"error": error}, 400

    tipos_validos = ["grado", "posgrado", "docente", "funcionario"]

    if datos["tipo"] not in tipos_validos:
        return {"error": "Tipo de jugador inválido"}, 400

    try:
        crear_jugador(
            datos["ci"],
            datos["nombre"],
            datos["apellido"],
            datos.get("email"),
            datos["fecha_nacimiento"],
            datos["id_facultad"],
            datos["tipo"]
        )

    except IntegrityError as error:
        if error.errno == 1062:
            return {"error": "Ya existe un jugador con esa cédula"}, 409

        if error.errno == 1452:
            return {"error": "La facultad indicada no existe"}, 400

        return {"error": "No se pudo registrar el jugador"}, 400

    return {"mensaje": "Jugador creado correctamente"}, 201


@app.route("/jugadores/<int:ci>", methods=["PUT"])
@requiere_rol("administrador")
def editar_jugador(ci):
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return {"error": "Debés enviar los datos del jugador"}, 400

    campos = [
        "nombre",
        "apellido",
        "fecha_nacimiento",
        "id_facultad",
        "tipo"
    ]

    if any(campo not in datos or datos[campo] is None for campo in campos):
        return {"error": "Faltan campos obligatorios"}, 400

    error = validar_datos_jugador(datos)
    if error:
        return {"error": error}, 400

    error = validar_textos_jugador(datos)
    if error:
        return {"error": error}, 400

    tipos_validos = ["grado", "posgrado", "docente", "funcionario"]

    if datos["tipo"] not in tipos_validos:
        return {"error": "Tipo de jugador inválido"}, 400

    try:
        filas = modificar_jugador(
            ci,
            datos["nombre"],
            datos["apellido"],
            datos.get("email"),
            datos["fecha_nacimiento"],
            datos["id_facultad"],
            datos["tipo"]
        )

    except IntegrityError as error:
        if error.errno == 1452:
            return {"error": "La facultad indicada no existe"}, 400

        return {"error": "No se pudo modificar el jugador"}, 400

    if filas == 0:
        if existe_jugador(ci):
            return {"mensaje": "El jugador ya tenía esos datos"}, 200

        return {"error": "No se encontró el jugador"}, 404

    return {"mensaje": "Jugador modificado correctamente"}, 200


@app.route("/jugadores/<int:ci>", methods=["DELETE"])
@requiere_rol("administrador")
def borrar_jugador(ci):
    try:
        filas = eliminar_jugador(ci)

    except IntegrityError as error:
        if error.errno == 1451:
            return {
                "error": (
                    "No se puede eliminar el jugador porque "
                    "tiene registros relacionados"
                )
            }, 409

        return {"error": "No se pudo eliminar el jugador"}, 400

    if filas == 0:
        return {"error": "No se encontró el jugador"}, 404

    return {"mensaje": "Jugador eliminado correctamente"}, 200


if __name__ == "__main__":
    app.run(debug=True)
