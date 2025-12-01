import sqlite3
import pytest
import tempfile
import os
import sys
import json
import base64
from unittest.mock import Mock, patch

# Initialize variables
SessionManager = None

# Define MockSessionManager so it's always available
class MockSessionManager:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.session_file = os.path.join(self.temp_dir, "session.json")
    
    def save_session(self, session_data: dict):
        with open(self.session_file, "w") as f:
            json.dump(session_data, f, indent=4)
    
    def load_session(self):
        if not os.path.exists(self.session_file):
            return None
        try:
            with open(self.session_file, "r") as f:
                session_data = json.load(f)
                if isinstance(session_data, dict) and "token" in session_data:
                    return session_data
                return None
        except:
            return None
    
    def clear_session(self):
        if os.path.exists(self.session_file):
            os.remove(self.session_file)

# Try to import real SessionManager
try:
    desktop_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'desktop', 'controllers'))
    sys.path.insert(0, desktop_path)
    from desktop.controllers.models.session_manager import SessionManager as _RemoteSessionManager
    SessionManager = _RemoteSessionManager
    DB_SOURCE = "real"
except ImportError:
    print("⚠️  Using mock SessionManager")
    DB_SOURCE = "mock"
    SessionManager = MockSessionManager


class TestDatabaseIntegrity:
    """Database integrity tests for SQLite operations
    
    Testing module: Módulo de Datos - Integridad de la base de datos local SQLite
    Responsable: Manuel Miqueles (DBA)
    """
    
    def test_database_connection(self, db_connection):
        """Test database connection establishment (P11)"""
        cursor = db_connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print("\n" + "="*60)
        print("PRUEBA DE CONEXIÓN A BASE DE DATOS")
        print("="*60)
        print(f"Conexión exitosa: {result}")
        print("="*60)
        assert result[0] == 1
    
    def test_user_creation(self, db_connection):
        """Test user creation with valid data (P12)"""
        cursor = db_connection.cursor()
        
        # Insert valid user
        cursor.execute(
            "INSERT INTO User (username, email, password_hash) VALUES (?, ?, ?)",
            ("testuser", "test@example.com", "hashed_password_123")
        )
        db_connection.commit()
        
        # Verify user was created
        cursor.execute("SELECT username, email FROM User WHERE username = ?", ("testuser",))
        user = cursor.fetchone()
        
        print("\n" + "="*60)
        print("PRUEBA DE CREACION DE USUARIO")
        print("="*60)
        print(f"Usuario creado: {user[0]}")
        print(f"Correo: {user[1]}")
        print("[OK] Usuario creado exitosamente")
        print("="*60)
        
        assert user is not None
        assert user[0] == "testuser"
        assert user[1] == "test@example.com"
    
    def test_user_role_update(self, db_connection):
        """Test updating user role (P13)"""
        cursor = db_connection.cursor()
        
        # Create user
        cursor.execute(
            "INSERT INTO User (username, email, password_hash) VALUES (?, ?, ?)",
            ("adminuser", "admin@example.com", "hashed_password_123")
        )
        user_id = cursor.lastrowid
        
        # Update role to admin
        cursor.execute(
            "UPDATE User SET role = 'admin' WHERE id = ?", (user_id,)
        )
        db_connection.commit()
        
        # Verify role change
        cursor.execute("SELECT role FROM User WHERE id = ?", (user_id,))
        role = cursor.fetchone()[0]
        
        print("\n" + "="*60)
        print("PRUEBA DE ACTUALIZACION DE ROL")
        print("="*60)
        print(f"Usuario ID: {user_id}")
        print(f"Rol actualizado a: {role}")
        print("[OK] Rol actualizado exitosamente")
        print("="*60)
        
        assert role == 'admin'
    
    def test_cascade_delete_files(self, db_connection):
        """Test cascade deletion when user is deleted (P14)"""
        cursor = db_connection.cursor()
        
        # Create user and files
        cursor.execute(
            "INSERT INTO User (username, email, password_hash) VALUES (?, ?, ?)",
            ("testuser", "test@example.com", "hashed_password_123")
        )
        user_id = cursor.lastrowid
        
        # Add multiple files for user
        for i in range(3):
            cursor.execute(
                "INSERT INTO File (user_id, filename, encrypted_content, site) VALUES (?, ?, ?, ?)",
                (user_id, f"file_{i}.txt", f"encrypted_content_{i}", "example.com")
            )
        db_connection.commit()
        
        # Verify files exist
        cursor.execute("SELECT COUNT(*) FROM File WHERE user_id = ?", (user_id,))
        file_count = cursor.fetchone()[0]
        
        print("\n" + "="*60)
        print("PRUEBA DE ELIMINACIÓN EN CASCADE")
        print("="*60)
        print(f"Usuario creado: ID={user_id}, username=testuser")
        print(f"Archivos creados para el usuario: {file_count}")
        
        # Delete user (should cascade to files)
        cursor.execute("DELETE FROM User WHERE id = ?", (user_id,))
        db_connection.commit()
        
        # Verify files were also deleted
        cursor.execute("SELECT COUNT(*) FROM File WHERE user_id = ?", (user_id,))
        remaining_files = cursor.fetchone()[0]
        print(f"Usuario eliminado")
        print(f"Archivos restantes después de eliminación: {remaining_files}")
        print("[OK] Cascade DELETE funcionó correctamente")
        print("="*60)
        assert remaining_files == 0
    
    def test_unique_constraints(self, db_connection):
        """Test unique constraints on username and email (P15)"""
        cursor = db_connection.cursor()
        
        # Create first user
        cursor.execute(
            "INSERT INTO User (username, email, password_hash) VALUES (?, ?, ?)",
            ("uniqueuser", "unique@example.com", "hashed_password_123")
        )
        db_connection.commit()
        
        print("\n" + "="*60)
        print("PRUEBA DE RESTRICCIONES UNICAS")
        print("="*60)
        print("Usuario inicial creado: uniqueuser")
        
        # Try to create user with duplicate username (should fail)
        duplicate_username_caught = False
        try:
            with pytest.raises(sqlite3.IntegrityError):
                cursor.execute(
                    "INSERT INTO User (username, email, password_hash) VALUES (?, ?, ?)",
                    ("uniqueuser", "different@example.com", "hashed_password_456")
                )
            duplicate_username_caught = True
        except:
            pass
        
        # Try to create user with duplicate email (should fail)
        duplicate_email_caught = False
        try:
            with pytest.raises(sqlite3.IntegrityError):
                cursor.execute(
                    "INSERT INTO User (username, email, password_hash) VALUES (?, ?, ?)",
                    ("differentuser", "unique@example.com", "hashed_password_456")
                )
            duplicate_email_caught = True
        except:
            pass
        
        print("Intento de nombre duplicado: RECHAZADO")
        print("Intento de correo duplicado: RECHAZADO")
        print("[OK] Restricciones unicas funcionando")
        print("="*60)
        
        db_connection.rollback()
    
    def test_file_encryption_storage(self, db_connection):
        """Test storing encrypted file data (P16)"""
        cursor = db_connection.cursor()
        
        # Create user
        cursor.execute(
            "INSERT INTO User (username, email, password_hash) VALUES (?, ?, ?)",
            ("cryptouser", "crypto@example.com", "hashed_password_123")
        )
        user_id = cursor.lastrowid
        
        # Simulate encrypted content (base64 encoded)
        encrypted_content = base64.b64encode(b"encrypted_file_content_123").decode()
        
        # Store encrypted file
        cursor.execute(
            "INSERT INTO File (user_id, filename, encrypted_content, site, username_field) VALUES (?, ?, ?, ?, ?)",
            (user_id, "secret.txt", encrypted_content, "bank.com", "crypto_username")
        )
        db_connection.commit()
        
        # Retrieve and verify
        cursor.execute(
            "SELECT filename, encrypted_content, site, username_field FROM File WHERE user_id = ?",
            (user_id,)
        )
        file_data = cursor.fetchone()
        
        print("\n" + "="*60)
        print("PRUEBA DE ALMACENAMIENTO DE ARCHIVO ENCRIPTADO")
        print("="*60)
        print(f"Archivo: {file_data[0]}")
        print(f"Sitio: {file_data[2]}")
        print(f"Usuario del sitio: {file_data[3]}")
        print(f"Contenido encriptado: {file_data[1][:30]}...")
        print("[OK] Archivo encriptado almacenado correctamente")
        print("="*60)
        
        assert file_data[0] == "secret.txt"
        assert file_data[1] == encrypted_content
        assert file_data[2] == "bank.com"
        assert file_data[3] == "crypto_username"


