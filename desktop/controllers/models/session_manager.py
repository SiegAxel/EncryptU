import json
import os

class SessionManager:
    """
    Gestiona la sesión del usuario guardando y cargando un diccionario 
    de un archivo JSON local.
    """
    def __init__(self):
        # Se mantiene tu lógica para crear una carpeta oculta y el archivo de sesión.
        self.config_dir = os.path.join(os.path.expanduser("~"), ".encryptu_desktop")
        self.session_file = os.path.join(self.config_dir, "session.json")
        os.makedirs(self.config_dir, exist_ok=True)

    def save_session(self, session_data: dict):
        """
        Guarda el diccionario de sesión completo en el archivo.
        Ahora acepta un solo argumento de tipo diccionario.
        """
        try:
            with open(self.session_file, "w") as f:
                json.dump(session_data, f, indent=4)
            print(f"Sesión guardada para el usuario {session_data.get('username')}")
        except IOError as e:
            print(f"Error al guardar la sesión: {e}")

    def load_session(self) -> dict | None:
        """
        Carga la sesión desde el archivo.
        Ahora retorna el diccionario completo o None si no tiene éxito.
        """
        if not os.path.exists(self.session_file):
            return None
        
        try:
            with open(self.session_file, "r") as f:
                session_data = json.load(f)
                # Se verifica que sea un diccionario y contenga las claves esperadas
                if isinstance(session_data, dict) and "token" in session_data and "username" in session_data:
                    print(f"Sesión cargada para el usuario {session_data['username']}")
                    return session_data # Se devuelve el diccionario
                return None
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error al cargar la sesión: {e}")
            return None

    def clear_session(self):
        """Elimina el archivo de sesión para cerrar la sesión."""
        if os.path.exists(self.session_file):
            try:
                os.remove(self.session_file)
                print("Sesión eliminada.")
            except OSError as e:
                print(f"Error al eliminar la sesión: {e}")