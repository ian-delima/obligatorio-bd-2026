use obligatorio_bd;

INSERT INTO facultad (nombre)
VALUES
('Ingenieria'),
('Derecho'),
('Medicina'),
('Arquitectura'),
('Psicologia'),
('Ciencias Empresariales');

INSERT INTO turno (hora_inicio, hora_fin)
VALUES
('18:00:00', '19:00:00'),
('19:00:00', '20:00:00'),
('20:00:00', '21:00:00'),
('21:00:00', '22:00:00'),
('22:00:00', '23:00:00');


INSERT INTO complejo (nombre, direccion, departamento)
VALUES
('Arena 5', 'Martin Fierro 2470', 'Montevideo'),
('Supermatch 5', 'Valencia 1961', 'Montevideo'),
('Cordon Futbol 5', 'Av. Uruguay 1998', 'Montevideo');

INSERT INTO cancha
(nombre_cancha, id_complejo, superficie, techada)
VALUES
('Cancha 1', 1, 'sintetico', TRUE),
('Cancha 2', 1, 'sintetico', TRUE),
('Cancha 3', 1, 'sintetico', TRUE),
('Cancha 4', 1, 'sintetico', TRUE);

INSERT INTO cancha
(nombre_cancha, id_complejo, superficie, techada)
VALUES
('Cancha 1', 2, 'sintetico', TRUE),
('Cancha 2', 2, 'sintetico', TRUE);

INSERT INTO cancha
(nombre_cancha, id_complejo, superficie, techada)
VALUES
('Cancha 1', 3, 'sintetico', TRUE),
('Cancha 2', 3, 'sintetico', TRUE);


INSERT INTO jugador
(ci, nombre, apellido, fecha_nacimiento, id_facultad, tipo)
VALUES
(90000001, 'Juan', 'Medina', '2005-04-12', 1, 'grado'),
(90000002, 'Santiago', 'Ripa', '2004-08-20', 1, 'grado'),
(90000003, 'Valentin', 'Guerrico', '2006-10-10', 1, 'grado'),
(90000004, 'Alejo', 'Silveira', '2005-02-15', 1, 'grado'),
(90000005, 'Cristiano', 'Ronaldo', '2003-06-18', 1, 'posgrado'),


(90000006, 'Lionel', 'Messi', '2004-09-25', 2, 'grado'),
(90000007, 'German', 'Caubarrere', '2005-01-10', 2, 'grado'),
(90000008, 'Lucio', 'Lasso', '2004-03-14', 2, 'grado'),
(90000009, 'Luis', 'Suarez', '2003-07-21', 2, 'posgrado'),
(90000010, 'Martin', 'Rodriguez', '2005-11-08', 2, 'grado'),


(90000011, 'Lucas', 'Fernandez', '2004-05-16', 3, 'grado'),
(90000012, 'Mateo', 'Pereira', '2005-09-02', 3, 'grado'),
(90000013, 'Facundo', 'Gonzalez', '2003-12-11', 3, 'posgrado'),
(90000014, 'Agustin', 'Lopez', '1985-06-23', 3, 'docente'),
(90000015, 'Nicolas', 'Torres', '2004-04-30', 3, 'grado'),


(90000016, 'Joaquin', 'Martinez', '2005-01-19', 4, 'grado'),
(90000017, 'Bruno', 'Garcia', '2004-07-07', 4, 'grado'),
(90000018, 'Franco', 'Diaz', '2003-10-12', 4, 'posgrado'),
(90000019, 'Sebastian', 'Castro', '2005-02-28', 4, 'grado'),
(90000020, 'Diego', 'Morales', '1988-08-15', 4, 'funcionario'),


(90000021, 'Tomas', 'Silva', '2004-11-05', 5, 'grado'),
(90000022, 'Ignacio', 'Romero', '2005-06-17', 5, 'grado'),
(90000023, 'Emiliano', 'Acosta', '2003-03-22', 5, 'posgrado'),
(90000024, 'Federico', 'Sosa', '2004-09-13', 5, 'grado'),
(90000025, 'Andres', 'Varela', '1982-12-09', 5, 'docente'),


