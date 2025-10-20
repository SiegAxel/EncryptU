from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64
import os
from typing import Tuple

def generar_nonce(sitio_web: str):
    return sitio_web.encode().ljust(12, b'\0')[:12]

def encriptar_contraseña(password: str, sitio_web: str, master_password: bytes | None = None):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=sitio_web.encode(),
        iterations=100000
    )
    # Backwards compatibility: if no master_password provided, use a dev default
    if master_password is None:
        # Tests expect this default value (used in tests/test_encryption.py)
        master_password = os.getenv('MASTER_PASSWORD', 'clave_secreta_super_larga_123!').encode()
    clave = kdf.derive(master_password)
    nonce = generar_nonce(sitio_web)

    cipher = Cipher(algorithms.AES(clave), modes.GCM(nonce), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(password.encode()) + encryptor.finalize()

    return base64.urlsafe_b64encode(nonce + encrypted + encryptor.tag)


def encriptar_bytes(plaintext: bytes, sitio_web: str, master_password: bytes) -> bytes:
    """Encrypt raw bytes and return bytes (nonce + ciphertext + tag) base64-encoded.
    This mirrors encriptar_contraseña but works with bytes input.
    """
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
    encrypted = encryptor.update(plaintext) + encryptor.finalize()

    return base64.urlsafe_b64encode(nonce + encrypted + encryptor.tag)


def desencriptar_bytes(data_b64: bytes, sitio_web: str, master_password: bytes) -> bytes:
    """Decrypt bytes produced by encriptar_bytes (expects base64-encoded nonce+ciphertext+tag).
    Returns plaintext bytes.
    """
    raw = base64.urlsafe_b64decode(data_b64)
    nonce = raw[:12]
    tag = raw[-16:]
    ciphertext = raw[12:-16]

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=sitio_web.encode(),
        iterations=100000
    )
    clave = kdf.derive(master_password)

    cipher = Cipher(algorithms.AES(clave), modes.GCM(nonce, tag), backend=default_backend())
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    return plaintext

