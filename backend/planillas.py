from functools import wraps
from flask import Blueprint, request, session, redirect, url_for
from mysql.connector import IntegrityError, DataError
from db import conectar
from torneos_equipos import entero, error_bd

planillas_bp = Blueprint('planillas', __name__)


# Permite el acceso a administradores y planilleros.
def planillero_o_admin(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if 'rol' not in session:
            return redirect(url_for('login'))
        if session['rol'] not in ('administrador', 'planillero'):
            return {'error': 'No tenés permiso para cargar planillas'}, 403
        return fn(*args, **kwargs)
    return wrapper


# Ejecuta una operación con el usuario MySQL del rol logueado.
def ejecutar_segun_rol(fn):
    conn = conectar(session['rol'])
    cur = conn.cursor(dictionary=True, buffered=True)
    try:
        resultado = fn(cur)
        conn.commit()
        return resultado
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


# Devuelve los datos de un partido, o None si no existe.
def buscar_partido(cur, id_partido):
    cur.execute(
        """
        SELECT id_partido, id_torneo, numero_fecha,
               id_equipo_local, id_equipo_visitante, estado
        FROM partido
        WHERE id_partido=%s
        """,
        (id_partido,)
    )
    return cur.fetchone()

# Indica si el jugador tiene una sanción que abarca esa fecha del torneo.
def esta_suspendido(cur, ci, id_torneo, numero_fecha):
    cur.execute(
        """
        SELECT 1
        FROM sancion_jugador
        WHERE ci_jugador=%s
          AND id_torneo=%s
          AND %s BETWEEN numero_fecha_inicio
                     AND numero_fecha_inicio + cantidad_fechas - 1
        LIMIT 1
        """,
        (ci, id_torneo, numero_fecha)
    )
    return cur.fetchone() is not None   


# Agrega un jugador a la planilla, validando que sea del plantel de algún equipo del partido.
@planillas_bp.post('/partidos/<int:id_partido>/planilla')
@planillero_o_admin
def agregar_a_planilla(id_partido):
    d = request.get_json(silent=True)

    if not isinstance(d, dict) or not entero(d.get('ci_jugador')):
        return {'error': 'Se requiere ci_jugador (entero positivo)'}, 400

    ci = d['ci_jugador']

    def op(cur):
        partido = buscar_partido(cur, id_partido)

        if not partido:
            return {'error': 'No existe el partido'}, 404

        if partido['estado'] in ('postergado', 'cancelado'):
            return {'error': 'El partido está ' + partido['estado']}, 409

        cur.execute(
            """
            SELECT id_equipo
            FROM equipo_jugador_torneo
            WHERE ci_jugador=%s
              AND id_torneo=%s
              AND id_equipo IN (%s, %s)
            """,
            (
                ci,
                partido['id_torneo'],
                partido['id_equipo_local'],
                partido['id_equipo_visitante']
            )
        )
        fila = cur.fetchone()

        if not fila:
            return {'error': 'El jugador no está en el plantel de ninguno de los dos equipos'}, 409

        if esta_suspendido(cur, ci, partido['id_torneo'], partido['numero_fecha']):
            return {'error': 'El jugador está suspendido para esta fecha'}, 409
        
        cur.execute(
            """
            INSERT INTO planilla_partido (id_partido, ci_jugador, id_equipo)
            VALUES (%s, %s, %s)
            """,
            (id_partido, ci, fila['id_equipo'])
        )

        return {'mensaje': 'Jugador agregado a la planilla', 'id_equipo': fila['id_equipo']}, 201

    try:
        return ejecutar_segun_rol(op)
    except IntegrityError as e:
        if e.errno == 1062:
            return {'error': 'El jugador ya figura en la planilla'}, 409
        return error_bd(e)
    except DataError as e:
        return error_bd(e)


# Lista los jugadores que figuran en la planilla de un partido.
@planillas_bp.get('/partidos/<int:id_partido>/planilla')
@planillero_o_admin
def ver_planilla(id_partido):
    def op(cur):
        if not buscar_partido(cur, id_partido):
            return {'error': 'No existe el partido'}, 404

        cur.execute(
            """
            SELECT p.ci_jugador, j.nombre, j.apellido,
                   p.id_equipo, e.nombre AS equipo
            FROM planilla_partido p
            JOIN jugador j ON j.ci = p.ci_jugador
            JOIN equipo e ON e.id_equipo = p.id_equipo
            WHERE p.id_partido=%s
            ORDER BY e.nombre, j.apellido
            """,
            (id_partido,)
        )
        return {'planilla': cur.fetchall()}, 200


    return ejecutar_segun_rol(op)

# Registra un gol de un jugador que figura en la planilla del partido.
@planillas_bp.post('/partidos/<int:id_partido>/goles')
@planillero_o_admin
def registrar_gol(id_partido):
    d = request.get_json(silent=True)

    if not isinstance(d, dict) or not entero(d.get('ci_jugador')):
        return {'error': 'Se requiere ci_jugador (entero positivo)'}, 400

    if not entero(d.get('minuto'), 0, 60):
        return {'error': 'El minuto debe ser un entero entre 0 y 60'}, 400

    autogol = d.get('autogol', False)

    if type(autogol) is not bool:
        return {'error': 'autogol debe ser true o false'}, 400

    def op(cur):
        partido = buscar_partido(cur, id_partido)

        if not partido:
            return {'error': 'No existe el partido'}, 404

        if partido['estado'] in ('postergado', 'cancelado'):
            return {'error': 'El partido está ' + partido['estado']}, 409

        cur.execute(
            """
            INSERT INTO gol (id_partido, ci_jugador, minuto, autogol)
            VALUES (%s, %s, %s, %s)
            """,
            (id_partido, d['ci_jugador'], d['minuto'], autogol)
        )

        return {'mensaje': 'Gol registrado', 'id_gol': cur.lastrowid}, 201

    try:
        return ejecutar_segun_rol(op)
    except IntegrityError as e:
        if e.errno == 1452:
            return {'error': 'El jugador no figura en la planilla de este partido'}, 409
        return error_bd(e)
    except DataError as e:
        return error_bd(e)
    

# Si corresponde, crea la sanción automática por roja o por acumular 3 amarillas.
def sancion_automatica(cur, ci, partido, color):
    if color == 'roja':
        motivo = 'roja'
    else:
        cur.execute(
            """
            SELECT COUNT(*) AS cantidad
            FROM tarjeta t
            JOIN partido p ON p.id_partido = t.id_partido
            WHERE t.ci_jugador=%s
              AND p.id_torneo=%s
              AND t.color='amarilla'
            """,
            (ci, partido['id_torneo'])
        )
        if cur.fetchone()['cantidad'] % 3 != 0:
            return None
        motivo = 'acumulacion de amarillas'

    cur.execute(
        """
        INSERT INTO sancion_jugador
        (ci_jugador, id_torneo, motivo, numero_fecha_inicio, cantidad_fechas)
        VALUES (%s, %s, %s, %s, 1)
        """,
        (ci, partido['id_torneo'], motivo, partido['numero_fecha'] + 1)
    )
    return motivo
    

# Registra una tarjeta a un jugador que figura en la planilla del partido.
@planillas_bp.post('/partidos/<int:id_partido>/tarjetas')
@planillero_o_admin
def registrar_tarjeta(id_partido):
    d = request.get_json(silent=True)

    if not isinstance(d, dict) or not entero(d.get('ci_jugador')):
        return {'error': 'Se requiere ci_jugador (entero positivo)'}, 400

    if not entero(d.get('minuto'), 0, 60):
        return {'error': 'El minuto debe ser un entero entre 0 y 60'}, 400

    if d.get('color') not in ('amarilla', 'roja'):
        return {'error': 'El color debe ser amarilla o roja'}, 400

    def op(cur):
        partido = buscar_partido(cur, id_partido)

        if not partido:
            return {'error': 'No existe el partido'}, 404

        if partido['estado'] in ('postergado', 'cancelado'):
            return {'error': 'El partido está ' + partido['estado']}, 409

        cur.execute(
            """
            INSERT INTO tarjeta (id_partido, ci_jugador, minuto, color)
            VALUES (%s, %s, %s, %s)
            """,
            (id_partido, d['ci_jugador'], d['minuto'], d['color'])
        )

        id_tarjeta = cur.lastrowid
        sancion = sancion_automatica(cur, d['ci_jugador'], partido, d['color'])

        return {'mensaje': 'Tarjeta registrada', 'id_tarjeta': id_tarjeta, 'sancion': sancion}, 201
        

    try:
        return ejecutar_segun_rol(op)
    except IntegrityError as e:
        if e.errno == 1452:
            return {'error': 'El jugador no figura en la planilla de este partido'}, 409
        return error_bd(e)
    except DataError as e:
        return error_bd(e)