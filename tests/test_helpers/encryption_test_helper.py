"""
Test helper to bridge import paths for encryption functions
"""
import sys
import os
from typing import Any, Callable, Optional, Type, cast

# Add the full path to desktop/controllers to Python path
desktop_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'desktop'))
controllers_path = os.path.join(desktop_path, 'controllers')
sys.path.insert(0, controllers_path)


# Initialize module-level exports
encriptar_contraseña: Optional[Callable[..., bytes]] = None
desencriptar_contraseña: Optional[Callable[..., str]] = None
EncryptionModel: Optional[Type[Any]] = None
generar_nonce: Optional[Callable[..., bytes]] = None
generar_salt: Optional[Callable[..., bytes]] = None


def _import_from_desktop_controllers() -> bool:
    """Try to import encryption functions from desktop/controllers."""
    global encriptar_contraseña, desencriptar_contraseña, EncryptionModel, generar_nonce, generar_salt
    
    try:
        from desktop.controllers.models.encryption_model import (
            encriptar_contraseña as imported_encriptar,
            desencriptar_contraseña as imported_desencriptar,
            EncryptionModel as imported_model,
            generar_nonce as imported_nonce,
        )
        encriptar_contraseña = cast(Callable[..., bytes], imported_encriptar)
        desencriptar_contraseña = cast(Callable[..., str], imported_desencriptar)
        EncryptionModel = cast(Type[Any], imported_model)
        generar_nonce = cast(Callable[..., bytes], imported_nonce)
        
        # Try to import generar_salt separately as it might not be available
        try:
            from desktop.controllers.models.encryption_model import generar_salt as imported_salt
            generar_salt = cast(Callable[..., bytes], imported_salt)
        except ImportError:
            pass
        
        return True
    except ImportError:
        return False


def _import_from_src_crypto() -> bool:
    """Try to import encryption functions from src/crypto."""
    global encriptar_contraseña, desencriptar_contraseña, EncryptionModel, generar_nonce, generar_salt
    
    src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
    sys.path.insert(0, src_path)
    
    try:
        from crypto.encryption import encriptar_contraseña as imported_encriptar
        encriptar_contraseña = cast(Callable[..., bytes], imported_encriptar)
        
        try:
            from crypto.encryption import generar_nonce as imported_nonce
            generar_nonce = cast(Callable[..., bytes], imported_nonce)
        except ImportError:
            pass
        
        if desencriptar_contraseña is None:
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.backends import default_backend
            import base64
            
            def fallback_decrypt(encrypted_data: bytes, domain: str, master_password: bytes) -> str:
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
            
            desencriptar_contraseña = cast(Callable[..., str], fallback_decrypt)
        
        # Create fallback EncryptionModel if needed
        if EncryptionModel is None:
            class FallbackEncryptionModel:
                pass
            
            EncryptionModel = cast(Type[Any], FallbackEncryptionModel)
        
        return True
    except ImportError:
        return False


def _setup_fallbacks() -> None:
    """Set up fallback implementations when imports fail."""
    global encriptar_contraseña, desencriptar_contraseña, EncryptionModel, generar_nonce, generar_salt
    
    if encriptar_contraseña is None:
        def fallback_encrypt(*args: Any, **kwargs: Any) -> bytes:
            raise ImportError("Could not import encryption functions")
        encriptar_contraseña = cast(Callable[..., bytes], fallback_encrypt)
    
    if desencriptar_contraseña is None:
        def fallback_decrypt_err(*args: Any, **kwargs: Any) -> str:
            raise ImportError("Could not import encryption functions")
        desencriptar_contraseña = cast(Callable[..., str], fallback_decrypt_err)
    
    if EncryptionModel is None:
        class FallbackModel:
            pass
        EncryptionModel = cast(Type[Any], FallbackModel)
    
    if generar_nonce is None:
        def fallback_nonce(*args: Any, **kwargs: Any) -> bytes:
            return b'\x00' * 12
        generar_nonce = cast(Callable[..., bytes], fallback_nonce)
    
    if generar_salt is None:
        def fallback_salt_gen(*args: Any, **kwargs: Any) -> bytes:
            return b'\x00' * 16
        generar_salt = cast(Callable[..., bytes], fallback_salt_gen)


# Try to import encryption functions in order of preference
if not _import_from_desktop_controllers():
    if not _import_from_src_crypto():
        print("Warning: Could not import encryption functions from preferred locations")

# Set up fallbacks for any missing functions
_setup_fallbacks()

# Re-export the functions
__all__ = [
    'encriptar_contraseña', 
    'desencriptar_contraseña',
    'EncryptionModel',
    'generar_nonce',
    'generar_salt'
]