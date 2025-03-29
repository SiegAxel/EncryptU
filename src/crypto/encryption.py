from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64
import os
import sqlite3

def generar_nonce(sitio_web: str):
    # Nonce único basado en el sitio web
    return sitio_web.encode().ljust(12, b'\0')[:12]  # 12 bytes para AES-GCM

def encriptar_contraseña(password: str, sitio_web: str):
    # Clave maestra temporal (debes cambiarla luego)
    master_password = b"clave_secreta_super_larga_123!"
    
    # Derivar clave única
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=sitio_web.encode(),
        iterations=100000
    )
    clave = kdf.derive(master_password)
    
    # Configurar AES-GCM con nonce determinista
    nonce = generar_nonce(sitio_web)
    cipher = Cipher(algorithms.AES(clave), modes.GCM(nonce), backend=default_backend())
    encryptor = cipher.encryptor()
    
    # Encriptar
    encrypted = encryptor.update(password.encode()) + encryptor.finalize()
    return base64.urlsafe_b64encode(nonce + encrypted + encryptor.tag)


    