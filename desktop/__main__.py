import customtkinter as ctk
from desktop.controllers.app_controller import AppController
from desktop.config import configure_appearance
import sys
from ctypes import windll
import ctypes

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
        self._window_controls = None

        # Mejorar la calidad del texto en Windows
        if sys.platform.startswith('win'):
            try:
                # Configurar la calidad del texto
                self.tk.call('tk', 'scaling', 1.0)
            except Exception:
                print("No se pudo configurar el scaling de texto")

        self.controller = AppController(self)
        self.after(200, self._init_custom_chrome)

        self.controller = AppController(self)
        self.controller.start_app() # <--- Cambio Clave

    # ------------------------------------------------------------------
    # Chrome personalizado sin overrideredirect
    # ------------------------------------------------------------------
    def _init_custom_chrome(self):
        if sys.platform.startswith("win"):
            self._strip_window_chrome(self)
        self._ensure_window_controls()

    def _ensure_window_controls(self):
        if self._window_controls and self._window_controls.winfo_exists():
            self._window_controls.lift()
            return
        self._window_controls = self._build_window_controls()

    def _build_window_controls(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=1.0, x=-10, y=10, anchor="ne")

        button_cfg = {
            "width": 28,
            "height": 22,
            "corner_radius": 8,
            "fg_color": "transparent",
            "font": ctk.CTkFont(size=14, weight="bold"),
        }

        minimize_btn = ctk.CTkButton(
            container,
            text="─",
            hover_color="#E2E8F0",
            text_color="#0F172A",
            command=self._on_minimize,
            **button_cfg,
        )
        minimize_btn.grid(row=0, column=0, padx=2)

        maximize_btn = ctk.CTkButton(
            container,
            text="▢",
            hover_color="#E2E8F0",
            text_color="#0F172A",
            command=self._on_toggle_maximize,
            **button_cfg,
        )
        maximize_btn.grid(row=0, column=1, padx=2)

        close_btn = ctk.CTkButton(
            container,
            text="✕",
            hover_color="#FBD5DC",
            text_color="#EE5A72",
            command=self._on_close,
            **button_cfg,
        )
        close_btn.grid(row=0, column=2, padx=2)
        return container

    def _on_minimize(self):
        self.iconify()

    def _on_toggle_maximize(self):
        try:
            if self.state() == "zoomed":
                self.state("normal")
            else:
                self.state("zoomed")
        except Exception:
            return
        if sys.platform.startswith("win"):
            self.after(60, lambda: self._strip_window_chrome(self))

    def _on_close(self):
        self.on_closing()

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
        if sys.platform.startswith("win"):
            window.after(80, lambda: self._strip_window_chrome(window))

    def _strip_window_chrome(self, window):
        if not sys.platform.startswith("win"):
            return
        try:
            hwnd = int(window.winfo_id())
        except Exception:
            return

        GWL_STYLE = -16
        WS_CAPTION = 0x00C00000
        WS_THICKFRAME = 0x00040000
        WS_MINIMIZEBOX = 0x00020000
        WS_MAXIMIZEBOX = 0x00010000
        WS_SYSMENU = 0x00080000
        SWP_NOSIZE = 0x0001
        SWP_NOMOVE = 0x0002
        SWP_NOZORDER = 0x0004
        SWP_FRAMECHANGED = 0x0020

        try:
            user32 = windll.user32
            style = user32.GetWindowLongW(hwnd, GWL_STYLE)
            new_style = (style | WS_SYSMENU) & ~(WS_CAPTION | WS_THICKFRAME | WS_MINIMIZEBOX | WS_MAXIMIZEBOX)
            user32.SetWindowLongW(hwnd, GWL_STYLE, new_style)
            user32.SetWindowPos(
                hwnd,
                0,
                0,
                0,
                0,
                0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED,
            )
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
