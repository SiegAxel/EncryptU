import os
import sys
from typing import Callable
import pytest
from types import SimpleNamespace

# Add project paths to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
desktop_path = os.path.join(project_root, 'desktop', 'controllers')
src_path = os.path.join(project_root, 'src')

# Add paths in order of preference
if os.path.exists(desktop_path):
    sys.path.insert(0, desktop_path)
if os.path.exists(src_path):
    sys.path.insert(0, src_path)
sys.path.insert(0, project_root)

try:
    # pytest-html provides `extras.image(path)` helper used by the hook
    from pytest_html import extras
except Exception:
    # If pytest-html is not installed, provide a no-op fallback so tests still run.
    extras = SimpleNamespace(image=lambda path: path)

from tests.helpers.evidence import text_to_image, take_screenshot

# Global configuration for testing
TEST_CONFIG = {
    "crypto_source": None,  # Will be set based on successful imports
    "test_data_dir": os.path.join(project_root, "tests", "test_data"),
    "reports_dir": os.path.join(project_root, "reports"),
    "temp_dir": os.path.join(project_root, "tests", "temp")
}

# Create necessary directories
for dir_path in [TEST_CONFIG["test_data_dir"], TEST_CONFIG["reports_dir"], TEST_CONFIG["temp_dir"]]:
    os.makedirs(dir_path, exist_ok=True)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to attach saved screenshots/images to the html report when available.

    Tests can append file paths to `request.node.screenshots` (a list of paths).
    """
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call":
        extra = getattr(rep, "extra", [])
        screenshots = getattr(item, "screenshots", [])
        for path in screenshots:
            if os.path.exists(path):
                extra.append(extras.image(path))
        rep.extra = extra


@pytest.fixture(scope="session")
def crypto_functions():
    """Fixture to provide encryption functions with fallback implementations"""
    # Try to import real functions first
    try:
        from desktop.controllers.models.encryption_model import encriptar_contraseña, desencriptar_contraseña
        TEST_CONFIG["crypto_source"] = "desktop"
        return encriptar_contraseña, desencriptar_contraseña
    except ImportError:
        try:
            from crypto.encryption import encriptar_contraseña as real_encriptar
            TEST_CONFIG["crypto_source"] = "src"
            
            # Implement fallback for desencriptar_contraseña
            import base64
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.backends import default_backend
            
            def fallback_desencriptar(data_b64: bytes, sitio_web: str, master_password: bytes) -> str:
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
            
            return real_encriptar, fallback_desencriptar
        except ImportError:
            # Final fallback
            TEST_CONFIG["crypto_source"] = "mock"
            
            def fallback_encriptar(password: str, sitio_web: str, master_password: bytes | None = None) -> bytes:
                return f"encrypted_{password}_{sitio_web}".encode()
            
            def fallback_desencriptar_final(encrypted_data: bytes, sitio_web: str, master_password: bytes) -> str:
                return encrypted_data.decode().replace("encrypted_", "").replace(f"_{sitio_web}", "")
            
            return fallback_encriptar, fallback_desencriptar_final


@pytest.fixture
def evidence(request) -> dict:
    """Fixture that exposes two helpers:
    - `text_to_image(text, name=None)` -> saves text as PNG and attaches to report
    - `screenshot(name=None)` -> takes a screenshot and attaches to report
    """
    node = request.node

    def _attach_path(path: str):
        node.screenshots = getattr(node, "screenshots", [])
        node.screenshots.append(path)
        return path

    def _text_to_image(text: str, name: str | None = None) -> str:
        filename = name
        path = text_to_image(text, filename=filename) if name else text_to_image(text)
        return _attach_path(path)

    def _screenshot(name: str | None = None) -> str:
        path = take_screenshot(filename=name) if name else take_screenshot()
        return _attach_path(path)

    return {
        "text_to_image": _text_to_image,
        "screenshot": _screenshot,
    }


@pytest.fixture
def test_config():
    """Fixture providing test configuration"""
    return TEST_CONFIG


@pytest.fixture
def session_manager():
    """Fixture providing session manager for testing"""
    try:
        from desktop.controllers.models.session_manager import SessionManager
        manager = SessionManager()
        yield manager
        manager.clear_session()
    except ImportError:
        # Fallback session manager
        import tempfile
        import json
        
        class FallbackSessionManager:
            def __init__(self):
                self.temp_dir = tempfile.mkdtemp()
                self.session_file = os.path.join(self.temp_dir, "session.json")
            
            def save_session(self, session_data):
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
        
        manager = FallbackSessionManager()
        yield manager
        manager.clear_session()


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers and settings"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "functional: mark test as a functional test"
    )
    config.addinivalue_line(
        "markers", "usability: mark test as a usability test"
    )
    config.addinivalue_line(
        "markers", "regression: mark test as a regression test"
    )
    config.addinivalue_line(
        "markers", "elderly: mark test as specifically for elderly users"
    )
    config.addinivalue_line(
        "markers", "critical: mark test as critical priority"
    )
    config.addinivalue_line(
        "markers", "high: mark test as high priority"
    )
    config.addinivalue_line(
        "markers", "medium: mark test as medium priority"
    )
    config.addinivalue_line(
        "markers", "low: mark test as low priority"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# Print crypto source on test discovery
def pytest_sessionstart(session):
    """Print test configuration when session starts"""
    print(f"\n{'='*60}")
    print(f"EncryptU Test Suite Configuration")
    print(f"{'='*60}")
    print(f"Project Root: {project_root}")
    print(f"Crypto Source: {TEST_CONFIG.get('crypto_source', 'unknown')}")
    print(f"Test Data Dir: {TEST_CONFIG['test_data_dir']}")
    print(f"Reports Dir: {TEST_CONFIG['reports_dir']}")
    print(f"Temporary Dir: {TEST_CONFIG['temp_dir']}")
    print(f"{'='*60}\n")
