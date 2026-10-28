import os
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash
from db import conectar
from functools import wraps

app = Flask(__name__)
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

@app.route("/")
@requiere_rol("administrador", "planillero")
def inicio():
    return f"Hola {session['correo']}, entraste como {session['rol']}. <a href='/logout'>Salir</a>"

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        correo = request.form["correo"]
        contrasena = request.form["contrasena"]

        conexion = conectar("planillero")
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT contrasena, rol FROM login WHERE correo = %s",
            (correo,),
        )
        usuario = cursor.fetchone()
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

if __name__ == "__main__":
    app.run(debug=True)