(90000026, 'Maximiliano', 'Perez', '2005-05-24', 6, 'grado'),
(90000027, 'Rodrigo', 'Alvarez', '2004-02-18', 6, 'grado'),
(90000028, 'Gonzalo', 'Mendez', '2003-07-09', 6, 'posgrado'),
(90000029, 'Matias', 'Cabrera', '2005-08-31', 6, 'grado'),
(90000030, 'Daniel', 'Suarez', '1987-04-20', 6, 'funcionario');

INSERT INTO torneo
(nombre, anio, semestre, fecha_inicio, fecha_fin, estado)
VALUES
('Torneo Interfacultades 2026', 2026, 2,
 '2026-09-01', '2026-11-30', 'en curso');

INSERT INTO equipo
(nombre, id_torneo, id_facultad)
VALUES
('Ingenieria FC', 1, 1),
('Derecho FC', 1, 2),
('Medicina FC', 1, 3),
('Arquitectura FC', 1, 4),
('Psicologia FC', 1, 5),
('Empresariales FC', 1, 6);

INSERT INTO equipo_jugador_torneo
(id_equipo, ci_jugador, id_torneo, numero_camiseta)
VALUES
(1, 90000001, 1, 8),
(1, 90000002, 1, 10),
(1, 90000003, 1, 7),
(1, 90000004, 1, 9),
(1, 90000005, 1, 11),

(2, 90000006, 1, 10),
(2, 90000007, 1, 7),
(2, 90000008, 1, 8),
(2, 90000009, 1, 9),
(2, 90000010, 1, 11),

(3, 90000011, 1, 10),
(3, 90000012, 1, 7),
(3, 90000013, 1, 8),
(3, 90000014, 1, 9),
(3, 90000015, 1, 11),

(4, 90000016, 1, 10),
(4, 90000017, 1, 7),
(4, 90000018, 1, 8),
(4, 90000019, 1, 9),
(4, 90000020, 1, 11),

(5, 90000021, 1, 10),
(5, 90000022, 1, 7),
(5, 90000023, 1, 8),
(5, 90000024, 1, 9),
(5, 90000025, 1, 11),

(6, 90000026, 1, 10),
(6, 90000027, 1, 7),
(6, 90000028, 1, 8),
(6, 90000029, 1, 9),
(6, 90000030, 1, 11);

UPDATE equipo
SET ci_capitan = 90000003
WHERE id_equipo = 1;

UPDATE equipo
SET ci_capitan = 90000006
WHERE id_equipo = 2;

UPDATE equipo
SET ci_capitan = 90000011
WHERE id_equipo = 3;

UPDATE equipo
SET ci_capitan = 90000016
WHERE id_equipo = 4;

UPDATE equipo
SET ci_capitan = 90000021
WHERE id_equipo = 5;

UPDATE equipo
SET ci_capitan = 90000026
WHERE id_equipo = 6;

UPDATE jugador
SET nombre = 'Angel', apellido = 'Caffa'
WHERE ci = 90000010;

UPDATE jugador
SET nombre = 'Geronimo', apellido = 'Sosa'
WHERE ci = 90000012;

UPDATE jugador
SET nombre = 'Geronimo', apellido = 'Benavidez'
WHERE ci = 90000017;

INSERT INTO partido
(id_torneo, numero_fecha, id_equipo_local,
 id_equipo_visitante, dia, id_turno,
 nombre_cancha, id_complejo, estado)
VALUES
(1, 1, 1, 2, '2026-10-10', 1, 'Cancha 1', 1, 'jugado'),
(1, 1, 3, 4, '2026-10-10', 2, 'Cancha 2', 1, 'jugado'),
(1, 1, 5, 6, '2026-10-10', 3, 'Cancha 1', 2, 'jugado');

INSERT INTO partido
(id_torneo, numero_fecha, id_equipo_local,
 id_equipo_visitante, dia, id_turno,
 nombre_cancha, id_complejo, estado)
VALUES
(1, 2, 1, 3, '2026-10-17', 1, 'Cancha 1', 1, 'jugado'),
(1, 2, 2, 5, '2026-10-17', 2, 'Cancha 2', 1, 'jugado'),
(1, 2, 4, 6, '2026-10-17', 3, 'Cancha 1', 2, 'jugado');

