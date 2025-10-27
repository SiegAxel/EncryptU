# desktop/controllers/views/profile_view.py
import customtkinter as ctk
from datetime import datetime
from typing import Any, Dict, List, Optional

from PIL import Image

try:
    import pywinstyles  # type: ignore
except ImportError:
    pywinstyles = None  # type: ignore

COLOR_BACKGROUND = "#050030"

# Paleta hero (zona superior)
COLOR_TOP_CARD = "#FFFFFF"
COLOR_TOP_CARD_LIGHT = "#EBEBEB"
COLOR_TOP_BORDER = "#3C3D4D"

# Paleta secciones inferiores
COLOR_BOTTOM_CARD = "#FFFFFF"
COLOR_BOTTOM_BORDER = "#F3BABA"
COLOR_BOTTOM_SOFT = "#FFF1F2"

# Paleta de texto (tonalidades rojas)
COLOR_TEXT_PRIMARY = "#B91C1C"
COLOR_TEXT_SECONDARY = "#DC2626"
COLOR_TEXT_MUTED = "#F76A6A"
COLOR_TEXT_LIGHT = "#FECACA"

# Accentos/estados
COLOR_ACCENT = "#F43F5E"
COLOR_ACCENT_DARK = "#DC1F45"
COLOR_PRIMARY = "#DC2626"
COLOR_PRIMARY_DARK = "#B91C1C"

# Colores de texto para cards top (glass effect)
COLOR_TOP_TEXT_PRIMARY = "#FF0000"
COLOR_TOP_TEXT_MUTED = "#FD2F2F"

GRADIENT_PATH = "desktop/controllers/img/bannerEncryptU.png"
HERO_HEIGHT = 300


from .base_view import BaseView


