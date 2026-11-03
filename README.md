# Obligatorio Base de Datos 1 – 2° semestre 2026

Sistema de gestión del Torneo Interfacultades de Fútbol 5 de la Universidad Católica del Uruguay.

Permite organizar el fixture, registrar resultados, planillas y sanciones, y generar reportes del torneo.

## Integrantes

- Ian de Lima
- Santiago Ripa
- Valentín Guerrico

## Tecnologías

- Base de datos: MySQL
- Backend: Python (sin ORM)
- Frontend: a definir

## Estructura del repositorio

| Carpeta     | Contenido                                       |
|-------------|-------------------------------------------------|
| `db/`       | Scripts SQL: creación, datos de prueba, usuarios y reportes |
| `backend/`  | Aplicación en Python                            |
| `frontend/` | Interfaz de usuario                             |
| `docs/`     | Informe, bitácora y documentación               |

## Cómo ejecutar

## Ejecución con Docker

Para ejecutar el sistema completo se necesita tener Docker Desktop instalado y funcionando.

1. Clonar el repositorio.
2. Copiar el archivo `.env.docker.example` con el nombre `.env.docker`.
3. Configurar las contraseñas y la clave secreta en `.env.docker`.
4. Desde la carpeta principal del proyecto, ejecutar:

```bash
docker compose --env-file .env.docker up --build -d
```

5. Abrir la aplicación en http://localhost:5001.

**Usuarios de prueba de la aplicación:**

- Administrador: `admin@ucu.edu.uy` / `admin123`
- Planillero: `planillero@ucu.edu.uy` / `planillero123`

**Para detener los contenedores:**

```bash
docker compose --env-file .env.docker down
```

**Para volver a iniciarlos:**

```bash
docker compose --env-file .env.docker up -d
```

Los datos se conservan en un volumen de Docker. No utilizar `down -v` si se desea conservarlos.

Los scripts SQL se ejecutan automáticamente cuando se crea la base de datos por primera vez.
