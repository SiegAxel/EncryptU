import customtkinter as ctk
from datetime import datetime
from typing import Dict, Optional
import pywinstyles
from PIL import Image

# --- Colores de fondo ---
COLOR_BACKGROUND = None        # Color de fondo principal de la aplicación
COLOR_SURFACE = "#050030"     # Color de fondo para tarjetas y elementos elevados
COLOR_HERO = "#FFFFFF"        # Color de fondo para la sección hero
COLOR_CARD = "#FFFFFF"        # Color gris medio para tarjetas
COLOR_STAT_CARD = "#FFFFFF"   # Color gris claro para tarjetas de estadísticas

# --- Colores de texto ---
COLOR_TEXT = "#FFFFFF"        # Color principal para texto
COLOR_TEXT_MUTED = "#94A3B8"  # Color para texto secundario/descriptivo
COLOR_HERO_TITLE = "#F5F5F5"  # Rojo brillante para título del hero
COLOR_STAT_TEXT = "#FF0000"  # Color claro para texto de estadísticas
COLOR_HERO_SUBTITLE = "#C4C4C4"  # Rojo más claro para subtítulo del hero

# --- Colores de acento para tarjetas ---
COLOR_CARD_TITLE = "#FF4D3D"  # Rojo suave para títulos de tarjetas
COLOR_CARD_TEXT = "#FF6969"   # Rojo muy suave para texto de tarjetas

# --- Colores de acento y primario ---
COLOR_ACCENT = "#F43F5E"      # Color de acento (rojo) - Para elementos destacados y acciones secundarias
COLOR_ACCENT_DARK = "#DC1F45" # Versión oscura del acento - Para estados hover
COLOR_PRIMARY = "#2563EB"     # Color primario (azul) - Para acciones principales
COLOR_PRIMARY_DARK = "#1D4ED8" # Versión oscura del primario - Para estados hover

# --- Colores de borde ---
COLOR_CARD_BORDER = "#FF0000" # Color para bordes de tarjetas y separadores

# --- Otros colores usados en la vista ---
# Profile card: "#050030" (Fondo de la tarjeta de perfil)
# Text light: "#F8FAFC" (Texto claro sobre fondos oscuros)
# Text muted light: "#E2E8F0" (Texto secundario sobre fondos oscuros)
# Hover effects: "#2B2B2B" (Efecto hover en botones sobre fondos oscuros)

GRADIENT_PATH = "desktop/controllers/img/bannerEncryptU.png"
MIN_HERO_HEIGHT = 260  # Altura mínima del hero
HERO_ASPECT_RATIO = 0.3  # Proporción alto/ancho deseada para el hero (30% del ancho)


from .base_view import BaseView

