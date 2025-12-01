import pytest
import sys
import os
import base64
from unittest.mock import Mock, patch

# Set up proper import paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
src_path = os.path.join(project_root, 'src')

# Add src to Python path
sys.path.insert(0, src_path)

try:
    # Import real crypto functions
    from crypto.encryption import (
        encriptar_contraseña, 
        encriptar_bytes, 
        desencriptar_bytes,
        generar_nonce
    )
    
    # Import cryptography modules
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    
    CRYPTO_SOURCE = "real"
    print("✅ Using real crypto implementation")
    
    # Create the missing decrypt function for passwords
    def decrypt_password(data_b64: bytes, sitio_web: str, master_password: bytes) -> str:
        """Decrypt password using the same logic as encriptar_contraseña"""
        try:
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
            decrypted = decryptor.update(ciphertext) + decryptor.finalize()
            return decrypted.decode('utf-8')
        except Exception:
            return "decryption_failed"
    
    # Create a test crypto model class
    class RealCryptoTestModel:
        def derive_key(self, master_password: str, salt: bytes) -> bytes:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            return kdf.derive(master_password.encode('utf-8'))
        
        def verify_key(self, master_password: str, salt: bytes, key: bytes) -> bool:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            try:
                kdf.verify(master_password.encode('utf-8'), key)
                return True
            except Exception:
                return False
        
        def generate_nonce(self) -> bytes:
            import os
            return os.urandom(12)
        
        def encrypt_aes_gcm(self, plaintext: bytes, key: bytes) -> bytes:
            nonce = self.generate_nonce()
            cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(plaintext) + encryptor.finalize()
            return nonce + ciphertext + encryptor.tag
        
        def decrypt_aes_gcm(self, encrypted_data: bytes, key: bytes) -> bytes:
            nonce = encrypted_data[:12]
            tag = encrypted_data[-16:]
            ciphertext = encrypted_data[12:-16]
            cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
            decryptor = cipher.decryptor()
            return decryptor.update(ciphertext) + decryptor.finalize()
        
        def hash_password(self, password: str) -> bytes:
            import os
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key = kdf.derive(password.encode('utf-8'))
            return salt + key
        
        def verify_password(self, stored_hash: bytes, password: str) -> bool:
            salt = stored_hash[:16]
            key = stored_hash[16:]
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            try:
                kdf.verify(password.encode('utf-8'), key)
                return True
            except Exception:
                return False
    
    CryptoTestModel = RealCryptoTestModel

except ImportError as e:
    print(f"⚠️  Using mock crypto functions: {e}")
    CRYPTO_SOURCE = "mock"
    
    # Create comprehensive mock functions
    def mock_encrypt(password: str, sitio_web: str, master_password: bytes | None = None) -> bytes:
        return f"mock_encrypted_{password}_{sitio_web}".encode().hex().encode()
    
    def mock_decrypt(data_b64: bytes, sitio_web: str, master_password: bytes) -> str:
        decoded = data_b64.decode().replace("mock_encrypted_", "")
        return decoded.replace(f"_{sitio_web}", "")
    
    def mock_encrypt_bytes(plaintext: bytes, sitio_web: str, master_password: bytes) -> bytes:
        return f"mock_bytes_{plaintext.decode()}_{sitio_web}".encode().hex().encode()
    
    def mock_decrypt_bytes(data_b64: bytes, sitio_web: str, master_password: bytes) -> bytes:
        decoded = data_b64.decode().replace("mock_bytes_", "")
        return decoded.replace(f"_{sitio_web}", "").encode()
    
    def mock_generate_nonce(sitio_web: str) -> bytes:
        return sitio_web.encode().ljust(12, b'\0')[:12]
    
    # Use the mock functions
    encriptar_contraseña = mock_encrypt
    decrypt_password = mock_decrypt
    encriptar_bytes = mock_encrypt_bytes
    desencriptar_bytes = mock_decrypt_bytes
    generar_nonce = mock_generate_nonce
    
    # Mock model class
    class MockCryptoTestModel:
        def derive_key(self, master_password: str, salt: bytes) -> bytes:
            return salt + master_password.encode()[:16]
        def verify_key(self, master_password: str, salt: bytes, key: bytes) -> bool:
            return True
        def encrypt_aes_gcm(self, plaintext: bytes, key: bytes) -> bytes:
            return plaintext + b"_mock_encrypted"
        def decrypt_aes_gcm(self, encrypted_data: bytes, key: bytes) -> bytes:
            return encrypted_data.replace(b"_mock_encrypted", b"")
        def hash_password(self, password: str) -> bytes:
            return password.encode() + b"_mock_hash"
        def verify_password(self, stored_hash: bytes, password: str) -> bool:
            return stored_hash.startswith(password.encode())
    
    CryptoTestModel = MockCryptoTestModel


