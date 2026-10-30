from flask import Blueprint
from torneos_equipos import admin, leer

reportes_bp = Blueprint('reportes', __name__)

REPORTES = {
    'jugadores-por-facultad': """
        SELECT facultad.nombre, jugador.tipo, COUNT(*) AS cantidad
        FROM facultad
        JOIN jugador ON facultad.id_facultad = jugador.id_facultad
        GROUP BY facultad.nombre, jugador.tipo
    """,

    'canchas-mas-usadas': """
        SELECT complejo.nombre, partido.nombre_cancha, COUNT(*) AS cantidad_partidos
        FROM partido
        JOIN complejo ON partido.id_complejo = complejo.id_complejo
        GROUP BY complejo.nombre, partido.nombre_cancha
        ORDER BY cantidad_partidos DESC
    """,

    'turnos-mas-usados': """
        SELECT CAST(turno.hora_inicio AS CHAR) AS hora_inicio,
               CAST(turno.hora_fin AS CHAR) AS hora_fin,
               COUNT(*) AS cantidad_partidos
        FROM partido
        JOIN turno ON partido.id_turno = turno.id_turno
        GROUP BY turno.hora_inicio, turno.hora_fin
        ORDER BY cantidad_partidos DESC
    """,

    'sanciones-por-equipo': """
        SELECT equipo.nombre, sancion_jugador.motivo, COUNT(*) AS cantidad_sanciones
        FROM sancion_jugador
        JOIN equipo_jugador_torneo
        ON sancion_jugador.ci_jugador = equipo_jugador_torneo.ci_jugador
        AND sancion_jugador.id_torneo = equipo_jugador_torneo.id_torneo
        JOIN equipo ON equipo_jugador_torneo.id_equipo = equipo.id_equipo
        GROUP BY equipo.nombre, sancion_jugador.motivo
        ORDER BY cantidad_sanciones DESC
    """,

    'estados-partidos': """
        SELECT estado, COUNT(*) AS cantidad_partidos,
               COUNT(*) * 100.0 / (SELECT COUNT(*) FROM partido) AS porcentaje
        FROM partido
        GROUP BY estado
    """,

    'goleadores': """
        SELECT jugador.nombre, jugador.apellido, COUNT(*) AS cantidad_goles
        FROM jugador
        JOIN gol ON jugador.ci = gol.ci_jugador
        WHERE gol.autogol = FALSE
        GROUP BY jugador.ci, jugador.nombre, jugador.apellido
        ORDER BY cantidad_goles DESC
        LIMIT 10
    """,

    'jugadores-sin-jugar': """
        SELECT jugador.nombre, jugador.apellido
        FROM jugador
        JOIN equipo_jugador_torneo ON jugador.ci = equipo_jugador_torneo.ci_jugador
        LEFT JOIN planilla_partido ON jugador.ci = planilla_partido.ci_jugador
        WHERE planilla_partido.ci_jugador IS NULL
    """,

    'fair-play': """
        SELECT equipo.nombre,
               COUNT(IF(tarjeta.color = 'amarilla', tarjeta.id_tarjeta, NULL)) AS amarillas,
               COUNT(IF(tarjeta.color = 'roja', tarjeta.id_tarjeta, NULL)) AS rojas,
               COUNT(IF(tarjeta.color = 'amarilla', tarjeta.id_tarjeta, NULL)) +
               COUNT(IF(tarjeta.color = 'roja', tarjeta.id_tarjeta, NULL)) * 3 AS puntos
        FROM equipo
        LEFT JOIN planilla_partido ON equipo.id_equipo = planilla_partido.id_equipo
        LEFT JOIN tarjeta
        ON planilla_partido.id_partido = tarjeta.id_partido
        AND planilla_partido.ci_jugador = tarjeta.ci_jugador
        GROUP BY equipo.id_equipo, equipo.nombre
        ORDER BY puntos ASC
    """,

    'promedio-goles-por-fecha': """
        SELECT partido.numero_fecha,
               COUNT(gol.id_gol) AS cantidad_goles,
               COUNT(gol.id_gol) / COUNT(DISTINCT partido.id_partido) AS promedio_goles
        FROM partido
        LEFT JOIN gol ON partido.id_partido = gol.id_partido
        WHERE partido.estado = 'jugado'
        GROUP BY partido.numero_fecha
        ORDER BY partido.numero_fecha
    """,

    'promedio-goles-edicion': """
        SELECT COUNT(gol.id_gol) AS cantidad_goles,
               COUNT(gol.id_gol) / COUNT(DISTINCT partido.id_partido) AS promedio_goles
        FROM partido
        LEFT JOIN gol ON partido.id_partido = gol.id_partido
        WHERE partido.estado = 'jugado'
    """,

    'posiciones': """
        SELECT nombre,
               COUNT(*) AS PJ,
               SUM(GF > GC) AS PG,
               SUM(GF = GC) AS PE,
               SUM(GF < GC) AS PP,
               SUM(GF) AS GF,
               SUM(GC) AS GC,
               SUM(GF - GC) AS DG,
               3 * SUM(GF > GC) + SUM(GF = GC) AS puntos
        FROM goles_equipos
        GROUP BY id_equipo, nombre
        ORDER BY puntos DESC, DG DESC, GF DESC
    """,

    'partido-con-mas-goles': """
        SELECT equipo_local, equipo_visitante, goles_local, goles_visitante,
               goles_local + goles_visitante AS total_goles
        FROM resultado_partidos
        ORDER BY total_goles DESC
        LIMIT 1
    """,

    'jugadores-mas-tarjetas': """
        SELECT jugador.nombre, jugador.apellido,
               COUNT(tarjeta.id_tarjeta) AS cantidad_tarjetas
        FROM jugador
        JOIN tarjeta ON jugador.ci = tarjeta.ci_jugador
        GROUP BY jugador.ci, jugador.nombre, jugador.apellido
        ORDER BY cantidad_tarjetas DESC
    """,

    'equipo-con-mas-goles': """
        SELECT nombre, SUM(GF) AS total_goles
        FROM goles_equipos
        GROUP BY id_equipo, nombre
        ORDER BY total_goles DESC
        LIMIT 1
    """,
}


# Lista los nombres de los reportes disponibles.
@reportes_bp.get('/reportes')
@admin
def listar_reportes():
    return {'reportes': list(REPORTES)}, 200


# Ejecuta el reporte pedido y devuelve sus filas.
@reportes_bp.get('/reportes/<nombre>')
@admin
def ver_reporte(nombre):
    if nombre not in REPORTES:
        return {'error': 'No existe ese reporte'}, 404

    return {'reporte': nombre, 'filas': leer(REPORTES[nombre])}, 200