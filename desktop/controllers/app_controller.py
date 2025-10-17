from .views.login_view import LoginView
from .views.main_view import MainView
from .views.register_view import RegisterView
from .api.api_client import APIClient
from .models.encryption_model import encriptar_contraseña, desencriptar_contraseña
from .models.session_manager import SessionManager
import sys
import customtkinter as ctk
from typing import Any, Dict, List, Optional

class AppController:
    """
    Orquesta las interacciones entre las Vistas (UI) y los Modelos (datos/lógica).
    """
    def __init__(self, root):
        self.root = root
        self.current_view = None
        self.api_client = APIClient(base_url="https://encryptu.onrender.com") 
        self.session_manager = SessionManager()
        self.master_key: str | None = None
        self.support_tickets_cache: List[Dict[str, Any]] = []
        self.support_messages_cache: Dict[int, List[Dict[str, Any]]] = {}

    def start_app(self):
        session = self.session_manager.load_session()
        
        if isinstance(session, dict) and isinstance(session.get("token"), str):
            token = session["token"]
            username = session.get("username", "Usuario")
            
            print(f"Sesión encontrada para {username}. Validando token con la API...")
            self.api_client.set_token(token)
            
            if self.api_client.check_token_validity():
                print("Token válido. Mostrando vista principal.")
                self.show_main_view(username)
            else:
                print("Token inválido o caducado. Se requiere nuevo inicio de sesión.")
                self.session_manager.clear_session()
                self.show_login_view()
        else:
            print("No hay sesión válida. Iniciando flujo de primer uso.")
            self._show_initial_view()

    def _show_initial_view(self):
        if self._check_api_status():
            self.show_register_view()
        else:
            print("Error crítico: La API no está disponible. La aplicación se cerrará.")
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

    def show_main_view(self, username: str):
        self._switch_view(MainView, username=username)

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
                    msg = error_detail[0].get('msg', 'Error de validación')
                    if isinstance(self.current_view, RegisterView): self.current_view.show_error(msg)
                else:
                    if isinstance(self.current_view, RegisterView): self.current_view.show_error(str(error_detail))
        else:
            if isinstance(self.current_view, RegisterView): self.current_view.show_error("Error de conexión con el servidor.")
    
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
        self.support_tickets_cache.clear()
        self.support_messages_cache.clear()
        self.show_login_view()

    def get_saved_passwords(self):
        passwords = self.api_client.list_files()
        if passwords is None:
            print("Token inválido al listar archivos. Forzando logout.")
            self.handle_logout()
            return None
        return passwords

    def handle_encrypt_and_save(self, site: str, username: str, password: str) -> bool:
        # --- SECCIÓN CORREGIDA ---
        # 1. Verificar si la master_key no existe.
        if not self.master_key:
            print("Error: No hay clave maestra en la sesión. Solicitando al usuario.")
            
            # 2. Solicitar la clave al usuario.
            dialog = ctk.CTkInputDialog(text="Se requiere tu Clave Maestra para continuar:", title="Verificación de Sesión")
            key = dialog.get_input()
            
            # 3. Si el usuario la ingresa, la guardamos.
            if key:
                self.master_key = key
            # 4. Si el usuario cancela, detenemos la operación de forma segura.
            else:
                print("Operación cancelada. No se proporcionó la clave maestra.")
                if isinstance(self.current_view, MainView):
                    self.current_view.show_status("Operación cancelada. Se requiere la Clave Maestra.", "save", "red")
                return False

        # 5. A este punto, self.master_key está garantizado que es un string.
        try:
            combined_filename = f"{site} | {username}"
            encrypted_data = encriptar_contraseña(password, site, self.master_key.encode('utf-8'))
            result = self.api_client.upload_password_data(filename=combined_filename, content=encrypted_data)
            
            if result is None: 
                self.handle_logout()
            
            return result is not None
        except Exception as e:
            print(f"Error durante la encriptación o subida: {e}")
            return False
        # --- FIN DE LA SECCIÓN CORREGIDA ---

    def handle_delete_password(self, file_id: int) -> bool:
        success = self.api_client.delete_file(file_id)
        if not success: self.handle_logout()
        return success

    def handle_decrypt_password(self, file_id: int, site: str, user_provided_master_key: str) -> str | None:
        encrypted_content = self.api_client.download_password_data(file_id)
        if encrypted_content:
            try:
                return desencriptar_contraseña(encrypted_content, site, user_provided_master_key.encode('utf-8'))
            except Exception:
                return None
        else:
            self.handle_logout()
        return None

    # --- Metodos de soporte ---
    def get_support_tickets(self, force_refresh: bool = False) -> Optional[List[Dict[str, Any]]]:
        if not force_refresh and self.support_tickets_cache:
            return self.support_tickets_cache

        tickets = self.api_client.list_support_tickets()
        if tickets is None:
            self.handle_logout()
            return None

        self.support_tickets_cache = tickets
        return tickets

    def get_support_ticket_messages(self, ticket_id: int, force_refresh: bool = False) -> Optional[List[Dict[str, Any]]]:
        if not force_refresh and ticket_id in self.support_messages_cache:
            return self.support_messages_cache[ticket_id]

        messages = self.api_client.get_support_ticket_messages(ticket_id)
        if messages is None:
            self.handle_logout()
            return None

        self.support_messages_cache[ticket_id] = messages
        return messages

    def handle_send_support_message(self, ticket_id: int, body: str) -> bool:
        body = body.strip()
        if not body:
            return False

        result = self.api_client.send_support_message(ticket_id, body)
        if result is None:
            self.handle_logout()
            return False
        if isinstance(result, dict) and result.get("ok") is False:
            print(f"No se pudo enviar el mensaje de soporte: {result.get('error')}")
            return False

        self.support_messages_cache.pop(ticket_id, None)
        self.support_tickets_cache.clear()
        return True

    def on_closing(self):
        self.root.destroy()
        sys.exit(0)


