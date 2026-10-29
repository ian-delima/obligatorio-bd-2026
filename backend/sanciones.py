from flask import Blueprint, request
from mysql.connector import IntegrityError, DataError
from torneos_equipos import admin, ejecutar, leer, entero, error_bd

sanciones_bp = Blueprint('sanciones', __name__)

MOTIVOS = {
    'roja',
    'acumulacion de amarillas',
    'disciplinaria'
}


def validar(d):
    if not isinstance(d, dict):
        return 'Se requiere JSON'

    if not entero(d.get('ci_jugador')) or not entero(d.get('id_torneo')):
        return 'Jugador y torneo deben ser IDs positivos'

    if d.get('motivo') not in MOTIVOS:
        return 'Motivo inválido'

    if not entero(d.get('numero_fecha_inicio')):
        return 'Número de fecha de inicio inválido'

    if not entero(d.get('cantidad_fechas'), 1, 127):
        return 'Cantidad de fechas inválida'

    return None


@sanciones_bp.get('/sanciones')
@admin
def listar_sanciones():
    return {
        'sanciones': leer(
            'SELECT * FROM sancion_jugador ORDER BY id_sancion'
        )
    }, 200


@sanciones_bp.post('/sanciones')
@admin
def crear_sancion():
    d = request.get_json(silent=True)
    err = validar(d)

    if err:
        return {'error': err}, 400

    def op(cur):
        cur.execute(
            """
            SELECT 1
            FROM equipo_jugador_torneo
            WHERE ci_jugador=%s AND id_torneo=%s
            LIMIT 1
            """,
            (d['ci_jugador'], d['id_torneo'])
        )

        if not cur.fetchone():
            return {
                'error': 'El jugador no está inscripto en este torneo'
            }, 409

        cur.execute(
            """
            INSERT INTO sancion_jugador
            (
                ci_jugador,
                id_torneo,
                motivo,
                numero_fecha_inicio,
                cantidad_fechas
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                d['ci_jugador'],
                d['id_torneo'],
                d['motivo'],
                d['numero_fecha_inicio'],
                d['cantidad_fechas']
            )
        )

        return {
            'mensaje': 'Sanción creada',
            'id_sancion': cur.lastrowid
        }, 201

    try:
        return ejecutar(op)
    except (IntegrityError, DataError) as e:
        return error_bd(e)


@sanciones_bp.put('/sanciones/<int:id_sancion>')
@admin
def modificar_sancion(id_sancion):
    d = request.get_json(silent=True)
    err = validar(d)

    if err:
        return {'error': err}, 400

    def op(cur):
        cur.execute(
            """
            SELECT id_sancion
            FROM sancion_jugador
            WHERE id_sancion=%s
            FOR UPDATE
            """,
            (id_sancion,)
        )

        if not cur.fetchone():
            return {'error': 'No existe la sanción'}, 404

        cur.execute(
            """
            SELECT 1
            FROM equipo_jugador_torneo
            WHERE ci_jugador=%s AND id_torneo=%s
            LIMIT 1
            """,
            (d['ci_jugador'], d['id_torneo'])
        )

        if not cur.fetchone():
            return {
                'error': 'El jugador no está inscripto en este torneo'
            }, 409

        cur.execute(
            """
            UPDATE sancion_jugador
            SET ci_jugador=%s,
                id_torneo=%s,
                motivo=%s,
                numero_fecha_inicio=%s,
                cantidad_fechas=%s
            WHERE id_sancion=%s
            """,
            (
                d['ci_jugador'],
                d['id_torneo'],
                d['motivo'],
                d['numero_fecha_inicio'],
                d['cantidad_fechas'],
                id_sancion
            )
        )

        return {'mensaje': 'Sanción modificada'}, 200

    try:
        return ejecutar(op)
    except (IntegrityError, DataError) as e:
        return error_bd(e)


@sanciones_bp.delete('/sanciones/<int:id_sancion>')
@admin
def borrar_sancion(id_sancion):
    def op(cur):
        cur.execute(
            'DELETE FROM sancion_jugador WHERE id_sancion=%s',
            (id_sancion,)
        )

        if cur.rowcount == 0:
            return {'error': 'No existe la sanción'}, 404

        return {'mensaje': 'Sanción eliminada'}, 200

    try:
        return ejecutar(op)
    except IntegrityError as e:
        return error_bd(e)
