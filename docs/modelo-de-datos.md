# Modelo de datos

## Tablas y atributos

### Personas
- **login**: correo, contrasena, rol
- **facultad**: id_facultad, nombre
- **jugador**: ci, nombre, apellido, email, fecha_nacimiento, id_facultad, tipo

### Torneo y equipos
- **torneo**: id_torneo, nombre, anio, semestre, fecha_inicio, fecha_fin, estado
- **equipo**: id_equipo, nombre, id_torneo, id_facultad, ci_capitan
- **equipo_jugador_torneo**: id_equipo, ci_jugador, id_torneo, numero_camiseta

### Lugares y horarios
- **complejo**: id_complejo, nombre, direccion, departamento
- **cancha**: nombre_cancha, id_complejo, superficie, techada
- **turno**: id_turno, hora_inicio, hora_fin

### Partidos
- **partido**: id_partido, id_torneo, numero_fecha, id_equipo_local, id_equipo_visitante, dia, id_turno, nombre_cancha, id_complejo, estado
- **planilla_partido**: id_partido, ci_jugador, id_equipo
- **gol**: id_gol, id_partido, ci_jugador, minuto, autogol
- **tarjeta**: id_tarjeta, id_partido, ci_jugador, minuto, color

### Sanciones
- **sancion_jugador**: id_sancion, ci_jugador, id_torneo, motivo, numero_fecha_inicio, cantidad_fechas
