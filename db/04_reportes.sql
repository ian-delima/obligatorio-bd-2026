USE obligatorio_bd;

/* Obtener los jugadores de cada facultad y su tipo */
SELECT facultad.nombre, jugador.tipo, COUNT(*) AS cantidad
FROM facultad
JOIN jugador ON facultad.id_facultad = jugador.id_facultad
GROUP BY facultad.nombre, jugador.tipo;

/* Obtener la cantidad de partidos por cancha */
SELECT complejo.nombre, partido.nombre_cancha, COUNT(*) AS cantidad_partidos
FROM partido
JOIN complejo ON partido.id_complejo = complejo.id_complejo
GROUP BY complejo.nombre, partido.nombre_cancha
ORDER BY cantidad_partidos DESC;

/* Obtener los turnos mas utilizados y la cantidad de partidos */
SELECT turno.hora_inicio, turno.hora_fin, COUNT(*) AS cantidad_partidos
FROM partido
JOIN turno ON partido.id_turno = turno.id_turno
GROUP BY turno.hora_inicio, turno.hora_fin
ORDER BY cantidad_partidos DESC;

/* Obtener la cantidad de sanciones por equipo y motivo */
SELECT equipo.nombre, sancion_jugador.motivo, COUNT(*) AS cantidad_sanciones
FROM sancion_jugador
JOIN equipo_jugador_torneo
ON sancion_jugador.ci_jugador = equipo_jugador_torneo.ci_jugador
AND sancion_jugador.id_torneo = equipo_jugador_torneo.id_torneo
JOIN equipo
ON equipo_jugador_torneo.id_equipo = equipo.id_equipo
GROUP BY equipo.nombre, sancion_jugador.motivo
ORDER BY cantidad_sanciones DESC;

/* Obtener el porcentaje de partidos segun su estado */
SELECT estado, COUNT(*) AS cantidad_partidos,
       COUNT(*) * 100.0 / (SELECT COUNT(*) FROM partido) AS porcentaje
FROM partido
GROUP BY estado;

/* Obtener los 10 jugadores con mas goles, sin contar los autogoles */
SELECT jugador.nombre, jugador.apellido, COUNT(*) AS cantidad_goles
FROM jugador
JOIN gol ON jugador.ci = gol.ci_jugador
WHERE gol.autogol = FALSE
GROUP BY jugador.ci, jugador.nombre, jugador.apellido
ORDER BY cantidad_goles DESC
LIMIT 10;

/* Obtener los jugadores inscriptos que nunca jugaron un partido */
SELECT jugador.nombre, jugador.apellido
FROM jugador
JOIN equipo_jugador_torneo
ON jugador.ci = equipo_jugador_torneo.ci_jugador
LEFT JOIN planilla_partido
ON jugador.ci = planilla_partido.ci_jugador
WHERE planilla_partido.ci_jugador IS NULL;

/* Obtener los puntos de fair play de cada equipo */
SELECT equipo.nombre,
       COUNT(IF(tarjeta.color = 'amarilla', tarjeta.id_tarjeta, NULL)) AS amarillas,
       COUNT(IF(tarjeta.color = 'roja', tarjeta.id_tarjeta, NULL)) AS rojas,
       COUNT(IF(tarjeta.color = 'amarilla', tarjeta.id_tarjeta, NULL)) +
       COUNT(IF(tarjeta.color = 'roja', tarjeta.id_tarjeta, NULL)) * 3 AS puntos
FROM equipo
LEFT JOIN planilla_partido
ON equipo.id_equipo = planilla_partido.id_equipo
LEFT JOIN tarjeta
ON planilla_partido.id_partido = tarjeta.id_partido
AND planilla_partido.ci_jugador = tarjeta.ci_jugador
GROUP BY equipo.id_equipo, equipo.nombre
ORDER BY puntos ASC;

