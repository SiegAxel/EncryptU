import customtkinter as ctk
from datetime import datetime
from typing import Any, Dict, List, Optional

import pyperclip
from PIL import Image

COLOR_ROJO_PRINCIPAL = "#E11D48"
COLOR_ROJO_HOVER = "#BE123C"
COLOR_ROJO_ACENTO = "#FB7185"
COLOR_BLANCO = "#FFFFFF"
TEXT_COLOR_PRIMARY = ("#1A202C", "#F7FAFC")
TEXT_COLOR_SECONDARY = ("#4A5568", "#CBD5F5")
TEXT_COLOR_MUTED = ("#718096", "#94A3B8")
COLOR_FONDO_APP = ("#FFFFFF", "#111827")
COLOR_FONDO_CARD = ("#FFFFFF", "#1F2937")
COLOR_FONDO_CARD_ALT = ("#F8FAFC", "#1A1F2B")
COLOR_DIVIDER_LIGHT = "#E2E8F0"
BADGE_REASON_COLOR = ("#FDE8EC", "#7F1D1D")
BADGE_REASON_TEXT = (COLOR_ROJO_PRINCIPAL, COLOR_BLANCO)
BADGE_STATUS_COLORS = {
    "open": {"bg": ("#ECFDF5", "#064E3B"), "text": ("#047857", "#D1FAE5")},
    "pending": {"bg": ("#FEF3C7", "#7C2D12"), "text": ("#B45309", "#FDE68A")},
    "closed": {"bg": ("#E2E8F0", "#2D3748"), "text": ("#4A5568", "#E2E8F0")},
}
SUPPORT_AGENT_NAME = "Equipo EncryptU"