class ProfileView(BaseView):
    """Vista estilizada para gestionar el perfil del usuario en EncryptU."""

    def __init__(self, master, controller, username: str):
        super().__init__(master, fg_color=COLOR_BACKGROUND)
        self.controller = controller
        self.username = username or "Usuario"
        self.display_name = self._format_username(self.username)
        self.last_sync = datetime.now().strftime("%d/%m/%Y %H:%M")

        self.fonts = self._build_fonts()
        self.hero_source = self._load_gradient()
        self.hero_image: Optional[ctk.CTkImage] = None
        self.hero_label: Optional[ctk.CTkLabel] = None
        self._hero_image_ref: Optional[ctk.CTkImage] = None
        self.transparent_color = "#000001"
        self._transparent_widgets: List[Any] = []

        self.profile_stats = self._build_profile_stats()
        self.security_items = self._build_security_items()
        self.security_checklist = self._build_security_checklist()

        self._build_layout()
        self.bind("<Configure>", self._handle_resize)
        self.after(140, self._apply_transparencies)

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def _build_fonts(self) -> Dict[str, ctk.CTkFont]:
        return {
            "hero_title": ctk.CTkFont(family="Arial", size=52, weight="bold"),
            "hero_sub": ctk.CTkFont(family="Arial", size=20),
            "section": ctk.CTkFont(size=20, weight="bold"),
            "body": ctk.CTkFont(size=14),
            "muted": ctk.CTkFont(size=13),
            "badge": ctk.CTkFont(size=12, weight="bold"),
            "button": ctk.CTkFont(size=15, weight="bold"),
            "stat_value": ctk.CTkFont(size=24, weight="bold"),
            "stat_hint": ctk.CTkFont(size=12),
        }

    def _build_profile_stats(self) -> List[Dict[str, str]]:
        return [
            {"label": "Estado", "value": "Activo", "hint": "Sesion verificada en este equipo"},
            {"label": "Ultima sincronizacion", "value": self.last_sync, "hint": "Hora local al abrir la vista"},
            {"label": "Identificador", "value": self._user_initials(self.username), "hint": "Iniciales generadas automaticamente"},
        ]

    def _build_security_items(self) -> List[Dict[str, str]]:
        return [
            {
                "title": "Respaldo cifrado",
                "description": (
                    "Tus credenciales se resguardan con cifrado AES-256 y derivacion PBKDF2. "
                    "La clave maestra nunca abandona tu dispositivo."
                ),
            },
            {
                "title": "Gestion de sesiones",
                "description": "Controla y cierra sesiones remotas desde la boveda para evitar accesos no autorizados.",
            },
            {
                "title": "Buenas practicas",
                "description": (
                    "Anade notas seguras, actualiza contrasenas periodicamente y utiliza 2FA en servicios criticos."
                ),
            },
        ]

    def _build_security_checklist(self) -> List[str]:
        return [
            "Actualiza tu clave maestra con un patron facil de recordar pero complejo de adivinar.",
            "Activa 2FA en los servicios que guardas dentro de EncryptU.",
            "Revisa las alertas de actividad inusual en la seccion de soporte.",
        ]

    def _build_layout(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_hero()
        self._build_body()

    def _build_hero(self):
        hero = ctk.CTkFrame(self, fg_color=COLOR_TOP_CARD)
        hero.grid(row=0, column=0, sticky="nsew")
        hero.grid_propagate(False)
        hero.configure(height=HERO_HEIGHT)

        initial_width = max(self.winfo_toplevel().winfo_width() or 1024, 1024)
        img_ratio = self.hero_source.width / self.hero_source.height
        if HERO_HEIGHT > 0:
            window_ratio = initial_width / HERO_HEIGHT
        else:
            window_ratio = img_ratio

        if window_ratio > img_ratio:
            target_width = int(initial_width * 1.1)
            target_height = int(target_width / img_ratio)
        else:
            target_height = HERO_HEIGHT
            target_width = int(target_height * img_ratio)
            if target_width < initial_width:
                target_width = initial_width

        self.hero_image = ctk.CTkImage(
            light_image=self.hero_source,
            dark_image=self.hero_source,
            size=(target_width, target_height),
        )
        self.hero_label = ctk.CTkLabel(hero, text="", image=self.hero_image, fg_color=self.transparent_color)
        self.hero_label.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)
        self._hero_image_ref = self.hero_image
        self._make_transparent(self.hero_label)

        content = ctk.CTkFrame(hero, fg_color=self.transparent_color)
        content.pack(expand=True, fill="both", padx=36, pady=28)
        content.lift()  # Ensure interactive widgets stay above the background image
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)
        self._make_transparent(content)

        self.back_button = ctk.CTkButton(
            content,
            text="Volver al inicio",
            command=self._go_home,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_DARK,
            text_color="#FEF2F2",
            font=self.fonts["button"],
            corner_radius=20,
            border_width=1,
            border_color=COLOR_BOTTOM_BORDER,
            height=42,
            width=180,
        )
        self.back_button.grid(row=0, column=0, sticky="w", pady=(0, 12))
        self.back_button.lift()

        glass_wrapper = ctk.CTkFrame(content, fg_color=self.transparent_color)
        glass_wrapper.grid(row=1, column=0, sticky="nsew")
        glass_wrapper.grid_columnconfigure(0, weight=1)
        glass_wrapper.grid_rowconfigure(0, weight=1)
        self._make_transparent(glass_wrapper)

        glass_body = ctk.CTkFrame(
            glass_wrapper,
            fg_color=COLOR_TOP_CARD,
            corner_radius=30,
            border_width=1,
            border_color=COLOR_TOP_BORDER,
        )
        glass_body.grid(row=0, column=0, sticky="nsew")
        glass_body.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            glass_body,
            text=f"Hola, {self.display_name}",
            font=self.fonts["hero_title"],
            text_color=COLOR_TOP_TEXT_PRIMARY,
            fg_color="transparent",
        )
        title.grid(row=0, column=0, sticky="w", padx=28, pady=(24, 6))

        subtitle = ctk.CTkLabel(
            glass_body,
            text="Administra tu identidad digital, tu suscripcion y la seguridad de tu boveda.",
            font=self.fonts["hero_sub"],
            text_color=COLOR_TOP_TEXT_MUTED,
            wraplength=760,
            justify="left",
            fg_color="transparent",
        )
        subtitle.grid(row=1, column=0, sticky="w", padx=28)

        stats_row = ctk.CTkFrame(
            glass_body,
            fg_color=COLOR_TOP_CARD,
            corner_radius=22,
            border_width=1,
            border_color=COLOR_TOP_BORDER,
        )
        stats_row.grid(row=2, column=0, sticky="ew", padx=24, pady=(28, 24))
        stats_row.grid_columnconfigure(tuple(range(len(self.profile_stats))), weight=1)

        for idx, stat in enumerate(self.profile_stats):
            stat_card = ctk.CTkFrame(
                stats_row,
                fg_color=COLOR_TOP_CARD_LIGHT,
                corner_radius=18,
                border_width=1,
                border_color=COLOR_TOP_BORDER,
            )
            stat_card.grid(row=0, column=idx, sticky="nsew", padx=(0, 18) if idx < len(self.profile_stats) - 1 else 0)

            value_label = ctk.CTkLabel(
                stat_card,
                text=stat["value"],
                font=self.fonts["stat_value"],
                text_color=COLOR_TEXT_PRIMARY,
                fg_color="transparent",
            )
            value_label.grid(row=0, column=0, sticky="w", padx=20, pady=(18, 6))

            hint_label = ctk.CTkLabel(
                stat_card,
                text=stat["label"],
                font=self.fonts["muted"],
                text_color=COLOR_TEXT_LIGHT,
                fg_color="transparent",
            )
            hint_label.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 12))

            note_label = ctk.CTkLabel(
                stat_card,
                text=stat["hint"],
                font=self.fonts["stat_hint"],
                text_color=COLOR_TEXT_MUTED,
                wraplength=220,
                justify="left",
                fg_color="transparent",
            )
            note_label.grid(row=2, column=0, sticky="w", padx=20, pady=(0, 18))

    # ------------------------------------------------------------------
    # Cuerpo (sin cambios respecto a la versión anterior)
    # ------------------------------------------------------------------
    def _build_body(self):
        body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=36, pady=(0, 36))
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)

        primary = ctk.CTkFrame(body, fg_color="transparent")
        primary.grid(row=0, column=0, sticky="nsew", padx=(0, 24))
        primary.grid_columnconfigure(0, weight=1)

        secondary = ctk.CTkFrame(body, fg_color="transparent")
        secondary.grid(row=0, column=1, sticky="nsew")
        secondary.grid_columnconfigure(0, weight=1)

        self._build_primary_column(primary)
        self._build_secondary_column(secondary)

    def _build_primary_column(self, parent: ctk.CTkFrame):
        overview_card = self._create_card(parent, "Resumen de cuenta", row=0)
        self._populate_overview_card(overview_card)

        security_card = self._create_card(parent, "Seguridad y privacidad", row=1, pady=(24, 0))
        self._populate_security_card(security_card)

    def _build_secondary_column(self, parent: ctk.CTkFrame):
        subscription_card = self._create_card(parent, "Suscripcion y plan", row=0)
        self._populate_subscription_card(subscription_card)

        quick_actions_card = self._create_card(parent, "Accesos rapidos", row=1, pady=(24, 0))
        self._populate_quick_actions_card(quick_actions_card)

        checklist_card = self._create_card(parent, "Checklist de seguridad", row=2, pady=(24, 0))
        self._populate_checklist_card(checklist_card)

    def _create_card(
        self,
        parent: ctk.CTkFrame,
        title: Optional[str],
        row: int,
        column: int = 0,
        pady: tuple[int, int] = (0, 0),
    ) -> ctk.CTkFrame:
        card = ctk.CTkFrame(
            parent,
            fg_color=COLOR_BOTTOM_CARD,
            corner_radius=28,
            border_width=1,
            border_color=COLOR_BOTTOM_BORDER,
        )
        card.grid(row=row, column=column, sticky="nsew", pady=pady)
        card.grid_columnconfigure(0, weight=1)
        if title:
            header = ctk.CTkLabel(
                card,
                text=title,
                font=self.fonts["section"],
                text_color=COLOR_TEXT_PRIMARY,
                fg_color="transparent",
            )
            header.grid(row=0, column=0, sticky="w", padx=24, pady=(24, 10))
        return card

    def _populate_overview_card(self, card: ctk.CTkFrame):
        info_row = ctk.CTkFrame(card, fg_color="transparent")
        info_row.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 20))
        info_row.grid_columnconfigure(1, weight=1)

        avatar = ctk.CTkFrame(
            info_row,
            fg_color=COLOR_BOTTOM_SOFT,
            width=90,
            height=90,
            corner_radius=45,
            border_width=1,
            border_color=COLOR_TEXT_PRIMARY,
        )
        avatar.grid(row=0, column=0, sticky="w")
        avatar.grid_propagate(False)

        initials = ctk.CTkLabel(
            avatar,
            text=self._user_initials(self.username),
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
            fg_color="transparent",
        )
        initials.place(relx=0.5, rely=0.5, anchor="center")

        text_block = ctk.CTkFrame(info_row, fg_color="transparent")
        text_block.grid(row=0, column=1, sticky="w", padx=(18, 0))
        text_block.grid_columnconfigure(0, weight=1)

        name_label = ctk.CTkLabel(
            text_block,
            text=self.display_name,
            font=self.fonts["section"],
            text_color=COLOR_TEXT_PRIMARY,
            fg_color="transparent",
        )
        name_label.grid(row=0, column=0, sticky="w")

        email_label = ctk.CTkLabel(
            text_block,
            text=self.username,
            font=self.fonts["muted"],
            text_color=COLOR_TEXT_SECONDARY,
            fg_color="transparent",
        )
        email_label.grid(row=1, column=0, sticky="w", pady=(2, 10))

        badge = ctk.CTkFrame(
            text_block,
            fg_color=COLOR_BOTTOM_SOFT,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_TEXT_PRIMARY,
        )
        badge.grid(row=2, column=0, sticky="w")
        ctk.CTkLabel(
            badge,
            text="Cuenta segura",
            font=self.fonts["badge"],
            text_color=COLOR_TEXT_PRIMARY,
            fg_color="transparent",
        ).pack(padx=12, pady=6)

        divider = ctk.CTkFrame(card, fg_color=COLOR_BOTTOM_BORDER, height=2)
        divider.grid(row=2, column=0, sticky="ew", padx=24)

        details = [
            ("Nombre visible", self.display_name),
            ("Identificador de inicio de sesion", self.username),
            ("Modo de cifrado", "AES-256 + PBKDF2"),
        ]

        details_frame = ctk.CTkFrame(card, fg_color="transparent")
        details_frame.grid(row=3, column=0, sticky="ew", padx=24, pady=(16, 0))
        details_frame.grid_columnconfigure(1, weight=1)

        for idx, (label, value) in enumerate(details):
            row = ctk.CTkFrame(details_frame, fg_color="transparent")
            row.grid(row=idx, column=0, sticky="ew", pady=(0, 10))
            row.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                row,
                text=label,
                font=self.fonts["muted"],
                text_color=COLOR_TEXT_SECONDARY,
                fg_color="transparent",
            ).grid(row=0, column=0, sticky="w")

            ctk.CTkLabel(
                row,
                text=value,
                font=self.fonts["body"],
                text_color=COLOR_TEXT_PRIMARY,
                fg_color="transparent",
            ).grid(row=0, column=1, sticky="w")

        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.grid(row=4, column=0, sticky="ew", padx=24, pady=(20, 24))
        actions.grid_columnconfigure((0, 1), weight=1)

        cancel_button = ctk.CTkButton(
            actions,
            text="Cancelar suscripcion",
            command=lambda: self._show_notification(
                "Un asesor se pondra en contacto contigo para completar la cancelacion."
            ),
            fg_color=COLOR_BOTTOM_SOFT,
            hover_color="#FFE4E6",
            text_color=COLOR_TEXT_SECONDARY,
            font=self.fonts["button"],
            corner_radius=20,
            border_width=1,
            border_color=COLOR_TEXT_SECONDARY,
        )
        cancel_button.grid(row=0, column=0, sticky="ew", padx=(0, 12))

        logout_button = ctk.CTkButton(
            actions,
            text="Cerrar sesion",
            command=self.controller.handle_logout,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_DARK,
            text_color="#FEF2F2",
            font=self.fonts["button"],
            corner_radius=20,
        )
        logout_button.grid(row=0, column=1, sticky="ew")

    def _populate_security_card(self, card: ctk.CTkFrame):
        for idx, item in enumerate(self.security_items, start=1):
            feature = ctk.CTkFrame(
                card,
                fg_color=COLOR_BOTTOM_SOFT,
                corner_radius=18,
                border_width=1,
                border_color=COLOR_BOTTOM_BORDER,
            )
            feature.grid(row=idx, column=0, sticky="ew", padx=24, pady=(0, 16))

            title = ctk.CTkLabel(
                feature,
                text=item["title"],
                font=self.fonts["body"],
                text_color=COLOR_TEXT_PRIMARY,
                fg_color="transparent",
            )
            title.grid(row=0, column=0, sticky="w", padx=20, pady=(16, 4))

            description = ctk.CTkLabel(
                feature,
                text=item["description"],
                font=self.fonts["muted"],
                text_color=COLOR_TEXT_SECONDARY,
                wraplength=460,
                justify="left",
                fg_color="transparent",
            )
            description.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 16))

        manage_button = ctk.CTkButton(
            card,
            text="Administrar boveda",
            command=lambda: self.controller.show_vault_view(self.username),
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_DARK,
            text_color="#FEF2F2",
            font=self.fonts["button"],
            corner_radius=20,
        )
        manage_button.grid(row=len(self.security_items) + 1, column=0, sticky="ew", padx=24, pady=(0, 24))

    def _populate_subscription_card(self, card: ctk.CTkFrame):
        badge = ctk.CTkFrame(
            card,
            fg_color=COLOR_BOTTOM_SOFT,
            corner_radius=14,
            border_width=1,
            border_color=COLOR_PRIMARY,
        )
        badge.grid(row=1, column=0, sticky="w", padx=24, pady=(0, 16))
        ctk.CTkLabel(
            badge,
            text="Suscripcion activa",
            font=self.fonts["badge"],
            text_color=COLOR_PRIMARY,
            fg_color="transparent",
        ).pack(padx=12, pady=6)

        description = ctk.CTkLabel(
            card,
            text=(
                "Tu plan incluye almacenamiento cifrado, monitoreo basico de filtraciones "
                "y soporte prioritario. Cambia de plan o actualiza tus datos cuando lo necesites."
            ),
            font=self.fonts["body"],
            text_color=COLOR_TEXT_SECONDARY,
            wraplength=320,
            justify="left",
            fg_color="transparent",
        )
        description.grid(row=2, column=0, sticky="w", padx=24)

        progress_label = ctk.CTkLabel(
            card,
            text="Uso estimado de boveda",
            font=self.fonts["muted"],
            text_color=COLOR_TEXT_SECONDARY,
            fg_color="transparent",
        )
        progress_label.grid(row=3, column=0, sticky="w", padx=24, pady=(20, 6))

        progress = ctk.CTkProgressBar(
            card,
            fg_color=COLOR_BOTTOM_SOFT,
            progress_color=COLOR_PRIMARY,
            corner_radius=10,
            height=14,
        )
        progress.grid(row=4, column=0, sticky="ew", padx=24)
        progress.set(0.65)

        progress_hint = ctk.CTkLabel(
            card,
            text="65% de tus registros estan sincronizados en este dispositivo.",
            font=self.fonts["stat_hint"],
            text_color=COLOR_TEXT_MUTED,
            fg_color="transparent",
        )
        progress_hint.grid(row=5, column=0, sticky="w", padx=24, pady=(6, 20))

        manage_button = ctk.CTkButton(
            card,
            text="Actualizar plan",
            command=lambda: self._show_notification(
                "Gestiona cambios de plan escribiendo a soporte o desde el portal web."
            ),
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_DARK,
            text_color="#FEF2F2",
            font=self.fonts["button"],
            corner_radius=20,
        )
        manage_button.grid(row=6, column=0, sticky="ew", padx=24, pady=(0, 24))

    def _populate_quick_actions_card(self, card: ctk.CTkFrame):
        description = ctk.CTkLabel(
            card,
            text="Accede rapidamente a las secciones clave de EncryptU.",
            font=self.fonts["body"],
            text_color=COLOR_TEXT_SECONDARY,
            wraplength=320,
            justify="left",
            fg_color="transparent",
        )
        description.grid(row=1, column=0, sticky="w", padx=24, pady=(0, 20))

        buttons = ctk.CTkFrame(card, fg_color="transparent")
        buttons.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 24))
        buttons.grid_columnconfigure(0, weight=1)
        buttons.grid_columnconfigure(1, weight=1)

        vault_button = ctk.CTkButton(
            buttons,
            text="Boveda de contrasenas",
            command=lambda: self.controller.show_vault_view(self.username),
            fg_color=COLOR_BOTTOM_SOFT,
            hover_color="#FFE4E6",
            text_color=COLOR_TEXT_PRIMARY,
            font=self.fonts["button"],
            corner_radius=18,
        )
        vault_button.grid(row=0, column=0, sticky="ew", padx=(0, 12))

        support_button = ctk.CTkButton(
            buttons,
            text="Soporte prioritario",
            command=lambda: self.controller.show_support_view(self.username),
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_DARK,
            text_color="#FEF2F2",
            font=self.fonts["button"],
            corner_radius=18,
        )
        support_button.grid(row=0, column=1, sticky="ew")

    def _populate_checklist_card(self, card: ctk.CTkFrame):
        for idx, item in enumerate(self.security_checklist, start=1):
            row = ctk.CTkFrame(
                card,
                fg_color=COLOR_BOTTOM_SOFT,
                corner_radius=16,
                border_width=1,
                border_color=COLOR_BOTTOM_BORDER,
            )
            row.grid(row=idx, column=0, sticky="ew", padx=24, pady=(0, 12))
            row.grid_columnconfigure(1, weight=1)

            check = ctk.CTkLabel(
                row,
                text="✓",
                font=self.fonts["section"],
                text_color=COLOR_PRIMARY,
                fg_color="transparent",
            )
            check.grid(row=0, column=0, sticky="nw", padx=18, pady=14)

            text = ctk.CTkLabel(
                row,
                text=item,
                font=self.fonts["body"],
                text_color=COLOR_TEXT_PRIMARY,
                wraplength=280,
                justify="left",
                fg_color="transparent",
            )
            text.grid(row=0, column=1, sticky="w", padx=(0, 18), pady=14)

    # ------------------------------------------------------------------
    # Navegacion
    # ------------------------------------------------------------------
    def _go_home(self):
        controller = getattr(self, "controller", None)
        if controller is None or not hasattr(controller, "show_main_view"):
            self._show_notification("No se puede volver al inicio en este momento.")
            return

        username = getattr(controller, "current_username", None) or self.username
        try:
            controller.show_main_view(username)
        except Exception:
            self._show_notification("Ocurrio un error al volver al inicio.")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _make_transparent(self, widget: Any):
        if pywinstyles is None or widget is None:
            return
        if hasattr(widget, "configure") and hasattr(widget, "winfo_id"):
            try:
                widget.configure(bg_color=self.transparent_color)
                self._transparent_widgets.append(widget)
            except Exception:
                pass

    def _apply_transparencies(self):
        if pywinstyles is None:
            return
        for widget in list(self._transparent_widgets):
            if hasattr(widget, "winfo_id"):
                try:
                    pywinstyles.set_opacity(widget.winfo_id(), color=self.transparent_color)
                except Exception:
                    pass

    def _load_gradient(self) -> Image.Image:
        try:
            return Image.open(GRADIENT_PATH)
        except Exception:
            gradient = Image.new("RGB", (1200, HERO_HEIGHT), "#050030")
            overlay = Image.new("RGB", (1200, HERO_HEIGHT), "#1E1B54")
            mask = Image.new("L", (1, HERO_HEIGHT))
            for y in range(HERO_HEIGHT):
                mask.putpixel((0, y), int(255 * (y / max(HERO_HEIGHT - 1, 1))))
            mask = mask.resize((1200, HERO_HEIGHT))
            return Image.composite(overlay, gradient, mask)

    def _handle_resize(self, event):
        if event.widget is self and self.hero_label and self.hero_source:
            width = max(event.width, 1024)
            img_ratio = self.hero_source.width / self.hero_source.height
            window_ratio = width / HERO_HEIGHT if HERO_HEIGHT else img_ratio

            if window_ratio > img_ratio:
                new_width = int(width * 1.1)
                new_height = int(new_width / img_ratio)
            else:
                new_height = HERO_HEIGHT
                new_width = int(new_height * img_ratio)
                if new_width < width:
                    new_width = width

            self.hero_image = ctk.CTkImage(
                light_image=self.hero_source,
                dark_image=self.hero_source,
                size=(new_width, new_height),
            )
            self.hero_label.configure(image=self.hero_image)
            self._hero_image_ref = self.hero_image

    def _show_notification(self, message: str):
        toplevel = self.winfo_toplevel()
        if not isinstance(toplevel, ctk.CTk):
            return

        popup = ctk.CTkToplevel(toplevel)
        popup.title("EncryptU")
        popup.geometry("380x190")
        popup.resizable(False, False)
        popup.configure(fg_color=COLOR_BOTTOM_CARD)

        label = ctk.CTkLabel(
            popup,
            text=message,
            font=self.fonts["body"],
            text_color=COLOR_TEXT_PRIMARY,
            wraplength=320,
            justify="center",
            fg_color="transparent",
        )
        label.pack(expand=True, fill="both", padx=28, pady=(28, 12))

        popup.after(2600, popup.destroy)

    def _format_username(self, username: str) -> str:
        if "@" in username:
            username = username.split("@", 1)[0]
        return username.replace("_", " ").replace(".", " ").title()

    def _user_initials(self, username: str) -> str:
        if not username:
            return "EU"
        if "@" in username:
            username = username.split("@", 1)[0]
        parts = [part for part in username.replace("_", " ").replace(".", " ").split() if part]
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        return username[:2].upper()
