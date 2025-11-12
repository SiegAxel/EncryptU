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
        self._drag_data = {}

        # Mejorar la calidad del texto en Windows
        if sys.platform.startswith('win'):
            try:
                # Configurar la calidad del texto
                self.tk.call('tk', 'scaling', 1.0)
            except Exception:
                print("No se pudo configurar el scaling de texto")

        self.controller = AppController(self)
        self.controller.start_app() # <--- Cambio Clave

    def register_drag_handle(self, widget, *, window=None, direct_only=False):
        target = window or self
        if not isinstance(target, (ctk.CTk, ctk.CTkToplevel)):
            return
        widget.bind(
            "<ButtonPress-1>",
            lambda event, win=target, src=widget, direct=direct_only: self._start_window_drag(event, win, src, direct),
            add="+",
        )
        widget.bind("<B1-Motion>", lambda event, win=target: self._perform_window_drag(event, win), add="+")
        widget.bind("<ButtonRelease-1>", lambda _event, win=target: self._stop_window_drag(win), add="+")

    def _start_window_drag(self, event, window, source, direct_only):
        if direct_only and event.widget is not source:
            return
        offset_x = event.x_root - window.winfo_x()
        offset_y = event.y_root - window.winfo_y()
        self._drag_data[window] = (offset_x, offset_y)

    def _perform_window_drag(self, event, window):
        offset = self._drag_data.get(window)
        if not offset:
            return
        try:
            if hasattr(window, "state") and callable(window.state):
                if window.state() == "zoomed":
                    return
        except Exception:
            pass
        x = event.x_root - offset[0]
        y = event.y_root - offset[1]
        window.geometry(f"+{x}+{y}")

    def _stop_window_drag(self, window):
        self._drag_data.pop(window, None)

    def make_child_borderless(self, window: ctk.CTkToplevel):
        # En esta configuración devolvemos los bordes por defecto del sistema operativo.
        try:
            window.overrideredirect(False)
        except Exception:
            pass

    def on_closing(self):
        self.controller.on_closing()

if __name__ == "__main__":
    # Configurar apariencia antes de crear la ventana
    configure_appearance()
    
    # Iniciar la aplicación
    app = App()
    app.mainloop()
