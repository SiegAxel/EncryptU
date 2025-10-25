import customtkinter as ctk
from .controllers.app_controller import AppController
from .config import configure_appearance
import sys
from ctypes import windll

def set_dpi_awareness():
    """Configura la aplicación para ser DPI aware y mejorar la calidad del texto."""
    try:
        # Intentar el método más nuevo primero (Windows 10 1607 o posterior)
        windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
    except AttributeError:
        try:
            # Método más antiguo
            windll.user32.SetProcessDPIAware()
        except AttributeError:
            # Falló la configuración de DPI
            pass

class App(ctk.CTk):
    def __init__(self):
        # Configurar DPI awareness antes de crear la ventana
        if sys.platform.startswith('win'):
            set_dpi_awareness()
            
        super().__init__()
        self.title("EncryptU Desktop")
        self.geometry("1024x768")  # Tamaño inicial ajustado
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Mejorar la calidad del texto en Windows
        if sys.platform.startswith('win'):
            try:
                # Configurar la calidad del texto
                self.tk.call('tk', 'scaling', 1.0)
            except Exception:
                print("No se pudo configurar el scaling de texto")

        self.controller = AppController(self)
        self.controller.start_app() # <--- Cambio Clave

    def on_closing(self):
        self.controller.on_closing()

if __name__ == "__main__":
    # Configurar apariencia antes de crear la ventana
    configure_appearance()
    
    # Iniciar la aplicación
    app = App()
    app.mainloop()
