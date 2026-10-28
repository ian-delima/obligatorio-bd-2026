import os
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash
from db import conectar

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


@app.route("/")
def inicio():
    if "rol" not in session:
        return redirect(url_for("login"))
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

if __name__ == "__main__":
    app.run(debug=True)