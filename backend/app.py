from flask import Flask
from db import conectar

app = Flask(__name__)


@app.route("/")
def inicio():
    conexion = conectar("administrador")
    cursor = conexion.cursor()
    cursor.execute("SELECT nombre FROM facultad")
    facultades = cursor.fetchall()
    cursor.close()
    conexion.close()
    return str(facultades)


if __name__ == "__main__":
    app.run(debug=True)