import os
import sqlite3

def borrar_tabla_claves():
    base_path = os.path.join('EncryptU','src', 'database')
    db_path = os.path.join(base_path, 'claves_maestras.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS claves")
    conn.commit()
    conn.close()
    print("Tabla 'claves' borrada completamente")

def crear_base_datos():
    base_path = os.path.join('EncryptU','src', 'database')
    os.makedirs(base_path, exist_ok=True)
    db_path = os.path.join(base_path, 'claves_maestras.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS claves (
        sitio_web TEXT NOT NULL UNIQUE,
        clave_maestra TEXT NOT NULL
    )
    ''')

    conn.commit()
    conn.close()
    print("Base de datos creada correctamente")

if __name__ == "__main__":
    borrar_tabla_claves() 
    crear_base_datos()      