class MainView(ctk.CTkFrame):
    """
    Vista principal con navegacion moderna, tarjetas tematicas y gradientes
    acorde a la identidad visual de EncryptU.
    """

    def __init__(self, master, controller, username):
        super().__init__(master)
        self.controller = controller
        self.username = username
        self.configure(fg_color="transparent")

        self.original_bg_image: Optional[Image.Image] = None
        self.bg_image_object: Optional[ctk.CTkImage] = None
        self.bg_label: Optional[ctk.CTkLabel] = None

        self.support_tickets: List[Dict[str, Any]] = []
        self.support_ticket_messages: Dict[int, List[Dict[str, Any]]] = {}
        self.support_loading = False
        self.support_active_ticket_id: Optional[int] = None

        self.password_count_var = ctk.StringVar(value="--")
        self.profile_ticket_metric_var = ctk.StringVar(value="0")
        self.profile_last_sync_var = ctk.StringVar(value=datetime.now().strftime("%d/%m/%Y %H:%M"))
        self.support_list_count_var = ctk.StringVar(
            value="Cargando tickets..."
        )
        self.ticket_search_var = ctk.StringVar(value="")
        self.support_chat_title_var = ctk.StringVar(value="Selecciona un ticket para ver los detalles.")
        self.support_chat_meta_var = ctk.StringVar(value="")
        self.support_status_var = ctk.StringVar(value="")

        self.nav_segmented: Optional[ctk.CTkSegmentedButton] = None
        self.nav_map = {"Perfil": "profile", "Encriptacion": "encryption", "Soporte": "support"}
        self.sections: Dict[str, ctk.CTkFrame] = {}
        self.content_container: Optional[ctk.CTkFrame] = None
        self.scrollable_frame: Optional[ctk.CTkScrollableFrame] = None
        self.status_label_save: Optional[ctk.CTkLabel] = None
        self.support_ticket_list_container: Optional[ctk.CTkScrollableFrame] = None
        self.support_messages_container: Optional[ctk.CTkScrollableFrame] = None
        self.support_badge_holder: Optional[ctk.CTkFrame] = None
        self.support_message_input: Optional[ctk.CTkTextbox] = None
        self.support_send_button: Optional[ctk.CTkButton] = None
        self.support_status_label: Optional[ctk.CTkLabel] = None

        self.site_entry: Optional[ctk.CTkEntry] = None
        self.username_entry_save: Optional[ctk.CTkEntry] = None
        self.password_entry: Optional[ctk.CTkEntry] = None
        self.save_button: Optional[ctk.CTkButton] = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._setup_background_image()
        self._create_header()
        self._create_navigation()
        self._build_content_area()

        self.ticket_search_var.trace_add("write", lambda *_: self._render_support_ticket_list())

        self.support_loading = True
        self._render_support_ticket_list()
        self.after(150, self._initialize_support_data)

        if self.nav_segmented:
            self.nav_segmented.set("Encriptacion")
        self._show_section("encryption")
        self.refresh_password_list()

    # ------------------------------------------------------------------
    # Fondo y ambientacion visual
    # ------------------------------------------------------------------
    def _setup_background_image(self):
        try:
            self.original_bg_image = self._generate_gradient_image(1600, 900)
            self.bg_label = ctk.CTkLabel(self, text="", fg_color="transparent")
            self.bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.bg_label.lower()
            self.bind("<Configure>", self._resize_image)
            self.after(20, self._resize_image)
        except Exception as exc:
            print(f"Error al crear el fondo degradado: {exc}")

    def _generate_gradient_image(self, width: int, height: int) -> Image.Image:
        size = max(width, height) * 2
        gradient = Image.linear_gradient("L").resize((size, size))
        gradient = gradient.rotate(45, expand=True)
        x_offset = (gradient.width - width) // 2
        y_offset = (gradient.height - height) // 2
        mask = gradient.crop((x_offset, y_offset, x_offset + width, y_offset + height))
        base = Image.new("RGB", (width, height), COLOR_ROJO_PRINCIPAL)
        top = Image.new("RGB", (width, height), COLOR_BLANCO)
        return Image.composite(top, base, mask)

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
    # Cabecera y navegacion
    # ------------------------------------------------------------------
    def _create_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=24, pady=(24, 16), sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)

        brand_badge = ctk.CTkLabel(
            header_frame,
            text="EncryptU Desktop",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=(COLOR_ROJO_PRINCIPAL, COLOR_ROJO_HOVER),
            text_color=(COLOR_BLANCO, COLOR_BLANCO),
            corner_radius=12,
            padx=14,
            pady=6,
        )
        brand_badge.grid(row=0, column=0, rowspan=2, sticky="nw")

        welcome_label = ctk.CTkLabel(
            header_frame,
            text=f"Hola, {self.username}",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=TEXT_COLOR_PRIMARY,
        )
        welcome_label.grid(row=0, column=1, sticky="w", padx=(18, 0))

        subtitle = ctk.CTkLabel(
            header_frame,
            text="Gestiona tu perfil, tus contrasenas cifradas y los tickets de soporte aqui mismo.",
            font=ctk.CTkFont(size=14),
            text_color=TEXT_COLOR_SECONDARY,
        )
        subtitle.grid(row=1, column=1, sticky="w", padx=(18, 0), pady=(6, 0))

        logout_button = ctk.CTkButton(
            header_frame,
            text="Cerrar Sesion",
            command=self.logout_action,
            fg_color=COLOR_ROJO_PRINCIPAL,
            hover_color=COLOR_ROJO_HOVER,
            height=42,
            corner_radius=14,
        )
        logout_button.grid(row=0, column=2, rowspan=2, sticky="e")

    def _create_navigation(self):
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.grid(row=1, column=0, padx=24, pady=(0, 18), sticky="ew")
        nav_frame.grid_columnconfigure(0, weight=1)

        nav_caption = ctk.CTkLabel(
            nav_frame,
            text="Panel principal",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_COLOR_MUTED,
        )
        nav_caption.grid(row=0, column=0, sticky="w")

        self.nav_segmented = ctk.CTkSegmentedButton(
            nav_frame,
            values=list(self.nav_map.keys()),
            command=self._on_nav_change,
            corner_radius=18,
            selected_color=COLOR_ROJO_PRINCIPAL,
            selected_hover_color=COLOR_ROJO_HOVER,
            unselected_color=COLOR_FONDO_CARD,
            unselected_hover_color=COLOR_FONDO_CARD_ALT,
            text_color=(TEXT_COLOR_PRIMARY[0], TEXT_COLOR_PRIMARY[1]),
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.nav_segmented.grid(row=1, column=0, sticky="ew", pady=(8, 0))

    def _on_nav_change(self, value: str):
        section = self.nav_map.get(value)
        if section:
            self._show_section(section)

    # ------------------------------------------------------------------
    # Secciones principales
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

        hero_card = ctk.CTkFrame(
            frame,
            fg_color=COLOR_FONDO_CARD,
            corner_radius=24,
            border_width=1,
            border_color=COLOR_DIVIDER_LIGHT,
        )
        hero_card.pack(fill="x", padx=8, pady=(0, 24))
        hero_card.grid_columnconfigure(0, weight=1)

        headline = ctk.CTkLabel(
            hero_card,
            text="Tu panel personal seguro",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT_COLOR_PRIMARY,
        )
        headline.grid(row=0, column=0, sticky="w", padx=24, pady=(24, 4))

        tagline = ctk.CTkLabel(
            hero_card,
            text="Controla tus credenciales cifradas y mantente al dia con las solicitudes de soporte.",
            font=ctk.CTkFont(size=14),
            text_color=TEXT_COLOR_SECONDARY,
        )
        tagline.grid(row=1, column=0, sticky="w", padx=24)

        button_row = ctk.CTkFrame(hero_card, fg_color="transparent")
        button_row.grid(row=2, column=0, sticky="w", padx=24, pady=(18, 24))

        goto_vault = ctk.CTkButton(
            button_row,
            text="Ir a contrasenas guardadas",
            command=lambda: self._navigate_to("encryption"),
            fg_color=COLOR_ROJO_PRINCIPAL,
            hover_color=COLOR_ROJO_HOVER,
            height=40,
            corner_radius=14,
        )
        goto_vault.pack(side="left")

        goto_support = ctk.CTkButton(
            button_row,
            text="Ver soporte",
            command=lambda: self._navigate_to("support"),
            fg_color="transparent",
            hover_color=COLOR_ROJO_ACENTO,
            border_width=1,
            border_color=COLOR_ROJO_PRINCIPAL,
            text_color=(COLOR_ROJO_PRINCIPAL, COLOR_ROJO_ACENTO),
            height=40,
            corner_radius=14,
            width=160,
        )
        goto_support.pack(side="left", padx=(12, 0))

        stats_wrapper = ctk.CTkFrame(frame, fg_color="transparent")
        stats_wrapper.pack(fill="both", expand=True, padx=8, pady=(0, 12))
        stats_wrapper.grid_columnconfigure((0, 1, 2), weight=1, uniform="stats")

        vault_stat = ctk.CTkFrame(
            stats_wrapper,
            fg_color=COLOR_FONDO_CARD_ALT,
            corner_radius=20,
            border_width=1,
            border_color=COLOR_DIVIDER_LIGHT,
        )
        vault_stat.grid(row=0, column=0, padx=8, pady=0, sticky="nsew")

        ctk.CTkLabel(
            vault_stat,
            text="Contrasenas cifradas",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_COLOR_MUTED,
        ).pack(anchor="w", padx=20, pady=(20, 8))

        ctk.CTkLabel(
            vault_stat,
            textvariable=self.password_count_var,
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color=TEXT_COLOR_PRIMARY,
        ).pack(anchor="w", padx=20)

        support_stat = ctk.CTkFrame(
            stats_wrapper,
            fg_color=COLOR_FONDO_CARD_ALT,
            corner_radius=20,
            border_width=1,
            border_color=COLOR_DIVIDER_LIGHT,
        )
        support_stat.grid(row=0, column=1, padx=8, sticky="nsew")

        ctk.CTkLabel(
            support_stat,
            text="Tickets en seguimiento",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_COLOR_MUTED,
        ).pack(anchor="w", padx=20, pady=(20, 8))

        ctk.CTkLabel(
            support_stat,
            textvariable=self.profile_ticket_metric_var,
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color=TEXT_COLOR_PRIMARY,
        ).pack(anchor="w", padx=20)

        sync_stat = ctk.CTkFrame(
            stats_wrapper,
            fg_color=COLOR_FONDO_CARD_ALT,
            corner_radius=20,
            border_width=1,
            border_color=COLOR_DIVIDER_LIGHT,
        )
        sync_stat.grid(row=0, column=2, padx=8, sticky="nsew")

        ctk.CTkLabel(
            sync_stat,
            text="Ultima sincronizacion",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_COLOR_MUTED,
        ).pack(anchor="w", padx=20, pady=(20, 8))

        ctk.CTkLabel(
            sync_stat,
            textvariable=self.profile_last_sync_var,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT_COLOR_PRIMARY,
        ).pack(anchor="w", padx=20)

        return frame

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
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=TEXT_COLOR_PRIMARY,
        ).grid(row=0, column=0, sticky="w", padx=24, pady=(24, 6))

        ctk.CTkLabel(
            form_card,
            text="Usamos cifrado avanzado con tu clave maestra. Completa la informacion para registrarla.",
            font=ctk.CTkFont(size=14),
            text_color=TEXT_COLOR_SECONDARY,
            wraplength=380,
            justify="left",
        ).grid(row=1, column=0, sticky="w", padx=24, pady=(0, 18))

        self.site_entry = ctk.CTkEntry(
            form_card,
            placeholder_text="Sitio o servicio (ej. encryptu.com)",
            height=44,
            corner_radius=12,
        )
        self.site_entry.grid(row=2, column=0, sticky="ew", padx=24, pady=6)

        self.username_entry_save = ctk.CTkEntry(
            form_card,
            placeholder_text="Usuario asociado",
            height=44,
            corner_radius=12,
        )
        self.username_entry_save.grid(row=3, column=0, sticky="ew", padx=24, pady=6)

        self.password_entry = ctk.CTkEntry(
            form_card,
            placeholder_text="Contrasena a cifrar",
            show="*",
            height=44,
            corner_radius=12,
        )
        self.password_entry.grid(row=4, column=0, sticky="ew", padx=24, pady=6)

        self.save_button = ctk.CTkButton(
            form_card,
            text="Guardar de forma segura",
            command=self.save_action,
            fg_color=COLOR_ROJO_PRINCIPAL,
            hover_color=COLOR_ROJO_HOVER,
            height=44,
            corner_radius=14,
        )
        self.save_button.grid(row=5, column=0, sticky="ew", padx=24, pady=(18, 8))

        self.status_label_save = ctk.CTkLabel(
            form_card,
            text="",
            font=ctk.CTkFont(size=12),
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
            text="Vault de contrasenas",
            font=ctk.CTkFont(size=20, weight="bold"),
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
        )
        refresh_button.grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(
            list_card,
            text="Gestiona, visualiza y copia credenciales bajo demanda.",
            font=ctk.CTkFont(size=14),
            text_color=TEXT_COLOR_SECONDARY,
        ).grid(row=1, column=0, sticky="w", padx=24, pady=(8, 12))

        self.scrollable_frame = ctk.CTkScrollableFrame(list_card, fg_color="transparent")
        self.scrollable_frame.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 12))

        ctk.CTkLabel(
            list_card,
            text="Selecciona Ver / Copiar para desencriptar usando tu clave maestra.",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_COLOR_MUTED,
        ).grid(row=3, column=0, sticky="w", padx=24, pady=(0, 24))

        return frame

    def _build_support_section(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=2)
        frame.grid_rowconfigure(0, weight=1)

        tickets_panel = ctk.CTkFrame(
            frame,
            fg_color=COLOR_FONDO_CARD,
            corner_radius=24,
            border_width=1,
            border_color=COLOR_DIVIDER_LIGHT,
        )
        tickets_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=8)
        tickets_panel.grid_rowconfigure(4, weight=1)
        tickets_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tickets_panel,
            text="Tickets de soporte",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=TEXT_COLOR_PRIMARY,
        ).grid(row=0, column=0, sticky="w", padx=24, pady=(24, 6))

        ctk.CTkLabel(
            tickets_panel,
            text="Sincronizado con la mesa de ayuda de EncryptU.",
            font=ctk.CTkFont(size=14),
            text_color=TEXT_COLOR_SECONDARY,
        ).grid(row=1, column=0, sticky="w", padx=24)

        search_entry = ctk.CTkEntry(
            tickets_panel,
            placeholder_text="Buscar por id, nombre o correo...",
            textvariable=self.ticket_search_var,
            height=40,
            corner_radius=14,
        )
        search_entry.grid(row=2, column=0, sticky="ew", padx=24, pady=(18, 12))

        ctk.CTkLabel(
            tickets_panel,
            textvariable=self.support_list_count_var,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_COLOR_MUTED,
        ).grid(row=3, column=0, sticky="w", padx=24, pady=(0, 8))

        self.support_ticket_list_container = ctk.CTkScrollableFrame(
            tickets_panel, fg_color="transparent"
        )
        self.support_ticket_list_container.grid(row=4, column=0, sticky="nsew", padx=16, pady=(0, 20))

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
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT_COLOR_PRIMARY,
        ).grid(row=0, column=0, sticky="w")

        self.support_badge_holder = ctk.CTkFrame(header, fg_color="transparent")
        self.support_badge_holder.grid(row=0, column=1, sticky="e", padx=(12, 0))

        ctk.CTkLabel(
            header,
            textvariable=self.support_chat_meta_var,
            font=ctk.CTkFont(size=12),
            text_color=TEXT_COLOR_MUTED,
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))

        self.support_messages_container = ctk.CTkScrollableFrame(
            chat_panel, fg_color="transparent"
        )
        self.support_messages_container.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 12))

        composer = ctk.CTkFrame(chat_panel, fg_color="transparent")
        composer.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 24))
        composer.grid_columnconfigure(0, weight=1)

        self.support_message_input = ctk.CTkTextbox(composer, height=80, corner_radius=14)
        self.support_message_input.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.support_message_input.bind("<Control-Return>", self._send_support_message)
        self.support_message_input.bind("<Command-Return>", self._send_support_message)

        self.support_status_label = ctk.CTkLabel(
            composer,
            textvariable=self.support_status_var,
            font=ctk.CTkFont(size=11),
            text_color=TEXT_COLOR_MUTED,
        )
        self.support_status_label.grid(row=1, column=0, sticky="w", pady=(6, 0))

        self.support_send_button = ctk.CTkButton(
            composer,
            text="Enviar respuesta",
            command=self._send_support_message,
            fg_color=COLOR_ROJO_PRINCIPAL,
            hover_color=COLOR_ROJO_HOVER,
            height=42,
            corner_radius=14,
        )
        self.support_send_button.grid(row=1, column=1, sticky="e", padx=(12, 0), pady=(6, 0))

        return frame

    def _initialize_support_data(self):
        self._load_support_tickets(force_refresh=True)

    # ------------------------------------------------------------------
    # Support hub helpers
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
                text_color=TEXT_COLOR_MUTED,
                wraplength=240,
                justify="center",
            ).pack(fill="x", padx=12, pady=32)
            return

        if query and not tickets:
            ctk.CTkLabel(
                self.support_ticket_list_container,
                text="Sin resultados para tu busqueda.",
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
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=title_color,
                anchor="w",
            )
            title.pack(fill="x", padx=16, pady=(14, 4))
            self._bind_card_click(title, ticket["id"])

            meta = ctk.CTkLabel(
                card,
                text=f"{email} - {reason} - {status}",
                font=ctk.CTkFont(size=12),
                text_color=meta_color,
                anchor="w",
            )
            meta.pack(fill="x", padx=16, pady=(0, 14))
            self._bind_card_click(meta, ticket["id"])

    def _bind_card_click(self, widget, ticket_id: int):
        widget.bind("<Button-1>", lambda _event, tid=ticket_id: self._handle_select_ticket(tid))

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
            font=ctk.CTkFont(size=11, weight="bold"),
            padx=10,
            pady=4,
        )

    def _render_support_messages(self, ticket: Optional[Dict[str, Any]]):
        if not self.support_messages_container:
            return

        for widget in self.support_messages_container.winfo_children():
            widget.destroy()

        if not ticket:
            ctk.CTkLabel(
                self.support_messages_container,
                text="Selecciona un ticket para iniciar la conversacion.",
                text_color=TEXT_COLOR_MUTED,
                wraplength=420,
                justify="center",
            ).pack(fill="both", expand=True, padx=20, pady=60)
            return

        messages = ticket.get("messages") or []
        if not messages:
            ctk.CTkLabel(
                self.support_messages_container,
                text="Aun no hay mensajes registrados en este ticket.",
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
                font=ctk.CTkFont(size=11),
                text_color=header_color,
                anchor="w",
                justify="left",
            ).pack(fill="x", padx=14, pady=(10, 4))

            body_color = (COLOR_BLANCO, COLOR_BLANCO) if is_agent else TEXT_COLOR_PRIMARY
            ctk.CTkLabel(
                inner,
                text=message.get("body") or "",
                font=ctk.CTkFont(size=13),
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
            self._set_support_status("Selecciona un ticket antes de responder.", error=True)
            return "break" if event else None
        if not message:
            self._set_support_status("Escribe un mensaje para el cliente.", error=True)
            return "break" if event else None

        ticket_id = self.support_active_ticket_id
        ticket = self._get_support_ticket(ticket_id) if ticket_id is not None else None
        if not ticket_id or not ticket:
            self._set_support_status("El ticket seleccionado ya no existe.", error=True)
            return "break" if event else None

        send_button.configure(state="disabled")
        self._set_support_status("Enviando respuesta...", success=False)

        success = self.controller.handle_send_support_message(ticket_id, message)

        if success:
            message_input.delete("0.0", "end")
            self._load_ticket_messages(ticket_id, force_refresh=True, notify=False)
            self._load_support_tickets(force_refresh=True)
            self._set_support_status("Mensaje enviado y sincronizado.", success=True)
        else:
            self._set_support_status(
                "No se pudo enviar el mensaje. Intenta nuevamente.", error=True
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

    # ------------------------------------------------------------------
    # Vault actions and status helpers
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
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=TEXT_COLOR_PRIMARY,
            ).pack(anchor="w")

            ctk.CTkLabel(
                info,
                text=username_site,
                font=ctk.CTkFont(size=12),
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
            )
            view_button.pack(anchor="e")

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
            )
            delete_button.pack(anchor="e", pady=(8, 0))

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
        toplevel_window = self.winfo_toplevel()
        if isinstance(toplevel_window, ctk.CTk):
            popup = ctk.CTkToplevel(toplevel_window)
            popup.geometry("320x120")
            popup.title("Notificacion")
            popup.transient(toplevel_window)
            popup.grab_set()

            ctk.CTkLabel(
                popup,
                text=message,
                font=ctk.CTkFont(size=14),
                text_color=color,
                wraplength=280,
                justify="center",
            ).pack(expand=True, padx=20, pady=24)

            popup.after(2000, popup.destroy)