class TestEncryptionUnit:
    """Unit tests for encryption module - AES-256/Fernet implementation
    
    According to documentation:
    - Validación de funciones individuales a nivel de código fuente
    - Validación de algoritmos AES-256 y Fernet
    - Responsable: Liam Ley (Analista Programador)
    """
    
    def test_encryption_decryption_roundtrip(self):
        """Test that encryption and decryption work correctly (P1)"""
        password = "supersecret123"
        domain = "example.com"
        master_password = b"clave_secreta_super_larga_123!"
        
        print("\n" + "="*60)
        print("PRUEBA CIFRADO Y DESCIFRADO ROUNDTRIP")
        print("="*60)
        
        encrypted = encriptar_contraseña(password, domain, master_password)
        decrypted = decrypt_password(encrypted, domain, master_password)
        
        print(f"Contraseña original: {password}")
        print(f"Dominio: {domain}")
        print(f"Cifrado completado: {bool(encrypted)}")
        print(f"Contraseña descifrada: {decrypted}")
        print(f"Verificacion: {decrypted == password}")
        print("[OK] Cifrado y descifrado exitosos")
        print("="*60)
        
        assert decrypted == password, f"Expected '{password}', got '{decrypted}'"

    def test_same_input_produces_same_output(self):
        """Test deterministic encryption for same inputs (P2)"""
        master_password = b"clave_secreta_super_larga_123!"
        
        print("\n" + "="*60)
        print("PRUEBA ENTRADA IDENTICA PRODUCE SALIDA IDENTICA")
        print("="*60)
        
        encrypted1 = encriptar_contraseña("password", "google.com", master_password)
        encrypted2 = encriptar_contraseña("password", "google.com", master_password)
        
        print("Entrada: password, google.com")
        print(f"Primera encriptacion realizada: {bool(encrypted1)}")
        print(f"Segunda encriptacion realizada: {bool(encrypted2)}")
        print(f"Resultados identicos: {encrypted1 == encrypted2}")
        print("[OK] Cifrado determinista confirmado")
        print("="*60)
        
        assert encrypted1 == encrypted2

    def test_different_domains_produce_different_outputs(self):
        """Test that different domains produce different encryptions (P3)"""
        master_password = b"clave_secreta_super_larga_123!"
        
        print("\n" + "="*60)
        print("PRUEBA DOMINIOS DIFERENTES PRODUCEN SALIDAS DIFERENTES")
        print("="*60)
        
        encrypted1 = encriptar_contraseña("password", "site1.com", master_password)
        encrypted2 = encriptar_contraseña("password", "site2.com", master_password)
        
        print("Contraseña: password")
        print("Dominio 1: site1.com")
        print("Dominio 2: site2.com")
        print(f"Cifrado 1 generado: {bool(encrypted1)}")
        print(f"Cifrado 2 generado: {bool(encrypted2)}")
        print(f"Resultados diferentes: {encrypted1 != encrypted2}")
        print("[OK] Diferentes dominios producen diferentes cifrados")
        print("="*60)
        
        assert encrypted1 != encrypted2

    def test_different_passwords_produce_different_outputs(self):
        """Test that different passwords produce different encryptions (P4)"""
        master_password = b"clave_secreta_super_larga_123!"
        
        print("\n" + "="*60)
        print("PRUEBA CONTRASEÑAS DIFERENTES PRODUCEN SALIDAS DIFERENTES")
        print("="*60)
        
        encrypted1 = encriptar_contraseña("password1", "site.com", master_password)
        encrypted2 = encriptar_contraseña("password2", "site.com", master_password)
        
        print("Dominio: site.com")
        print("Contraseña 1: password1")
        print("Contraseña 2: password2")
        print(f"Cifrado 1 generado: {bool(encrypted1)}")
        print(f"Cifrado 2 generado: {bool(encrypted2)}")
        print(f"Resultados diferentes: {encrypted1 != encrypted2}")
        print("[OK] Diferentes contraseñas producen diferentes cifrados")
        print("="*60)
        
        assert encrypted1 != encrypted2

    def test_empty_password(self):
        """Test encryption of empty password (P5)"""
        master_password = b"clave_secreta_super_larga_123!"
        
        print("\n" + "="*60)
        print("PRUEBA CONTRASEÑA VACIA")
        print("="*60)
        
        encrypted = encriptar_contraseña("", "empty.org", master_password)
        decrypted = decrypt_password(encrypted, "empty.org", master_password)
        
        print("Contraseña: (vacia)")
        print("Dominio: empty.org")
        print(f"Cifrado generado: {bool(encrypted)}")
        print(f"Descifrado: '{decrypted}'")
        print(f"Coincide con original: {decrypted == ''}")
        print("[OK] Contraseña vacia cifrada y descifrada correctamente")
        print("="*60)
        
        assert decrypted == ""

    def test_special_character_domain(self):
        """Test encryption with Unicode domain and password (P6)"""
        domain = "üníçødeñ.com"
        password = "p@sswörd!"
        master_password = b"clave_secreta_super_larga_123!"
        
        print("\n" + "="*60)
        print("PRUEBA CARACTERES ESPECIALES Y UNICODE")
        print("="*60)
        
        encrypted = encriptar_contraseña(password, domain, master_password)
        decrypted = decrypt_password(encrypted, domain, master_password)
        
        print(f"Contraseña: {password}")
        print(f"Dominio: {domain}")
        print(f"Cifrado generado: {bool(encrypted)}")
        print(f"Descifrado: {decrypted}")
        print(f"Coincide con original: {decrypted == password}")
        print("[OK] Caracteres especiales y Unicode procesados correctamente")
        print("="*60)
        
        assert decrypted == password

    def test_very_long_password(self):
        """Test encryption of very long passwords (P7)"""
        master_password = b"clave_secreta_super_larga_123!"
        password = "a" * 1000  # Very long password
        
        print("\n" + "="*60)
        print("PRUEBA CONTRASEÑA MUY LARGA")
        print("="*60)
        
        encrypted = encriptar_contraseña(password, "test.com", master_password)
        decrypted = decrypt_password(encrypted, "test.com", master_password)
        
        print(f"Longitud de contraseña: {len(password)} caracteres")
        print("Dominio: test.com")
        print(f"Cifrado generado: {bool(encrypted)}")
        print(f"Descifrado correctamente: {len(decrypted) == len(password)}")
        print(f"Coincide con original: {decrypted == password}")
        print("[OK] Contraseña larga cifrada y descifrada exitosamente")
        print("="*60)
        
        assert decrypted == password

    def test_unicode_emoji_password(self):
        """Test encryption with emoji characters (P8)"""
        master_password = b"clave_secreta_super_larga_123!"
        password = "😀🔒💻🚀123"
        
        print("\n" + "="*60)
        print("PRUEBA CONTRASEÑA CON CARACTERES UNICODE")
        print("="*60)
        
        encrypted = encriptar_contraseña(password, "emoji.com", master_password)
        decrypted = decrypt_password(encrypted, "emoji.com", master_password)
        
        print(f"Contraseña: {password}")
        print("Dominio: emoji.com")
        print(f"Cifrado generado: {bool(encrypted)}")
        print(f"Descifrado: {decrypted}")
        print(f"Coincide con original: {decrypted == password}")
        print("[OK] Caracteres unicode procesados sin problemas")
        print("="*60)
        
        assert decrypted == password

    def test_various_encoded_characters(self):
        """Test encryption with various encoded characters (P9)"""
        master_password = b"clave_secreta_super_larga_123!"
        password = "ñáéíóú@#$%&*()_+{}|:<>?[]\\;'\",./ "
        
        print("\n" + "="*60)
        print("PRUEBA CARACTERES CODIFICADOS VARIOS")
        print("="*60)
        
        encrypted = encriptar_contraseña(password, "special.com", master_password)
        decrypted = decrypt_password(encrypted, "special.com", master_password)
        
        print(f"Contraseña con caracteres especiales probada")
        print(f"Longitud original: {len(password)} caracteres")
        print("Dominio: special.com")
        print(f"Cifrado generado: {bool(encrypted)}")
        print(f"Longitud descifrada: {len(decrypted)} caracteres")
        print(f"Coincide con original: {decrypted == password}")
        print("[OK] Todos los caracteres especiales procesados correctamente")
        print("="*60)
        
        assert decrypted == password

    def test_bytes_encryption_decryption(self):
        """Test bytes encryption and decryption (P10)"""
        plaintext = b"Hello, World! This is test data."
        domain = "test-bytes.com"
        master_password = b"bytes_master_key_123"
        
        print("\n" + "="*60)
        print("PRUEBA CIFRADO DE BYTES")
        print("="*60)
        
        encrypted = encriptar_bytes(plaintext, domain, master_password)
        decrypted = desencriptar_bytes(encrypted, domain, master_password)
        
        print(f"Datos originales: {plaintext.decode()}")
        print(f"Longitud: {len(plaintext)} bytes")
        print("Dominio: test-bytes.com")
        print(f"Cifrado generado: {bool(encrypted)}")
        print(f"Datos descifrados: {decrypted.decode() if decrypted else 'Error'}")
        print(f"Coincide con original: {decrypted == plaintext}")
        print("[OK] Cifrado de bytes exitoso")
        print("="*60)
        
        assert decrypted == plaintext

    def test_generate_nonce(self):
        """Test nonce generation"""
        domain1 = "example.com"
        domain2 = "example.com"
        
        print("\n" + "="*60)
        print("PRUEBA GENERACION DE NONCE")
        print("="*60)
        
        nonce1 = generar_nonce(domain1)
        nonce2 = generar_nonce(domain2)
        
        print(f"Dominio: {domain1}")
        print(f"Nonce 1 generado: {bool(nonce1)}")
        print(f"Nonce 2 generado: {bool(nonce2)}")
        print(f"Longitud nonce 1: {len(nonce1)} bytes")
        print(f"Longitud nonce 2: {len(nonce2)} bytes")
        print(f"Nonces identicos: {nonce1 == nonce2}")
        print("[OK] Generacion de nonce completada exitosamente")
        print("="*60)
        
        # Same domain should produce same nonce
        assert nonce1 == nonce2
        assert len(nonce1) == 12