INSERT INTO partido
(id_torneo, numero_fecha, id_equipo_local,
 id_equipo_visitante, dia, id_turno,
 nombre_cancha, id_complejo, estado)
VALUES
(1, 3, 1, 5, '2026-10-24', 1, 'Cancha 1', 1, 'jugado'),
(1, 3, 2, 4, '2026-10-24', 2, 'Cancha 2', 1, 'jugado'),
(1, 3, 3, 6, '2026-10-24', 3, 'Cancha 1', 2, 'jugado');

/*Insertamos 3 jugadores mas por equipo*/
INSERT INTO jugador
(ci, nombre, apellido, fecha_nacimiento, id_facultad, tipo)
VALUES
/*Ingenieria*/
(90000031, 'Thiago', 'Bentancur', '2004-03-12', 1, 'grado'),
(90000032, 'Bautista', 'Olivera', '2005-07-18', 1, 'grado'),
(90000033, 'Ramiro', 'Fagundez', '2003-11-24', 1, 'posgrado'),

/*Derecho*/
(90000034, 'Lautaro', 'Machado', '2005-01-15', 2, 'grado'),
(90000035, 'Enzo', 'Villalba', '2004-09-21', 2, 'grado'),
(90000036, 'Felipe', 'Cardozo', '2003-06-08', 2, 'posgrado'),

/*Medicina*/
(90000037, 'Dante', 'Ferreira', '2005-05-14', 3, 'grado'),
(90000038, 'Axel', 'Pintos', '2004-12-03', 3, 'grado'),
(90000039, 'Kevin', 'Duarte', '2003-08-27', 3, 'posgrado'),

/*Arquitectura*/
(90000040, 'Iker', 'Barrios', '2005-04-19', 4, 'grado'),
(90000041, 'Alan', 'Perdomo', '2004-10-11', 4, 'grado'),
(90000042, 'Ezequiel', 'Molina', '2003-02-26', 4, 'posgrado'),

/*Psicologia*/
(90000043, 'Santino', 'Correa', '2005-06-07', 5, 'grado'),
(90000044, 'Fabricio', 'Techera', '2004-01-29', 5, 'grado'),
(90000045, 'Leandro', 'Nunez', '2003-09-16', 5, 'posgrado'),

/*Ciencias Empresariales*/
(90000046, 'Benicio', 'Ramos', '2005-08-13', 6, 'grado'),
(90000047, 'Francesco', 'Medina', '2004-05-22', 6, 'grado'),
(90000048, 'Ulises', 'Sanchez', '2003-12-04', 6, 'posgrado');


/*Insertamos los jugadores en sus equipos para el torneo*/
INSERT INTO equipo_jugador_torneo
(id_equipo, ci_jugador, id_torneo, numero_camiseta)
VALUES
/*Ingenieria*/
(1, 90000031, 1, 12),
(1, 90000032, 1, 13),
(1, 90000033, 1, 14),

/*Derecho*/
(2, 90000034, 1, 12),
(2, 90000035, 1, 13),
(2, 90000036, 1, 14),

/*Medicina*/
(3, 90000037, 1, 12),
(3, 90000038, 1, 13),
(3, 90000039, 1, 14),

/*Arquitectura*/
(4, 90000040, 1, 12),
(4, 90000041, 1, 13),
(4, 90000042, 1, 14),

/*Psicologia*/
(5, 90000043, 1, 12),
(5, 90000044, 1, 13),
(5, 90000045, 1, 14),

/*Empresariales*/
(6, 90000046, 1, 12),
(6, 90000047, 1, 13),
(6, 90000048, 1, 14);



INSERT INTO planilla_partido
(id_partido, ci_jugador, id_equipo)
VALUES
(1, 90000001, 1),
(1, 90000002, 1),
(1, 90000003, 1),
(1, 90000004, 1),
(1, 90000005, 1),
(1, 90000006, 2),
(1, 90000007, 2),
(1, 90000008, 2),
(1, 90000009, 2),
(1, 90000010, 2);

