# =============================================================================
# ARCHIVO: main_view.py - Vista Principal de EncryptU
# =============================================================================
# Este archivo contiene la implementación de la interfaz gráfica principal de la
# aplicación EncryptU, desarrollada con CustomTkinter para una experiencia moderna.
#
# FUNCIONALIDADES PRINCIPALES:
# - Gestión de credenciales cifradas (almacenamiento/descifrado)
# - Sistema de tickets de soporte integrado
# - Panel de usuario con métricas y estadísticas
# - Navegación responsiva y moderna
# - Efectos visuales con gradientes animados
# - Diseño adaptativo para diferentes tamaños de ventana
#
# SECCIONES DEL ARCHIVO:
# 1. Imports y constantes de colores
# 2. Configuración de iconos profesionales
# 3. Clase MainView (componente principal)
# 4. Gestión de fuentes responsivas
# 5. Sistema de diseño responsivo
# 6. Efectos visuales y fondo animado
# 7. Cabecera y navegación principal
# 8. Secciones de contenido (Perfil, Encriptación, Soporte)
# 9. Funcionalidades del sistema de soporte
# 10. Gestión del vault de contraseñas
# =============================================================================

import customtkinter as ctk
from datetime import datetime
from typing import Any, Dict, List, Optional
import re
import pyperclip
from PIL import Image

# =============================================================================
# PALETA DE COLORES MODERNA DE ENCRYPTU
# =============================================================================
# Definición de la paleta de colores corporativa utilizada en toda la interfaz.
# Los colores están diseñados para mantener la identidad visual de EncryptU
# con un esquema rojo moderno y elegante.
#
# ESTRUCTURA DE COLORES:
# - COLOR_ROJO_PRINCIPAL: Color rojo principal de la marca
# - Variantes para hover, acentos y estados
# - Colores para fondos, textos y elementos interactivos
# - Sistema de colores para badges y estados de tickets
# =============================================================================
COLOR_ROJO_PRINCIPAL = "#E53E3E"
COLOR_ROJO_HOVER = "#C53030"
COLOR_ROJO_ACENTO = "#FC8181"
COLOR_ROJO_LIGHT = "#FED7D7"
COLOR_BLANCO = "#FFFFFF"
COLOR_BLANCO_WARM = "#FEFEFE"
TEXT_COLOR_PRIMARY = ("#C01010", "#C01010")
TEXT_COLOR_SECONDARY = ("#812828", "#812828")
TEXT_COLOR_MUTED = ("#967171", "#967171")
COLOR_FONDO_APP = ("#FFFFFF", "#FFFFFF")
COLOR_FONDO_CARD = ("#FFFFFF", "#FFFFFF")
COLOR_FONDO_CARD_ALT = ("#F8FAFC", "#FF0707")
COLOR_FONDO_HERO = ("#FEFEFE", "#FBFCFF")
COLOR_DIVIDER_LIGHT = "#E2E8F0"
COLOR_DIVIDER_DARK = "#2D3748"
COLOR_SHADOW = ("#000000", "#000000")
COLOR_SUCCESS = ("#38A169", "#68D391")
COLOR_WARNING = ("#D69E2E", "#F6E05E")
COLOR_ERROR = (COLOR_ROJO_PRINCIPAL, COLOR_ROJO_ACENTO)
BADGE_REASON_COLOR = ("#FDE8EC", "#7F1D1D")
BADGE_REASON_TEXT = (COLOR_ROJO_PRINCIPAL, COLOR_BLANCO)
BADGE_STATUS_COLORS = {
    "open": {"bg": ("#ECFDF5", "#064E3B"), "text": ("#047857", "#D1FAE5")},
    "pending": {"bg": ("#FEF3C7", "#7C2D12"), "text": ("#B45309", "#FDE68A")},
    "closed": {"bg": ("#E2E8F0", "#2D3748"), "text": ("#4A5568", "#E2E8F0")},
}
SUPPORT_AGENT_NAME = "Equipo EncryptU"
SUPPORT_REASON_OPTIONS = ["Soporte", "Consulta"]



# Logo images with appropriate size
img_logo_blanco = ctk.CTkImage(
    light_image=Image.open("desktop/controllers/img/Whitelogo.png"),
    size=(120, 120)  # Appropriate size for header
)

img_logo_negro = ctk.CTkImage(
    dark_image=Image.open("desktop/controllers/img/Blacklogo.png"),
    size=(120, 120)  # Appropriate size for header
)

# =============================================================================
# CLASE MAINVIEW - VISTA PRINCIPAL DE LA APLICACIÓN
# =============================================================================
# Esta clase representa la interfaz principal de la aplicación EncryptU.
# Implementa una interfaz moderna y responsiva con funcionalidades avanzadas.
#
# CARACTERÍSTICAS PRINCIPALES:
# - Navegación por pestañas (Perfil, Encriptación, Soporte)
# - Diseño responsivo que se adapta a diferentes tamaños de ventana
# - Sistema de gestión de contraseñas cifradas
# - Integración completa con el sistema de soporte técnico
# - Efectos visuales modernos con gradientes animados
# - Gestión de fuentes escalables automáticamente
#
# COMPONENTES PRINCIPALES:
# - Header con información del usuario y botón de logout
# - Navegación segmentada moderna
# - Área de contenido dinámica con tres secciones principales
# - Sistema de soporte con tickets y chat integrado
# - Vault de contraseñas con funciones de cifrado/descifrado
# =============================================================================

