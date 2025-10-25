import customtkinter as ctk

def configure_appearance():
    """Configura la apariencia global de CustomTkinter para mejor calidad de texto."""
    # Configurar el tema por defecto
    ctk.set_appearance_mode("dark")
    
    # Configurar la familia de fuentes predeterminada para mejor renderizado
    ctk.FontManager.load_font("assets/fonts/Segoe UI.ttf")  # Asegúrate de tener esta fuente
    
    # Configuraciones globales de CustomTkinter
    ctk.set_widget_scaling(1.0)  # Escala de widgets
    ctk.set_window_scaling(1.0)  # Escala de ventanas
    
    # Configurar temas personalizados si es necesario
    ctk.set_default_color_theme("blue")