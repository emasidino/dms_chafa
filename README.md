# dms_chafa

1. Instalar dependecias de Python

    python3 -m pip install psycopg2


2. Ejecutar docker-compose.yml -d

3. Conectar a la base de datos 1

    psql -U base1_usr -h 127.0.0.1 -p 5432 postgres

4. Crear base de datos

    CREATE DATABASE db_prueba;

5. Crear tabla de prueba

    CREATE TABLE mi_tabla (
        id SERIAL PRIMARY KEY,
        existe VARCHAR(50),
        folio INTEGER,
        ingresado TIMESTAMP
    );

6. Insertar 100 mil registros de datos reandom\

    INSERT INTO mi_tabla (existe, folio, ingresado)
    SELECT 
        md5(random()::text),
        floor(random() * 10000) + 1,
        CURRENT_TIMESTAMP - (random() * 365 * 10) * INTERVAL '1 day'
    FROM generate_series(1, 100000) ON CONFLICT DO NOTHING;


7. Conectar a la base de datos 2

    psql base2_usr -h 127.0.0.1 -p 5433 postgres


8. Repetir pasos 4 y 5

9. Ejecutar python3 copy.py

10. Revisar archivos de logs process.log para ver la copia de los lotes y el archivo error.lo que indicara los registros repetidos que se ha evitado.