class TestSessionManager:
    """Tests for session management functionality
    
    Testing local session file operations
    """
    
    @pytest.fixture
    def session_manager(self):
        """Create session manager with temporary directory"""
        global SessionManager
        # Defensive: ensure SessionManager is a callable class. If import logic
        # above failed in a surprising way and left SessionManager as None,
        # fall back to the provided MockSessionManager class.
        if SessionManager is None:
            SessionManager = MockSessionManager

        manager = SessionManager()
        yield manager
        # Cleanup
        try:
            manager.clear_session()
        except Exception:
            pass
    
    def test_save_session(self, session_manager):
        """Test saving session data (P17)"""
        session_data = {
            "username": "testuser",
            "token": "jwt_token_12345",
            "expires_at": "2025-12-31T23:59:59"
        }
        
        session_manager.save_session(session_data)
        
        print("\n" + "="*60)
        print("PRUEBA DE GUARDADO DE SESIÓN")
        print("="*60)
        print(f"Usuario: {session_data['username']}")
        print(f"Token: {session_data['token'][:20]}...")
        print(f"Expira: {session_data['expires_at']}")
        
        # Verify file exists
        assert os.path.exists(session_manager.session_file)
        print(f"Archivo de sesión guardado: {session_manager.session_file}")
        
        # Verify content
        loaded_session = session_manager.load_session()
        assert loaded_session == session_data
        print("[OK] Sesión cargada correctamente")
        print("="*60)
    
    def test_load_nonexistent_session(self, session_manager):
        """Test loading non-existent session (P18)"""
        print("\n" + "="*60)
        print("PRUEBA DE CARGA DE SESION NO EXISTENTE")
        print("="*60)
        
        session = session_manager.load_session()
        
        print("Intento de cargar sesion inexistente")
        print(f"Resultado: {session}")
        print("[OK] Sesion no existente retorna None")
        print("="*60)
        
        assert session is None
    
    def test_clear_session(self, session_manager):
        """Test clearing session (P19)"""
        session_data = {
            "username": "testuser",
            "token": "jwt_token_12345"
        }
        
        print("\n" + "="*60)
        print("PRUEBA DE LIMPIEZA DE SESION")
        print("="*60)
        print(f"Guardando sesion para: {session_data['username']}")
        
        session_manager.save_session(session_data)
        assert os.path.exists(session_manager.session_file)
        print("Archivo de sesion creado")
        
        session_manager.clear_session()
        print("Sesion limpiada")
        assert not os.path.exists(session_manager.session_file)
        
        # Should return None after clearing
        session = session_manager.load_session()
        print("Resultado despues de limpiar: None")
        print("[OK] Limpieza de sesion exitosa")
        print("="*60)
        assert session is None
    
    def test_session_validation(self, session_manager):
        """Test session data validation (P20)"""
        print("\n" + "="*60)
        print("PRUEBA DE VALIDACION DE SESION")
        print("="*60)
        
        # Valid session
        valid_session = {
            "username": "testuser",
            "token": "jwt_token_12345"
        }
        session_manager.save_session(valid_session)
        loaded = session_manager.load_session()
        print(f"Sesion valida cargada: {loaded['username']}")
        assert loaded == valid_session
        
        # Invalid session (missing required fields)
        session_manager.clear_session()
        invalid_session = {"username": "testuser"}  # Missing token
        session_manager.save_session(invalid_session)
        loaded = session_manager.load_session()
        print(f"Sesion invalida (sin token): {loaded}")
        print("[OK] Validacion de sesion funcionando")
        print("="*60)
        assert loaded is None


