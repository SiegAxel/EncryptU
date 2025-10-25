import customtkinter as ctk

class BaseView(ctk.CTkFrame):
    """Clase base para todas las vistas que proporciona funcionalidad común."""
    
    MIN_WIDTH = 1024
    MIN_HEIGHT = 768
    
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self._configure_min_size()
    
    def _configure_min_size(self):
        """Configura el tamaño mínimo de la ventana."""
        root = self.winfo_toplevel()
        if isinstance(root, ctk.CTk):
            # Establecer tamaño inicial si la ventana es más pequeña
            width = max(root.winfo_width(), self.MIN_WIDTH)
            height = max(root.winfo_height(), self.MIN_HEIGHT)
            if width != root.winfo_width() or height != root.winfo_height():
                root.geometry(f"{width}x{height}")
                
            # Función para mantener el tamaño mínimo
            def ensure_min_size():
                w, h = root.winfo_width(), root.winfo_height()
                if w < self.MIN_WIDTH or h < self.MIN_HEIGHT:
                    root.geometry(f"{max(w, self.MIN_WIDTH)}x{max(h, self.MIN_HEIGHT)}")
                root.after(100, ensure_min_size)
            
            # Iniciar el monitoreo del tamaño
            root.after(100, ensure_min_size)