import customtkinter as ctk
import os
import sys

def configure_appearance():
    """Configura la apariencia global de CustomTkinter para mejor calidad de texto."""
    # Configurar el tema por defecto
    ctk.set_appearance_mode("dark")
    
    font_path = resource_path(os.path.join("assets", "fonts", "Segoe UI.ttf"))
    if os.path.exists(font_path):
        try:
            ctk.FontManager.load_font(font_path)
        except Exception:
            pass
    
    # Configuraciones globales de CustomTkinter
    ctk.set_widget_scaling(1.0)  # Escala de widgets
    ctk.set_window_scaling(1.0)  # Escala de ventanas
    
    # Configurar temas personalizados si es necesario
    ctk.set_default_color_theme("blue")

def resource_path(relative_path: str) -> str:
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return os.path.join(base, relative_path)
    here = os.path.dirname(__file__)
    return os.path.join(here, relative_path)