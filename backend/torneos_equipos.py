from datetime import date
from functools import wraps
from flask import Blueprint, request, session, redirect, url_for
from mysql.connector import IntegrityError, DataError
from db import conectar

te_bp = Blueprint('torneos_equipos', __name__)
TIPOS = {'grado', 'posgrado', 'docente', 'funcionario'}
ESTADOS = {'inscripcion', 'en curso', 'finalizado'}


def admin(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if 'rol' not in session:
            return redirect(url_for('login'))
        if session['rol'] != 'administrador':
            return {'error': 'Acceso exclusivo de administradores'}, 403
        return fn(*args, **kwargs)
    return wrapper


def error_bd(ex):
    if isinstance(ex, IntegrityError):
        if ex.errno == 1062:
            return {'error': 'Registro duplicado'}, 409
        if ex.errno == 1451:
            return {'error': 'No se puede eliminar: existen registros relacionados'}, 409
        if ex.errno == 1452:
            return {'error': 'Referencia inexistente'}, 400
    return {'error': 'Datos no admitidos por la base de datos'}, 400


def ejecutar(fn):
    conn = conectar('administrador')
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


def leer(sql, params=()):
    def op(cur):
        cur.execute(sql, params)
        return cur.fetchall()
    return ejecutar(op)


def objeto():
    d = request.get_json(silent=True)
    return d if isinstance(d, dict) else None


def entero(v, minimo=1, maximo=2147483647):
    return type(v) is int and minimo <= v <= maximo


def texto(v, maximo):
    return isinstance(v, str) and bool(v.strip()) and len(v) <= maximo


def fecha_valida(v):
    if not isinstance(v, str) or len(v) != 10:
        return False
    try:
        return date.fromisoformat(v).isoformat() == v
    except ValueError:
        return False


def torneo_bloqueado(cur, id_torneo):
    cur.execute(
        'SELECT * FROM torneo WHERE id_torneo=%s FOR UPDATE',
        (id_torneo,)
    )
    return cur.fetchone()


def equipo_bloqueado(cur, id_equipo):
    cur.execute(
        'SELECT * FROM equipo WHERE id_equipo=%s FOR UPDATE',
        (id_equipo,)
    )
    return cur.fetchone()


def verificar_inscripcion(cur, id_torneo):
    t = torneo_bloqueado(cur, id_torneo)
    if not t:
        return {'error': 'No existe el torneo'}, 404
    if t['estado'] != 'inscripcion':
        return {'error': 'Solo se permite modificar durante inscripción'}, 409
    return None


def datos_torneo(d):
    if d is None:
        return 'Se requiere un objeto JSON'
    if not texto(d.get('nombre'), 100):
        return 'Nombre obligatorio (máximo 100 caracteres)'
    if not entero(d.get('anio'), 1900, 9999):
        return 'Año inválido'
    if type(d.get('semestre')) is not int or d['semestre'] not in (1, 2):
        return 'Semestre inválido'
    if not fecha_valida(d.get('fecha_inicio')) or not fecha_valida(d.get('fecha_fin')):
        return 'Fechas inválidas (AAAA-MM-DD)'
    if d['fecha_fin'] <= d['fecha_inicio']:
        return 'La fecha final debe ser posterior a la inicial'
    return None


def datos_equipo(d):
    if d is None:
        return 'Se requiere un objeto JSON'
    if not texto(d.get('nombre'), 50):
        return 'Nombre obligatorio (máximo 50 caracteres)'
    if not entero(d.get('id_torneo')) or not entero(d.get('id_facultad')):
        return 'Torneo y facultad deben ser enteros positivos'
    return None


@te_bp.get('/torneos')
@admin
def listar_torneos():
    return {'torneos': leer('SELECT * FROM torneo ORDER BY id_torneo')}


@te_bp.post('/torneos')
@admin
def crear_torneo():
    d = objeto()
    err = datos_torneo(d)
    if err:
        return {'error': err}, 400

    try:
        def op(cur):
            cur.execute(
                """
                INSERT INTO torneo
                (nombre, anio, semestre, fecha_inicio, fecha_fin, estado)
                VALUES (%s, %s, %s, %s, %s, 'inscripcion')
                """,
                (
                    d['nombre'].strip(),
                    d['anio'],
                    d['semestre'],
                    d['fecha_inicio'],
                    d['fecha_fin']
                )
            )
            return cur.lastrowid

        ident = ejecutar(op)
        return {'mensaje': 'Torneo creado', 'id_torneo': ident}, 201

    except (IntegrityError, DataError) as e:
        return error_bd(e)


@te_bp.put('/torneos/<int:id_torneo>')
@admin
def modificar_torneo(id_torneo):
    d = objeto()
    err = datos_torneo(d)
    if err:
        return {'error': err}, 400

    def op(cur):
        r = verificar_inscripcion(cur, id_torneo)
        if r:
            return r

        cur.execute(
            """
            UPDATE torneo
            SET nombre=%s,
                anio=%s,
                semestre=%s,
                fecha_inicio=%s,
                fecha_fin=%s
            WHERE id_torneo=%s
            """,
            (
                d['nombre'].strip(),
                d['anio'],
                d['semestre'],
                d['fecha_inicio'],
                d['fecha_fin'],
                id_torneo
            )
        )
        return {'mensaje': 'Torneo modificado'}, 200

    try:
        return ejecutar(op)
    except (IntegrityError, DataError) as e:
        return error_bd(e)


@te_bp.put('/torneos/<int:id_torneo>/estado')
@admin
def cambiar_estado_torneo(id_torneo):
    d = objeto()
    nuevo = d.get('estado') if d else None

    if nuevo not in ESTADOS:
        return {'error': 'Estado inválido'}, 400

    def op(cur):
        t = torneo_bloqueado(cur, id_torneo)

        if not t:
            return {'error': 'No existe el torneo'}, 404

        anterior = t['estado']

        if nuevo == anterior:
            return {'mensaje': 'El torneo ya tenía ese estado'}, 200

        if (anterior, nuevo) not in {
            ('inscripcion', 'en curso'),
            ('en curso', 'finalizado')
        }:
            return {'error': 'Transición de estado no permitida'}, 409

        if nuevo == 'en curso':
            cur.execute(
                """
                SELECT id_equipo, ci_capitan
                FROM equipo
                WHERE id_torneo=%s
                FOR UPDATE
                """,
                (id_torneo,)
            )
            equipos = cur.fetchall()

            if not equipos:
                return {'error': 'No se puede iniciar un torneo sin equipos'}, 409

            for eq in equipos:
                cur.execute(
                    """
                    SELECT ci_jugador
                    FROM equipo_jugador_torneo
                    WHERE id_equipo=%s AND id_torneo=%s
                    """,
                    (eq['id_equipo'], id_torneo)
                )

                cedulas = {
                    row['ci_jugador']
                    for row in cur.fetchall()
                }

                if not 5 <= len(cedulas) <= 10:
                    return {
                        'error': (
                            f'El equipo {eq["id_equipo"]} '
                            'debe tener entre 5 y 10 jugadores'
                        )
                    }, 409

                if eq['ci_capitan'] not in cedulas:
                    return {
                        'error': (
                            f'El equipo {eq["id_equipo"]} '
                            'no tiene capitán válido'
                        )
                    }, 409

        cur.execute(
            'UPDATE torneo SET estado=%s WHERE id_torneo=%s',
            (nuevo, id_torneo)
        )

        return {'mensaje': 'Estado actualizado', 'estado': nuevo}, 200

    return ejecutar(op)


@te_bp.delete('/torneos/<int:id_torneo>')
@admin
def borrar_torneo(id_torneo):
    def op(cur):
        r = verificar_inscripcion(cur, id_torneo)
        if r:
            return r

        cur.execute(
            'DELETE FROM torneo WHERE id_torneo=%s',
            (id_torneo,)
        )
        return {'mensaje': 'Torneo eliminado'}, 200

    try:
        return ejecutar(op)
    except IntegrityError as e:
        return error_bd(e)


@te_bp.get('/equipos')
@admin
def listar_equipos():
    return {'equipos': leer('SELECT * FROM equipo ORDER BY id_equipo')}


@te_bp.post('/equipos')
@admin
def crear_equipo():
    d = objeto()
    err = datos_equipo(d)
    if err:
        return {'error': err}, 400

    def op(cur):
        r = verificar_inscripcion(cur, d['id_torneo'])
        if r:
            return r

        cur.execute(
            'SELECT 1 FROM facultad WHERE id_facultad=%s',
            (d['id_facultad'],)
        )

        if not cur.fetchone():
            return {'error': 'No existe la facultad'}, 400

        cur.execute(
            """
            INSERT INTO equipo
            (nombre, id_torneo, id_facultad, ci_capitan)
            VALUES (%s, %s, %s, NULL)
            """,
            (
                d['nombre'].strip(),
                d['id_torneo'],
                d['id_facultad']
            )
        )

        return {
            'mensaje': 'Equipo creado',
            'id_equipo': cur.lastrowid
        }, 201

    try:
        return ejecutar(op)
    except (IntegrityError, DataError) as e:
        return error_bd(e)


@te_bp.put('/equipos/<int:id_equipo>')
@admin
def modificar_equipo(id_equipo):
    d = objeto()
    err = datos_equipo(d)
    if err:
        return {'error': err}, 400

    def op(cur):
        eq = equipo_bloqueado(cur, id_equipo)

        if not eq:
            return {'error': 'No existe el equipo'}, 404

        for t_id in sorted({eq['id_torneo'], d['id_torneo']}):
            r = verificar_inscripcion(cur, t_id)
            if r:
                return r

        cur.execute(
            """
            SELECT 1
            FROM equipo_jugador_torneo
            WHERE id_equipo=%s
            LIMIT 1
            """,
            (id_equipo,)
        )

        tiene_plantel = cur.fetchone() is not None

        if (
            eq['id_torneo'] != d['id_torneo']
            or eq['id_facultad'] != d['id_facultad']
        ) and tiene_plantel:
            return {
                'error': (
                    'No se puede cambiar torneo/facultad '
                    'de un equipo con plantel'
                )
            }, 409

        cur.execute(
            """
            UPDATE equipo
            SET nombre=%s, id_torneo=%s, id_facultad=%s
            WHERE id_equipo=%s
            """,
            (
                d['nombre'].strip(),
                d['id_torneo'],
                d['id_facultad'],
                id_equipo
            )
        )

        return {'mensaje': 'Equipo modificado'}, 200

    try:
        return ejecutar(op)
    except (IntegrityError, DataError) as e:
        return error_bd(e)


@te_bp.delete('/equipos/<int:id_equipo>')
@admin
def borrar_equipo(id_equipo):
    def op(cur):
        eq = equipo_bloqueado(cur, id_equipo)

        if not eq:
            return {'error': 'No existe el equipo'}, 404

        r = verificar_inscripcion(cur, eq['id_torneo'])
        if r:
            return r

        cur.execute(
            'DELETE FROM equipo WHERE id_equipo=%s',
            (id_equipo,)
        )

        return {'mensaje': 'Equipo eliminado'}, 200

    try:
        return ejecutar(op)
    except IntegrityError as e:
        return error_bd(e)


@te_bp.get('/equipos/<int:id_equipo>/plantel')
@admin
def ver_plantel(id_equipo):
    equipo = leer(
        'SELECT * FROM equipo WHERE id_equipo=%s',
        (id_equipo,)
    )

    if not equipo:
        return {'error': 'No existe el equipo'}, 404

    jugadores = leer(
        """
        SELECT
            j.ci,
            j.nombre,
            j.apellido,
            j.tipo,
            j.id_facultad,
            p.numero_camiseta
        FROM equipo_jugador_torneo p
        JOIN jugador j ON j.ci=p.ci_jugador
        WHERE p.id_equipo=%s AND p.id_torneo=%s
        ORDER BY j.ci
        """,
        (id_equipo, equipo[0]['id_torneo'])
    )

    return {
        'equipo': equipo[0],
        'plantel': jugadores
    }, 200


@te_bp.post('/equipos/<int:id_equipo>/plantel')
@admin
def agregar_plantel(id_equipo):
    d = objeto()

    if not d or not entero(d.get('ci_jugador')):
        return {
            'error': 'La CI del jugador debe ser un entero positivo'
        }, 400

    nro = d.get('numero_camiseta')

    if nro is not None and not entero(nro, 0, 127):
        return {'error': 'Número de camiseta inválido'}, 400

    def op(cur):
        eq = equipo_bloqueado(cur, id_equipo)

        if not eq:
            return {'error': 'No existe el equipo'}, 404

        r = verificar_inscripcion(cur, eq['id_torneo'])
        if r:
            return r

        cur.execute(
            """
            SELECT ci, tipo, id_facultad
            FROM jugador
            WHERE ci=%s
            """,
            (d['ci_jugador'],)
        )

        j = cur.fetchone()

        if not j:
            return {'error': 'No existe el jugador'}, 404

        if j['id_facultad'] != eq['id_facultad']:
            return {
                'error': 'El jugador debe ser de la facultad del equipo'
            }, 409

        cur.execute(
            """
            SELECT j.tipo
            FROM equipo_jugador_torneo p
            JOIN jugador j ON j.ci=p.ci_jugador
            WHERE p.id_equipo=%s AND p.id_torneo=%s
            """,
            (id_equipo, eq['id_torneo'])
        )

        tipos = [r['tipo'] for r in cur.fetchall()]

        if len(tipos) >= 10:
            return {'error': 'El plantel ya tiene 10 jugadores'}, 409

        if (
            j['tipo'] in {'docente', 'funcionario'}
            and sum(
                t in {'docente', 'funcionario'}
                for t in tipos
            ) >= 2
        ):
            return {
                'error': 'Máximo dos docentes/funcionarios por plantel'
            }, 409

        cur.execute(
            """
            INSERT INTO equipo_jugador_torneo
            (id_equipo, ci_jugador, id_torneo, numero_camiseta)
            VALUES (%s, %s, %s, %s)
            """,
            (
                id_equipo,
                d['ci_jugador'],
                eq['id_torneo'],
                nro
            )
        )

        return {'mensaje': 'Jugador incorporado al plantel'}, 201

    try:
        return ejecutar(op)
    except (IntegrityError, DataError) as e:
        return error_bd(e)


@te_bp.delete('/equipos/<int:id_equipo>/plantel/<int:ci>')
@admin
def quitar_plantel(id_equipo, ci):
    def op(cur):
        eq = equipo_bloqueado(cur, id_equipo)

        if not eq:
            return {'error': 'No existe el equipo'}, 404

        r = verificar_inscripcion(cur, eq['id_torneo'])
        if r:
            return r

        if eq['ci_capitan'] == ci:
            return {'error': 'Primero cambiá el capitán'}, 409

        cur.execute(
            """
            DELETE FROM equipo_jugador_torneo
            WHERE id_equipo=%s
              AND id_torneo=%s
              AND ci_jugador=%s
            """,
            (id_equipo, eq['id_torneo'], ci)
        )

        if cur.rowcount == 0:
            return {
                'error': 'El jugador no está en ese plantel'
            }, 404

        return {'mensaje': 'Jugador quitado del plantel'}, 200

    try:
        return ejecutar(op)
    except IntegrityError as e:
        return error_bd(e)


@te_bp.put('/equipos/<int:id_equipo>/capitan')
@admin
def asignar_capitan(id_equipo):
    d = objeto()

    if not d or not entero(d.get('ci_capitan')):
        return {'error': 'CI de capitán inválida'}, 400

    def op(cur):
        eq = equipo_bloqueado(cur, id_equipo)

        if not eq:
            return {'error': 'No existe el equipo'}, 404

        r = verificar_inscripcion(cur, eq['id_torneo'])
        if r:
            return r

        cur.execute(
            """
            SELECT 1
            FROM equipo_jugador_torneo
            WHERE id_equipo=%s
              AND id_torneo=%s
              AND ci_jugador=%s
            """,
            (
                id_equipo,
                eq['id_torneo'],
                d['ci_capitan']
            )
        )

        if not cur.fetchone():
            return {
                'error': 'El capitán debe integrar el plantel'
            }, 409

        cur.execute(
            'UPDATE equipo SET ci_capitan=%s WHERE id_equipo=%s',
            (d['ci_capitan'], id_equipo)
        )

        return {'mensaje': 'Capitán asignado'}, 200

    return ejecutar(op)
