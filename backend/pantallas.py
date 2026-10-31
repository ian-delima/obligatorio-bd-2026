from flask import Blueprint, render_template
from torneos_equipos import admin, leer

pantallas_bp = Blueprint('pantallas', __name__, url_prefix='/panel')


# Pantalla de ABM de jugadores.
@pantallas_bp.get('/jugadores')
@admin
def jugadores():
    facultades = leer('SELECT id_facultad, nombre FROM facultad ORDER BY nombre')
    return render_template('jugadores.html', facultades=facultades)


# Pantalla de ABM de complejos y sus canchas.
@pantallas_bp.get('/instalaciones')
@admin
def instalaciones():
    return render_template('instalaciones.html')


# Pantalla de ABM de sanciones.
@pantallas_bp.get('/sanciones')
@admin
def sanciones():
    return render_template('sanciones.html')
