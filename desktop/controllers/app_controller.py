from .views.login_view import LoginView
from .views.main_view import MainView
from .views.register_view import RegisterView
from .api.api_client import APIClient
from .models.encryption_model import encriptar_contraseña, desencriptar_contraseña
from .models.session_manager import SessionManager
import sys

class AppController:
    """
    Orquesta las interacciones entre las Vistas (UI) y los Modelos (datos/lógica).
    """
    def __init__(self, root):
        self.root = root
        self.current_view = None
        # Asegúrate que esta URL es la correcta para tu API desplegada
        self.api_client = APIClient(base_url="https://encryptu.onrender.com") 
        self.session_manager = SessionManager()
        self.master_key: str | None = None

    def start_app(self):
        """Punto de entrada que decide qué vista mostrar."""
        session = self.session_manager.load_session()
        
        if isinstance(session, dict) and isinstance(session.get("token"), str):
            token = session["token"]
            username = session.get("username", "Usuario")
            
            print(f"Sesión encontrada para {username}. Validando token con la API...")
            self.api_client.set_token(token)
            
            # NUEVO: Verificar si el token guardado sigue siendo válido
            if self.api_client.check_token_validity():
                print("Token válido. Mostrando vista principal.")
                self.show_main_view(username)
            else:
                print("Token inválido o caducado. Se requiere nuevo inicio de sesión.")
                self.session_manager.clear_session() # Limpiamos la sesión corrupta
                self.show_login_view() # Llevamos al login para re-autenticar
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
        if isinstance(self.current_view, (LoginView, RegisterView)):
            self.current_view.pack(expand=True, fill="both")
        else:
            self.current_view.pack(expand=True, fill="both", padx=20, pady=20)

    def show_register_view(self):
        self._switch_view(RegisterView)

    def show_login_view(self):
        self._switch_view(LoginView)

    def show_main_view(self, username: str):
        self._switch_view(MainView, username=username)

    def handle_register(self, email: str):
        # (Sin cambios en esta sección)
        if not email:
            if isinstance(self.current_view, RegisterView): self.current_view.show_error("El correo es requerido.")
            return
        result = self.api_client.register(email)
        if isinstance(result, dict):
            if "master_key" in result:
                if isinstance(self.current_view, RegisterView): self.current_view.show_master_key(result["master_key"])
            elif "detail" in result:
                if isinstance(self.current_view, RegisterView): self.current_view.show_error(str(result["detail"]))
        else:
            if isinstance(self.current_view, RegisterView): self.current_view.show_error("Error de conexión con el servidor.")
    
    def handle_login(self, username: str, password: str):
        # (Sin cambios en esta sección)
        if not username or not password:
            if isinstance(self.current_view, LoginView): self.current_view.show_error("Correo y Clave Maestra son requeridos.")
            return
        token = self.api_client.login(username, password)
        if token:
            session_data = {"username": username, "token": token}
            self.session_manager.save_session(session_data)
            self.master_key = password
            self.show_main_view(username)
        else:
            if isinstance(self.current_view, LoginView): self.current_view.show_error("Correo o Clave Maestra incorrectos.")

    def handle_logout(self):
        self.session_manager.clear_session()
        self.api_client.logout()
        self.master_key = None
        self.show_login_view()

    def get_saved_passwords(self):
        passwords = self.api_client.list_files()
        if passwords is None: # Si el token es inválido, list_files ahora puede devolver None
            print("Token inválido al listar archivos. Forzando logout.")
            self.handle_logout()
            return None
        return passwords

    def handle_encrypt_and_save(self, site: str, username: str, password: str) -> bool:
        if not self.master_key:
            print("Error: No hay clave maestra en la sesión para encriptar.")
            return False
        try:
            combined_filename = f"{site} | {username}"
            encrypted_data = encriptar_contraseña(password, site, self.master_key.encode('utf-8'))
            result = self.api_client.upload_password_data(filename=combined_filename, content=encrypted_data)
            if result is None: self.handle_logout()
            return result is not None
        except Exception as e:
            print(f"Error durante la encriptación o subida: {e}")
            return False

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

    def on_closing(self):
        self.root.destroy()
        sys.exit(0)