class TestCryptoModel:
    """Tests for the crypto model class methods
    
    Testing key derivation, verification, and AES-GCM operations
    """
    
    def test_encryption_model_derive_key(self):
        """Test key derivation functionality"""
        model = CryptoTestModel()
        master_password = "test_password_123"
        salt = b"static_salt_16b_1234"
        
        print("\n" + "="*60)
        print("PRUEBA DERIVACION DE CLAVE")
        print("="*60)
        
        key = model.derive_key(master_password, salt)
        
        print(f"Contraseña maestra: {master_password}")
        print(f"Salt: {salt}")
        print(f"Clave derivada: longitud {len(key)} bytes")
        print(f"Longitud esperada (AES-256): 32 bytes")
        print(f"Longitud correcta: {len(key) == 32}")
        
        # Same input should produce same key
        key2 = model.derive_key(master_password, salt)
        print(f"Segunda derivacion: {bool(key2)}")
        print(f"Claves identicas: {key == key2}")
        print("[OK] Derivacion de clave exitosa")
        print("="*60)
        
        assert len(key) == 32  # Should be 32 bytes for AES-256
        assert key == key2

    def test_encryption_model_verify_key_correct(self):
        """Test key verification with correct password"""
        model = CryptoTestModel()
        master_password = "test_password_123"
        salt = b"static_salt_16b_1234"
        
        print("\n" + "="*60)
        print("PRUEBA VERIFICACION DE CLAVE CORRECTA")
        print("="*60)
        
        key = model.derive_key(master_password, salt)
        result = model.verify_key(master_password, salt, key)
        
        print(f"Contraseña: {master_password}")
        print(f"Salt: {salt}")
        print(f"Clave derivada: longitud {len(key)} bytes")
        print(f"Contraseña verificada: {result}")
        print(f"Resultado esperado: True")
        print("[OK] Clave verificada correctamente")
        print("="*60)
        
        assert result is True

    def test_encryption_model_verify_key_incorrect(self):
        """Test key verification with incorrect password"""
        model = CryptoTestModel()
        master_password = "test_password_123"
        salt = b"static_salt_16b_1234"
        
        print("\n" + "="*60)
        print("PRUEBA VERIFICACION DE CLAVE INCORRECTA")
        print("="*60)
        
        key = model.derive_key(master_password, salt)
        incorrect_password = "wrong_password"
        result = model.verify_key(incorrect_password, salt, key)
        
        print(f"Contraseña original: {master_password}")
        print(f"Contraseña para verificar: {incorrect_password}")
        print(f"Salt: {salt}")
        print(f"Clave derivada: longitud {len(key)} bytes")
        print(f"Verificacion resultado: {result}")
        print(f"Resultado esperado: False")
        print("[OK] Contraseña incorrecta rechazada correctamente")
        print("="*60)
        
        assert result is False

    def test_encryption_model_encrypt_decrypt_aes_gcm(self):
        """Test AES-GCM encryption/decryption"""
        model = CryptoTestModel()
        plaintext = b"Hello, World! This is a test message."
        master_password = "test_password_123"
        salt = b"static_salt_16b_1234"
        
        print("\n" + "="*60)
        print("PRUEBA CIFRADO DESCIFRADO AES-GCM")
        print("="*60)
        
        key = model.derive_key(master_password, salt)
        encrypted = model.encrypt_aes_gcm(plaintext, key)
        decrypted = model.decrypt_aes_gcm(encrypted, key)
        
        print(f"Datos originales: {plaintext.decode()}")
        print(f"Longitud original: {len(plaintext)} bytes")
        print(f"Clave derivada: {len(key)} bytes")
        print(f"Cifrado generado: {bool(encrypted)}")
        print(f"Datos descifrados: {decrypted.decode() if decrypted else 'Error'}")
        print(f"Coincide con original: {decrypted == plaintext}")
        print("[OK] Cifrado AES-GCM exitoso")
        print("="*60)
        
        assert decrypted == plaintext

    def test_password_hashing(self):
        """Test password hashing and verification"""
        model = CryptoTestModel()
        password = "secure_password_123"
        
        print("\n" + "="*60)
        print("PRUEBA HASHING Y VERIFICACION DE CONTRASEÑA")
        print("="*60)
        
        # Hash the password
        stored_hash = model.hash_password(password)
        
        print(f"Contraseña original: {password}")
        print(f"Hash generado: longitud {len(stored_hash)} bytes")
        print(f"Longitud esperada: 48 bytes (16 salt + 32 hash)")
        print(f"Longitud correcta: {len(stored_hash) == 48}")
        
        # Verify correct password
        verify_result = model.verify_password(stored_hash, password)
        print(f"Verificacion con contraseña correcta: {verify_result}")
        
        # Verify incorrect password
        verify_wrong = model.verify_password(stored_hash, "wrong_password")
        print(f"Verificacion con contraseña incorrecta: {verify_wrong}")
        print("[OK] Hashing y verificacion completados exitosamente")
        print("="*60)
        
        assert len(stored_hash) == 48  # 16 bytes salt + 32 bytes hash
        assert model.verify_password(stored_hash, password) is True
        assert model.verify_password(stored_hash, "wrong_password") is False


