import sqlite3
import os

def crear_base_datos():

    # Definir la ruta para crear la base de datos dentro de EncryptU/src/database
    base_path = os.path.join('src', 'database')
    os.makedirs(base_path, exist_ok=True)  # Crear el directorio si no existe

    # Definir el archivo de la base de datos con la ruta completa
    db_path = os.path.join(base_path, 'claves_maestras.db')

    # Conectar a la base de datos (se crea si no existe)
    conn = sqlite3.connect(db_path)
    
    cursor = conn.cursor()

    query =(''' DROP TABLE if exists claves
                ''')
    cursor.execute(query)
    
    # Crear la tabla con el campo único que acepta varios caracteres
    cursor.execute('''CREATE TABLE IF NOT EXISTS claves ( 
                        clave_maestra TEXT NOT NULL UNIQUE)''')
    # Comando para rescatar el nombre de las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type ='table'")
    print (cursor.fetchall())

    conn.commit()
    conn.close()
    print("Base de datos creada correctamente")

def insertar_clave(clave):

    base_path = os.path.join('src', 'database')
    db_path = os.path.join(base_path, 'claves_maestras.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO claves (clave_maestra) VALUES (?)", (clave,))
        conn.commit()
        print("Clave insertada correctamente")
    except sqlite3.IntegrityError:
        print("Error: Esta clave ya existe en la base de datos")
    finally:
        conn.close()

# Ejemplo de uso
if __name__ == "__main__":
    crear_base_datos()
    
    # Insertar claves con diferentes caracteres
    insertar_clave("Clave123#$@")
    insertar_clave("Otra#Clave@987")
    insertar_clave("mix!@#$%123ABC")
