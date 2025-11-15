from desktop.controllers.views.login_view import LoginView
from desktop.controllers.views.main_view import MainView
from desktop.controllers.views.profile_view import ProfileView
from desktop.controllers.views.support_view import SupportView
from desktop.controllers.views.vault_view import VaultView
from desktop.controllers.views.register_view import RegisterView
from desktop.controllers.api.api_client import APIClient
from desktop.controllers.models.encryption_model import encriptar_contraseña, desencriptar_contraseña
from desktop.controllers.models.session_manager import SessionManager
import sys
import customtkinter as ctk
from typing import Any, Dict, List, Optional

class AppController:
    """
    Orquesta las interacciones entre las Vistas (UI) y los Modelos (datos/logica).
    """
    def __init__(self, root):
        self.root = root
        self.root.geometry("1024x640")
        self.root.resizable(True, True)
        try:
            self.root.minsize(1024, 600)
            self.root.maxsize(1200, 720)
        except Exception:
            pass
        
        self.current_view = None
        self.api_client = APIClient(base_url="https://encryptu.onrender.com") 
        self.session_manager = SessionManager()
        self.master_key: str | None = None
        self.current_username: Optional[str] = None
        self.support_tickets_cache: List[Dict[str, Any]] = []
        self.support_messages_cache: Dict[int, List[Dict[str, Any]]] = {}

    def start_app(self):
        session = self.session_manager.load_session()
        
        if isinstance(session, dict) and isinstance(session.get("token"), str):
            token = session["token"]
            username = session.get("username", "Usuario")
            
            print(f"Sesion encontrada para {username}. Validando token con la API...")
            self.api_client.set_token(token)
            
            if self.api_client.check_token_validity():
                print("Token valido. Mostrando vista principal.")
                self.show_main_view(username)
            else:
                print("Token invalido o caducado. Se requiere nuevo inicio de sesion.")
                self.session_manager.clear_session()
                self.show_login_view()
        else:
            print("No hay sesion valida. Iniciando flujo de primer uso.")
            self._show_initial_view()

    def _show_initial_view(self):
        if self._check_api_status():
            self.show_register_view()
        else:
            print("Error cri­tico: La API no esta disponible. La aplicacion se cerrara.")
            self.on_closing()

    def _check_api_status(self) -> bool:
        return self.api_client.check_status()

    def _switch_view(self, new_view_class, *args, **kwargs):
        if self.current_view:
            self.current_view.destroy()
        self.current_view = new_view_class(self.root, self, *args, **kwargs)
        self.current_view.pack(expand=True, fill="both")

    def show_register_view(self):
        self._switch_view(RegisterView)

    def show_login_view(self):
        self._switch_view(LoginView)

    def show_main_view(self, username: Optional[str] = None):
        if username is not None:
            self.current_username = username
        elif self.current_username:
            username = self.current_username
        else:
            username = "Usuario"
            self.current_username = username
        self._switch_view(MainView, username=username)

    def show_profile_view(self, username: Optional[str] = None):
        username = username or self.current_username or "Usuario"
        self._switch_view(ProfileView, username=username)

    def show_vault_view(self, username: Optional[str] = None):
        username = username or self.current_username or "Usuario"
        self._switch_view(VaultView, username=username)

    def show_support_view(self, username: Optional[str] = None):
        username = username or self.current_username or "Usuario"
        self._switch_view(SupportView, username=username)

    def handle_register(self, name: str, email: str, password: str):
        if not name or not email or not password:
            if isinstance(self.current_view, RegisterView): self.current_view.show_error("Todos los campos son requeridos.")
            return
            
        result = self.api_client.register(name, email, password)
        
        if isinstance(result, dict):
            if "id" in result:
                if isinstance(self.current_view, RegisterView): self.current_view.show_registration_success()
            elif "detail" in result:
                error_detail = result["detail"]
                if isinstance(error_detail, list) and len(error_detail) > 0:
                    msg = error_detail[0].get('msg', 'Error de validacion')
                    if isinstance(self.current_view, RegisterView): self.current_view.show_error(msg)
                else:
                    if isinstance(self.current_view, RegisterView): self.current_view.show_error(str(error_detail))
        else:
            if isinstance(self.current_view, RegisterView): self.current_view.show_error("Error de conexion con el servidor.")
    
    def handle_login(self, username: str, password: str):
        if not username or not password:
            if isinstance(self.current_view, LoginView): self.current_view.show_error("Correo y Contraseña son requeridos.")
            return
        
        token = self.api_client.login(username, password)
        
        if token:
            session_data = {"username": username, "token": token}
            self.session_manager.save_session(session_data)
            self.master_key = password
            self.show_main_view(username)
        else:
            if isinstance(self.current_view, LoginView): self.current_view.show_error("Correo o Contraseña incorrectos.")

    def handle_logout(self):
        self.session_manager.clear_session()
        self.api_client.logout()
        self.master_key = None
        self.current_username = None
        self.support_tickets_cache.clear()
        self.support_messages_cache.clear()
        self.show_login_view()

    def get_saved_passwords(self):
        passwords = self.api_client.list_files()
        if passwords is None:
            print("No se pudieron obtener las credenciales desde la API. La sesión continúa activa.")
            return None
        return passwords

    def handle_encrypt_and_save(self, site: str, username: str, password: str) -> bool:
        # --- SECCIiN CORREGIDA ---
        # 1. Verificar si la master_key no existe.
        if not self.master_key:
            print("Error: No hay clave maestra en la sesion. Solicitando al usuario.")
            
            # 2. Solicitar la clave al usuario.
            dialog = ctk.CTkInputDialog(text="Se requiere tu Clave Maestra para continuar:", title="Verificacion de Sesion")
            key = dialog.get_input()
            
            # 3. Si el usuario la ingresa, la guardamos.
            if key:
                self.master_key = key
            # 4. Si el usuario cancela, detenemos la operacion de forma segura.
            else:
                print("Operacion cancelada. No se proporciono la clave maestra.")
                view = self.current_view
                if view is not None and hasattr(view, "show_status"):
                    try:
                        view.show_status("Operacion cancelada. Se requiere la Clave Maestra.", "save", "red")
                    except Exception:
                        pass
                return False

        # 5. A este punto, self.master_key esta garantizado que es un string.
        try:
            combined_filename = f"{site} | {username}"
            encrypted_data = encriptar_contraseña(password, site, self.master_key.encode('utf-8'))
            result = self.api_client.upload_password_data(filename=combined_filename, content=encrypted_data)

            if result is None:
                print("La API rechazó la subida de la credencial, pero no se cerrará la sesión del usuario.")
            return result is not None
        except Exception as e:
            print(f"Error durante la encriptacion o subida: {e}")
            return False
        # --- FIN DE LA SECCIiN CORREGIDA ---

    def handle_delete_password(self, file_id: int) -> bool:
        success = self.api_client.delete_file(file_id)
        return success

    def handle_decrypt_password(self, file_id: int, site: str, user_provided_master_key: str) -> str | None:
        encrypted_content = self.api_client.download_password_data(file_id)
        if encrypted_content:
            try:
                return desencriptar_contraseña(encrypted_content, site, user_provided_master_key.encode('utf-8'))
            except Exception:
                return None
        return None

    def handle_get_encrypted_password(self, file_id: int) -> bytes | None:
        return self.api_client.download_password_data(file_id)

    # --- Metodos de soporte ---
    def get_support_tickets(self, force_refresh: bool = False) -> Optional[List[Dict[str, Any]]]:
        if not force_refresh and self.support_tickets_cache:
            return self.support_tickets_cache

        tickets = self.api_client.list_support_tickets()
        if tickets is None:
            return None

        self.support_tickets_cache = tickets
        return tickets

    def get_support_ticket_messages(self, ticket_id: int, force_refresh: bool = False) -> Optional[List[Dict[str, Any]]]:
        if not force_refresh and ticket_id in self.support_messages_cache:
            return self.support_messages_cache[ticket_id]

        messages = self.api_client.get_support_ticket_messages(ticket_id)
        if messages is None:
            return None

        self.support_messages_cache[ticket_id] = messages
        return messages

    def handle_send_support_message(self, ticket_id: int, body: str) -> bool:
        body = body.strip()
        if not body:
            return False

        result = self.api_client.send_support_message(ticket_id, body)
        if result is None:
            return False
        if isinstance(result, dict) and result.get("ok") is False:
            print(f"No se pudo enviar el mensaje de soporte: {result.get('error')}")
            return False

        self.support_messages_cache.pop(ticket_id, None)
        self.support_tickets_cache.clear()
        return True

    def handle_create_support_ticket(self, ticket_data: Dict[str, Any]) -> tuple[bool, Optional[int], str]:
        cleaned_payload = {
            key: value.strip() if isinstance(value, str) else value
            for key, value in ticket_data.items()
        }

        response = self.api_client.create_support_ticket(cleaned_payload)
        if response is None:
            return False, None, "No pudimos contactar al servidor. Intenta nuevamente."

        if isinstance(response, dict):
            if response.get("ok") is False:
                error_msg = str(response.get("error") or "No se pudo crear el ticket.")
                return False, None, error_msg

            ticket_id = None
            ticket_payload = response.get("ticket")
            message = response.get("message") or response.get("msg") or "Ticket creado correctamente."

            if isinstance(ticket_payload, dict):
                ticket_id = ticket_payload.get("id")

            self.support_tickets_cache.clear()
            self.support_messages_cache.clear()
            return True, ticket_id, message

        self.support_tickets_cache.clear()
        self.support_messages_cache.clear()
        return True, None, "Ticket creado correctamente."

    # --- Metodos de exportacion/importacion ---
    def handle_export_passwords(self, credentials_data: List[Dict[str, Any]]) -> Optional[bytes]:
        """
        Exporta las credenciales como un archivo JSON.
        """
        if not credentials_data:
            return None
        
        try:
            # Preparar datos para exportacion (incluir contenido encriptado)
            export_data = []
            for cred in credentials_data:
                file_id = cred.get("id")
                if file_id:
                    encrypted_content = self.api_client.download_password_data(int(file_id))
                    if encrypted_content:
                        try:
                            encrypted_text = encrypted_content.decode("utf-8").strip()
                        except UnicodeDecodeError:
                            encrypted_text = encrypted_content.decode("latin-1").strip()
                        
                        export_data.append({
                            "site": cred.get("site", ""),
                            "username": cred.get("username", ""),
                            "encrypted_content": encrypted_text
                        })
            
            return self.api_client.export_passwords_data(export_data)
        except Exception as e:
            print(f"Error al exportar contraseñas: {e}")
            return None

    def handle_import_passwords(self, file_content: str) -> tuple[bool, List[str]]:
        """
        Importa credenciales desde un archivo JSON.
        Retorna (success, error_messages)
        """
        success, errors = self.api_client.import_passwords_from_file(file_content)
        if success:
            self.refresh_vault_data()
        return success, errors

    def refresh_vault_data(self):
        """
        Refresca los datos del vault en la vista actual si es un VaultView.
        """
        if isinstance(self.current_view, VaultView):
            self.current_view.refresh_password_list()

    def on_closing(self):
        self.root.destroy()
        sys.exit(0)