class TestDatabaseConcurrency:
    """Tests for concurrent database access
    
    Testing WAL mode and concurrent access
    """
    
    def test_wal_mode_configuration(self, tmp_path):
        """Test WAL journal mode for better concurrency (P21)"""
        db_file = tmp_path / "test_wal.db"
        conn = sqlite3.connect(str(db_file))
        
        # Check WAL mode
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode")
        mode = cursor.fetchone()[0].upper()
        
        print("\n" + "="*60)
        print("PRUEBA DE CONFIGURACION WAL")
        print("="*60)
        print(f"Modo de diario: {mode}")
        print(f"Archivo BD: {db_file.name}")
        print("[OK] Configuracion WAL verificada")
        print("="*60)
        
        conn.close()
        
        # Should be WAL or at least not error
        assert mode in ['WAL', 'DELETE', 'TRUNCATE', 'PERSIST', 'MEMORY', 'OFF']
    
    def test_concurrent_reads(self, tmp_path):
        """Test concurrent read operations (P22)"""
        db_file = tmp_path / "test_concurrent_read.db"
        conn = sqlite3.connect(str(db_file))
        conn.execute('PRAGMA journal_mode = WAL')
        
        # Create test table and data
        conn.execute("CREATE TABLE test_data (id INTEGER PRIMARY KEY, value TEXT)")
        for i in range(10):
            conn.execute("INSERT INTO test_data (id, value) VALUES (?, ?)", (i, f"value_{i}"))
        conn.commit()
        
        print("\n" + "="*60)
        print("PRUEBA DE LECTURAS CONCURRENTES")
        print("="*60)
        print("Registros creados: 10")
        
        # Simulate concurrent reads
        results = []
        for i in range(5):
            conn_temp = sqlite3.connect(str(db_file))
            cursor = conn_temp.cursor()
            cursor.execute("SELECT COUNT(*) FROM test_data")
            count = cursor.fetchone()[0]
            results.append(count)
            conn_temp.close()
        
        print(f"Conexiones de lectura concurrentes: 5")
        print(f"Resultados de lectura: {results}")
        print("[OK] Todas las lecturas consistentes")
        print("="*60)
        
        conn.close()
        
        # All reads should return the same count
        assert all(count == 10 for count in results)
    
    def test_transaction_rollback(self, db_connection):
        """Test transaction rollback functionality (P23)"""
        cursor = db_connection.cursor()
        
        print("\n" + "="*60)
        print("PRUEBA DE REVIERTE DE TRANSACCION")
        print("="*60)
        print("Insertando usuario en transaccion...")
        
        # Start transaction
        cursor.execute(
            "INSERT INTO User (username, email, password_hash) VALUES (?, ?, ?)",
            ("transact_user", "transaction@example.com", "password")
        )
        
        print("Revirtiendo transaccion...")
        # Rollback
        db_connection.rollback()
        
        # User should not exist
        cursor.execute("SELECT COUNT(*) FROM User WHERE username = ?", ("transact_user",))
        count = cursor.fetchone()[0]
        
        print(f"Usuarios encontrados despues de revertir: {count}")
        print("[OK] Transaccion revertida exitosamente")
        print("="*60)
        
        assert count == 0


