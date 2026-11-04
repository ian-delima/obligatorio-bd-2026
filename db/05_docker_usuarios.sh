#!/bin/sh
set -eu

export MYSQL_PWD="$MYSQL_ROOT_PASSWORD"

mysql -uroot <<SQL
CREATE USER IF NOT EXISTS 'admin'@'%' IDENTIFIED BY '${DB_ADMIN_PASS}';
CREATE USER IF NOT EXISTS 'planillero'@'%' IDENTIFIED BY '${DB_PLANILLERO_PASS}';

GRANT ALL PRIVILEGES ON obligatorio_bd.* TO 'admin'@'%';

GRANT SELECT ON obligatorio_bd.* TO 'planillero'@'%';
GRANT INSERT, UPDATE, DELETE ON obligatorio_bd.planilla_partido TO 'planillero'@'%';
GRANT INSERT, UPDATE, DELETE ON obligatorio_bd.gol TO 'planillero'@'%';
GRANT INSERT, UPDATE, DELETE ON obligatorio_bd.tarjeta TO 'planillero'@'%';
GRANT INSERT ON obligatorio_bd.sancion_jugador TO 'planillero'@'%';
SQL

unset MYSQL_PWD