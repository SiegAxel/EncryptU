import sqlite3
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.crypto.encryption import encriptar_contraseña

def crear_base_datos():
    base_path = os.path.join('EncryptU', 'src', 'database') #Este path me jodio la vida, me faltó solo el 'EncryptU' pa que la muestre en la bd :CCCCCCCCCCCCCCC
    os.makedirs(base_path, exist_ok=True)
    db_path = os.path.join(base_path, 'claves_maestras.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''DROP TABLE IF EXISTS claves''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS claves (
            sitio_web TEXT NOT NULL UNIQUE,
            clave_maestra TEXT NOT NULL
        )
    ''')

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print(cursor.fetchall())

    conn.commit()
    conn.close()
    print("Base de datos creada correctamente")

def insertar_clave(sitio_web: str, clave: str, master_password: bytes):
    base_path = os.path.join('EncryptU', 'src', 'database')
    db_path = os.path.join(base_path, 'claves_maestras.db')

    clave_encriptada = encriptar_contraseña(clave, sitio_web, master_password).decode()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO claves (sitio_web, clave_maestra) VALUES (?, ?)", (sitio_web, clave_encriptada))
        conn.commit()
        print("Clave insertada correctamente")
    except sqlite3.IntegrityError:
        print("Error: Ya existe una clave para ese sitio web")
    finally:
        conn.close()

# Ejemplo para crear la base:
if __name__ == "__main__":
    crear_base_datos()
