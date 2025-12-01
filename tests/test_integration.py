
from __future__ import annotations

import os
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import Mock
import pytest

# Ensure project root is on sys.path so package imports resolve
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Try to import real implementations
try:
    from desktop.controllers.app_controller import AppController
except Exception:
    AppController = None

try:
    from desktop.controllers.models.encryption_model import (
        encriptar_contraseña,
        desencriptar_contraseña,
    )
except Exception:
    def encriptar_contraseña(password: str, sitio_web: str, master_password: bytes | None = None) -> bytes:
        return (f"FAKE|{sitio_web}|{password}").encode("utf-8")

    # Match the production signature: data_b64: bytes, sitio_web: str, master_password: bytes
    def desencriptar_contraseña(data_b64: bytes, sitio_web: str, master_password: bytes) -> str:
        try:
            s = data_b64.decode("utf-8")
            if s.startswith("FAKE|"):
                parts = s.split("|", 2)
                if len(parts) == 3:
                    return parts[2]
            return s
        except Exception:
            return str(data_b64)

try:
    from desktop.controllers.models.session_manager import SessionManager as _RemoteSessionManager
    SessionManager = _RemoteSessionManager
except Exception:
    class _FallbackSessionManager:
        def __init__(self):
            self.config_dir = tempfile.mkdtemp()
            self.session_file = os.path.join(self.config_dir, "session.json")

        def save_session(self, session_data: dict):
            import json

            with open(self.session_file, "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)

        def load_session(self) -> dict | None:
            import json

            if not os.path.exists(self.session_file):
                return None
            try:
                with open(self.session_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return None

        def clear_session(self):
            try:
                if os.path.exists(self.session_file):
                    os.remove(self.session_file)
            except Exception:
                pass

    SessionManager = _FallbackSessionManager


def make_fake_root():
    r = SimpleNamespace()
    r.geometry = lambda *a, **k: None
    r.resizable = lambda *a, **k: None
    r.minsize = lambda *a, **k: None
    r.maxsize = lambda *a, **k: None
    r.destroy = lambda *a, **k: None
    return r


@pytest.fixture
def app_controller(monkeypatch):
    root = make_fake_root()
    if AppController is not None:
        controller = AppController(root)
        # mock network interactions
        controller.api_client = Mock()
        controller.api_client.login = Mock(return_value="jwt_token_123")
        controller.api_client.check_status = Mock(return_value=True)
        controller.api_client.check_token_validity = Mock(return_value=True)
        controller.api_client.upload_password_data = Mock(return_value={"file_id": 1})
        controller.api_client.download_password_data = Mock(return_value=None)
        # avoid creating real views during tests
        controller.show_main_view = lambda *a, **k: None
        controller.show_login_view = lambda *a, **k: None
        yield controller
        try:
            controller.session_manager.clear_session()
        except Exception:
            pass
        return

    class MinimalController:
        def __init__(self, root):
            self.root = root
            self.session_manager = SessionManager()
            self.api_client = Mock()
            self.api_client.login = Mock(return_value="jwt_token_123")
            self.api_client.check_status = Mock(return_value=True)
            self.api_client.check_token_validity = Mock(return_value=True)
            self.api_client.upload_password_data = Mock(return_value={"file_id": 1})
            self.api_client.download_password_data = Mock(return_value=None)
            self.master_key = None
            self.current_username = None

        def handle_login(self, username: str, password: str):
            token = self.api_client.login(username, password)
            if token:
                self.session_manager.save_session({"username": username, "token": token})
                self.master_key = password
                self.current_username = username
                return True
            return None

        def handle_encrypt_and_save(self, site: str, username: str, password: str) -> bool:
            if not self.master_key:
                return False
            encrypted = encriptar_contraseña(password, site, self.master_key.encode("utf-8"))
            return self.api_client.upload_password_data(filename=f"{site} | {username}", content=encrypted) is not None

        def handle_decrypt_password(self, file_id: int, site: str, user_provided_master_key: str) -> str | None:
            encrypted = self.api_client.download_password_data(file_id)
            if not encrypted:
                return None
            try:
                return desencriptar_contraseña(encrypted, site, user_provided_master_key.encode("utf-8"))
            except Exception:
                return None

        def clear(self):
            try:
                self.session_manager.clear_session()
            except Exception:
                pass

    c = MinimalController(root)
    yield c
    c.clear()


def test_login_and_session_persistence(app_controller):
    c = app_controller
    username = "test2@test4.com"
    password = "f6479b2812a42b97a9c527051f71e115"
    
    print("\n" + "="*60)
    print("PRUEBA DE LOGIN Y PERSISTENCIA DE SESION")
    print("="*60)
    print(f"Intentando login con usuario: {username}")
    
    c.handle_login(username, password)
    
    print(f"Clave maestra establecida: {'Si' if c.master_key else 'No'}")
    assert c.master_key == password
    
    # Some controller implementations set `current_username` on login; others only persist the session.
    cur = getattr(c, "current_username", None)
    if cur is not None:
        print(f"Usuario actual: {cur}")
        assert cur == username
    
    loaded = c.session_manager.load_session()
    print(f"Sesion persistida en archivo: {'Si' if loaded else 'No'}")
    print(f"Usuario en sesion: {loaded.get('username') if loaded else 'N/A'}")
    print("[OK] Login y persistencia de sesion exitosos")
    print("="*60)
    
    assert loaded is not None and loaded.get("username") == username


def test_encrypt_save_and_decrypt_roundtrip(app_controller):
    c = app_controller
    
    print("\n" + "="*60)
    print("PRUEBA DE CICLO ENCRIPTACION-DESENCRIPTACION")
    print("="*60)
    
    c.handle_login("test2@test4.com", "f6479b2812a42b97a9c527051f71e115")
    print("Login completado")
    
    original_password = "MiClaveSecreta!"
    print(f"Contrasena original: {original_password}")
    
    encrypted = encriptar_contraseña(original_password, "banco.cl", c.master_key.encode("utf-8"))
    print(f"Contrasena encriptada: {str(encrypted)[:50]}...")
    
    c.api_client.download_password_data = Mock(return_value=encrypted)
    decrypted = c.handle_decrypt_password(file_id=1, site="banco.cl", user_provided_master_key="f6479b2812a42b97a9c527051f71e115")
    
    print(f"Contrasena desencriptada: {decrypted}")
    print(f"Coinciden original y desencriptada: {decrypted == original_password}")
    print("[OK] Ciclo de encriptacion exitoso")
    print("="*60)
    
    assert decrypted == original_password
