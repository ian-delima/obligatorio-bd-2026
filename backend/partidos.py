from datetime import date, datetime, time, timedelta
from flask import Blueprint
from mysql.connector import IntegrityError, DataError
from torneos_equipos import admin, leer, ejecutar, objeto, entero, fecha_valida, error_bd

partidos_bp = Blueprint('partidos', __name__)
CAMPOS = ('id_torneo', 'numero_fecha', 'id_equipo_local', 'id_equipo_visitante',
          'dia', 'id_turno', 'nombre_cancha', 'id_complejo')


def validar_datos(datos):
    if not isinstance(datos, dict) or any(datos.get(c) is None for c in CAMPOS):
        return 'Faltan datos obligatorios'
    for campo in ('id_torneo', 'numero_fecha', 'id_equipo_local',
                  'id_equipo_visitante', 'id_turno', 'id_complejo'):
        if not entero(datos[campo]):
            return f'{campo} debe ser un entero positivo'
    if not fecha_valida(datos['dia']):
        return 'La fecha debe tener formato AAAA-MM-DD'
    if not isinstance(datos['nombre_cancha'], str) or not datos['nombre_cancha'].strip():
        return 'La cancha es obligatoria'
    return None


def validar_partido(cursor, datos, excluir=None):
    if datos['id_equipo_local'] == datos['id_equipo_visitante']:
        return {'error': 'Un equipo no puede jugar contra sí mismo'}, 400

    cursor.execute('SELECT id_torneo FROM torneo WHERE id_torneo=%s FOR UPDATE',
                   (datos['id_torneo'],))
    if not cursor.fetchone():
        return {'error': 'No existe el torneo'}, 404

    cursor.execute('SELECT id_equipo, id_torneo FROM equipo WHERE id_equipo IN (%s,%s)',
                   (datos['id_equipo_local'], datos['id_equipo_visitante']))
    equipos = cursor.fetchall()
    if len(equipos) != 2 or any(e['id_torneo'] != datos['id_torneo'] for e in equipos):
        return {'error': 'Los equipos no existen o no pertenecen al torneo'}, 400

    for id_equipo in (datos['id_equipo_local'], datos['id_equipo_visitante']):
        cursor.execute('''SELECT COUNT(*) AS cantidad FROM equipo_jugador_torneo
                          WHERE id_equipo=%s AND id_torneo=%s''',
                       (id_equipo, datos['id_torneo']))
        if cursor.fetchone()['cantidad'] < 5:
            return {'error': 'Ambos equipos deben tener al menos 5 jugadores'}, 409

    cursor.execute('''SELECT id_partido FROM partido
                      WHERE id_torneo=%s AND estado <> 'cancelado'
                      AND ((id_equipo_local=%s AND id_equipo_visitante=%s)
                        OR (id_equipo_local=%s AND id_equipo_visitante=%s))
                      AND (%s IS NULL OR id_partido <> %s)''',
                   (datos['id_torneo'], datos['id_equipo_local'],
                    datos['id_equipo_visitante'], datos['id_equipo_visitante'],
                    datos['id_equipo_local'], excluir, excluir))
    if cursor.fetchone():
        return {'error': 'Estos equipos ya tienen un partido registrado'}, 409

    cursor.execute('''SELECT id_partido FROM partido
                      WHERE id_torneo=%s AND numero_fecha=%s AND estado <> 'cancelado'
                      AND (id_equipo_local IN (%s,%s) OR id_equipo_visitante IN (%s,%s))
                      AND (%s IS NULL OR id_partido <> %s)''',
                   (datos['id_torneo'], datos['numero_fecha'],
                    datos['id_equipo_local'], datos['id_equipo_visitante'],
                    datos['id_equipo_local'], datos['id_equipo_visitante'],
                    excluir, excluir))
    if cursor.fetchone():
        return {'error': 'Uno de los equipos ya tiene partido en esta fecha'}, 409

    cursor.execute('''SELECT id_partido FROM partido
                      WHERE dia=%s AND id_turno=%s AND nombre_cancha=%s
                      AND id_complejo=%s AND estado <> 'cancelado'
                      AND (%s IS NULL OR id_partido <> %s)''',
                   (datos['dia'], datos['id_turno'], datos['nombre_cancha'],
                    datos['id_complejo'], excluir, excluir))
    if cursor.fetchone():
        return {'error': 'La cancha está ocupada en ese día y turno'}, 409
    return None


@partidos_bp.get('/partidos')
@admin
def listar_partidos():
    return {'partidos': leer('SELECT * FROM partido ORDER BY id_partido')}, 200