class MainView(ctk.CTkFrame):
    """
    Vista principal con navegación moderna, tarjetas temáticas y gradientes
    acorde a la identidad visual de EncryptU.

    Esta clase maneja toda la interfaz de usuario principal incluyendo:
    - Gestión del diseño responsivo y fuentes adaptativas
    - Sistema de navegación entre secciones
    - Integración con el controlador para funcionalidades backend
    - Gestión del estado de la aplicación y componentes UI
    """

    def __init__(self, master, controller, username):
        super().__init__(master)
        # Configuración inicial de la vista principal
        self.controller = controller  # Referencia al controlador principal
        self.username = username      # Nombre del usuario actual
        self.configure(fg_color="transparent")  # Fondo transparente para efectos visuales

        # Diccionarios para gestión de fuentes responsivas
        self.fonts: Dict[str, ctk.CTkFont] = {}                    # Fuentes CTkFont por nombre
        self._font_specs: Dict[str, Dict[str, Optional[float]]] = {} # Especificaciones de fuentes
        self._responsive_components: List[Dict[str, Any]] = []      # Componentes responsivos
        self._responsive_wraplengths: List[Dict[str, Any]] = []     # Wraplengths responsivos
        self._responsive_job: Optional[str] = None                  # ID del job de actualización responsiva
        self._current_scale: float = 1.0                           # Escala actual de la interfaz
        self._validators: Dict[str, Any] = {}                       # Validadores de entrada de datos

        # Inicialización del sistema de fuentes y validadores
        self._init_fonts()           # Configura todas las fuentes de la aplicación
        self._setup_validators()     # Establece validadores para campos de entrada

        # Variables para gestión de imágenes de fondo y logos
        self.original_bg_image: Optional[Image.Image] = None    # Imagen de fondo original
        self.bg_image_object: Optional[ctk.CTkImage] = None     # Objeto CTkImage del fondo
        self.bg_label: Optional[ctk.CTkLabel] = None           # Label del fondo
        self.logo_image: Optional[ctk.CTkImage] = None         # Imagen del logo

        # Sistema de gestión de tickets de soporte
        self.support_tickets: List[Dict[str, Any]] = []                    # Lista de tickets de soporte
        self.support_ticket_messages: Dict[int, List[Dict[str, Any]]] = {} # Mensajes por ticket ID
        self.support_loading = False                                       # Estado de carga de soporte
        self.support_active_ticket_id: Optional[int] = None               # ID del ticket activo

        # Variables StringVar para métricas y estados de la interfaz
        self.password_count_var = ctk.StringVar(value="--")                    # Contador de contraseñas
        self.profile_ticket_metric_var = ctk.StringVar(value="0")              # Métrica de tickets en perfil
        self.profile_last_sync_var = ctk.StringVar(value=datetime.now().strftime("%d/%m/%Y %H:%M"))  # Última sincronización
        self.support_list_count_var = ctk.StringVar(value="Cargando tickets...")  # Estado de lista de soporte
        # Variables StringVar para funcionalidades de tickets de soporte
        self.ticket_search_var = ctk.StringVar(value="")                           # Búsqueda de tickets
        self.support_chat_title_var = ctk.StringVar(value="Selecciona un ticket para ver los detalles.")  # Título del chat
        self.support_chat_meta_var = ctk.StringVar(value="")                       # Metadatos del chat
        self.support_status_var = ctk.StringVar(value="")                         # Estado del soporte
        self.ticket_first_name_var = ctk.StringVar(value="")                      # Nombre del solicitante
        self.ticket_last_name_var = ctk.StringVar(value="")                       # Apellido del solicitante
        self.ticket_email_var = ctk.StringVar(value=username or "")              # Email del solicitante
        self.ticket_phone_var = ctk.StringVar(value="")                          # Teléfono del solicitante
        self.ticket_reason_var = ctk.StringVar(value=SUPPORT_REASON_OPTIONS[0])   # Razón del ticket
        self.ticket_form_status_var = ctk.StringVar(value="")                     # Estado del formulario
        self.ticket_description_count_var = ctk.StringVar(value="0 / 500")        # Contador de descripción
        self.support_message_count_var = ctk.StringVar(value="0 / 500")           # Contador de mensajes
        # Referencias a componentes principales de la interfaz
        self.nav_segmented: Optional[ctk.CTkSegmentedButton] = None      # Navegación segmentada
        self.nav_map = {"Perfil": "profile", "Encriptacion": "encryption", "Soporte": "support"}  # Mapeo navegación
        self.sections: Dict[str, ctk.CTkFrame] = {}                     # Secciones de contenido
        self.content_container: Optional[ctk.CTkFrame] = None           # Contenedor principal de contenido
        self.scrollable_frame: Optional[ctk.CTkScrollableFrame] = None  # Frame scrollable para contraseñas
        self.status_label_save: Optional[ctk.CTkLabel] = None           # Label de estado para guardar
        # Componentes del sistema de soporte técnico
        self.support_ticket_list_container: Optional[ctk.CTkScrollableFrame] = None  # Lista de tickets
        self.support_messages_container: Optional[ctk.CTkScrollableFrame] = None     # Mensajes del chat
        self.support_badge_holder: Optional[ctk.CTkFrame] = None                    # Contenedor de badges
        self.support_message_input: Optional[ctk.CTkTextbox] = None                 # Input de mensajes
        self.support_send_button: Optional[ctk.CTkButton] = None                    # Botón enviar mensaje
        self.support_status_label: Optional[ctk.CTkLabel] = None                    # Estado del soporte
        self.ticket_form_status_label: Optional[ctk.CTkLabel] = None                # Estado del formulario
        self.support_create_button: Optional[ctk.CTkButton] = None                  # Botón crear ticket
        self.support_ticket_description_input: Optional[ctk.CTkTextbox] = None      # Descripción del ticket
        self.support_form_card: Optional[ctk.CTkFrame] = None                       # Tarjeta del formulario

        # Componentes del formulario de encriptación
        self.site_entry: Optional[ctk.CTkEntry] = None                    # Campo sitio web
        self.username_entry_save: Optional[ctk.CTkEntry] = None           # Campo usuario
        self.password_entry: Optional[ctk.CTkEntry] = None               # Campo contraseña
        self.save_button: Optional[ctk.CTkButton] = None                  # Botón guardar

        # Configuración del layout principal
        self.grid_columnconfigure(0, weight=1)  # Columna 0 expandible
        self.grid_rowconfigure(2, weight=1)     # Fila 2 (contenido) expandible

        # Inicialización de componentes principales
        self._setup_background_image()      # Fondo degradado animado
        self._create_header()              # Cabecera con usuario y logout
        self._create_navigation()          # Navegación segmentada
        self._build_content_area()         # Construye las tres secciones principales

        # Configuración de eventos y estado inicial
        self.ticket_search_var.trace_add("write", lambda *_: self._render_support_ticket_list())  # Búsqueda en tiempo real

        self.support_loading = True                    # Estado de carga inicial
        self._render_support_ticket_list()             # Renderiza lista de tickets
        self.after(150, self._initialize_support_data) # Inicializa datos de soporte

        # Configuración inicial de navegación y contenido
        if self.nav_segmented:
            self.nav_segmented.set("Encriptacion")     # Selecciona pestaña de encriptación
        self._show_section("encryption")               # Muestra sección de encriptación
        self.refresh_password_list()                   # Carga lista de contraseñas
        self._setup_responsive_behavior()              # Configura comportamiento responsivo

    # ------------------------------------------------------------------
    # GESTIÓN DE FUENTES RESPONSIVAS
    # ------------------------------------------------------------------
    # Sistema avanzado para gestión de fuentes que se adaptan automáticamente
    # al tamaño de la ventana y mantienen una excelente legibilidad.
    #
    # FUNCIONALIDADES:
    # - Registro de fuentes con parámetros específicos (tamaño, peso, límites)
    # - Escalado automático basado en el tamaño de la ventana
    # - Mantenimiento de proporciones y jerarquía visual
    # - Límites mínimos y máximos para evitar textos ilegibles
    # ------------------------------------------------------------------

    def _register_font(
        self,
        key: str,
        size: int,
        *,
        weight: Optional[str] = None,
        min_size: int = 8,
        max_size: Optional[int] = None,
    ) -> ctk.CTkFont:
        if weight is not None:
            font = ctk.CTkFont(size=size, weight=weight)  # type: ignore
        else:
            font = ctk.CTkFont(size=size)
        self.fonts[key] = font
        self._font_specs[key] = {"base": float(size), "min": float(min_size), "max": float(max_size) if max_size is not None else None}
        return font

    def _init_fonts(self):
        """Inicializa todas las fuentes utilizadas en la aplicación con sus especificaciones responsivas.

        Cada fuente está diseñada para un propósito específico en la jerarquía visual:
        - badge: Para badges y etiquetas pequeñas
        - header_*: Para títulos y subtítulos del encabezado
        - nav_*: Para elementos de navegación
        - hero_*: Para secciones destacadas (hero sections)
        - card_*: Para tarjetas de estadísticas y contenido
        - section_*: Para títulos de secciones
        - form_*: Para títulos de formularios
        - body_*: Para texto general del cuerpo
        - button: Para botones de acción
        - support_*: Para elementos específicos del soporte
        - list_*: Para listas y elementos de navegación
        """
        self._register_font("badge", 14, weight="bold", min_size=10)           # Badges pequeños
        self._register_font("header_title", 26, weight="bold", min_size=16)    # Título principal del header
        self._register_font("header_subtitle", 14, min_size=10)                # Subtítulo del header
        self._register_font("nav_caption", 12, weight="bold", min_size=9)       # Títulos de navegación
        self._register_font("nav_segmented", 14, weight="bold", min_size=11)    # Navegación segmentada
        self._register_font("hero_headline", 22, weight="bold", min_size=16)    # Títulos hero principales
        self._register_font("hero_tagline", 14, min_size=11)                    # Subtítulos hero
        self._register_font("card_label", 12, weight="bold", min_size=9)        # Etiquetas de tarjetas
        self._register_font("card_stat_primary", 30, weight="bold", min_size=20)  # Estadísticas principales
        self._register_font("card_stat_secondary", 18, weight="bold", min_size=14) # Estadísticas secundarias
        self._register_font("section_title", 20, weight="bold", min_size=15)    # Títulos de sección
        self._register_font("form_title", 16, weight="bold", min_size=12)       # Títulos de formularios
        self._register_font("body", 14, min_size=11)                           # Texto del cuerpo estándar
        self._register_font("body_medium", 13, min_size=11)                     # Texto del cuerpo mediano
        self._register_font("body_small", 12, min_size=10)                      # Texto del cuerpo pequeño
        self._register_font("tiny", 11, min_size=9)                            # Texto muy pequeño
        self._register_font("button", 14, weight="bold", min_size=12)           # Texto de botones
        self._register_font("support_chat_title", 18, weight="bold", min_size=14)  # Títulos del chat de soporte
        self._register_font("list_title", 14, weight="bold", min_size=11)       # Títulos de listas
        self._register_font("badge_small", 11, weight="bold", min_size=9)       # Badges pequeños

    def _setup_validators(self):
        """Configura los validadores para los diferentes tipos de campos de entrada.

        Estos validadores se utilizan para validar datos en tiempo real mientras
        el usuario escribe, asegurando que los datos cumplan con los formatos
        y restricciones requeridas antes de enviarlos.
        """
        self._validators["site"] = self.register(self._validate_site)           # Validación de sitios web
        self._validators["username"] = self.register(self._validate_username)   # Validación de usuarios
        self._validators["password"] = self.register(self._validate_password)   # Validación de contraseñas
        self._validators["name"] = self.register(self._validate_name)           # Validación de nombres
        self._validators["email"] = self.register(self._validate_email)         # Validación de emails
        self._validators["phone"] = self.register(self._validate_phone)         # Validación de teléfonos

    def _setup_responsive_behavior(self):
        """Configura el comportamiento responsivo de la aplicación.

        Vincula eventos de redimensionamiento de ventana y programa la aplicación
        inicial de estilos responsivos para asegurar una experiencia óptima
        desde el inicio.
        """
        self.bind("<Configure>", self._handle_root_resize)       # Detecta cambios de tamaño de ventana
        self.after(120, self._apply_responsive_styles)          # Aplica estilos iniciales después de 120ms

    def _handle_root_resize(self, event=None):
        self._resize_image(event)
        self._schedule_responsive_update()

    def _schedule_responsive_update(self):
        if self._responsive_job is not None:
            self.after_cancel(self._responsive_job)
        self._responsive_job = self.after(80, self._apply_responsive_styles)

    def _apply_responsive_styles(self):
        width = max(self.winfo_width(), 600)
        height = max(self.winfo_height(), 480)
        scale_width = width / 1280
        scale_height = height / 800

        # Enhanced responsive breakpoints for desktop optimization
        if width < 768:
            # Small desktop window
            base_scale = 0.8
        elif width < 900:
            # Medium-small desktop
            base_scale = 0.85
        elif width < 1200:
            # Medium desktop
            base_scale = 0.9
        elif width < 1440:
            # Standard desktop
            base_scale = 1.0
        else:
            # Large desktop
            base_scale = 1.05

        scale = max(0.65, min(base_scale * min(scale_width, scale_height), 1.4))

        if abs(scale - self._current_scale) < 0.02:
            return

        self._current_scale = scale
        self._apply_font_scale(scale)
        self._apply_component_scale(scale)
        self._apply_wraplength_scale(scale)

        # Apply layout-specific adjustments
        self._apply_responsive_layout(width)

    def _apply_responsive_layout(self, width: int):
        """Aplica ajustes de layout basados en el ancho de la pantalla.

        Esta función implementa diferentes estrategias de diseño responsivo
        según el tamaño de la ventana:

        - < 768px: Ajustes para ventanas pequeñas de escritorio
        - 768-900px: Ajustes para escritorio mediano-pequeño
        - 900-1200px: Ajustes para escritorio mediano
        - > 1200px: Ajustes para escritorio grande (óptimo)
        """
        if width < 768:
            # Ajustes para ventanas pequeñas de escritorio
            self._mobile_layout_adjustments()
        elif width < 900:
            # Ajustes para escritorio mediano-pequeño
            self._medium_small_layout_adjustments()
        elif width < 1200:
            # Ajustes para escritorio mediano
            self._medium_layout_adjustments()
        else:
            # Ajustes para escritorio grande
            self._desktop_layout_adjustments()

    def _medium_small_layout_adjustments(self):
        """Medium-small desktop layout adjustments (768-900px)"""
        if hasattr(self, 'content_container') and self.content_container:
            self.content_container.grid_configure(padx=20, pady=(0, 18))

        # Moderate form card adjustments
        if hasattr(self, 'support_form_card') and self.support_form_card:
            self.support_form_card.grid_configure(padx=20, pady=(12, 8))

    def _medium_layout_adjustments(self):
        """Medium desktop layout adjustments (900-1200px)"""
        if hasattr(self, 'content_container') and self.content_container:
            self.content_container.grid_configure(padx=24, pady=(0, 20))

    def _mobile_layout_adjustments(self):
        """Small desktop window layout adjustments"""
        # Reduce padding and margins for smaller desktop windows
        if hasattr(self, 'content_container') and self.content_container:
            self.content_container.grid_configure(padx=16, pady=(0, 16))

        # Ensure form card is properly sized for smaller windows
        if hasattr(self, 'support_form_card') and self.support_form_card:
            # Reduce form card padding and ensure it fits
            self.support_form_card.grid_configure(padx=16, pady=(6, 4))
            # Set a maximum height for the form card
            self.support_form_card.configure(height=340)

        # Ensure tickets panel can scroll properly
        if hasattr(self, 'support_ticket_list_container') and self.support_ticket_list_container:
            # Make sure the scrollable container takes full width
            self.support_ticket_list_container.grid_configure(padx=8, pady=(0, 12))

    def _tablet_layout_adjustments(self):
        """Tablet-specific layout adjustments"""
        # Medium padding for tablet
        if hasattr(self, 'content_container') and self.content_container:
            self.content_container.grid_configure(padx=24, pady=(0, 20))

    def _desktop_layout_adjustments(self):
        """Desktop-specific layout adjustments"""
        # Full padding for desktop
        if hasattr(self, 'content_container') and self.content_container:
            self.content_container.grid_configure(padx=32, pady=(0, 24))

    def _apply_font_scale(self, scale: float):
        for key, spec in self._font_specs.items():
            base = spec["base"]
            min_size = spec["min"]
            max_size = spec.get("max")
            if base is not None and min_size is not None:
                new_size = max(min_size, int(base * scale))
                if max_size is not None:
                    new_size = min(new_size, max_size)
                # Ensure font size is always a positive integer
                new_size = max(8, int(new_size))  # Minimum font size of 8
                if new_size != self.fonts[key].cget("size"):
                    self.fonts[key].configure(size=new_size)

    def _register_responsive_widget(
        self,
        widget: Any,
        *,
        base_height: Optional[int] = None,
        base_width: Optional[int] = None,
        min_height: int = 28,
        min_width: int = 80,
    ):
        self._responsive_components.append(
            {
                "widget": widget,
                "base_height": base_height,
                "base_width": base_width,
                "min_height": min_height,
                "min_width": min_width,
            }
        )

    def _apply_component_scale(self, scale: float):
        for item in self._responsive_components:
            widget = item["widget"]
            if not widget:
                continue
            base_height = item.get("base_height")
            base_width = item.get("base_width")
            min_height = item.get("min_height", 28)
            min_width = item.get("min_width", 80)

            if base_height:
                new_height = max(min_height, int(base_height * scale))
                # Ensure height is always positive and reasonable
                new_height = max(20, min(new_height, 200))
                try:
                    current_height = widget.cget("height")
                    if current_height != new_height:
                        widget.configure(height=new_height)
                except Exception:
                    pass

            if base_width:
                new_width = max(min_width, int(base_width * scale))
                # Ensure width is always positive and reasonable
                new_width = max(50, min(new_width, 500))
                try:
                    current_width = widget.cget("width")
                    if current_width != new_width:
                        widget.configure(width=new_width)
                except Exception:
                    pass

    def _register_wraplength(self, widget: ctk.CTkLabel, base_wrap: int):
        self._responsive_wraplengths.append({"widget": widget, "base": base_wrap})

    def _apply_wraplength_scale(self, scale: float):
        for item in self._responsive_wraplengths:
            widget = item.get("widget")
            if not widget:
                continue
            base = item.get("base", 0)
            if base:
                new_wraplength = max(200, int(base * scale))  # Minimum wraplength of 200
                try:
                    widget.configure(wraplength=new_wraplength)
                except Exception:
                    pass

    def _bind_text_limit(
        self,
        widget: ctk.CTkTextbox,
        limit: int,
        counter_var: Optional[ctk.StringVar] = None,
    ):
        def handler(_event=None, target=widget, maximum=limit, var=counter_var):
            self._enforce_text_limit(target, maximum, var)

        widget.bind("<KeyRelease>", handler)
        widget.bind("<FocusOut>", handler)
        self.after(10, handler)

    def _enforce_text_limit(
        self,
        widget: ctk.CTkTextbox,
        limit: int,
        counter_var: Optional[ctk.StringVar] = None,
    ):
        content = widget.get("1.0", "end-1c")
        if len(content) > limit:
            trimmed = content[:limit]
            widget.delete("1.0", "end")
            widget.insert("1.0", trimmed)
            content = trimmed
        if counter_var is not None:
            counter_var.set(f"{len(content)} / {limit}")

    def _validate_site(self, value: str) -> bool:
        if len(value) > 120:
            return False
        if not value:
            return True
        return bool(
            re.fullmatch(r"[A-Za-z0-9ÁÉÍÓÚáéíóúÜüÑñ@._:/\- ]*", value)
        )

    def _validate_username(self, value: str) -> bool:
        if len(value) > 80:
            return False
        if not value:
            return True
        return bool(re.fullmatch(r"[\wÁÉÍÓÚáéíóúÜüÑñ.@\- ]*", value))

    def _validate_password(self, value: str) -> bool:
        return len(value) <= 128

    def _validate_name(self, value: str) -> bool:
        if len(value) > 60:
            return False
        if not value:
            return True
        return bool(re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÜüÑñ' -]*", value))

    def _validate_email(self, value: str) -> bool:
        if len(value) > 120:
            return False
        if not value:
            return True
        return bool(re.fullmatch(r"[A-Za-z0-9._%+\-@]*", value))

    def _validate_phone(self, value: str) -> bool:
        if len(value) > 9:
            return False
        if not value:
            return True
        return value.isdigit()
    def _setup_background_image(self):
        """Configura el fondo degradado animado de la aplicación.

        Crea un fondo visualmente atractivo con gradientes que utiliza los colores
        corporativos de EncryptU. El fondo se adapta automáticamente al tamaño
        de la ventana y proporciona una experiencia visual moderna.

        FUNCIONALIDADES:
        - Genera gradiente base con colores corporativos
        - Configura label de fondo transparente para superponer efectos
        - Inicia sistema de animación sutil cada 5 segundos
        - Programa redimensionamiento automático de la imagen
        - Manejo de errores silencioso para mantener estabilidad
        """
        try:
            # Genera imagen de fondo degradado con colores corporativos
            self.original_bg_image = self._generate_gradient_image(1600, 900)

            # Crea label de fondo transparente que ocupará toda la ventana
            self.bg_label = ctk.CTkLabel(self, text="", fg_color="transparent")
            self.bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.bg_label.lower()  # Envía al fondo para no interferir con otros elementos

            # Inicia sistema de animación sutil del fondo
            self._animate_background()
            # Programa ajuste inicial del tamaño después de 20ms
            self.after(20, self._resize_image)
        except Exception as exc:
            # Manejo de errores silencioso para mantener estabilidad
            print(f"Error al crear el fondo degradado: {exc}")

    def _animate_background(self):
        """Añade animación sutil al fondo degradado de la aplicación.

        Crea una transición suave del fondo cada 5 segundos cambiando ligeramente
        los colores y la rotación del gradiente. Esta animación es sutil para no
        distraer al usuario pero mantiene el interés visual.

        MECANISMO:
        - Verifica que existan los componentes necesarios para la animación
        - Genera una variante sutilmente diferente del gradiente original
        - Aplica la nueva imagen al label de fondo
        - Programa la siguiente animación cada 5 segundos
        - Manejo de errores silencioso para mantener estabilidad
        """
        if self.bg_label and self.original_bg_image:
            # Animación sutil de transición de colores
            try:
                # Crea una variante ligeramente diferente del gradiente para animación
                animated_image = self._generate_animated_gradient(1600, 900)
                if animated_image:
                    # Crea objeto CTkImage con la nueva imagen animada
                    self.bg_image_object = ctk.CTkImage(
                        light_image=animated_image,
                        dark_image=animated_image,
                        size=(self.winfo_width(), self.winfo_height())
                    )
                    # Aplica la nueva imagen al label de fondo
                    self.bg_label.configure(image=self.bg_image_object)
            except Exception:
                # Falla silenciosamente si hay problemas con la animación
                pass

        # Programa el siguiente frame de animación cada 5 segundos
        self.after(5000, self._animate_background)

    def _generate_animated_gradient(self, width: int, height: int) -> Optional[Image.Image]:
        """Genera una variante sutil del gradiente para la animación de fondo.

        Crea una versión ligeramente diferente del gradiente original con cambios
        sutiles en rotación y colores para proporcionar una transición suave.

        TÉCNICA:
        - Crea gradiente lineal base y lo redimensiona al doble del tamaño necesario
        - Aplica rotación ligeramente diferente (50°) para variar el efecto
        - Recorta la imagen al tamaño exacto requerido
        - Usa colores corporativos con variaciones sutiles para animación
        - Combina capa base con capa superior usando máscara de gradiente

        Args:
            width: Ancho deseado de la imagen generada
            height: Alto deseado de la imagen generada

        Returns:
            Optional[Image.Image]: Imagen de gradiente animado o None si hay error
        """
        try:
            # Crea una variante sutilmente diferente del gradiente
            size = max(width, height) * 2  # Tamaño doble para mejor calidad
            gradient = Image.linear_gradient("L").resize((size, size))
            gradient = gradient.rotate(50, expand=True)  # Rotación ligeramente diferente
            x_offset = (gradient.width - width) // 2
            y_offset = (gradient.height - height) // 2
            mask = gradient.crop((x_offset, y_offset, x_offset + width, y_offset + height))

            # Usa colores ligeramente diferentes para la animación
            # Calcula variaciones sutiles del color rojo principal
            base_color = f"#{int(COLOR_ROJO_PRINCIPAL[1:3],16)+10:02x}{int(COLOR_ROJO_PRINCIPAL[3:5],16)+5:02x}{int(COLOR_ROJO_PRINCIPAL[5:7],16)+10:02x}"
            base = Image.new("RGB", (width, height), base_color)  # Capa base con color modificado
            top = Image.new("RGB", (width, height), COLOR_BLANCO)  # Capa superior blanca
            return Image.composite(top, base, mask)  # Combina capas usando gradiente como máscara
        except Exception:
            return None

    def _generate_gradient_image(self, width: int, height: int) -> Image.Image:
        """Genera la imagen de fondo degradado principal de la aplicación.

        Crea un gradiente lineal sofisticado que combina los colores corporativos
        de EncryptU (rojo principal y blanco) con una rotación de 45° para obtener
        un efecto visual elegante y moderno.

        PROCESO:
        1. Crea gradiente lineal base con tamaño doble para mejor calidad
        2. Aplica rotación de 45° para efecto diagonal elegante
        3. Recorta la imagen al tamaño exacto requerido
        4. Crea capas base (rojo corporativo) y superior (blanco)
        5. Combina capas usando el gradiente como máscara de transparencia

        Args:
            width: Ancho deseado de la imagen generada
            height: Alto deseado de la imagen generada

        Returns:
            Image.Image: Imagen de gradiente lista para usar como fondo
        """
        size = max(width, height) * 2  # Tamaño doble para mejor calidad de imagen
        gradient = Image.linear_gradient("L").resize((size, size))  # Crea gradiente lineal base
        gradient = gradient.rotate(45, expand=True)  # Rotación de 45° para efecto diagonal
        x_offset = (gradient.width - width) // 2   # Calcula offset para recorte horizontal
        y_offset = (gradient.height - height) // 2  # Calcula offset para recorte vertical
        mask = gradient.crop((x_offset, y_offset, x_offset + width, y_offset + height))  # Recorta al tamaño deseado
        base = Image.new("RGB", (width, height), COLOR_ROJO_PRINCIPAL)  # Capa base roja corporativa
        top = Image.new("RGB", (width, height), COLOR_BLANCO)         # Capa superior blanca
        return Image.composite(top, base, mask)  # Combina capas con gradiente como máscara

    def _resize_image(self, event=None):
        if not self.original_bg_image or not self.bg_label:
            return
        new_width, new_height = self.winfo_width(), self.winfo_height()
        if new_width <= 1 or new_height <= 1:
            return

        img_ratio = self.original_bg_image.width / self.original_bg_image.height
        frame_ratio = new_width / new_height
        if frame_ratio > img_ratio:
            resize_width = new_width
            resize_height = int(resize_width / img_ratio)
        else:
            resize_height = new_height
            resize_width = int(resize_height * img_ratio)

        resized_img = self.original_bg_image.resize(
            (resize_width, resize_height), Image.Resampling.LANCZOS
        )
        self.bg_image_object = ctk.CTkImage(
            light_image=resized_img, dark_image=resized_img, size=(resize_width, resize_height)
        )
        self.bg_label.configure(image=self.bg_image_object)
        self.bg_label.place(relx=0.5, rely=0.5, anchor="center")

    # ------------------------------------------------------------------
    # CABECERA Y NAVEGACIÓN PRINCIPAL
    # ------------------------------------------------------------------
    # Implementa la cabecera moderna de la aplicación con información del usuario,
    # logo corporativo y botón de cierre de sesión. También configura la navegación
    # segmentada que permite cambiar entre las diferentes secciones de la aplicación.
    #
    # COMPONENTES DE CABECERA:
    # - Logo corporativo con badge moderno
    # - Información de bienvenida del usuario con icono
    # - Subtítulo descriptivo de la aplicación
    # - Botón de cierre de sesión con efectos hover
    #
    # NAVEGACIÓN:
    # - Navegación segmentada moderna (Perfil, Encriptación, Soporte)
    # - Efectos visuales y animaciones sutiles
    # - Diseño responsivo que se adapta a diferentes tamaños
    # ------------------------------------------------------------------

    def _create_header(self):
        # Modern header with subtle background and better spacing
        header_frame = ctk.CTkFrame(
            self,
            fg_color=(COLOR_FONDO_HERO[0], "#FFFFFF"),
            corner_radius=0,
            border_width=0
        )
        header_frame.grid(row=0, column=0, padx=0, pady=(0, 20), sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)

        # Subtle top border
        top_border = ctk.CTkFrame(
            header_frame,
            fg_color="transparent",
            height=1,
            border_width=0
        )
        top_border.grid(row=0, column=0, columnspan=3, sticky="ew", padx=32, pady=(0, 20))

        # Brand section with modern badge
        brand_section = ctk.CTkFrame(header_frame, fg_color="transparent")
        brand_section.grid(row=1, column=0, sticky="nw", padx=32)

        brand_badge = ctk.CTkLabel(
            brand_section,
            image=img_logo_blanco,
            text="",
            font=self.fonts["badge"],
            fg_color=(COLOR_ROJO_LIGHT[0], "#610000"), 
            text_color=(COLOR_BLANCO, COLOR_BLANCO),
            corner_radius=0,  # No corner radius needed for image-only badge
            padx=0,
            pady=0,
        )
        brand_badge.pack(anchor="w")

        # Welcome section with better hierarchy
        welcome_section = ctk.CTkFrame(header_frame, fg_color="transparent")
        welcome_section.grid(row=1, column=1, sticky="w", padx=(24, 0))

        welcome_label = ctk.CTkLabel(
            welcome_section,
            text=f"Hola, {self.username}",
            image=None,
            compound="top",
            font=self.fonts["header_title"],
            text_color=TEXT_COLOR_PRIMARY,
            anchor="w"
        )
        welcome_label.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            welcome_section,
            text="Tu gestor seguro de contraseñas y soporte técnico",
            font=self.fonts["header_subtitle"],
            text_color=TEXT_COLOR_SECONDARY,
            anchor="w"
        )
        subtitle.pack(anchor="w", pady=(4, 0))

        # Modern logout button
        logout_section = ctk.CTkFrame(header_frame, fg_color="transparent")
        logout_section.grid(row=1, column=2, sticky="e", padx=(0, 32))

        logout_button = ctk.CTkButton(
            logout_section,
            text="Cerrar Sesión",
            image=None,
            compound="left",
            command=self.logout_action,
            fg_color="transparent",
            hover_color=COLOR_ROJO_LIGHT,
            border_width=1,
            border_color=COLOR_ROJO_PRINCIPAL,
            text_color=(COLOR_ROJO_PRINCIPAL, COLOR_ROJO_ACENTO),
            height=44,
            corner_radius=16,
            width=160,
            font=self.fonts["button"],
        )
        logout_button.pack(anchor="e")

        # Add subtle hover animation
        def on_enter(e):
            logout_button.configure(
                fg_color=COLOR_ROJO_LIGHT,
                text_color=(COLOR_ROJO_HOVER, COLOR_ROJO_PRINCIPAL)
            )

        def on_leave(e):
            logout_button.configure(
                fg_color="transparent",
                text_color=(COLOR_ROJO_PRINCIPAL, COLOR_ROJO_ACENTO)
            )

        logout_button.bind("<Enter>", on_enter)
        logout_button.bind("<Leave>", on_leave)

        self._register_responsive_widget(
            logout_button,
            base_height=44,
            base_width=160,
            min_height=36,
            min_width=140,
        )

    def _create_navigation(self):

        nav_frame = ctk.CTkFrame(
            self,
            fg_color=(COLOR_FONDO_CARD_ALT[0], "#FFFFFF"),
            corner_radius=20,
            border_width=1,
            border_color=COLOR_DIVIDER_LIGHT
        )
        nav_frame.grid(row=1, column=0, padx=32, pady=(0, 24), sticky="ew")
        nav_frame.grid_columnconfigure(0, weight=1)

        title_frame = ctk.CTkFrame(nav_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 16))
        title_frame.grid_columnconfigure(0, weight=1)

        nav_caption = ctk.CTkLabel(
            title_frame,
            text="Navegación Principal",
            compound="left",
            font=self.fonts["nav_caption"],
            text_color=TEXT_COLOR_PRIMARY,
            anchor="w"
        )
        nav_caption.grid(row=0, column=0, sticky="w")


        self.nav_segmented = ctk.CTkSegmentedButton(
            nav_frame,
            values=list(self.nav_map.keys()),
            command=self._on_nav_change,
            corner_radius=16,
            selected_color=(COLOR_ROJO_PRINCIPAL, "#e6e6e6"),
            selected_hover_color=COLOR_ROJO_HOVER,
            unselected_color=(COLOR_BLANCO_WARM, "#660000"),
            unselected_hover_color=(COLOR_ROJO_LIGHT, "#E40303"),
            text_color=(COLOR_BLANCO, COLOR_BLANCO),
            font=self.fonts["nav_segmented"],
            bg_color="#ffffff",
            height=48,
            border_width=0,
        )
        self.nav_segmented.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))

        def on_nav_enter(e):
            nav_frame.configure(
                fg_color=(COLOR_ROJO_LIGHT[0], "#FFFFFF"),
                border_color=COLOR_ROJO_PRINCIPAL
            )

        def on_nav_leave(e):
            nav_frame.configure(
                fg_color=(COLOR_FONDO_CARD_ALT[0], "#FFFFFF"),
                border_color=COLOR_DIVIDER_LIGHT
            )

        nav_frame.bind("<Enter>", on_nav_enter)
        nav_frame.bind("<Leave>", on_nav_leave)

        self._register_responsive_widget(
            self.nav_segmented,
            base_height=48,
            min_height=40,
            min_width=200,
        )

    def _on_nav_change(self, value: str):
        section = self.nav_map.get(value)
        if section:
            self._show_section(section)

    # ------------------------------------------------------------------
    # SECCIONES PRINCIPALES DE CONTENIDO
    # ------------------------------------------------------------------
    # Construye y gestiona las tres secciones principales de la aplicación:
    # 1. PERFIL: Panel personal con métricas y estadísticas del usuario
    # 2. ENCRIPTACIÓN: Vault de contraseñas con funciones de almacenamiento/descifrado
    # 3. SOPORTE: Sistema completo de tickets y chat de soporte técnico
    #
    # ARQUITECTURA:
    # - Contenedor principal que alberga todas las secciones
    # - Cada sección se construye en su propio frame independiente
    # - Sistema de mostrar/ocultar secciones dinámicamente
    # - Layout responsivo que se adapta a diferentes configuraciones
    # ------------------------------------------------------------------

    def _build_content_area(self):
        self.content_container = ctk.CTkFrame(self, fg_color="transparent")
        self.content_container.grid(row=2, column=0, padx=24, pady=(0, 24), sticky="nsew")
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        profile = self._build_profile_section(self.content_container)
        encryption = self._build_encryption_section(self.content_container)
        support = self._build_support_section(self.content_container)

        self.sections = {"profile": profile, "encryption": encryption, "support": support}
        for frame in self.sections.values():
            frame.grid_remove()

    def _build_profile_section(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)

        # Modern hero card with enhanced styling
        hero_card = ctk.CTkFrame(
            frame,
            fg_color=COLOR_FONDO_HERO,
            corner_radius=28,
            border_width=0,
        )
        hero_card.pack(fill="x", padx=0, pady=(0, 32))

        # Add subtle shadow effect
        hero_card._corner_radius = 28
        hero_card.configure(
            fg_color=[
                f"#{int(c[1:3],16)+20:02x}{int(c[3:5],16)+20:02x}{int(c[5:7],16)+20:02x}"
                if isinstance(c, str) and c.startswith('#') else c
                for c in [COLOR_FONDO_HERO[0], "#1C2331"]
            ]
        )

        hero_card.grid_columnconfigure(0, weight=1)

        # Enhanced header section
        header_section = ctk.CTkFrame(hero_card, fg_color="transparent")
        header_section.grid(row=0, column=0, sticky="ew", padx=32, pady=(32, 16))
        header_section.grid_columnconfigure(0, weight=1)

        headline = ctk.CTkLabel(
            header_section,
            text="Tu Panel Personal Seguro",
            image=None,
            compound="top",
            font=self.fonts["hero_headline"],
            text_color=TEXT_COLOR_PRIMARY,
            anchor="w"
        )
        headline.grid(row=0, column=0, sticky="w")

        tagline = ctk.CTkLabel(
            header_section,
            text="Gestiona tus credenciales cifradas y mantén el control total de tu seguridad digital",
            font=self.fonts["hero_tagline"],
            text_color=TEXT_COLOR_SECONDARY,
            wraplength=480,
            justify="left",
            anchor="w"
        )
        tagline.grid(row=1, column=0, sticky="w", pady=(8, 0))
        self._register_wraplength(tagline, 480)

        # Modern button section with enhanced styling
        button_section = ctk.CTkFrame(hero_card, fg_color="transparent")
        button_section.grid(row=1, column=0, sticky="ew", padx=32, pady=(0, 32))
        button_section.grid_columnconfigure((0, 1), weight=1)

        # Primary action button
        goto_vault = ctk.CTkButton(
            button_section,
            text="Ir a Contraseñas Guardadas",
            image=None,
            compound="left",
            command=lambda: self._navigate_to("encryption"),
            fg_color=COLOR_ROJO_PRINCIPAL,
            hover_color=COLOR_ROJO_HOVER,
            height=48,
            corner_radius=16,
            font=self.fonts["button"],
        )
        goto_vault.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        # Add subtle press animation
        def animate_vault_press():
            original_height = 48
            goto_vault.configure(height=original_height - 2)
            self.after(100, lambda: goto_vault.configure(height=original_height))

        def vault_click():
            animate_vault_press()
            self._navigate_to("encryption")

        goto_vault.configure(command=vault_click)
        self._register_responsive_widget(goto_vault, base_height=48, min_height=40)

        # Secondary action button
        goto_support = ctk.CTkButton(
            button_section,
            text="Ver Soporte",
            image=None,
            compound="left",
            command=lambda: self._navigate_to("support"),
            fg_color="transparent",
            hover_color=COLOR_ROJO_LIGHT,
            border_width=2,
            border_color=COLOR_ROJO_PRINCIPAL,
            text_color=(COLOR_ROJO_PRINCIPAL, COLOR_ROJO_ACENTO),
            height=48,
            corner_radius=16,
            font=self.fonts["button"],
        )
        goto_support.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        def animate_support_press():
            original_height = 48
            goto_support.configure(height=original_height - 2)
            self.after(100, lambda: goto_support.configure(height=original_height))

        def support_click():
            animate_support_press()
            self._navigate_to("support")

        goto_support.configure(command=support_click)
        self._register_responsive_widget(
            goto_support,
            base_height=48,
            min_height=40,
        )

        # Modern stats section
        stats_wrapper = ctk.CTkFrame(frame, fg_color="transparent")
        stats_wrapper.pack(fill="both", expand=True, padx=0, pady=(0, 16))
        stats_wrapper.grid_columnconfigure((0, 1, 2), weight=1, uniform="stats")

        # Enhanced vault stat card
        vault_stat = ctk.CTkFrame(
            stats_wrapper,
            fg_color=(COLOR_BLANCO_WARM, "#2D3748"),
            corner_radius=24,
            border_width=0,
        )
        vault_stat.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        # Add hover effect
        def on_vault_hover(e):
            vault_stat.configure(fg_color=(COLOR_ROJO_LIGHT[0], "#3D2F4A"))

        def on_vault_leave(e):
            vault_stat.configure(fg_color=(COLOR_BLANCO_WARM, "#2D3748"))

        vault_stat.bind("<Enter>", on_vault_hover)
        vault_stat.bind("<Leave>", on_vault_leave)

        vault_stat.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            vault_stat,
            text="Contraseñas Cifradas",
            image=None,
            compound="left",
            font=self.fonts["card_label"],
            text_color=TEXT_COLOR_MUTED,
            anchor="w"
        ).pack(anchor="w", padx=24, pady=(24, 8))

        ctk.CTkLabel(
            vault_stat,
            textvariable=self.password_count_var,
            font=self.fonts["card_stat_primary"],
            text_color=TEXT_COLOR_PRIMARY,
            anchor="w"
        ).pack(anchor="w", padx=24)

        # Enhanced support stat card
        support_stat = ctk.CTkFrame(
            stats_wrapper,
            fg_color=(COLOR_BLANCO_WARM, "#2D3748"),
            corner_radius=24,
            border_width=0,
        )
        support_stat.grid(row=0, column=1, padx=0, sticky="nsew")

        def on_support_hover(e):
            support_stat.configure(fg_color=(COLOR_ROJO_LIGHT[0], "#3D2F4A"))

        def on_support_leave(e):
            support_stat.configure(fg_color=(COLOR_BLANCO_WARM, "#2D3748"))

        support_stat.bind("<Enter>", on_support_hover)
        support_stat.bind("<Leave>", on_support_leave)

        support_stat.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            support_stat,
            text="Tickets de Soporte",
            image=None,
            compound="left",
            font=self.fonts["card_label"],
            text_color=TEXT_COLOR_MUTED,
            anchor="w"
        ).pack(anchor="w", padx=24, pady=(24, 8))

        ctk.CTkLabel(
            support_stat,
            textvariable=self.profile_ticket_metric_var,
            font=self.fonts["card_stat_primary"],
            text_color=TEXT_COLOR_PRIMARY,
            anchor="w"
        ).pack(anchor="w", padx=24)

        # Enhanced sync stat card
        sync_stat = ctk.CTkFrame(
            stats_wrapper,
            fg_color=(COLOR_BLANCO_WARM, "#2D3748"),
            corner_radius=24,
            border_width=0,
        )
        sync_stat.grid(row=0, column=2, padx=0, sticky="nsew")

        def on_sync_hover(e):
            sync_stat.configure(fg_color=(COLOR_ROJO_LIGHT[0], "#3D2F4A"))

        def on_sync_leave(e):
            sync_stat.configure(fg_color=(COLOR_BLANCO_WARM, "#2D3748"))

        sync_stat.bind("<Enter>", on_sync_hover)
        sync_stat.bind("<Leave>", on_sync_leave)

        sync_stat.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            sync_stat,
            text="Última Sincronización",
            image=None,
            compound="left",
            font=self.fonts["card_label"],
            text_color=TEXT_COLOR_MUTED,
            anchor="w"
        ).pack(anchor="w", padx=24, pady=(24, 8))

        ctk.CTkLabel(
            sync_stat,
            textvariable=self.profile_last_sync_var,
            font=self.fonts["card_stat_secondary"],
            text_color=TEXT_COLOR_PRIMARY,
            anchor="w"
        ).pack(anchor="w", padx=24)

        return frame

    def _create_modern_card(self, parent, fg_color=None, corner_radius=24, border_width=0,
                           border_color=None, padx=0, pady=0, **kwargs):
        """Create a modern card with consistent styling"""
        if fg_color is None:
            fg_color = (COLOR_BLANCO_WARM, "#2D3748")

        card = ctk.CTkFrame(
            parent,
            fg_color=fg_color,
            corner_radius=corner_radius,
            border_width=border_width,
            border_color=border_color or COLOR_DIVIDER_LIGHT,
            **kwargs
        )

        if padx or pady:
            card.grid_configure(padx=padx, pady=pady)

        return card

    def _create_modern_button(self, parent, text, command, fg_color=COLOR_ROJO_PRINCIPAL,
                            hover_color=COLOR_ROJO_HOVER, height=44, corner_radius=16,
                            width=None, font=None, **kwargs):
        """Create a modern button with consistent styling and animations"""
        if font is None:
            font = self.fonts["button"]

        button_kwargs = {
            "text": text,
            "command": command,
            "fg_color": fg_color,
            "hover_color": hover_color,
            "height": height,
            "corner_radius": corner_radius,
            "font": font,
            **kwargs
        }

        if width is not None:
            button_kwargs["width"] = width

        button = ctk.CTkButton(parent, **button_kwargs)

        # Add subtle press animation
        def animate_press():
            original_height = height
            button.configure(height=original_height - 2)
            self.after(100, lambda: button.configure(height=original_height))

        original_command = command
        if original_command:
            def animated_command():
                animate_press()
                if original_command:
                    original_command()
            button.configure(command=animated_command)

        return button

    def _navigate_to(self, section_key: str):
        if self.nav_segmented:
            for label, key in self.nav_map.items():
                if key == section_key:
                    self.nav_segmented.set(label)
                    break
        self._show_section(section_key)

    def _build_encryption_section(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_columnconfigure((0, 1), weight=1, uniform="vault")
        frame.grid_rowconfigure(0, weight=1)

        form_card = ctk.CTkFrame(
            frame,
            fg_color=COLOR_FONDO_CARD,
            corner_radius=24,
            border_width=1,
            border_color=COLOR_DIVIDER_LIGHT,
        )
        form_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=8)
        form_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            form_card,
            text="Guardar nueva credencial",
            font=self.fonts["section_title"],
            text_color=TEXT_COLOR_PRIMARY,
        ).grid(row=0, column=0, sticky="w", padx=24, pady=(24, 6))

        info_label = ctk.CTkLabel(
            form_card,
            text="Usamos cifrado avanzado con tu clave maestra. Completa la informacion para registrarla.",
            font=self.fonts["body"],
            text_color=TEXT_COLOR_SECONDARY,
            wraplength=380,
            justify="left",
        )
        info_label.grid(row=1, column=0, sticky="w", padx=24, pady=(0, 18))
        self._register_wraplength(info_label, 380)

        self.site_entry = ctk.CTkEntry(
            form_card,
            placeholder_text="Sitio o servicio (ej. encryptu.com)",
            height=44,
            corner_radius=12,
            font=self.fonts["body"],
            validate="key",
            validatecommand=(self._validators["site"], "%P"),
        )
        self.site_entry.grid(row=2, column=0, sticky="ew", padx=24, pady=6)
        self._register_responsive_widget(self.site_entry, base_height=44, min_height=34)

        self.username_entry_save = ctk.CTkEntry(
            form_card,
            placeholder_text="Usuario asociado",
            height=44,
            corner_radius=12,
            font=self.fonts["body"],
            validate="key",
            validatecommand=(self._validators["username"], "%P"),
        )
        self.username_entry_save.grid(row=3, column=0, sticky="ew", padx=24, pady=6)
        self._register_responsive_widget(self.username_entry_save, base_height=44, min_height=34)

        self.password_entry = ctk.CTkEntry(
            form_card,
            placeholder_text="Contrasena a cifrar",
            show="*",
            height=44,
            corner_radius=12,
            font=self.fonts["body"],
            validate="key",
            validatecommand=(self._validators["password"], "%P"),
        )
        self.password_entry.grid(row=4, column=0, sticky="ew", padx=24, pady=6)
        self._register_responsive_widget(self.password_entry, base_height=44, min_height=34)

        self.save_button = ctk.CTkButton(
            form_card,
            text="Guardar de forma segura",
            command=self.save_action,
            fg_color=COLOR_ROJO_PRINCIPAL,
            hover_color=COLOR_ROJO_HOVER,
            height=44,
            corner_radius=14,
            font=self.fonts["button"],
        )
        self.save_button.grid(row=5, column=0, sticky="ew", padx=24, pady=(18, 8))
        self._register_responsive_widget(self.save_button, base_height=44, min_height=34)

        self.status_label_save = ctk.CTkLabel(
            form_card,
            text="",
            font=self.fonts["body_small"],
            text_color=TEXT_COLOR_SECONDARY,
        )
        self.status_label_save.grid(row=6, column=0, sticky="w", padx=24, pady=(0, 24))

        list_card = ctk.CTkFrame(
            frame,
            fg_color=COLOR_FONDO_CARD,
            corner_radius=24,
            border_width=1,
            border_color=COLOR_DIVIDER_LIGHT,
        )
        list_card.grid(row=0, column=1, sticky="nsew", padx=(12, 0), pady=8)
        list_card.grid_rowconfigure(2, weight=1)
        list_card.grid_columnconfigure(0, weight=1)

        list_header = ctk.CTkFrame(list_card, fg_color="transparent")
        list_header.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 0))
        list_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            list_header,
            text="Vault de contraseñas",
            font=self.fonts["section_title"],
            text_color=TEXT_COLOR_PRIMARY,
        ).grid(row=0, column=0, sticky="w")

        refresh_button = ctk.CTkButton(
            list_header,
            text="Actualizar",
            command=self.refresh_password_list,
            fg_color="transparent",
            hover_color=COLOR_ROJO_ACENTO,
            border_width=1,
            border_color=COLOR_ROJO_PRINCIPAL,
            text_color=(COLOR_ROJO_PRINCIPAL, COLOR_ROJO_ACENTO),
            height=34,
            corner_radius=12,
            width=120,
            font=self.fonts["button"],
        )
        refresh_button.grid(row=0, column=1, sticky="e")
        self._register_responsive_widget(
            refresh_button,
            base_height=34,
            base_width=120,
            min_height=30,
            min_width=100,
        )

        ctk.CTkLabel(
            list_card,
            text="Gestiona, visualiza y copia credenciales bajo demanda.",
            font=self.fonts["body"],
            text_color=TEXT_COLOR_SECONDARY,
        ).grid(row=1, column=0, sticky="w", padx=24, pady=(8, 12))

        self.scrollable_frame = ctk.CTkScrollableFrame(list_card, fg_color="transparent")
        self.scrollable_frame.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 12))

        ctk.CTkLabel(
            list_card,
            text="Selecciona Ver / Copiar para desencriptar usando tu clave maestra.",
            font=self.fonts["body_small"],
            text_color=TEXT_COLOR_MUTED,
        ).grid(row=3, column=0, sticky="w", padx=24, pady=(0, 24))

        return frame

    def _build_support_section(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=0, sticky="nsew")
        # Start with mobile layout configuration
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=0)  # Initially hidden
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        tickets_panel = ctk.CTkFrame(
            frame,
            fg_color=COLOR_FONDO_CARD,
            corner_radius=24,
            border_width=1,
            border_color=COLOR_DIVIDER_LIGHT,
        )
        tickets_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=8)
        tickets_panel.grid_rowconfigure(5, weight=1)
        tickets_panel.grid_columnconfigure(0, weight=1)

        # Add modern scrolling behavior to tickets panel
        tickets_panel.configure(height=400)  # Set a reasonable max height

        ctk.CTkLabel(
            tickets_panel,
            text="Mis tickets de soporte",
            font=self.fonts["section_title"],
            text_color=(COLOR_ROJO_PRINCIPAL, COLOR_ROJO_ACENTO),
        ).grid(row=0, column=0, sticky="w", padx=24, pady=(24, 6))

        tickets_intro = ctk.CTkLabel(
            tickets_panel,
            text="Cuentanos que ocurre y enviaremos tu caso a soporte.",
            font=self.fonts["body_medium"],
            text_color=TEXT_COLOR_SECONDARY,
            wraplength=420,
            justify="left",
        )
        tickets_intro.grid(row=1, column=0, sticky="w", padx=24)
        self._register_wraplength(tickets_intro, 420)

        self.support_form_card = ctk.CTkFrame(
            tickets_panel,
            fg_color=(COLOR_BLANCO, "#1F2937"),
            corner_radius=20,
            border_width=1,
            border_color=COLOR_ROJO_PRINCIPAL,
        )
        self.support_form_card.grid(row=2, column=0, sticky="ew", padx=24, pady=(18, 12))
        self.support_form_card.grid_columnconfigure(0, weight=1)
        self.support_form_card.grid_columnconfigure(1, weight=1)

        # Constrain form card height to prevent it from growing too large
        self.support_form_card.grid_rowconfigure(10, weight=1)  # Button row can expand if needed

        ctk.CTkLabel(
            self.support_form_card,
            text="Crear nuevo ticket",
            font=self.fonts["form_title"],
            text_color=(COLOR_ROJO_PRINCIPAL, COLOR_ROJO_ACENTO),
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 4))

        form_intro = ctk.CTkLabel(
            self.support_form_card,
            text="Los mismos campos que el formulario web: nombre, apellido, correo, motivo, telefono y descripcion.",
            font=self.fonts["body_small"],
            text_color=TEXT_COLOR_MUTED,
            wraplength=440,
            justify="left",
        )
        form_intro.grid(row=1, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 12))
        self._register_wraplength(form_intro, 440)

        first_name_entry = ctk.CTkEntry(
            self.support_form_card,
            placeholder_text="Nombre",
            textvariable=self.ticket_first_name_var,
            height=38,
            corner_radius=12,
            font=self.fonts["body"],
            validate="key",
            validatecommand=(self._validators["name"], "%P"),
        )
        first_name_entry.grid(row=2, column=0, sticky="ew", padx=(20, 10), pady=(0, 10))
        self._register_responsive_widget(first_name_entry, base_height=38, min_height=32)

        last_name_entry = ctk.CTkEntry(
            self.support_form_card,
            placeholder_text="Apellido",
            textvariable=self.ticket_last_name_var,
            height=38,
            corner_radius=12,
            font=self.fonts["body"],
            validate="key",
            validatecommand=(self._validators["name"], "%P"),
        )
        last_name_entry.grid(row=2, column=1, sticky="ew", padx=(10, 20), pady=(0, 10))
        self._register_responsive_widget(last_name_entry, base_height=38, min_height=32)

        email_entry = ctk.CTkEntry(
            self.support_form_card,
            placeholder_text="Correo electronico",
            textvariable=self.ticket_email_var,
            height=38,
            corner_radius=12,
            font=self.fonts["body"],
            validate="key",
            validatecommand=(self._validators["email"], "%P"),
        )
        email_entry.grid(row=3, column=0, columnspan=2, sticky="ew", padx=20, pady=10)
        self._register_responsive_widget(email_entry, base_height=38, min_height=32)

        reason_menu = ctk.CTkOptionMenu(
            self.support_form_card,
            values=SUPPORT_REASON_OPTIONS,
            variable=self.ticket_reason_var,
            fg_color=COLOR_ROJO_PRINCIPAL,
            button_color=COLOR_ROJO_HOVER,
            button_hover_color=COLOR_ROJO_ACENTO,
            height=36,
            corner_radius=12,
            font=self.fonts["body"],
        )
        reason_menu.grid(row=4, column=0, columnspan=2, sticky="ew", padx=20, pady=10)
        self._register_responsive_widget(reason_menu, base_height=36, min_height=32)

        phone_entry = ctk.CTkEntry(
            self.support_form_card,
            placeholder_text="Telefono de contacto (9 digitos)",
            textvariable=self.ticket_phone_var,
            height=38,
            corner_radius=12,
            font=self.fonts["body"],
            validate="key",
            validatecommand=(self._validators["phone"], "%P"),
        )
        phone_entry.grid(row=5, column=0, columnspan=2, sticky="ew", padx=20, pady=10)
        self._register_responsive_widget(phone_entry, base_height=38, min_height=32)

        self.support_ticket_description_input = ctk.CTkTextbox(
            self.support_form_card,
            height=120,
            corner_radius=12,
            font=self.fonts["body"],
        )
        self.support_ticket_description_input.grid(row=6, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 12))
        self._register_responsive_widget(
            self.support_ticket_description_input,
            base_height=120,
            min_height=100,
        )
        self._bind_text_limit(
            self.support_ticket_description_input,
            500,
            self.ticket_description_count_var,
        )

        description_counter = ctk.CTkLabel(
            self.support_form_card,
            textvariable=self.ticket_description_count_var,
            font=self.fonts["tiny"],
            text_color=TEXT_COLOR_MUTED,
        )
        description_counter.grid(row=7, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 6))

        self.ticket_form_status_label = ctk.CTkLabel(
            self.support_form_card,
            textvariable=self.ticket_form_status_var,
            font=self.fonts["tiny"],
            text_color=TEXT_COLOR_MUTED,
        )
        self.ticket_form_status_label.grid(row=8, column=0, sticky="w", padx=20, pady=(0, 20))

        self.support_create_button = ctk.CTkButton(
            self.support_form_card,
            text="Enviar ticket",
            command=self._handle_create_support_ticket,
            fg_color=COLOR_ROJO_PRINCIPAL,
            hover_color=COLOR_ROJO_HOVER,
            height=42,
            corner_radius=14,
            font=self.fonts["button"],
        )
        self.support_create_button.grid(row=8, column=1, sticky="e", padx=20, pady=(0, 20))
        self._register_responsive_widget(self.support_create_button, base_height=42, min_height=34)

        search_entry = ctk.CTkEntry(
            tickets_panel,
            placeholder_text="Buscar por id, motivo o estado...",
            textvariable=self.ticket_search_var,
            height=40,
            corner_radius=14,
            font=self.fonts["body"],
        )
        search_entry.grid(row=3, column=0, sticky="ew", padx=24, pady=(12, 10))
        self._register_responsive_widget(search_entry, base_height=40, min_height=32)

        ctk.CTkLabel(
            tickets_panel,
            textvariable=self.support_list_count_var,
            font=self.fonts["card_label"],
            text_color=TEXT_COLOR_MUTED,
        ).grid(row=4, column=0, sticky="w", padx=24, pady=(0, 8))

        self.support_ticket_list_container = ctk.CTkScrollableFrame(
            tickets_panel, fg_color="transparent"
        )
        self.support_ticket_list_container.grid(row=5, column=0, sticky="nsew", padx=16, pady=(0, 20))

        chat_panel = ctk.CTkFrame(
            frame,
            fg_color=COLOR_FONDO_CARD,
            corner_radius=24,
            border_width=1,
            border_color=COLOR_DIVIDER_LIGHT,
        )
        chat_panel.grid(row=0, column=1, sticky="nsew", padx=(12, 0), pady=8)
        chat_panel.grid_rowconfigure(2, weight=1)
        chat_panel.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(chat_panel, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 12))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            textvariable=self.support_chat_title_var,
            font=self.fonts["support_chat_title"],
            text_color=TEXT_COLOR_PRIMARY,
        ).grid(row=0, column=0, sticky="w")

        self.support_badge_holder = ctk.CTkFrame(header, fg_color="transparent")
        self.support_badge_holder.grid(row=0, column=1, sticky="e", padx=(12, 0))

        ctk.CTkLabel(
            header,
            textvariable=self.support_chat_meta_var,
            font=self.fonts["body_small"],
            text_color=TEXT_COLOR_MUTED,
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))

        self.support_messages_container = ctk.CTkScrollableFrame(
            chat_panel, fg_color="transparent"
        )
        self.support_messages_container.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 12))

        composer = ctk.CTkFrame(chat_panel, fg_color="transparent")
        composer.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 24))
        composer.grid_columnconfigure(0, weight=1)

        self.support_message_input = ctk.CTkTextbox(
            composer,
            height=80,
            corner_radius=14,
            font=self.fonts["body"],
        )
        self.support_message_input.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.support_message_input.bind("<Control-Return>", self._send_support_message)
        self.support_message_input.bind("<Command-Return>", self._send_support_message)
        self._register_responsive_widget(
            self.support_message_input,
            base_height=80,
            min_height=64,
        )
        self._bind_text_limit(
            self.support_message_input,
            500,
            self.support_message_count_var,
        )

        self.support_send_button = ctk.CTkButton(
            composer,
            text="Enviar mensaje a soporte",
            command=self._send_support_message,
            fg_color=COLOR_ROJO_PRINCIPAL,
            hover_color=COLOR_ROJO_HOVER,
            height=42,
            corner_radius=14,
            font=self.fonts["button"],
        )
        self.support_send_button.grid(row=1, column=1, sticky="e", padx=(12, 0), pady=(6, 0))
        self._register_responsive_widget(self.support_send_button, base_height=42, min_height=34)

        message_counter = ctk.CTkLabel(
            composer,
            textvariable=self.support_message_count_var,
            font=self.fonts["tiny"],
            text_color=TEXT_COLOR_MUTED,
        )
        message_counter.grid(row=1, column=0, sticky="w", pady=(6, 0))

        self.support_status_label = ctk.CTkLabel(
            composer,
            textvariable=self.support_status_var,
            font=self.fonts["tiny"],
            text_color=TEXT_COLOR_MUTED,
        )
        self.support_status_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=(4, 0))

        self._set_composer_enabled(False)

        frame.bind(
            "<Configure>",
            lambda event: self._update_support_layout(frame, tickets_panel, chat_panel),
        )
        self.after(50, lambda: self._update_support_layout(frame, tickets_panel, chat_panel))

        return frame


    def _initialize_support_data(self):
        """Inicializa los datos del sistema de soporte técnico.

        Se ejecuta después de un breve retraso para asegurar que la interfaz
        esté completamente cargada antes de realizar peticiones de datos.
        """
        self._load_support_tickets(force_refresh=True)

    # ------------------------------------------------------------------
    # FUNCIONALIDADES DEL SISTEMA DE SOPORTE TÉCNICO
    # ------------------------------------------------------------------
    # Implementa un sistema completo de gestión de tickets de soporte con
    # funcionalidades avanzadas como búsqueda, filtrado, creación de tickets
    # y comunicación en tiempo real con el equipo de soporte.
    #
    # CARACTERÍSTICAS PRINCIPALES:
    # - Carga y gestión de tickets desde el servidor
    # - Búsqueda en tiempo real por ID, nombre, email o motivo
    # - Creación de nuevos tickets con validación completa
    # - Chat integrado para comunicación con soporte
    # - Estados y badges visuales para diferentes tipos de tickets
    # - Sincronización automática de datos y mensajes
    # ------------------------------------------------------------------

    def _load_support_tickets(self, force_refresh: bool = False):
        self.support_loading = True
        self.support_list_count_var.set("Cargando tickets...")
        self._render_support_ticket_list()

        data = self.controller.get_support_tickets(force_refresh=force_refresh)
        if data is None:
            self.support_loading = False
            return

        normalized: List[Dict[str, Any]] = []
        for raw_ticket in data:
            ticket = self._normalize_ticket(raw_ticket)
            ticket_id = ticket["id"]
            ticket["messages"] = self.support_ticket_messages.get(ticket_id, [])
            normalized.append(ticket)

        self.support_tickets = normalized
        self.support_loading = False

        total = len(self.support_tickets)
        self.support_list_count_var.set(f"{total} ticket{'s' if total != 1 else ''}")
        self.profile_ticket_metric_var.set(str(total))
        self.profile_last_sync_var.set(datetime.now().strftime("%d/%m/%Y %H:%M"))

        if not total:
            self.support_active_ticket_id = None
            self._render_support_ticket_list()
            self._render_support_header(None)
            self._render_support_messages(None)
            self._set_composer_enabled(False)
            return

        previous_active = self.support_active_ticket_id
        available_ids = [ticket["id"] for ticket in self.support_tickets]
        if previous_active not in available_ids:
            self.support_active_ticket_id = available_ids[0]

        self._render_support_ticket_list()

        active_ticket = self._get_support_ticket(self.support_active_ticket_id)
        self._render_support_header(active_ticket)
        self._render_support_messages(active_ticket)

        if self.support_active_ticket_id and (
            previous_active != self.support_active_ticket_id
            or not self.support_ticket_messages.get(self.support_active_ticket_id)
        ):
            self._load_ticket_messages(self.support_active_ticket_id, notify=False)

    def _update_support_layout(
        self,
        container: ctk.CTkFrame,
        tickets_panel: ctk.CTkFrame,
        chat_panel: ctk.CTkFrame,
    ):
        width = container.winfo_width()
        if width <= 0:
            return

        # Better breakpoint for desktop windows - 900px for better responsiveness
        if width < 900:
            # Smaller desktop: Stack vertically with constrained heights
            container.grid_columnconfigure(0, weight=1)
            container.grid_columnconfigure(1, weight=0)
            container.grid_rowconfigure(0, weight=0)  # Tickets panel gets constrained height
            container.grid_rowconfigure(1, weight=1)  # Chat panel gets remaining space

            # Configure tickets panel with max height and scrolling
            tickets_panel.grid_configure(
                row=0, column=0, sticky="ew", padx=0, pady=(0, 16),
                rowspan=1
            )
            # Constrain tickets panel height to prevent overflow
            tickets_panel.grid_rowconfigure(5, weight=1)  # Scrollable area gets weight

            chat_panel.grid_configure(
                row=1, column=0, sticky="nsew", padx=0, pady=(0, 8)
            )

            # Adjust form card for better fit in smaller windows
            if hasattr(self, 'support_form_card') and self.support_form_card:
                self.support_form_card.grid_configure(pady=(8, 4))
                # Make form card more compact and ensure it fits
                self.support_form_card.configure(height=380)

        else:
            # Larger desktop: Side by side with optimal layout
            container.grid_columnconfigure(0, weight=1)
            container.grid_columnconfigure(1, weight=2)
            container.grid_rowconfigure(0, weight=1)
            container.grid_rowconfigure(1, weight=0)

            tickets_panel.grid_configure(
                row=0, column=0, sticky="nsew", padx=(0, 16), pady=0,
                rowspan=2  # Take full height
            )
            chat_panel.grid_configure(
                row=0, column=1, sticky="nsew", padx=(16, 0), pady=0,
                rowspan=2  # Take full height
            )

            # Restore form card padding for desktop
            if hasattr(self, 'support_form_card') and self.support_form_card:
                self.support_form_card.grid_configure(pady=(18, 12))

    def _normalize_ticket(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        ticket_id = raw.get("id")
        first_name = raw.get("first_name") or raw.get("firstName") or ""
        last_name = raw.get("last_name") or raw.get("lastName") or ""
        email = raw.get("email") or ""
        reason = str(raw.get("reason", "")).lower()
        status = str(raw.get("status", "")).lower()
        created_raw = raw.get("created_at") or raw.get("createdAt")
        created_at = self._parse_datetime(created_raw)

        return {
            "id": ticket_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "reason": reason,
            "status": status,
            "created_at": created_at,
        }

    def _parse_datetime(self, value: Any) -> datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            iso_value = value.replace("Z", "+00:00") if value.endswith("Z") else value
            try:
                return datetime.fromisoformat(iso_value)
            except ValueError:
                pass
        return datetime.now()

    def _load_ticket_messages(
        self, ticket_id: Optional[int], force_refresh: bool = False, notify: bool = True
    ):
        if ticket_id is None:
            return

        if not force_refresh and ticket_id in self.support_ticket_messages:
            return

        if notify:
            self._set_support_status("Cargando conversacion...", success=False)

        data = self.controller.get_support_ticket_messages(ticket_id, force_refresh=force_refresh)
        if data is None:
            return

        normalized: List[Dict[str, Any]] = []
        for message in data:
            timestamp_raw = (
                message.get("timestamp")
                or message.get("created_at")
                or message.get("createdAt")
            )
            normalized.append(
                {
                    "id": message.get("id"),
                    "author": (message.get("author") or "user").lower(),
                    "body": message.get("body") or "",
                    "timestamp": self._parse_datetime(timestamp_raw),
                    "name": message.get("name"),
                }
            )

        normalized.sort(key=lambda msg: msg["timestamp"])
        self.support_ticket_messages[ticket_id] = normalized

        ticket = self._get_support_ticket(ticket_id)
        if ticket is not None:
            ticket["messages"] = normalized
            self._render_support_messages(ticket)

        if notify:
            if normalized:
                self._set_support_status("Conversacion actualizada.", success=True)
            else:
                self._set_support_status("Aun no hay mensajes en este ticket.", success=False)

    def _show_section(self, key: str):
        for frame in self.sections.values():
            frame.grid_remove()

        target = self.sections.get(key)
        if target:
            target.grid()

        if key == "profile":
            self._update_profile_metrics()
        elif key == "support":
            if not self.support_tickets and not self.support_loading:
                self._load_support_tickets()

    def _render_support_ticket_list(self):
        if not self.support_ticket_list_container:
            return

        for widget in self.support_ticket_list_container.winfo_children():
            widget.destroy()

        if self.support_loading:
            ctk.CTkLabel(
                self.support_ticket_list_container,
                text="Cargando tickets de soporte...",
                text_color=TEXT_COLOR_MUTED,
            ).pack(fill="x", padx=12, pady=24)
            return

        query = self.ticket_search_var.get().strip().lower()
        tickets = self.support_tickets
        if query:
            tickets = [
                ticket
                for ticket in self.support_tickets
                if query in str(ticket["id"]).lower()
                or query in f"{ticket.get('first_name', '')} {ticket.get('last_name', '')}".lower()
                or query in (ticket.get("email") or "").lower()
                or query in (ticket.get("reason") or "")
            ]

        if not self.support_tickets:
            ctk.CTkLabel(
                self.support_ticket_list_container,
                text="Aun no hay tickets de soporte registrados.",
                font=self.fonts["body_small"],
                text_color=TEXT_COLOR_MUTED,
                wraplength=240,
                justify="center",
            ).pack(fill="x", padx=12, pady=32)
            return

        if query and not tickets:
            ctk.CTkLabel(
                self.support_ticket_list_container,
                text="Sin resultados para tu busqueda.",
                font=self.fonts["body_small"],
                text_color=TEXT_COLOR_MUTED,
                wraplength=240,
                justify="center",
            ).pack(fill="x", padx=12, pady=32)
            return

        for ticket in tickets:
            is_active = ticket["id"] == self.support_active_ticket_id
            card = ctk.CTkFrame(
                self.support_ticket_list_container,
                fg_color=(COLOR_ROJO_ACENTO, "#7F1D1D") if is_active else COLOR_FONDO_CARD_ALT,
                corner_radius=16,
                border_width=2 if is_active else 1,
                border_color=COLOR_ROJO_PRINCIPAL if is_active else COLOR_DIVIDER_LIGHT,
            )
            card.pack(fill="x", padx=8, pady=6)
            card.configure(cursor="hand2")
            self._bind_card_click(card, ticket["id"])

            title_color = (COLOR_BLANCO, COLOR_BLANCO) if is_active else TEXT_COLOR_PRIMARY
            meta_color = (COLOR_BLANCO, COLOR_BLANCO) if is_active else TEXT_COLOR_SECONDARY
            reason = (ticket.get("reason") or "").capitalize() or "N/A"
            status = (ticket.get("status") or "").capitalize() or "N/A"
            email = ticket.get("email") or "sin correo"

            title = ctk.CTkLabel(
                card,
                text=f"Ticket #{ticket['id']} - {ticket.get('first_name', '')} {ticket.get('last_name', '')}".strip(),
                font=self.fonts["list_title"],
                text_color=title_color,
                anchor="w",
            )
            title.pack(fill="x", padx=16, pady=(14, 4))
            self._bind_card_click(title, ticket["id"])

            meta = ctk.CTkLabel(
                card,
                text=f"{email} - {reason} - {status}",
                font=self.fonts["body_small"],
                text_color=meta_color,
                anchor="w",
            )
            meta.pack(fill="x", padx=16, pady=(0, 14))
            self._bind_card_click(meta, ticket["id"])

    def _bind_card_click(self, widget, ticket_id: int):
        widget.bind("<Button-1>", lambda _event, tid=ticket_id: self._handle_select_ticket(tid))
    
    def _set_composer_enabled(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        if self.support_message_input is not None:
            self.support_message_input.configure(state=state)
        if self.support_send_button is not None:
            self.support_send_button.configure(state="normal" if enabled else "disabled")


    def _handle_select_ticket(self, ticket_id: int):
        self.support_active_ticket_id = ticket_id
        self._render_support_ticket_list()
        ticket = self._get_support_ticket(ticket_id)
        self._render_support_header(ticket)
        self._render_support_messages(ticket)
        self._set_support_status("")
        self._load_ticket_messages(ticket_id)

    def _get_support_ticket(self, ticket_id: Optional[int]) -> Optional[Dict[str, Any]]:
        if ticket_id is None:
            return None
        for ticket in self.support_tickets:
            if ticket["id"] == ticket_id:
                return ticket
        return None

    def _render_support_header(self, ticket: Optional[Dict[str, Any]]):
        if not self.support_badge_holder:
            return

        for widget in self.support_badge_holder.winfo_children():
            widget.destroy()

        if not ticket:
            self.support_chat_title_var.set("Selecciona un ticket para ver los detalles.")
            self.support_chat_meta_var.set("")
            return

        full_name = f"{ticket.get('first_name', '')} {ticket.get('last_name', '')}".strip()
        if not full_name:
            full_name = "Cliente"
        self.support_chat_title_var.set(f"Ticket #{ticket.get('id')} - {full_name}")

        created_at_value = ticket.get("created_at")
        if isinstance(created_at_value, datetime):
            created_text = created_at_value.strftime("%d/%m/%Y %H:%M")
        elif isinstance(created_at_value, str):
            created_text = created_at_value
        else:
            created_text = "Fecha desconocida"

        email = ticket.get("email") or "Sin correo registrado"
        self.support_chat_meta_var.set(f"{email} - Creado el {created_text}")

        reason_value = ticket.get("reason")
        if reason_value:
            reason_badge = self._create_badge(
                reason_value.capitalize(),
                BADGE_REASON_COLOR,
                BADGE_REASON_TEXT,
            )
            reason_badge.pack(side="left", padx=(0, 6))

        status_value = ticket.get("status", "")
        status_cfg = BADGE_STATUS_COLORS.get(status_value.lower())
        if status_cfg:
            status_badge = self._create_badge(
                status_value.capitalize(),
                status_cfg["bg"],
                status_cfg["text"],
            )
            status_badge.pack(side="left")

    def _create_badge(self, text: str, bg_colors, text_colors):
        return ctk.CTkLabel(
            self.support_badge_holder,
            text=text,
            fg_color=bg_colors,
            text_color=text_colors,
            corner_radius=12,
            font=self.fonts["badge_small"],
            padx=10,
            pady=4,
        )

    def _render_support_messages(self, ticket: Optional[Dict[str, Any]]):
        if not self.support_messages_container:
            return

        for widget in self.support_messages_container.winfo_children():
            widget.destroy()

        if not ticket:
            self._set_composer_enabled(False)
            ctk.CTkLabel(
                self.support_messages_container,
                text="Selecciona un ticket o crea uno nuevo para hablar con soporte.",
                font=self.fonts["body_small"],
                text_color=TEXT_COLOR_MUTED,
                wraplength=420,
                justify="center",
            ).pack(fill="both", expand=True, padx=20, pady=60)
            return
        self._set_composer_enabled(True)
        messages = ticket.get("messages") or []
        if not messages:
            ctk.CTkLabel(
                self.support_messages_container,
                text="Aun no hay mensajes registrados. El equipo de EncryptU te respondera pronto.",
                font=self.fonts["body_small"],
                text_color=TEXT_COLOR_MUTED,
                wraplength=420,
                justify="center",
            ).pack(fill="both", expand=True, padx=20, pady=40)
            return

        for message in messages:
            author_role = (message.get("author") or "user").lower()
            is_agent = author_role == "agent"

            bubble_holder = ctk.CTkFrame(self.support_messages_container, fg_color="transparent")
            bubble_holder.pack(fill="x", pady=4)

            inner = ctk.CTkFrame(
                bubble_holder,
                fg_color=(COLOR_ROJO_PRINCIPAL, "#7F1D1D")
                if is_agent
                else ("#F1F5F9", "#1E293B"),
                corner_radius=18,
            )
            inner.pack(side="right" if is_agent else "left", padx=12, pady=4)

            author_name = message.get("name")
            if is_agent:
                author = author_name or SUPPORT_AGENT_NAME
            else:
                author = author_name or "Cliente"
            header_text = f"{author} - {self._format_timestamp(message.get('timestamp'))}"
            header_color = (COLOR_BLANCO, COLOR_BLANCO) if is_agent else TEXT_COLOR_MUTED

            ctk.CTkLabel(
                inner,
                text=header_text,
                font=self.fonts["tiny"],
                text_color=header_color,
                anchor="w",
                justify="left",
            ).pack(fill="x", padx=14, pady=(10, 4))

            body_color = (COLOR_BLANCO, COLOR_BLANCO) if is_agent else TEXT_COLOR_PRIMARY
            ctk.CTkLabel(
                inner,
                text=message.get("body") or "",
                font=self.fonts["body_medium"],
                text_color=body_color,
                anchor="w",
                justify="left",
                wraplength=420,
            ).pack(fill="x", padx=14, pady=(0, 10))

        if hasattr(self.support_messages_container, "_parent_canvas"):
            canvas = self.support_messages_container._parent_canvas
            canvas.after(50, lambda: canvas.yview_moveto(1.0))

    def _format_timestamp(self, value) -> str:
        if isinstance(value, datetime):
            return value.strftime("%d/%m/%Y %H:%M")
        if isinstance(value, str) and value:
            return value
        return "--"

    def _send_support_message(self, event=None):
        message_input = self.support_message_input
        send_button = self.support_send_button
        if message_input is None or send_button is None:
            return "break" if event else None

        message = message_input.get("0.0", "end").strip()

        if not self.support_active_ticket_id:
            self._set_support_status("Selecciona un ticket o crea uno nuevo para enviar mensajes.", error=True)
            return "break" if event else None
        if not message:
            self._set_support_status("Escribe un mensaje para el equipo de soporte.", error=True)
            return "break" if event else None

        ticket_id = self.support_active_ticket_id
        ticket = self._get_support_ticket(ticket_id) if ticket_id is not None else None
        if not ticket_id or not ticket:
            self._set_support_status("El ticket seleccionado ya no existe.", error=True)
            return "break" if event else None

        send_button.configure(state="disabled")
        self._set_support_status("Enviando tu mensaje...", success=False)

        success = self.controller.handle_send_support_message(ticket_id, message)

        if success:
            message_input.delete("0.0", "end")
            if self.support_message_input is not None:
                self._enforce_text_limit(self.support_message_input, 500, self.support_message_count_var)
            self._load_ticket_messages(ticket_id, force_refresh=True, notify=False)
            self._load_support_tickets(force_refresh=True)
            self._set_support_status("Mensaje enviado al equipo de soporte.", success=True)
        else:
            self._set_support_status(
                "No pudimos enviar tu mensaje. Intenta nuevamente.", error=True
            )

        send_button.configure(state="normal")
        return "break" if event else None

    def _set_support_status(self, message: str, error: bool = False, success: bool = False):
        if success:
            color = ("#047857", "#34D399")
        elif error:
            color = (COLOR_ROJO_PRINCIPAL, COLOR_ROJO_ACENTO)
        else:
            color = TEXT_COLOR_MUTED

        self.support_status_var.set(message)
        if self.support_status_label is not None:
            self.support_status_label.configure(text_color=color)

    def _handle_create_support_ticket(self):
        description_widget = self.support_ticket_description_input
        submit_button = self.support_create_button
        if description_widget is None or submit_button is None:
            return

        first_name = self.ticket_first_name_var.get().strip()
        last_name = self.ticket_last_name_var.get().strip()
        email = self.ticket_email_var.get().strip()
        reason_label = self.ticket_reason_var.get().strip().lower()
        phone = self.ticket_phone_var.get().strip()
        description = description_widget.get("1.0", "end").strip()

        if reason_label.startswith("soporte"):
            reason_slug = "soporte"
        elif reason_label.startswith("consulta"):
            reason_slug = "consulta"
        else:
            reason_slug = ""

        if not first_name or not last_name or not email or not reason_slug or not phone or not description:
            self._set_ticket_form_status(
                "Completa nombre, apellido, correo, motivo, telefono y describe el problema.",
                error=True,
            )
            return

        digits = "".join(ch for ch in phone if ch.isdigit())
        if len(digits) != 9:
            self._set_ticket_form_status("El telefono debe tener 9 digitos.", error=True)
            return

        payload = {
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "reason": reason_slug,
            "phone": digits,
            "description": description,
        }

        submit_button.configure(state="disabled", text="Enviando...")
        self._set_ticket_form_status("Creando tu ticket, un momento...", pending=True)

        success, ticket_id, feedback = self.controller.handle_create_support_ticket(payload)

        if success:
            self._clear_ticket_form()
            self._set_ticket_form_status(feedback or "Ticket creado correctamente.", success=True)
            if ticket_id:
                self.support_active_ticket_id = ticket_id
            self._load_support_tickets(force_refresh=True)
        else:
            self._set_ticket_form_status(
                feedback or "No pudimos crear el ticket. Intenta nuevamente.",
                error=True,
            )

        submit_button.configure(state="normal", text="Enviar ticket")  

    def _set_ticket_form_status(
        self,
        message: str,
        error: bool = False,
        success: bool = False,
        pending: bool = False,
    ):
        if success:
            color = ("#047857", "#34D399")
        elif error:
            color = (COLOR_ROJO_PRINCIPAL, COLOR_ROJO_ACENTO)
        else:
            color = TEXT_COLOR_MUTED

        self.ticket_form_status_var.set(message)
        if self.ticket_form_status_label is not None:
            self.ticket_form_status_label.configure(text_color=color)

    def _clear_ticket_form(self):
        self.ticket_first_name_var.set("")
        self.ticket_last_name_var.set("")
        self.ticket_phone_var.set("")
        self.ticket_reason_var.set(SUPPORT_REASON_OPTIONS[0])
        if self.support_ticket_description_input is not None:
            self.support_ticket_description_input.delete("1.0", "end")
            self._enforce_text_limit(
                self.support_ticket_description_input,
                500,
                self.ticket_description_count_var,
            )

    # ------------------------------------------------------------------
    # GESTIÓN DEL VAULT DE CONTRASEÑAS Y ACCIONES DE ENCRIPTACIÓN
    # ------------------------------------------------------------------
    # Implementa la funcionalidad completa del vault de contraseñas incluyendo
    # almacenamiento seguro, recuperación, eliminación y gestión de credenciales
    # cifradas con la clave maestra del usuario.
    #
    # FUNCIONALIDADES PRINCIPALES:
    # - Almacenamiento seguro de nuevas credenciales
    # - Lista y navegación por contraseñas guardadas
    # - Descifrado bajo demanda con verificación de clave maestra
    # - Eliminación segura de credenciales
    # - Gestión de métricas y estadísticas del perfil
    # - Copia automática al portapapeles para facilitar el uso
    # - Validación en tiempo real de datos de entrada
    # ------------------------------------------------------------------

    def _update_profile_metrics(self):
        self.profile_ticket_metric_var.set(str(len(self.support_tickets)))
        self.profile_last_sync_var.set(datetime.now().strftime("%d/%m/%Y %H:%M"))

    def save_action(self):
        if not all([self.site_entry, self.username_entry_save, self.password_entry, self.save_button]):
            return

        site = self.site_entry.get().strip() # type: ignore
        username = self.username_entry_save.get().strip() # type: ignore
        password = self.password_entry.get().strip() # type: ignore

        if not site or not username or not password:
            self.show_status(
                "Completa todos los campos para continuar.",
                "save",
                (COLOR_ROJO_PRINCIPAL, COLOR_ROJO_ACENTO),
            )
            return

        self.save_button.configure(state="disabled", text="Guardando...") # type: ignore
        self.show_status("Guardando...", "save", TEXT_COLOR_SECONDARY)

        success = self.controller.handle_encrypt_and_save(site, username, password)

        if success:
            self.show_status(
                f"Credencial para '{site}' almacenada.",
                "save",
                ("#047857", "#34D399"),
            )
            self.site_entry.delete(0, "end") # type: ignore
            self.username_entry_save.delete(0, "end") # type: ignore
            self.password_entry.delete(0, "end") # type: ignore
            self.refresh_password_list()
        else:
            self.show_status(
                "Ocurrio un error al guardar. Intenta de nuevo.",
                "save",
                (COLOR_ROJO_PRINCIPAL, COLOR_ROJO_ACENTO),
            )

        self.save_button.configure(state="normal", text="Guardar de forma segura") # type: ignore

    def refresh_password_list(self):
        if not self.scrollable_frame:
            return

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        passwords = self.controller.get_saved_passwords()

        if passwords is None:
            ctk.CTkLabel(
                self.scrollable_frame,
                text="No se pudieron obtener las contrasenas. Inicia sesion nuevamente.",
                text_color=(COLOR_ROJO_PRINCIPAL, COLOR_ROJO_ACENTO),
                wraplength=360,
                justify="left",
            ).pack(pady=24, padx=20)
            self.password_count_var.set("--")
            return

        if not passwords:
            ctk.CTkLabel(
                self.scrollable_frame,
                text="Aun no has guardado ninguna contrasena.",
                text_color=TEXT_COLOR_MUTED,
            ).pack(pady=24, padx=20)
            self.password_count_var.set("0")
            self._update_profile_metrics()
            return

        count = 0
        for item in passwords:
            file_id = item.get("id")
            full_filename = item.get("filename", "")
            parts = full_filename.split(" | ", 1)
            site = parts[0]
            username_site = parts[1] if len(parts) > 1 else "Sin usuario"
            count += 1

            card = ctk.CTkFrame(
                self.scrollable_frame,
                fg_color=COLOR_FONDO_CARD_ALT,
                corner_radius=16,
                border_width=1,
                border_color=COLOR_DIVIDER_LIGHT,
            )
            card.pack(fill="x", padx=8, pady=6)

            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True, padx=16, pady=12)

            ctk.CTkLabel(
                info,
                text=site,
                font=self.fonts["list_title"],
                text_color=TEXT_COLOR_PRIMARY,
            ).pack(anchor="w")

            ctk.CTkLabel(
                info,
                text=username_site,
                font=self.fonts["body_small"],
                text_color=TEXT_COLOR_MUTED,
            ).pack(anchor="w", pady=(4, 0))

            actions = ctk.CTkFrame(card, fg_color="transparent")
            actions.pack(side="right", padx=12, pady=12)

            view_button = ctk.CTkButton(
                actions,
                text="Ver / Copiar",
                command=lambda fid=file_id, s=site: self.view_copy_action(fid, s),
                fg_color=COLOR_ROJO_PRINCIPAL,
                hover_color=COLOR_ROJO_HOVER,
                height=36,
                corner_radius=12,
                width=130,
                font=self.fonts["button"],
            )
            view_button.pack(anchor="e")
            self._register_responsive_widget(
                view_button,
                base_height=36,
                base_width=130,
                min_height=30,
                min_width=110,
            )

            delete_button = ctk.CTkButton(
                actions,
                text="Eliminar",
                command=lambda fid=file_id: self.delete_action(fid),
                fg_color="transparent",
                hover_color=COLOR_ROJO_ACENTO,
                border_width=1,
                border_color=COLOR_ROJO_PRINCIPAL,
                text_color=(COLOR_ROJO_PRINCIPAL, COLOR_ROJO_ACENTO),
                height=36,
                corner_radius=12,
                width=130,
                font=self.fonts["button"],
            )
            delete_button.pack(anchor="e", pady=(8, 0))
            self._register_responsive_widget(
                delete_button,
                base_height=36,
                base_width=130,
                min_height=30,
                min_width=110,
            )

        self.password_count_var.set(str(count))
        self._update_profile_metrics()

    def delete_action(self, file_id: int):
        if self.controller.handle_delete_password(file_id):
            self.refresh_password_list()
            self.show_temp_popup("Credencial eliminada correctamente.", "green")
        else:
            self.show_temp_popup("No fue posible eliminar la credencial.", COLOR_ROJO_PRINCIPAL)

    def view_copy_action(self, file_id: int, site: str):
        dialog = ctk.CTkInputDialog(
            text="Para desencriptar ingresa tu clave maestra:",
            title="Verificacion de seguridad",
        )
        master_key = dialog.get_input()

        if master_key:
            decrypted_pass = self.controller.handle_decrypt_password(file_id, site, master_key)
            if decrypted_pass:
                pyperclip.copy(decrypted_pass)
                self.show_temp_popup("Contrasena copiada al portapapeles.")
            else:
                self.show_temp_popup("Clave maestra incorrecta.", COLOR_ROJO_PRINCIPAL)

    def logout_action(self, event=None):
        self.controller.handle_logout()

    def show_status(self, message: str, target: str, color):
        if target == "save" and self.status_label_save:
            self.status_label_save.configure(text=message, text_color=color)
            self.status_label_save.after(4000, lambda: self.status_label_save.configure(text="")) # type: ignore

    def show_temp_popup(self, message: str, color: str = "green"):
        """Show a modern temporary popup with enhanced styling"""
        toplevel_window = self.winfo_toplevel()
        if isinstance(toplevel_window, ctk.CTk):
            # Create modern popup with better styling
            popup = ctk.CTkToplevel(toplevel_window)
            popup.geometry("360x140")
            popup.title("🔥 EncryptU")
            popup.transient(toplevel_window)
            popup.grab_set()

            # Configure popup styling
            popup.configure(
                fg_color=(COLOR_BLANCO_WARM, "#1A202C"),
                corner_radius=20,
                border_width=1,
                border_color=COLOR_ROJO_PRINCIPAL
            )

            # Main container
            container = ctk.CTkFrame(popup, fg_color="transparent")
            container.pack(expand=True, padx=24, pady=24, fill="both")
            container.grid_columnconfigure(0, weight=1)

            # Add appropriate icon based on message type
            if "error" in message.lower() or "incorrect" in message.lower():
                icon_image = None
                fallback_text = "Error"
            elif "success" in message.lower() or "copiada" in message.lower():
                icon_image = None
                fallback_text = "Success"
            elif "eliminada" in message.lower() or "eliminado" in message.lower():
                icon_image = None
                fallback_text = "Deleted"
            else:
                icon_image = None  # Default to success
                fallback_text = "Info"

            # Icon and message layout
            icon_label = ctk.CTkLabel(
                container,
                text=fallback_text,
                image=icon_image,
                compound="left",
                font=self.fonts["hero_headline"],
                text_color=color,
                justify="center",
            )
            icon_label.grid(row=0, column=0, pady=(0, 8))

            message_label = ctk.CTkLabel(
                container,
                text=message,
                font=self.fonts["body"],
                text_color=color,
                wraplength=320,
                justify="center",
            )
            message_label.grid(row=1, column=0, pady=(0, 12))

            # Add a subtle animation
            def fade_out():
                popup.destroy()

            popup.after(2500, fade_out)  # Show for 2.5 seconds