/* Obtener el promedio de goles por partido en cada fecha */
SELECT partido.numero_fecha,
       COUNT(gol.id_gol) AS cantidad_goles,
       COUNT(gol.id_gol) / COUNT(DISTINCT partido.id_partido) AS promedio_goles
FROM partido
LEFT JOIN gol ON partido.id_partido = gol.id_partido
WHERE partido.estado = 'jugado'
GROUP BY partido.numero_fecha
ORDER BY partido.numero_fecha;

/* Obtener el promedio de goles por partido en el torneo */
SELECT COUNT(gol.id_gol) AS cantidad_goles,
       COUNT(gol.id_gol) / COUNT(DISTINCT partido.id_partido) AS promedio_goles
FROM partido
LEFT JOIN gol ON partido.id_partido = gol.id_partido
WHERE partido.estado = 'jugado';

/* Obtener el resultado de cada partido jugado, incluyendo autogoles */
CREATE OR REPLACE VIEW resultado_partidos AS
SELECT partido.id_partido,
       local.nombre AS equipo_local,
       visitante.nombre AS equipo_visitante,
       COUNT(IF(
           (planilla_partido.id_equipo = partido.id_equipo_local AND gol.autogol = FALSE)
           OR
           (planilla_partido.id_equipo = partido.id_equipo_visitante AND gol.autogol = TRUE),
           gol.id_gol, NULL
       )) AS goles_local,
       COUNT(IF(
           (planilla_partido.id_equipo = partido.id_equipo_visitante AND gol.autogol = FALSE)
           OR
           (planilla_partido.id_equipo = partido.id_equipo_local AND gol.autogol = TRUE),
           gol.id_gol, NULL
       )) AS goles_visitante
FROM partido
JOIN equipo local ON partido.id_equipo_local = local.id_equipo
JOIN equipo visitante ON partido.id_equipo_visitante = visitante.id_equipo
LEFT JOIN gol ON partido.id_partido = gol.id_partido
LEFT JOIN planilla_partido
ON gol.id_partido = planilla_partido.id_partido
AND gol.ci_jugador = planilla_partido.ci_jugador
WHERE partido.estado = 'jugado'
GROUP BY partido.id_partido, local.nombre, visitante.nombre;

/* Obtener los goles a favor y en contra de cada equipo */
CREATE OR REPLACE VIEW goles_equipos AS
SELECT equipo.id_equipo, equipo.nombre,
       IF(equipo.id_equipo = partido.id_equipo_local,
          resultado_partidos.goles_local,
          resultado_partidos.goles_visitante) AS GF,
       IF(equipo.id_equipo = partido.id_equipo_local,
          resultado_partidos.goles_visitante,
          resultado_partidos.goles_local) AS GC
FROM equipo
JOIN partido
ON equipo.id_equipo = partido.id_equipo_local
OR equipo.id_equipo = partido.id_equipo_visitante
JOIN resultado_partidos
ON partido.id_partido = resultado_partidos.id_partido;

/* Obtener la tabla de posiciones del torneo */
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
ORDER BY puntos DESC, DG DESC, GF DESC;

/* Obtener el partido con mayor cantidad de goles */
SELECT equipo_local, equipo_visitante,
       goles_local, goles_visitante,
       goles_local + goles_visitante AS total_goles
FROM resultado_partidos
ORDER BY total_goles DESC
LIMIT 1;

/* Obtener los jugadores que recibieron mas tarjetas */
SELECT jugador.nombre, jugador.apellido,
       COUNT(tarjeta.id_tarjeta) AS cantidad_tarjetas
FROM jugador
JOIN tarjeta ON jugador.ci = tarjeta.ci_jugador
GROUP BY jugador.ci, jugador.nombre, jugador.apellido
ORDER BY cantidad_tarjetas DESC;

/* Obtener el equipo con mas goles a favor */
SELECT nombre, SUM(GF) AS total_goles
FROM goles_equipos
GROUP BY id_equipo, nombre
ORDER BY total_goles DESC
LIMIT 1;
