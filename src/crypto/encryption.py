from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64

def generar_nonce(sitio_web: str):
    return sitio_web.encode().ljust(12, b'\0')[:12]

def encriptar_contraseña(password: str, sitio_web: str, master_password: bytes):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=sitio_web.encode(),
        iterations=100000
    )
    clave = kdf.derive(master_password)
    nonce = generar_nonce(sitio_web)

    cipher = Cipher(algorithms.AES(clave), modes.GCM(nonce), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(password.encode()) + encryptor.finalize()

    return base64.urlsafe_b64encode(nonce + encrypted + encryptor.tag)
