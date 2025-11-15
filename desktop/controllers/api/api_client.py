import requests
import os
from typing import Optional, List, Dict, Any, cast
import io
from datetime import datetime
import json

class APIClient:
    """
    Encapsula toda la comunicación con la API REST de EncryptU.
    """
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.token: Optional[str] = None

    def _get_auth_headers(self) -> Dict[str, str]:
        if not self.token:
            raise PermissionError("No estás autenticado.")
        return {"Authorization": f"Bearer {self.token}"}
    
    def set_token(self, token: str):
        self.token = token
        
    def register(self, name: str, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Registra un nuevo usuario enviando un payload JSON.
        """
        try:
            payload = {"name": name, "email": email, "password": password}
            print(">>> [CLIENT] Enviando payload a /register:", payload)
            
            # La clave está aquí: usar json=payload para enviar como JSON.
            response = self.session.post(f"{self.base_url}/register", json=payload, timeout=20)
            
            print(">>> [CLIENT] Código de Respuesta:", response.status_code)
            print(">>> [CLIENT] Contenido de Respuesta:", response.text)

            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión al registrar: {e}")
            return None

    def login(self, email: str, password: str) -> Optional[str]:
        """
        Inicia sesión. El campo 'username' del formulario es el email del usuario.
        """
        try:
            form_data = {"username": email, "password": password}
            response = self.session.post(f"{self.base_url}/login", data=form_data, timeout=60)
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                return self.token
            else:
                print(f"Error en login: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión en login: {e}")
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
            response = self.session.get(f"{self.base_url}/status", timeout=60)
            return response.ok
        except requests.exceptions.RequestException:
            return False

    # --- ENDPOINTS DE SOPORTE ---
    def list_support_tickets(self) -> Optional[List[Dict[str, Any]]]:
        try:
            headers = self._get_auth_headers()
            response = self.session.get(f"{self.base_url}/support/tickets", headers=headers, timeout=20)
            if response.status_code == 401:
                return None
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict):
                if data.get("ok") is False:
                    print(f"API soporte respondio con error: {data.get('error')}")
                    return []
                tickets = data.get("tickets")
                if isinstance(tickets, list):
                    return cast(List[Dict[str, Any]], tickets)
            if isinstance(data, list):
                return cast(List[Dict[str, Any]], data)
            return []
        except (requests.exceptions.RequestException, PermissionError) as e:
            print(f"Error al obtener tickets de soporte: {e}")
            return []

    def get_support_ticket_messages(self, ticket_id: int) -> Optional[List[Dict[str, Any]]]:
        try:
            headers = self._get_auth_headers()
            response = self.session.get(
                f"{self.base_url}/support/tickets/{ticket_id}/messages",
                headers=headers,
                timeout=20,
            )
            if response.status_code == 401:
                return None
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict):
                if data.get("ok") is False:
                    print(f"API soporte respondio con error: {data.get('error')}")
                    return []
                messages = data.get("messages")
                if isinstance(messages, list):
                    return cast(List[Dict[str, Any]], messages)
            if isinstance(data, list):
                return cast(List[Dict[str, Any]], data)
            return []
        except (requests.exceptions.RequestException, PermissionError) as e:
            print(f"Error al obtener mensajes de soporte: {e}")
            return []

    def send_support_message(self, ticket_id: int, body: str) -> Optional[Dict[str, Any]]:
        try:
            headers = self._get_auth_headers()
            payload = {"body": body}
            response = self.session.post(
                f"{self.base_url}/support/tickets/{ticket_id}/messages",
                headers=headers,
                json=payload,
                timeout=20,
            )
            if response.status_code == 401:
                return None
            response.raise_for_status()
            try:
                data = response.json()
                if isinstance(data, dict):
                    return data
            except ValueError:
                pass
            return {"ok": True}
        except (requests.exceptions.RequestException, PermissionError) as e:
            print(f"Error al enviar mensaje de soporte: {e}")
            return {"ok": False, "error": str(e)}
    
    def create_support_ticket(self, ticket_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            headers = self._get_auth_headers()
            response = self.session.post(
                f"{self.base_url}/support/tickets",
                headers=headers,
                json=ticket_data,
                timeout=20,
            )
            if response.status_code == 401:
                return None
            response.raise_for_status()
            try:
                data = response.json()
                if isinstance(data, dict):
                    return data
            except ValueError:
                pass
            return {"ok": True}
        except (requests.exceptions.RequestException, PermissionError) as e:
            print(f"Error al crear el ticket de soporte: {e}")
            return {"ok": False, "error": str(e)}

    def export_passwords_data(self, credentials_data: List[Dict[str, Any]]) -> Optional[bytes]:
        """
        Exporta las credenciales como un archivo JSON para descarga.
        """
        try:
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "version": "1.0",
                "credentials": credentials_data
            }
            return json.dumps(export_data, indent=2, ensure_ascii=False).encode('utf-8')
        except Exception as e:
            print(f"Error al exportar datos: {e}")
            return None

    def import_passwords_from_file(self, file_content: str) -> tuple[bool, List[str]]:
        """
        Importa credenciales desde un archivo JSON.
        Retorna (success, error_messages)
        """
        try:
            data = json.loads(file_content)
            
            if not isinstance(data, dict) or "credentials" not in data:
                return False, ["Formato de archivo inválido"]
            
            credentials = data.get("credentials", [])
            if not isinstance(credentials, list):
                return False, ["Estructura de credenciales inválida"]
            
            success_count = 0
            errors = []
            
            for i, cred in enumerate(credentials):
                if not isinstance(cred, dict):
                    errors.append(f"Credencial {i+1}: Formato inválido")
                    continue
                
                required_fields = ["site", "username", "encrypted_content"]
                missing_fields = [field for field in required_fields if field not in cred]
                
                if missing_fields:
                    errors.append(f"Credencial {i+1}: Campos faltantes: {', '.join(missing_fields)}")
                    continue
                
                try:
                    # Upload each credential
                    filename = f"{cred['site']} | {cred['username']}"
                    encrypted_content = cred['encrypted_content'].encode('utf-8') if isinstance(cred['encrypted_content'], str) else cred['encrypted_content']
                    
                    result = self.upload_password_data(filename, encrypted_content)
                    if result:
                        success_count += 1
                    else:
                        errors.append(f"Credencial {i+1}: Error al subir al servidor")
                except Exception as e:
                    errors.append(f"Credencial {i+1}: {str(e)}")
            
            return success_count > 0, errors
            
        except json.JSONDecodeError:
            return False, ["Archivo JSON inválido"]
        except Exception as e:
            return False, [f"Error general: {str(e)}"]