class MainView(BaseView):
    """Pantalla principal que actua como hub de navegacion para EncryptU."""
    

    def __init__(self, master, controller, username: str):
        # Configurar escala para mejor renderizado
        try:
            self.tk.call('tk', 'scaling', 1.0)  # Ajustar scaling global
        except Exception:
            pass
            
        super().__init__(master, fg_color=COLOR_BACKGROUND)
        self.controller = controller
        self.username = username or "Usuario"
        self.transparent_color = "#000001"  # Color específico para elementos transparentes
        
        # Configurar tamaño mínimo de la ventana principal
        root = self.winfo_toplevel()
        if isinstance(root, ctk.CTk):
            root.geometry("1024x768")  # Tamaño inicial
            root.resizable(True, True)  # Permitir redimensionar
            
            def ensure_min_size():
                w, h = root.winfo_width(), root.winfo_height()
                if w < 1024 or h < 768:
                    root.geometry(f"{max(w, 1024)}x{max(h, 768)}")
                root.after(100, ensure_min_size)
            
            root.after(100, ensure_min_size)
        
        # Configurar tamaño mínimo de la ventana principal
        root = self.winfo_toplevel()
        if isinstance(root, ctk.CTk):
            root.geometry("1024x768")  # Tamaño inicial
            root.resizable(True, True)  # Permitir redimensionar
            try:
                root.minsize(1024, 768)  # Establecer tamaño mínimo
            except Exception as e:
                print(f"No se pudo establecer el tamaño mínimo: {e}")
                # Fallback usando geometry y after
                root.after(100, lambda: root.geometry(f"{max(root.winfo_width(), 1024)}x{max(root.winfo_height(), 768)}"))
        
        # Configurar tamaño mínimo de la ventana principal
        if isinstance(self.winfo_toplevel(), ctk.CTk):
            root = self.winfo_toplevel()
            root.geometry("1024x768")  # Tamaño inicial
            root.resizable(True, True)  # Permitir redimensionar
            root.after(100, lambda: root.geometry(f"{max(root.winfo_width(), 1024)}x{max(root.winfo_height(), 768)}"))
        
        # Configurar tamaño mínimo de la ventana principal
        root = self.winfo_toplevel()
        root.geometry("1024x768")  # Tamaño inicial
        root.resizable(True, True)  # Permitir redimensionar
        # Establecer tamaño mínimo de forma soportada por Tk/Toplevel
        def _safe_set_minsize(win, w=1024, h=768):
            try:
                # Solo llamar a minsize si el objeto realmente lo expone
                if hasattr(win, "minsize") and callable(getattr(win, "minsize")):
                    win.minsize(w, h)
                # Intentar con el toplevel si está disponible
                elif hasattr(win, "winfo_toplevel"):
                    toplevel = win.winfo_toplevel()
                    if hasattr(toplevel, "minsize") and callable(getattr(toplevel, "minsize")):
                        toplevel.minsize(w, h)
                    else:
                        setattr(win, "_min_width", w)
                        setattr(win, "_min_height", h)
                else:
                    setattr(win, "_min_width", w)
                    setattr(win, "_min_height", h)
            except Exception:
                # Fallback: almacenar atributos mínimos para que otras partes del código puedan leerlos
                try:
                    setattr(win, "_min_width", w)
                    setattr(win, "_min_height", h)
                except Exception:
                    pass

        _safe_set_minsize(root)

        # Configurar tamaño mínimo de la ventana principal para master.master si es CTk
        if hasattr(self, "master") and hasattr(self.master, "master") and isinstance(self.master.master, ctk.CTk):
            self.master.master.geometry("1024x768")  # Tamaño inicial
            self.master.master.resizable(True, True)  # Permitir redimensionar
            _safe_set_minsize(self.master.master)
        


        self.fonts = self._build_fonts()
        self.hero_source = self._load_gradient()
        self.hero_image: Optional[ctk.CTkImage] = None
        self.hero_label: Optional[ctk.CTkLabel] = None
        self._hero_width = 0
        self._transparent_widgets = []  # Lista para mantener referencia a widgets transparentes

        self._build_layout()
        self.bind("<Configure>", self._handle_resize)
        self.after(100, self._apply_transparencies)  # Aplicar transparencias después de que la UI esté construida
        
    def _make_transparent(self, widget):
        """Hacer un widget transparente y mantener su referencia."""
        if hasattr(widget, 'winfo_id'):  # Verificar si es un widget válido
            widget.configure(bg_color=self.transparent_color)
            self._transparent_widgets.append(widget)
            
    def _apply_transparencies(self):
        """Aplicar efecto de transparencia a todos los widgets registrados."""
        for widget in self._transparent_widgets:
            if hasattr(widget, 'winfo_id'):  # Verificar que el widget aún existe
                try:
                    pywinstyles.set_opacity(widget.winfo_id(), color=self.transparent_color)
                except Exception as e:
                    print(f"Error al aplicar transparencia: {e}")

    # ------------------------------------------------------------------
    # Construccion y diseno
    # ------------------------------------------------------------------
    def _build_fonts(self) -> Dict[str, ctk.CTkFont]:
        # Usar Arial para máxima legibilidad en el texto de bienvenida
        # y Segoe UI para el resto de la interfaz
        return {
            "hero_title": ctk.CTkFont(family="Arial", size=52, weight="bold"),
            "hero_sub": ctk.CTkFont(family="Arial", size=20),
            "section": ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            "card_title": ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            "card_body": ctk.CTkFont(family="Segoe UI", size=16),
            "button": ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            "stat": ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            "username": ctk.CTkFont(family="Arial", size=18, weight="bold"),  # Nuevo font específico para el nombre de usuario
        }

    def _load_gradient(self) -> Image.Image:
        try:
            # Cargar la imagen original sin modificar su tamaño
            img = Image.open(GRADIENT_PATH)
            return img
            
        except Exception as e:
            print(f"Error loading banner image: {e}")
            # En caso de error, crear un degradado como respaldo
            gradient = Image.new("RGB", (1200, int(1200 * HERO_ASPECT_RATIO)), COLOR_SURFACE)
            overlay = Image.new("RGB", gradient.size, COLOR_ACCENT)
            mask = Image.new("L", (1, gradient.height))
            for y in range(gradient.height):
                mask.putpixel((0, y), int(255 * (y / max(gradient.height - 1, 1))))
            mask = mask.resize(gradient.size)
            return Image.composite(overlay, gradient, mask)

    def _build_layout(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_hero_section()
        self._build_body_section()

    def _build_hero_section(self):
        # Crear el contenedor principal del hero
        hero = ctk.CTkFrame(self, fg_color=COLOR_SURFACE)
        hero.grid(row=0, column=0, sticky="nsew", pady=(0, 0))
        
        # Calcular altura inicial basada en el ancho de la ventana
        initial_width = max(self.winfo_toplevel().winfo_width() or 1024, 1024)
        initial_height = max(int(initial_width * HERO_ASPECT_RATIO), MIN_HERO_HEIGHT)
        
        # Configurar dimensiones iniciales
        hero.configure(height=initial_height)
        
        # Calcular dimensiones de la imagen
        img_ratio = self.hero_source.width / self.hero_source.height
        window_ratio = initial_width / initial_height
        
        if window_ratio > img_ratio:
            new_width = int(initial_width * 1.1)
            new_height = int(new_width / img_ratio)
        else:
            new_height = initial_height
            new_width = int(new_height * img_ratio)
            if new_width < initial_width:
                new_width = initial_width
        
        # Crear la imagen con las dimensiones calculadas
        self.hero_image = ctk.CTkImage(
            light_image=self.hero_source,
            dark_image=self.hero_source,
            size=(new_width, new_height)
        )
        
        # Container para la imagen que asegura el centrado
        image_container = ctk.CTkFrame(hero, fg_color="transparent")
        image_container.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)
        
        # Label de fondo con la imagen
        self.hero_label = ctk.CTkLabel(
            image_container,
            text="",
            image=self.hero_image,
            fg_color="transparent"
        )
        self.hero_label.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)
        
        # Frame para el contenido
        content = ctk.CTkFrame(hero, fg_color=self.transparent_color)
        content.pack(expand=True, fill="both", padx=36, pady=28)
        content.grid_columnconfigure(0, weight=2)
        content.grid_columnconfigure(1, weight=1)
        self._make_transparent(content)
        
        # También hacer transparente el label de la imagen para mejor integración
        self.hero_label.configure(fg_color=self.transparent_color)
        self._make_transparent(self.hero_label)

        title = ctk.CTkLabel(
            content,
            text="Bienvenido a EncryptU",
            font=self.fonts["hero_title"],
            text_color=COLOR_HERO_TITLE,
            fg_color="transparent"  # Asegurar que no haya fondo que pueda afectar la nitidez
        )
        title.grid(row=0, column=0, sticky="w")

        subtitle = ctk.CTkLabel(
            content,
            text="Administra tus credenciales, perfil y soporte desde un solo lugar.",
            font=self.fonts["hero_sub"],
            text_color=COLOR_HERO_SUBTITLE,
            fg_color="transparent"  # Asegurar que no haya fondo que pueda afectar la nitidez
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(10, 0))

        quick_action = ctk.CTkButton(
            content,
            text="Ir a mis credenciales",
            command=self._open_vault,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_DARK,
            text_color="#F9FAFB",
            font=self.fonts["button"],
            corner_radius=28,
            width=200,
        )
        quick_action.grid(row=2, column=0, sticky="w", pady=(20, 0))

    def _build_body_section(self):
        # Frame principal con degradado
        body = ctk.CTkFrame(self, fg_color=COLOR_SURFACE)
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure((0, 1), weight=1, uniform="col")
        body.grid_rowconfigure(1, weight=1)

        # Contenedor para elementos
        info = ctk.CTkFrame(body, fg_color="transparent")
        info.grid(row=0, column=0, columnspan=2, sticky="ew", padx=36, pady=(28, 12))
        info.grid_columnconfigure(0, weight=1)
        info.grid_columnconfigure(1, weight=1)
        info.grid_columnconfigure(2, weight=1)

        self._build_stat(info, 0, "Ultimo acceso", datetime.now().strftime("%d/%m/%Y %H:%M"))
        self._build_stat(info, 1, "Suscripcion", "Activa")
        self._build_stat(info, 2, "Estado de Seguridad", "Optimizado")

        nav_section = ctk.CTkFrame(body, fg_color=self.transparent_color)
        nav_section.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=36, pady=(10, 32))
        nav_section.grid_columnconfigure((0, 1, 2), weight=1, uniform="card")
        nav_section.grid_rowconfigure(0, weight=1)
        self._make_transparent(nav_section)

        self._build_nav_card(
            nav_section,
            column=0,
            title="Mi Perfil",
            description="Revisa tus datos personales y gestiona la suscripcion.",
            button_text="Ir al perfil",
            command=self._open_profile,
        )
        self._build_nav_card(
            nav_section,
            column=1,
            title="Credenciales",
            description="Guarda, encripta y organiza tus contrasenas seguras.",
            button_text="Gestionar credenciales",
            command=self._open_vault,
            accent_color=COLOR_PRIMARY,
        )
        self._build_nav_card(
            nav_section,
            column=2,
            title="Soporte & Tickets",
            description="Consulta el estado de tus tickets y chatea con soporte.",
            button_text="Ir a soporte",
            command=self._open_support,
            accent_color=COLOR_ACCENT,
        )

        footer = ctk.CTkFrame(body, fg_color="transparent")
        footer.grid(row=2, column=0, columnspan=2, sticky="ew", padx=36, pady=(0, 32))
        footer.grid_columnconfigure(0, weight=1)

        logout = ctk.CTkButton(
            footer,
            text="Cerrar Sesion",
            command=self.controller.handle_logout,
            fg_color="transparent",
            hover_color="#E5E7EB",
            text_color=COLOR_ACCENT,
            font=self.fonts["button"],
        )
        logout.pack(side="right")

    def _build_stat(self, parent: ctk.CTkFrame, column: int, label: str, value: str):
        frame = ctk.CTkFrame(parent, fg_color=COLOR_STAT_CARD, corner_radius=18, border_width=1, border_color="#404040")
        frame.grid(row=0, column=column, padx=12, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)

        label_widget = ctk.CTkLabel(frame, text=label, font=self.fonts["card_body"], text_color=COLOR_CARD_TEXT)
        label_widget.grid(row=0, column=0, padx=20, pady=(18, 4), sticky="w")

        # Usar el color rojo brillante del título para los valores
        value_widget = ctk.CTkLabel(
            frame,
            text=value,
            font=self.fonts["stat"],
            text_color=COLOR_STAT_TEXT  # Color rojo brillante
        )
        value_widget.grid(row=1, column=0, padx=20, pady=(0, 18), sticky="w")

    def _build_nav_card(
        self,
        parent: ctk.CTkFrame,
        column: int,
        title: str,
        description: str,
        button_text: str,
        command,
        accent_color: str = COLOR_PRIMARY,
    ):
        card = ctk.CTkFrame(parent, fg_color=COLOR_CARD, corner_radius=24, border_width=1, border_color="#404040")
        card.grid(row=0, column=column, padx=12, sticky="nsew")
        card.grid_rowconfigure(0, weight=1)
        card.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(card, text=title, font=self.fonts["card_title"], text_color=COLOR_CARD_TITLE)
        title_label.grid(row=0, column=0, sticky="w", padx=24, pady=(24, 8))

        # Si es la tarjeta de perfil, mostrar el nombre de usuario
        if title == "Mi Perfil" and hasattr(self, 'username'):
            username_label = ctk.CTkLabel(
                card,
                text=self._format_username(self.username),
                font=self.fonts["username"],  # Usando el nuevo font específico para el nombre
                text_color="#FFFFFF",
                fg_color="transparent"  # Asegurar máxima nitidez
            )
            username_label.grid(row=1, column=0, sticky="w", padx=24, pady=(0, 8))

        body_label = ctk.CTkLabel(
            card,
            text=description,
            font=self.fonts["card_body"],
            text_color=COLOR_CARD_TEXT,
            justify="left",
            wraplength=260,
        )
        body_label.grid(row=2 if title == "Mi Perfil" else 1, column=0, sticky="w", padx=24)

        action = ctk.CTkButton(
            card,
            text=button_text,
            command=command,
            fg_color=accent_color,
            hover_color=COLOR_PRIMARY_DARK if accent_color == COLOR_PRIMARY else COLOR_ACCENT_DARK,
            text_color="#F8FAFC",
            font=self.fonts["button"],
            height=42,
            corner_radius=22,
        )
        action.grid(row=3 if title == "Mi Perfil" else 2, column=0, sticky="w", padx=24, pady=(20, 24))

    # ------------------------------------------------------------------
    # Navegacion
    # ------------------------------------------------------------------
    def _open_profile(self):
        self.controller.show_profile_view(self.username)

    def _open_vault(self):
        self.controller.show_vault_view(self.username)

    def _open_support(self):
        self.controller.show_support_view(self.username)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _handle_resize(self, event):
        if event.widget is self:
            # Mantener tamaño mínimo de la ventana
            root = self.winfo_toplevel()
            width = max(root.winfo_width(), 1024)
            height = max(root.winfo_height(), 768)
            if width != root.winfo_width() or height != root.winfo_height():
                root.geometry(f"{width}x{height}")
            
            # Actualizar el tamaño de la imagen de fondo si cambió el ancho
            if hasattr(self, 'hero_image') and hasattr(self, 'hero_source') and self._hero_width != width:
                self._hero_width = width
                try:
                    # Calcular nueva altura del hero basada en el ancho
                    hero_height = max(int(width * HERO_ASPECT_RATIO), MIN_HERO_HEIGHT)
                    
                    # Actualizar altura del hero section
                    for widget in self.grid_slaves():
                        if widget.grid_info()['row'] == 0:  # El hero está en la fila 0
                            widget.grid_configure(minsize=hero_height)
                    
                    # Calcular las dimensiones óptimas para la imagen
                    img_ratio = self.hero_source.width / self.hero_source.height
                    window_ratio = width / hero_height
                    
                    if window_ratio > img_ratio:
                        # La ventana es más ancha que la imagen proporcionalmente
                        new_width = int(width * 1.1)  # 10% extra para cubrir
                        new_height = int(new_width / img_ratio)
                    else:
                        # La ventana es más alta que la imagen proporcionalmente
                        new_height = hero_height
                        new_width = int(new_height * img_ratio)
                        if new_width < width:
                            new_width = width
                    
                    # Crear nueva imagen con las dimensiones calculadas
                    self.hero_image = ctk.CTkImage(
                        light_image=self.hero_source,
                        dark_image=self.hero_source,
                        size=(new_width, new_height)
                    )
                    
                    # Actualizar la imagen y asegurar que está centrada
                    if hasattr(self, 'hero_label') and self.hero_label is not None:
                        self.hero_label.configure(image=self.hero_image)
                except Exception as e:
                    print(f"Error al redimensionar la imagen: {e}")

    def _format_username(self, username: str) -> str:
        if "@" in username:
            username = username.split("@", 1)[0]
        return username.replace(".", " ").replace("_", " ").title()

    def _user_initials(self, username: str) -> str:
        if not username:
            return "EU"
        if "@" in username:
            username = username.split("@", 1)[0]
        parts = [part for part in username.replace(".", " ").replace("_", " ").split() if part]
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        return username[:2].upper()