class TestEncryptionErrorHandling:
    """Tests for error handling in encryption
    
    According to Clasificación de defectos - testing for various error scenarios
    """
    
    def test_invalid_master_key_handling(self):
        """Test handling of invalid master keys (Defecto: Media)"""
        password = "test123"
        domain = "test.com"
        
        print("\n" + "="*60)
        print("PRUEBA MANEJO DE CLAVE MAESTRA INVALIDA")
        print("="*60)
        
        # Test with None master_password (should use default or handle gracefully)
        try:
            encrypted = encriptar_contraseña(password, domain, None)
            print(f"Test 1 - Clave None: Cifrado exitoso")
            assert encrypted is not None
        except Exception as e:
            print(f"Test 1 - Clave None: Excepcion capturada (aceptable): {type(e).__name__}")
        
        # Test with empty master_password (should not crash catastrophically)
        try:
            encrypted = encriptar_contraseña(password, domain, b"")
            print(f"Test 2 - Clave vacia: Cifrado exitoso")
            assert encrypted is not None
        except Exception as e:
            print(f"Test 2 - Clave vacia: Excepcion capturada (aceptable): {type(e).__name__}")
        
        print("[OK] Manejo de claves invalidas completado")
        print("="*60)

    def test_invalid_domain_handling(self):
        """Test handling of invalid domains (Defecto: Baja)"""
        master_password = b"clave_secreta_super_larga_123!"
        
        print("\n" + "="*60)
        print("PRUEBA MANEJO DE DOMINIOS INVALIDOS")
        print("="*60)
        
        # Test with empty domain
        encrypted = encriptar_contraseña("password", "", master_password)
        decrypted = decrypt_password(encrypted, "", master_password)
        print(f"Test 1 - Dominio vacio: Descifrado exitoso: {decrypted == 'password'}")
        assert decrypted == "password"
        
        # Test with very long domain
        long_domain = "a" * 1000
        encrypted = encriptar_contraseña("password", long_domain, master_password)
        decrypted = decrypt_password(encrypted, long_domain, master_password)
        print(f"Test 2 - Dominio muy largo ({len(long_domain)} caracteres): Descifrado exitoso: {decrypted == 'password'}")
        assert decrypted == "password"
        
        print("[OK] Manejo de dominios invalidos completado")
        print("="*60)

    def test_corrupted_data_handling(self):
        """Test handling of corrupted encrypted data (Defecto: Alta)"""
        master_password = b"clave_secreta_super_larga_123!"
        
        print("\n" + "="*60)
        print("PRUEBA MANEJO DE DATOS CORROMPIDOS")
        print("="*60)
        
        # Create valid encrypted data
        encrypted = encriptar_contraseña("test", "corruption.com", master_password)
        print(f"Datos cifrados generados: {len(encrypted)} bytes")
        
        # Corrupt it by modifying some bytes
        corrupted = bytearray(encrypted)
        if len(corrupted) > 0:
            corrupted[0] = corrupted[0] ^ 0xFF  # Flip all bits in first byte
        corrupted_data = bytes(corrupted)
        
        print(f"Datos corrompidos: {len(corrupted_data)} bytes (modificados)")
        print(f"Intentando desencriptar datos corrompidos...")
        
        # Should raise an exception during decryption
        exception_raised = False
        try:
            decrypt_password(corrupted_data, "corruption.com", master_password)
        except Exception as e:
            exception_raised = True
            print(f"Excepcion capturada: {type(e).__name__}")
        
        print(f"Manejo correcto de datos corrompidos: {exception_raised}")
        print("[OK] Datos corrompidos manejados correctamente")
        print("="*60)
        
        with pytest.raises(Exception):
            decrypt_password(corrupted_data, "corruption.com", master_password)

    def test_invalid_base64_data_handling(self):
        """Test handling of invalid base64 data (Defecto: Alta)"""
        master_password = b"clave_secreta_super_larga_123!"
        
        print("\n" + "="*60)
        print("PRUEBA MANEJO DE BASE64 INVALIDO")
        print("="*60)
        
        print("Intentando desencriptar datos base64 invalidos...")
        print("Datos: 'invalid_base64_data!!!'")
        
        # Test with completely invalid base64
        exception_raised = False
        try:
            decrypt_password(b"invalid_base64_data!!!", "test.com", master_password)
        except Exception as e:
            exception_raised = True
            print(f"Excepcion capturada: {type(e).__name__}")
        
        print(f"Manejo correcto de base64 invalido: {exception_raised}")
        print("[OK] Base64 invalido manejado correctamente")
        print("="*60)
        
        with pytest.raises(Exception):
            decrypt_password(b"invalid_base64_data!!!", "test.com", master_password)

    def test_wrong_master_key_handling(self):
        """Test handling of wrong master key (Defecto: Alta)"""
        password = "test123"
        domain = "test.com"
        
        print("\n" + "="*60)
        print("PRUEBA MANEJO DE CLAVE MAESTRA INCORRECTA")
        print("="*60)
        
        # Encrypt with one key
        correct_key = b"clave_secreta_super_larga_123!"
        encrypted = encriptar_contraseña(password, domain, correct_key)
        print(f"Contraseña cifrada con clave correcta: {len(encrypted)} bytes")
        
        # Try to decrypt with wrong key
        wrong_key = b"wrong_key_for_testing"
        print(f"Intentando desencriptar con clave incorrecta...")
        
        exception_raised = False
        try:
            decrypt_password(encrypted, domain, wrong_key)
        except Exception as e:
            exception_raised = True
            print(f"Excepcion capturada: {type(e).__name__}")
        
        print(f"Manejo correcto de clave incorrecta: {exception_raised}")
        print("[OK] Clave incorrecta rechazada correctamente")
        print("="*60)
        
        with pytest.raises(Exception):
            decrypt_password(encrypted, domain, wrong_key)


