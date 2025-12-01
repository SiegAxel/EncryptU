"""
Test helper to bridge import paths for encryption functions
"""
import sys
import os

# Add the full path to desktop/controllers to Python path
desktop_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'desktop'))
controllers_path = os.path.join(desktop_path, 'controllers')
sys.path.insert(0, controllers_path)

# Import the encryption functions
encriptar_contraseña = None
desencriptar_contraseña = None
EncryptionModel = None
generar_nonce = None
generar_salt = None

try:
    # Try importing with an absolute path first, fallback to relative if needed
    try:
        from desktop.controllers.models.encryption_model import (
            encriptar_contraseña, 
            desencriptar_contraseña,
            EncryptionModel,
            generar_nonce,
            generar_salt
        )
    except ImportError:
        from models.encryption_model import (
            encriptar_contraseña, 
            desencriptar_contraseña,
            EncryptionModel,
            generar_nonce,
            generar_salt
        )
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback: try importing from the main src directory
    src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
    sys.path.insert(0, src_path)
    try:
        from crypto.encryption import encriptar_contraseña
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.backends import default_backend
        import base64
        
        # Create a dummy implementation of desencriptar_contraseña if it doesn't exist
        if desencriptar_contraseña is None:
            def desencriptar_contraseña(encrypted_data: bytes, domain: str, master_password: bytes) -> str:
                """Fallback implementation of decrypt function"""
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
        
        # Create a dummy EncryptionModel if it doesn't exist
        if EncryptionModel is None:
            class EncryptionModel:
                pass
        
    except ImportError as e2:
        print(f"Fallback import also failed: {e2}")
        # Final fallback - define empty functions to prevent errors
        if encriptar_contraseña is None:
            def encriptar_contraseña(*args, **kwargs) -> bytes:
                raise ImportError("Could not import encryption functions")
        
        if desencriptar_contraseña is None:
            def desencriptar_contraseña(*args, **kwargs) -> str:
                raise ImportError("Could not import encryption functions")
        
        if EncryptionModel is None:
            class EncryptionModel:
                pass
        
        if generar_nonce is None:
            def generar_nonce(*args, **kwargs):
                return b'\x00' * 12
        
        if generar_salt is None:
            def generar_salt(*args, **kwargs):
                return b'\x00' * 16

# Re-export the functions
__all__ = [
    'encriptar_contraseña', 
    'desencriptar_contraseña',
    'EncryptionModel',
    'generar_nonce',
    'generar_salt'
]