CREATE USER 'admin'@'localhost'
IDENTIFIED BY 'contrasena';

GRANT ALL PRIVILEGES
ON obligatorio_bd.*
TO 'admin'@'loccalhost';

CREATE USER 'planillero'@'localhost'
IDENTIFIED BY 'contrasena';

GRANT INSERT,UPDATE, DELETE
on obligatorio_bd.gol
TO 'planillero'@'localhost';

GRANT INSERT, UPDATE, DELETE
ON obligatorio_bd.planilla_partido
TO 'planillero'@'localhost';

GRANT INSERT,UPDATE, DELETE
on obligatorio_bd.tarjeta   
TO 'planillero'@'localhost';

GRANT SELECT
ON obligatorio_bd.*
TO 'planillero'@'localhost';