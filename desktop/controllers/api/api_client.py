import requests
import os
from typing import Optional, List, Dict, Any
import io

class APIClient:
    """
    Encapsula toda la comunicación con la API REST de EncryptU.
    """
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.token: Optional[str] = None

    def _get_auth_headers(self) -> Dict[str, str]:
        if not self.token:
            raise PermissionError("No estás autenticado.")
        return {"Authorization": f"Bearer {self.token}"}
    
    def set_token(self, token: str):
        self.token = token
        
    def register(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Intenta registrar un nuevo usuario.
        Retorna un diccionario con la respuesta JSON (éxito o error), o None si hay error de conexión.
        """
        try:
            response = requests.post(f"{self.base_url}/register", data={"username": email})
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión al registrar: {e}")
            return None

    def login(self, username: str, password: str) -> Optional[str]:
        """
        Autentica al usuario y retorna el token de acceso si tiene éxito, de lo contrario None.
        """
        try:
            response = self.session.post(f"{self.base_url}/login", data={"username": username, "password": password})
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                return self.token
            else:
                print(f"Fallo de autenticación: {response.status_code} {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión en el login: {e}")
            return None

    def logout(self):
        self.token = None

    def list_files(self) -> Optional[List[Dict[str, Any]]]:
        try:
            headers = self._get_auth_headers()
            response = self.session.get(f"{self.base_url}/files", headers=headers)
            response.raise_for_status()
            return response.json()
        except (requests.exceptions.RequestException, PermissionError) as e:
            print(f"Error al listar archivos: {e}")
            return None

    def upload_password_data(self, filename: str, content: bytes) -> Optional[Dict[str, Any]]:
        """Sube datos en bytes (contraseña encriptada) directamente a la API."""
        try:
            headers = self._get_auth_headers()
            files = {'file': (filename, io.BytesIO(content), 'application/octet-stream')}
            response = self.session.post(f"{self.base_url}/upload", headers=headers, files=files)
            response.raise_for_status()
            return response.json()
        except (requests.exceptions.RequestException, PermissionError) as e:
            print(f"Error al subir la contraseña: {e}")
            return None

    def download_password_data(self, file_id: int) -> Optional[bytes]:
        """Descarga el contenido de un archivo (contraseña encriptada) y lo devuelve en bytes."""
        try:
            headers = self._get_auth_headers()
            with self.session.get(f"{self.base_url}/download/{file_id}", headers=headers, stream=True) as response:
                response.raise_for_status()
                return response.content
        except (requests.exceptions.RequestException, PermissionError) as e:
            print(f"Error al descargar la contraseña: {e}")
            return None

    def delete_file(self, file_id: int) -> bool:
        try:
            headers = self._get_auth_headers()
            response = self.session.delete(f"{self.base_url}/files/{file_id}", headers=headers)
            response.raise_for_status()
            return response.status_code == 200
        except (requests.exceptions.RequestException, PermissionError) as e:
            print(f"Error al eliminar el archivo: {e}")
            return False

    def check_status(self) -> bool:
        try:
            response = self.session.get(f"{self.base_url}/status", timeout=5)
            return response.ok
        except requests.exceptions.RequestException:
            return False