@partidos_bp.post('/partidos')
@admin
def crear_partido():
    datos = objeto()
    error = validar_datos(datos)
    if error:
        return {'error': error}, 400

    def guardar(cursor):
        error = validar_partido(cursor, datos)
        if error:
            return error
        cursor.execute('''INSERT INTO partido
                          (id_torneo, numero_fecha, id_equipo_local, id_equipo_visitante,
                           dia, id_turno, nombre_cancha, id_complejo, estado)
                          VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'programado')''',
                       tuple(datos[c] for c in CAMPOS))
        return {'mensaje': 'Partido creado', 'id_partido': cursor.lastrowid}, 201

    try:
        return ejecutar(guardar)
    except (IntegrityError, DataError) as ex:
        return error_bd(ex)


@partidos_bp.put('/partidos/<int:id_partido>')
@admin
def modificar_partido(id_partido):
    nuevos = objeto()
    if nuevos is None:
        return {'error': 'Debés enviar los datos del partido'}, 400

    def guardar(cursor):
        cursor.execute('SELECT * FROM partido WHERE id_partido=%s FOR UPDATE',
                       (id_partido,))
        actual = cursor.fetchone()
        if not actual:
            return {'error': 'No existe el partido'}, 404
        if actual['estado'] in ('jugado', 'cancelado'):
            return {'error': 'No se puede modificar un partido jugado o cancelado'}, 409
        datos = {c: nuevos.get(c, actual[c]) for c in CAMPOS}
        if isinstance(datos['dia'], date):
            datos['dia'] = datos['dia'].isoformat()
        error = validar_datos(datos)
        if error:
            return {'error': error}, 400
        if datos['id_torneo'] != actual['id_torneo']:
            return {'error': 'No se puede cambiar el torneo del partido'}, 409
        estado = nuevos.get('estado', actual['estado'])
        if estado not in ('programado', 'postergado', 'cancelado'):
            return {'error': 'Estado no permitido'}, 400
        if estado != 'cancelado':
            error = validar_partido(cursor, datos, id_partido)
            if error:
                return error
        cursor.execute('''UPDATE partido SET numero_fecha=%s, id_equipo_local=%s,
                          id_equipo_visitante=%s, dia=%s, id_turno=%s,
                          nombre_cancha=%s, id_complejo=%s, estado=%s
                          WHERE id_partido=%s''',
                       (datos['numero_fecha'], datos['id_equipo_local'],
                        datos['id_equipo_visitante'], datos['dia'], datos['id_turno'],
                        datos['nombre_cancha'], datos['id_complejo'], estado, id_partido))
        return {'mensaje': 'Partido actualizado'}, 200

    try:
        return ejecutar(guardar)
    except (IntegrityError, DataError) as ex:
        return error_bd(ex)


@partidos_bp.delete('/partidos/<int:id_partido>')
@admin
def eliminar_partido(id_partido):
    def guardar(cursor):
        cursor.execute('SELECT estado FROM partido WHERE id_partido=%s FOR UPDATE',
                       (id_partido,))
        actual = cursor.fetchone()
        if not actual:
            return {'error': 'No existe el partido'}, 404
        if actual['estado'] == 'jugado':
            return {'error': 'No se puede borrar un partido jugado'}, 409
        cursor.execute('DELETE FROM partido WHERE id_partido=%s', (id_partido,))
        return {'mensaje': 'Partido eliminado'}, 200

    try:
        return ejecutar(guardar)
    except (IntegrityError, DataError) as ex:
        return error_bd(ex)


@partidos_bp.put('/partidos/<int:id_partido>/jugado')
@admin
def marcar_jugado(id_partido):
    def guardar(cursor):
        cursor.execute('''SELECT p.estado, p.dia, t.hora_fin
                          FROM partido p JOIN turno t ON p.id_turno=t.id_turno
                          WHERE p.id_partido=%s FOR UPDATE''', (id_partido,))
        partido = cursor.fetchone()
        if not partido:
            return {'error': 'No existe el partido'}, 404
        if partido['estado'] not in ('programado', 'postergado'):
            return {'error': 'No se puede marcar como jugado en este estado'}, 409
        hora = partido['hora_fin']
        if isinstance(hora, timedelta):
            fin = datetime.combine(partido['dia'], time.min) + hora
        else:
            fin = datetime.combine(partido['dia'], hora)
        if fin > datetime.now():
            return {'error': 'El partido todavía no terminó su turno'}, 409
        cursor.execute("UPDATE partido SET estado='jugado' WHERE id_partido=%s",
                       (id_partido,))
        return {'mensaje': 'Partido marcado como jugado'}, 200

    return ejecutar(guardar)
