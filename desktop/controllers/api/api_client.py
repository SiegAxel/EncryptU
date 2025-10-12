import requests
import os
from typing import Optional, List, Dict, Any
import io

class APIClient:
    """
    Encapsula toda la comunicación con la API REST de EncryptU.
    """
    def __init__(self, base_url: str):
        # Normalizamos la URL base para quitar cualquier barra al final
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.token: Optional[str] = None

    def _get_auth_headers(self) -> Dict[str, str]:
        if not self.token:
            raise PermissionError("No estás autenticado.")
        return {"Authorization": f"Bearer {self.token}"}
    
    def set_token(self, token: str):
        self.token = token
        
    def register(self, email: str) -> Optional[Dict[str, Any]]:
        try:
            response = requests.post(f"{self.base_url}/register", data={"username": email})
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión al registrar: {e}")
            return None

    def login(self, username: str, password: str) -> Optional[str]:
        try:
            response = self.session.post(f"{self.base_url}/login", data={"username": username, "password": password})
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                return self.token
            else:
                return None
        except requests.exceptions.RequestException:
            return None

    def logout(self):
        self.token = None

    def check_token_validity(self) -> bool:
        if not self.token: return False
        try:
            headers = self._get_auth_headers()
            response = self.session.get(f"{self.base_url}/files", headers=headers, timeout=10)
            return response.status_code != 401
        except (requests.exceptions.RequestException, PermissionError):
            return False

    def list_files(self) -> Optional[List[Dict[str, Any]]]:
        try:
            headers = self._get_auth_headers()
            response = self.session.get(f"{self.base_url}/files", headers=headers)
            if response.status_code == 401: return None
            response.raise_for_status()
            return response.json()
        except (requests.exceptions.RequestException, PermissionError) as e:
            print(f"Error al listar archivos: {e}")
            return None

    def upload_password_data(self, filename: str, content: bytes) -> Optional[Dict[str, Any]]:
        try:
            headers = self._get_auth_headers()
            files = {'file': (filename, io.BytesIO(content), 'application/octet-stream')}
            response = self.session.post(f"{self.base_url}/upload", headers=headers, files=files)
            if response.status_code == 401: return None
            response.raise_for_status()
            return response.json()
        except (requests.exceptions.RequestException, PermissionError) as e:
            print(f"Error al subir la contraseña: {e}")
            return None

    def download_password_data(self, file_id: int) -> Optional[bytes]:
        try:
            headers = self._get_auth_headers()
            with self.session.get(f"{self.base_url}/download/{file_id}", headers=headers, stream=True) as response:
                if response.status_code == 401: return None
                response.raise_for_status()
                return response.content
        except (requests.exceptions.RequestException, PermissionError) as e:
            print(f"Error al descargar la contraseña: {e}")
            return None

    def delete_file(self, file_id: int) -> bool:
        try:
            headers = self._get_auth_headers()
            response = self.session.delete(f"{self.base_url}/files/{file_id}", headers=headers)
            if response.status_code == 401: return False
            response.raise_for_status()
            return response.status_code == 200
        except (requests.exceptions.RequestException, PermissionError) as e:
            print(f"Error al eliminar el archivo: {e}")
            return False

    def check_status(self) -> bool:
        try:
            # --- TIMEOUT AUMENTADO A 30 SEGUNDOS ---
            response = self.session.get(f"{self.base_url}/status", timeout=30)
            return response.ok
        except requests.exceptions.RequestException:
            return False