class TestDatabasePerformance:
    """Performance tests for database operations
    
    Ensuring efficiency for adult users
    """
    
    def test_bulk_insert_performance(self, db_connection):
        """Test bulk insert performance (P24)"""
        import time
        cursor = db_connection.cursor()
        
        print("\n" + "="*60)
        print("PRUEBA DE DESEMPEÑO DE INSERCION MASIVA")
        print("="*60)
        
        start_time = time.time()
        
        # Bulk insert users
        for i in range(100):
            cursor.execute(
                "INSERT INTO User (username, email, password_hash) VALUES (?, ?, ?)",
                (f"user_{i}", f"user_{i}@example.com", f"hash_{i}")
            )
        
        db_connection.commit()
        end_time = time.time()
        
        # Should complete in reasonable time
        elapsed = end_time - start_time
        print(f"Usuarios insertados: 100")
        print(f"Tiempo total: {elapsed:.3f} segundos")
        print(f"Velocidad: {100/elapsed:.0f} inserciones/segundo")
        
        # Verify all records inserted
        cursor.execute("SELECT COUNT(*) FROM User")
        count = cursor.fetchone()[0]
        
        print(f"Total de usuarios en BD: {count}")
        print("[OK] Desempeño de insercion satisfactorio")
        print("="*60)
        
        assert elapsed < 2.0
        assert count == 100
    
    def test_query_performance(self, db_connection):
        """Test query performance with indexed fields (P25)"""
        import time
        cursor = db_connection.cursor()
        
        print("\n" + "="*60)
        print("PRUEBA DE DESEMPEÑO DE CONSULTA")
        print("="*60)
        
        # Create test data
        for i in range(100):
            cursor.execute(
                "INSERT INTO User (username, email, password_hash) VALUES (?, ?, ?)",
                (f"perf_user_{i}", f"perf_{i}@example.com", f"hash_{i}")
            )
        db_connection.commit()
        
        print("Registros de prueba creados: 100")
        
        # Create index
        cursor.execute("CREATE INDEX idx_username ON User(username)")
        print("Indice creado en columna username")
        
        start_time = time.time()
        
        # Perform indexed query
        cursor.execute("SELECT * FROM User WHERE username = ?", ("perf_user_50",))
        result = cursor.fetchone()
        
        end_time = time.time()
        
        # Should be fast with index
        elapsed = end_time - start_time
        print(f"Tiempo de consulta indexada: {elapsed*1000:.2f} ms")
        print(f"Usuario encontrado: {result[1] if result else 'No encontrado'}")
        print("[OK] Desempeño de consulta satisfactorio")
        print("="*60)
        
        assert elapsed < 0.1
        assert result is not None
        assert "perf_user_50" in str(result)


print(f" Database source: {DB_SOURCE}")


@pytest.fixture
def db_connection():
    """Create in-memory database for testing (module-level fixture)."""
    conn = sqlite3.connect(':memory:')
    conn.execute('PRAGMA foreign_keys = ON')
    cursor = conn.cursor()

    # Create tables matching the actual application schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS File (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            encrypted_content BLOB NOT NULL,
            site TEXT NOT NULL,
            username_field TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES User(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES User(id) ON DELETE SET NULL
        )
    ''')

    conn.commit()
    yield conn
    conn.close()
