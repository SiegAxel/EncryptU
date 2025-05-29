import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from reset_bd import borrar_tabla_claves, crear_base_datos
"""
if __name__ == "__main__":
    borrar_tabla_claves()
    crear_base_datos()
"""

from crypto.encryption import encriptar_contraseña
from database.base_de_datos import insertar_clave

def main():
    print("=== EncryptU ===")
    master = input("Introduce tu clave maestra: ").encode()
    password = input("Introduce tu contraseña a guardar: ")
    domain = input("Introduce el dominio (ej. youtube.com): ")

    encrypted = encriptar_contraseña(password, domain, master)
    print("\nContraseña encriptada:")
    print(encrypted.decode())

    insertar_clave(domain, password, master)

if __name__ == "__main__":
    main()