INSERT INTO planilla_partido
(id_partido, ci_jugador, id_equipo)
VALUES
(2, 90000011, 3),
(2, 90000012, 3),
(2, 90000013, 3),
(2, 90000014, 3),
(2, 90000015, 3),

(2, 90000016, 4),
(2, 90000017, 4),
(2, 90000018, 4),
(2, 90000019, 4),
(2, 90000020, 4);

INSERT INTO planilla_partido
(id_partido, ci_jugador, id_equipo)
VALUES
(3, 90000021, 5),
(3, 90000022, 5),
(3, 90000023, 5),
(3, 90000024, 5),
(3, 90000025, 5),

(3, 90000026, 6),
(3, 90000027, 6),
(3, 90000028, 6),
(3, 90000029, 6),
(3, 90000030, 6);

INSERT INTO planilla_partido
(id_partido, ci_jugador, id_equipo)
VALUES
(4, 90000001, 1),
(4, 90000002, 1),
(4, 90000003, 1),
(4, 90000004, 1),
(4, 90000005, 1),

(4, 90000011, 3),
(4, 90000012, 3),
(4, 90000013, 3),
(4, 90000037, 3),
(4, 90000015, 3);

INSERT INTO planilla_partido
(id_partido, ci_jugador, id_equipo)
VALUES
(5, 90000006, 2),
(5, 90000007, 2),
(5, 90000008, 2),
(5, 90000009, 2),
(5, 90000010, 2),

(5, 90000021, 5),
(5, 90000022, 5),
(5, 90000023, 5),
(5, 90000024, 5),
(5, 90000025, 5);

INSERT INTO planilla_partido
(id_partido, ci_jugador, id_equipo)
VALUES
(6, 90000016, 4),
(6, 90000017, 4),
(6, 90000018, 4),
(6, 90000019, 4),
(6, 90000020, 4),

(6, 90000026, 6),
(6, 90000027, 6),
(6, 90000028, 6),
(6, 90000029, 6),
(6, 90000030, 6);

INSERT INTO planilla_partido
(id_partido, ci_jugador, id_equipo)
VALUES
(7, 90000001, 1),
(7, 90000002, 1),
(7, 90000003, 1),
(7, 90000004, 1),
(7, 90000005, 1),

(7, 90000021, 5),
(7, 90000022, 5),
(7, 90000023, 5),
(7, 90000024, 5),
(7, 90000025, 5);

INSERT INTO planilla_partido
(id_partido, ci_jugador, id_equipo)
VALUES
(8, 90000006, 2),
(8, 90000007, 2),
(8, 90000008, 2),
(8, 90000009, 2),
(8, 90000010, 2),

(8, 90000016, 4),
(8, 90000017, 4),
(8, 90000018, 4),
(8, 90000019, 4),
(8, 90000040, 4);

INSERT INTO planilla_partido
(id_partido, ci_jugador, id_equipo)
VALUES
(9, 90000011, 3),
(9, 90000012, 3),
(9, 90000013, 3),
(9, 90000014, 3),
(9, 90000015, 3),

(9, 90000026, 6),
(9, 90000027, 6),
(9, 90000028, 6),
(9, 90000029, 6),
(9, 90000030, 6);

/* Insertamos los goles de cada partido*/

    /* Goles partido 1 */
INSERT INTO gol
(id_partido, ci_jugador, minuto, autogol)
VALUES
(1, 90000003, 10, FALSE),
(1, 90000005, 22, FALSE),
(1, 90000001, 45, FALSE),
(1, 90000006, 30, FALSE),
(1, 90000009, 52, FALSE);

    /* Goles partido 2 */
INSERT INTO gol
(id_partido, ci_jugador, minuto, autogol)
VALUES
(2, 90000011, 12, FALSE),
(2, 90000012, 38, FALSE),
(2, 90000016, 50, FALSE);

    /* Goles partido 3 */
INSERT INTO gol
(id_partido, ci_jugador, minuto, autogol)
VALUES
(3, 90000021, 10, FALSE),
(3, 90000022, 25, FALSE),
(3, 90000026, 35, FALSE),
(3, 90000024, 48, TRUE);

    /* Goles partido 4 */
