import psycopg2
import logging

# Configurar el sistema de registro para errores
logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(message)s')

# Configurar el sistema de registro para información de proceso
process_logger = logging.getLogger('process_logger')
process_logger.setLevel(logging.INFO)
process_handler = logging.FileHandler('process.log')
process_formatter = logging.Formatter('%(asctime)s - %(message)s')
process_handler.setFormatter(process_formatter)
process_logger.addHandler(process_handler)

# Limpiar los archivos de logs antes de ejecutar el script
open('error.log', 'w').close()
open('process.log', 'w').close()

# Conexión a la primera base de datos (de donde obtendrás los registros)
conn_source = psycopg2.connect(
    dbname="postgres",
    user="base1_usr",
    password="riendel22",
    host="localhost",  # o la dirección IP del servidor donde se encuentra la base de datos
    port="5432"
)

# Conexión a la segunda base de datos (donde insertarás los registros)
conn_destination = psycopg2.connect(
    dbname="postgres",
    user="base2_usr",
    password="riendel22",
    host="localhost",  # o la dirección IP del servidor donde se encuentra la base de datos
    port="5433"
)

# Crear un cursor para la base de datos de origen
cur_source = conn_source.cursor()

# Crear un cursor para la base de datos de destino
cur_destination = conn_destination.cursor()

# Consulta SQL para recuperar los registros en lotes de 100
batch_size = 10000
offset = 0

try:
    # Iniciar la transacción en la base de datos de destino
    conn_destination.autocommit = False
    
    while True:  # Bucle infinito para iterar hasta que no haya más registros
        # Consulta SQL con OFFSET y LIMIT para obtener el siguiente lote de registros
        query = f"SELECT * FROM mi_tabla OFFSET {offset} LIMIT {batch_size};"
        
        # Log de proceso: indica en qué bucle de registros está trabajando
        process_logger.info(f"Trabajando en el bucle de registros desde {offset + 1}")
        
        # Ejecutar la consulta en la base de datos de origen
        cur_source.execute(query)
        
        # Obtener los registros recuperados
        records = cur_source.fetchall()
        
        # Si no hay más registros, salir del bucle
        if not records:
            break
        
        # Insertar los registros en la base de datos de destino dentro de una transacción
        for record in records:
            # Aquí, asumiendo que tienes una tabla llamada 'nombre_tabla_destino' en la base de datos de destino
            insert_query = "INSERT INTO mi_tabla VALUES (%s, %s, %s, %s);"  # ajusta la consulta según tu esquema
            try:
                cur_destination.execute(insert_query, record)
            except Exception as e:
                # Registrar el error en el archivo de logs
                logging.error(f"Error al insertar registro: {record} - {str(e)}")
                # Continuar con el siguiente registro
                continue
            else:
                conn_destination.commit()  # Confirmar la transacción si no hay error
        
        # Actualizar el desplazamiento para el próximo lote
        offset += batch_size

except Exception as e:
    # Si ocurre un error, hacer rollback y manejar la excepción
    conn_destination.rollback()
    logging.error(f"Error: {str(e)}")

finally:
    # Restaurar el modo de autocommit y cerrar los cursores y las conexiones
    conn_destination.autocommit = True
    cur_source.close()
    cur_destination.close()
    conn_source.close()
    conn_destination.close()
