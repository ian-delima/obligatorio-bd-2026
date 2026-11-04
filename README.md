# Obligatorio Base de Datos 1 – 2° semestre 2026

Sistema de gestión del Torneo Interfacultades de Fútbol 5 de la Universidad Católica del Uruguay.

Permite organizar el fixture, registrar resultados, planillas y sanciones, y generar reportes del torneo.

## Integrantes

- Ian de Lima
- Santiago Ripa
- Valentín Guerrico

## Tecnologías

- Base de datos: MySQL 8
- Backend: Python con Flask y mysql-connector-python (sin ORM)
- Frontend: plantillas de Flask (HTML, CSS y JavaScript)
- Ejecución opcional con Docker y Docker Compose

## Estructura del repositorio

| Carpeta             | Contenido                                                        |
|---------------------|------------------------------------------------------------------|
| `db/`               | Scripts SQL: creación, datos de prueba, usuarios y reportes      |
| `backend/`          | Aplicación Flask: rutas, reglas de negocio y acceso a datos      |
| `backend/templates` | Páginas HTML del frontend                                        |
| `backend/static`    | Estilos y JavaScript del frontend                                |
| `docs/`             | Documentación del modelo de datos                                |

## Usuarios de prueba

- Administrador: `admin@ucu.edu.uy` / `admin123`
- Planillero: `planillero@ucu.edu.uy` / `planillero123`

## Ejecución local

Requisitos: Python 3 y MySQL 8.

1. Clonar el repositorio.
2. Ejecutar los scripts de la carpeta `db/` en este orden: `01_schema.sql`, `02_datos.sql`, `03_usuarios.sql` y `04_reportes.sql`.
3. Copiar `backend/.env.example` con el nombre `backend/.env` y completar los datos de conexión. Los usuarios de MySQL que crea `03_usuarios.sql` son `admin` y `planillero`, ambos con la contraseña `contrasena`.
4. Instalar las dependencias:

```bash
pip install -r backend/requirements.txt
```

5. Desde la carpeta `backend/`, iniciar la aplicación:

```bash
python app.py
```

6. Abrir http://127.0.0.1:5000

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