INSERT INTO gol
(id_partido, ci_jugador, minuto, autogol)
VALUES
(4, 90000003, 15, FALSE),
(4, 90000002, 40, FALSE),
(4, 90000012, 53, FALSE);

    /* Goles partido 5 */
INSERT INTO gol
(id_partido, ci_jugador, minuto, autogol)
VALUES
(5, 90000006, 8, FALSE),
(5, 90000009, 20, FALSE),
(5, 90000010, 42, FALSE),
(5, 90000021, 55, FALSE);

    /* Goles partido 6 */
INSERT INTO gol
(id_partido, ci_jugador, minuto, autogol)
VALUES
(6, 90000016, 18, FALSE),
(6, 90000026, 32, FALSE),
(6, 90000028, 49, FALSE);

    /* Goles partido 7 */
INSERT INTO gol
(id_partido, ci_jugador, minuto, autogol)
VALUES
(7, 90000003, 8, FALSE),
(7, 90000005, 17, FALSE),
(7, 90000002, 30, FALSE),
(7, 90000003, 48, FALSE),
(7, 90000021, 55, FALSE);

    /* Goles partido 8 */
INSERT INTO gol
(id_partido, ci_jugador, minuto, autogol)
VALUES
(8, 90000006, 12, FALSE),
(8, 90000010, 36, FALSE),
(8, 90000016, 24, FALSE),
(8, 90000017, 51, FALSE);

    /* Goles partido 9 */
INSERT INTO gol
(id_partido, ci_jugador, minuto, autogol)
VALUES
(9, 90000012, 15, FALSE),
(9, 90000026, 22, FALSE),
(9, 90000027, 37, FALSE),
(9, 90000028, 54, FALSE);


/* Tarjetas de las fechas 1, 2 y 3 */
INSERT INTO tarjeta
(id_partido, ci_jugador, minuto, color)
VALUES
(1, 90000002, 20, 'amarilla'),
(1, 90000007, 35, 'amarilla'),
(2, 90000014, 40, 'roja'),
(3, 90000023, 25, 'amarilla'),

/*Tarjetas de la fecha 2*/
(4, 90000002, 30, 'amarilla'),
(5, 90000007, 45, 'amarilla'),
(6, 90000020, 50, 'roja'),

/*Tarjetas de la fecha 3*/
(7, 90000002, 28, 'amarilla'),
(8, 90000007, 32, 'amarilla'),
(9, 90000027, 42, 'roja');

/*Agregamos las sanciones en la tabla*/
INSERT INTO sancion_jugador
(ci_jugador, id_torneo, motivo, numero_fecha_inicio, cantidad_fechas)
VALUES
(90000014, 1, 'roja', 2, 1),
(90000020, 1, 'roja', 3, 1),
(90000027, 1, 'roja', 4, 1),
(90000002, 1, 'acumulacion de amarillas', 4, 1),
(90000007, 1, 'acumulacion de amarillas', 4, 1);

INSERT INTO sancion_jugador
(ci_jugador, id_torneo, motivo, numero_fecha_inicio, cantidad_fechas)
VALUES
(90000018, 1, 'disciplinaria', 4, 2);



INSERT INTO partido
(id_torneo, numero_fecha, id_equipo_local,
 id_equipo_visitante, dia, id_turno,
 nombre_cancha, id_complejo, estado)
VALUES
(1, 4, 1, 4, '2026-11-07', 1, 'Cancha 1', 1, 'programado'),
(1, 4, 2, 6, '2026-11-07', 2, 'Cancha 2', 1, 'programado'),
(1, 4, 3, 5, '2026-11-07', 3, 'Cancha 1', 2, 'postergado');


INSERT INTO partido
(id_torneo, numero_fecha, id_equipo_local,
 id_equipo_visitante, dia, id_turno,
 nombre_cancha, id_complejo, estado)
VALUES
(1, 5, 1, 6, '2026-11-14', 1, 'Cancha 1', 1, 'programado'),
(1, 5, 2, 3, '2026-11-14', 2, 'Cancha 2', 1, 'programado'),
(1, 5, 4, 5, '2026-11-14', 3, 'Cancha 1', 2, 'cancelado');