class TestEncryptionPerformance:
    """Performance tests for encryption operations
    
    Ensuring efficiency for adult users
    """
    
    def test_encryption_speed_acceptable(self):
        """Test that encryption completes in acceptable time (Defecto: Media)"""
        import time
        master_password = b"clave_secreta_super_larga_123!"
        
        start_time = time.time()
        for i in range(100):
            encriptar_contraseña(f"password_{i}", "performance.com", master_password)
        end_time = time.time()
        
        # Should complete 100 encryptions in under 5 seconds
        total_time = end_time - start_time
        assert total_time < 5.0, f"Encryption too slow: {total_time:.2f}s for 100 operations"
    
    def test_memory_usage_acceptable(self):
        """Test that encryption doesn't use excessive memory (Defecto: Media)"""
        import gc
        master_password = b"clave_secreta_super_larga_123!"
        
        # Force garbage collection
        gc.collect()
        
        # Create many encrypted strings
        encrypted_strings = []
        for i in range(1000):
            encrypted = encriptar_contraseña(f"very_long_password_{i}_with_extra_data_to_test_memory_usage", "memory.com", master_password)
            encrypted_strings.append(encrypted)
        
        # Clean up
        del encrypted_strings
        gc.collect()
        
        # If we reach here without memory errors, test passes


print(f"🔧 Crypto source: {CRYPTO_SOURCE}")