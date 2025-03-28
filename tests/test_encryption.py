#Futuro Testing 


""" 
import pytest
from cryptography.fernet import Fernet
# Ajusta la importación según tu estructura real
from src.crypto.manager import encrypt_password, decrypt_password

def test_encryption_decryption():
    master_password = "Sup3rS3cretP@ssw0rd!2023"
    website = "facebook.com"
    plain_password = "pepito123"
    
    # Encriptar
    encrypted = encrypt_password(master_password, website, plain_password)
    
    # Desencriptar
    decrypted = decrypt_password(master_password, website, encrypted)
    
    assert decrypted == plain_password, "El descifrado no coincide con el original"

def test_unique_encryption_per_website():
    master_password = "claveMaestra123"
    plain_password = "contraseñaComún"
    
    # Encriptar para dos sitios diferentes
    encrypted_facebook = encrypt_password(master_password, "facebook.com", plain_password)
    encrypted_google = encrypt_password(master_password, "google.com", plain_password)
    
    assert encrypted_facebook != encrypted_google, "Las contraseñas encriptadas deben ser únicas por sitio" """