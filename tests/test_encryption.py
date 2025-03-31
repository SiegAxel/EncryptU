import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from crypto.encryption import encriptar_contraseña
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64

def decrypt(encrypted_data: bytes, domain: str) -> str:
    master_password = b"clave_secreta_super_larga_123!"
    data = base64.urlsafe_b64decode(encrypted_data)
    nonce = data[:12]
    tag = data[-16:]
    ciphertext = data[12:-16]
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=domain.encode(),
        iterations=100000,
        backend=default_backend()
    )
    clave = kdf.derive(master_password)
    
    cipher = Cipher(algorithms.AES(clave), modes.GCM(nonce, tag), backend=default_backend())
    decryptor = cipher.decryptor()
    return (decryptor.update(ciphertext) + decryptor.finalize()).decode()

def test_encryption_decryption_roundtrip():
    password = "supersecret123"
    domain = "example.com"
    encrypted = encriptar_contraseña(password, domain)
    decrypted = decrypt(encrypted, domain)
    assert decrypted == password

def test_same_input_produces_same_output():
    encrypted1 = encriptar_contraseña("password", "google.com")
    encrypted2 = encriptar_contraseña("password", "google.com")
    assert encrypted1 == encrypted2

def test_different_domains_produce_different_outputs():
    encrypted1 = encriptar_contraseña("password", "site1.com")
    encrypted2 = encriptar_contraseña("password", "site2.com")
    assert encrypted1 != encrypted2

def test_different_passwords_produce_different_outputs():
    encrypted1 = encriptar_contraseña("password1", "site.com")
    encrypted2 = encriptar_contraseña("password2", "site.com")
    assert encrypted1 != encrypted2

def test_empty_password():
    encrypted = encriptar_contraseña("", "empty.org")
    decrypted = decrypt(encrypted, "empty.org")
    assert decrypted == ""

def test_special_character_domain():
    domain = "üníçødeñ.com"
    password = "p@sswörd!"
    encrypted = encriptar_contraseña(password, domain)
    decrypted = decrypt(encrypted, domain)
    assert decrypted == password