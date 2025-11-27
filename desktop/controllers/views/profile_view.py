import customtkinter as ctk
from datetime import datetime
from typing import Dict, List, Optional, Any

from PIL import Image

from desktop.controllers.views.base_view import BaseView

# ----------------------------------------------------------------------
# Paleta alineada con SupportView / VaultView
# ----------------------------------------------------------------------
COLOR_BACKGROUND = "#F4F6FB"
COLOR_CARD = "#FFFFFF"
COLOR_CARD_SOFT = "#FBFCFF"
COLOR_BORDER = "#E2E8F0"
COLOR_TEXT_PRIMARY = "#0F172A"
COLOR_TEXT_SECONDARY = "#1E293B"
COLOR_TEXT_MUTED = "#FF0000"
COLOR_ACCENT = "#EE5A72"
COLOR_ACCENT_DARK = "#D9435C"
COLOR_SUCCESS = "#16A34A"
COLOR_BADGE_BG = "#EEF2FF"
COLOR_AVATAR_BG = "#E0E7FF"

BLACK_LOGO_PATH = "desktop/controllers/img/Blacklogo.png"


class ProfileView(BaseView):
    """Vista de perfil con el mismo lenguaje visual que la vista de soporte."""

    def __init__(self, master, controller, username: str):
        super().__init__(master, fg_color=COLOR_BACKGROUND)
        self.controller = controller
        self.username = username or "Usuario"
        self.display_name = self._format_username(self.username)
        self.last_sync = datetime.now().strftime("%d/%m/%Y %H:%M")

        self.fonts = self._build_fonts()
        self.logo_image = self._load_logo_image()

        # Obtener información real de suscripción
        self.subscription_info = self._get_subscription_info()
        
        self.profile_stats = self._build_profile_stats()
        self.security_items = self._build_security_items()
        self.security_checklist = self._build_security_checklist()

        self._build_layout()

    # ------------------------------------------------------------------
    # Configuración base
    # ------------------------------------------------------------------
    def _build_fonts(self) -> Dict[str, ctk.CTkFont]:
        return {
            "hero_title": ctk.CTkFont(family="Arial", size=40, weight="bold"),
            "hero_sub": ctk.CTkFont(family="Arial", size=18),
            "section": ctk.CTkFont(size=20, weight="bold"),
            "card_title": ctk.CTkFont(size=16, weight="bold"),
            "body": ctk.CTkFont(size=14),
            "muted": ctk.CTkFont(size=13),
            "badge": ctk.CTkFont(size=12, weight="bold"),
            "button": ctk.CTkFont(size=15, weight="bold"),
            "stat_value": ctk.CTkFont(size=24, weight="bold"),
            "stat_hint": ctk.CTkFont(size=12),
        }

    def _build_profile_stats(self) -> List[Dict[str, str]]:
        return [
            {"label": "Estado", "value": "Activo", "hint": "Sesión verificada en este equipo"},
            {"label": "Última sincronización", "value": self.last_sync, "hint": "Horario local al abrir la vista"},
            {"label": "Identificador", "value": self._user_initials(self.username), "hint": "Iniciales generadas automáticamente"},
        ]

    def _build_security_items(self) -> List[Dict[str, str]]:
        return [
            {
                "title": "Respaldo cifrado",
                "description": (
                    "Tus credenciales se resguardan con cifrado AES‑256 y derivación PBKDF2. "
                    "La clave maestra nunca abandona tu dispositivo."
                ),
            },
            {
                "title": "Gestión de sesiones",
                "description": "Controla y cierra sesiones remotas desde la bóveda para evitar accesos no autorizados.",
            },
            {
                "title": "Buenas prácticas",
                "description": (
                    "Añade notas seguras, actualiza contraseñas periódicamente y utiliza 2FA en servicios críticos."
                ),
            },
        ]

    def _build_security_checklist(self) -> List[str]:
        return [
            "Actualiza tu clave maestra con un patrón fácil de recordar pero complejo de adivinar.",
            "Activa 2FA en los servicios que guardas dentro de EncryptU.",
            "Revisa las alertas de actividad inusual en la sección de soporte.",
        ]

    # ------------------------------------------------------------------
    # Layout principal
    # ------------------------------------------------------------------
    def _build_layout(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_body()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=COLOR_BACKGROUND)
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(20, 12))
        header.grid_columnconfigure(1, weight=1)
        header.grid_columnconfigure(2, weight=0)

        back_button = ctk.CTkButton(
            header,
            text="<",
            command=self._go_home,
            fg_color="transparent",
            hover_color="#6E0000",
            text_color=COLOR_ACCENT,
            font=self.fonts["button"],
            width=44,
            height=44,
            corner_radius=16,
            border_width=1,
            border_color=COLOR_ACCENT,
        )
        back_button.grid(row=0, column=0, rowspan=2, sticky="w")

        title_block = ctk.CTkFrame(header, fg_color="transparent")
        title_block.grid(row=0, column=1, sticky="w", padx=(16, 0))
        title_block.grid_columnconfigure(0, weight=1)

        badge = ctk.CTkLabel(title_block, text="Perfil · Desktop", font=self.fonts["muted"], text_color=COLOR_TEXT_MUTED)
        badge.grid(row=0, column=0, sticky="w")

        title = ctk.CTkLabel(
            title_block,
            text=f"Hola, {self.display_name}",
            font=self.fonts["hero_title"],
            text_color=COLOR_TEXT_PRIMARY,
        )
        title.grid(row=1, column=0, sticky="w")

        subtitle = ctk.CTkLabel(
            header,
            text="Gestiona tu identidad digital, suscripción y seguridad desde un solo lugar.",
            font=self.fonts["hero_sub"],
            text_color=COLOR_TEXT_MUTED,
        )
        subtitle.grid(row=1, column=1, sticky="w", padx=(16, 0))

        logo_label = ctk.CTkLabel(header, text="", image=self.logo_image)
        logo_label.grid(row=0, column=2, rowspan=2, sticky="e")
        self.register_drag_handle(header)

    def _build_body(self):
        wrapper = ctk.CTkFrame(self, fg_color=COLOR_BACKGROUND)
        wrapper.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        wrapper.grid_rowconfigure(0, weight=1)
        wrapper.grid_columnconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(wrapper, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        body = ctk.CTkFrame(scroll, fg_color=COLOR_CARD_SOFT, corner_radius=32)
        body.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        body.grid_columnconfigure(0, weight=48, minsize=520)
        body.grid_columnconfigure(1, weight=52, minsize=360)
        body.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(body, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(24, 12), pady=24)
        left.grid_columnconfigure(0, weight=1)

        right = ctk.CTkFrame(body, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(12, 24), pady=24)
        right.grid_columnconfigure(0, weight=1)

        self._build_identity_card(left)
        self._build_security_card(left)

        self._build_subscription_card(right)
        self._build_quick_actions_card(right)
        self._build_checklist_card(right)

    # ------------------------------------------------------------------
    # Tarjetas
    # ------------------------------------------------------------------
    def _create_card(self, parent: ctk.CTkFrame, title: str, row: int, pady: tuple[int, int] = (0, 0)) -> ctk.CTkFrame:
        card = ctk.CTkFrame(parent, fg_color=COLOR_CARD, corner_radius=24, border_width=1, border_color=COLOR_BORDER)
        card.grid(row=row, column=0, sticky="nsew", pady=pady)
        card.grid_columnconfigure(0, weight=1)
        header = ctk.CTkLabel(card, text=title, font=self.fonts["section"], text_color=COLOR_TEXT_PRIMARY)
        header.grid(row=0, column=0, sticky="w", padx=24, pady=(24, 10))
        return card

    def _build_identity_card(self, parent: ctk.CTkFrame):
        card = self._create_card(parent, "Resumen de cuenta", row=0)

        info_row = ctk.CTkFrame(card, fg_color="transparent")
        info_row.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 20))
        info_row.grid_columnconfigure(1, weight=1)

        avatar = ctk.CTkFrame(info_row, fg_color=COLOR_AVATAR_BG, width=88, height=88, corner_radius=44)
        avatar.grid(row=0, column=0, sticky="w")
        avatar.grid_propagate(False)

        initials = ctk.CTkLabel(
            avatar,
            text=self._user_initials(self.username),
            font=ctk.CTkFont(size=34, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        initials.place(relx=0.5, rely=0.5, anchor="center")

        info = ctk.CTkFrame(info_row, fg_color="transparent")
        info.grid(row=0, column=1, sticky="nsew", padx=(18, 0))
        info.grid_columnconfigure(0, weight=1)

        name_label = ctk.CTkLabel(info, text=self.display_name, font=self.fonts["card_title"], text_color=COLOR_TEXT_PRIMARY)
        name_label.grid(row=0, column=0, sticky="w")

        email_label = ctk.CTkLabel(info, text=self.username, font=self.fonts["muted"], text_color=COLOR_TEXT_MUTED)
        email_label.grid(row=1, column=0, sticky="w", pady=(4, 0))

        edit_button = ctk.CTkButton(
            info,
            text="Editar perfil",
            command=lambda: self._show_notification("Pronto podrás actualizar tu perfil desde la app."),
            fg_color="transparent",
            hover_color="#E2E8F0",
            text_color=COLOR_ACCENT,
            font=self.fonts["button"],
        )
        edit_button.grid(row=2, column=0, sticky="w", pady=(12, 0))

        stats_row = ctk.CTkFrame(card, fg_color="transparent")
        stats_row.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 24))
        stats_row.grid_columnconfigure(tuple(range(len(self.profile_stats))), weight=1, minsize=180, uniform="profile_stats")

        for idx, stat in enumerate(self.profile_stats):
            stat_card = ctk.CTkFrame(
                stats_row,
                fg_color=COLOR_CARD_SOFT,
                corner_radius=18,
                border_width=1,
                border_color=COLOR_BORDER,
            )
            stat_card.grid(row=0, column=idx, sticky="nsew", padx=(0 if idx == 0 else 12, 0))
            stat_card.grid_columnconfigure(0, weight=1)

            value_label = ctk.CTkLabel(
                stat_card,
                text=stat["value"],
                font=self.fonts["stat_value"],
                text_color=COLOR_TEXT_PRIMARY,
                anchor="w",
            )
            value_label.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 4))

            hint_label = ctk.CTkLabel(
                stat_card,
                text=stat["label"],
                font=self.fonts["muted"],
                text_color=COLOR_TEXT_MUTED,
                anchor="w",
            )
            hint_label.grid(row=1, column=0, sticky="ew", padx=20)

            note_label = ctk.CTkLabel(
                stat_card,
                text=stat["hint"],
                font=self.fonts["stat_hint"],
                text_color=COLOR_TEXT_MUTED,
                wraplength=220,
                justify="left",
            )
            note_label.grid(row=2, column=0, sticky="w", padx=20, pady=(0, 16))

    def _build_security_card(self, parent: ctk.CTkFrame):
        card = self._create_card(parent, "Seguridad y privacidad", row=1, pady=(24, 0))

        for idx, item in enumerate(self.security_items, start=1):
            feature = ctk.CTkFrame(card, fg_color=COLOR_CARD_SOFT, corner_radius=18, border_width=1, border_color=COLOR_BORDER)
            feature.grid(row=idx, column=0, sticky="ew", padx=24, pady=(0, 14))

            title = ctk.CTkLabel(feature, text=item["title"], font=self.fonts["body"], text_color=COLOR_TEXT_PRIMARY)
            title.grid(row=0, column=0, sticky="w", padx=18, pady=(16, 4))

            description = ctk.CTkLabel(
                feature,
                text=item["description"],
                font=self.fonts["muted"],
                text_color=COLOR_TEXT_SECONDARY,
                wraplength=480,
                justify="left",
            )
            description.grid(row=1, column=0, sticky="w", padx=18, pady=(0, 16))

        manage_button = ctk.CTkButton(
            card,
            text="Administrar bóveda",
            command=lambda: self.controller.show_vault_view(self.username),
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_DARK,
            text_color=COLOR_CARD,
            font=self.fonts["button"],
            corner_radius=20,
        )
        manage_button.grid(row=len(self.security_items) + 1, column=0, sticky="ew", padx=24, pady=(8, 24))

    def _build_subscription_card(self, parent: ctk.CTkFrame):
        card = self._create_card(parent, "Suscripción y plan", row=0)
        card.grid_columnconfigure(0, weight=1)

        # Mostrar información real de suscripción
        plan_name = self.subscription_info.get("plan_name", "Gratuito") if self.subscription_info else "Gratuito"
        plan_price = self.subscription_info.get("price", 0) if self.subscription_info else 0
        currency = self.subscription_info.get("currency", "USD") if self.subscription_info else "USD"
        status = self.subscription_info.get("status", "Activa") if self.subscription_info else "Activa"
        
        # Determinar color del badge según el estado
        badge_color = COLOR_ACCENT if status.lower() == "activa" else COLOR_TEXT_MUTED
        badge_bg = COLOR_BADGE_BG if status.lower() == "activa" else "#FEE2E2"
        
        badge = ctk.CTkFrame(card, fg_color=badge_bg, corner_radius=14, border_width=1, border_color=badge_color)
        badge.grid(row=1, column=0, sticky="w", padx=24, pady=(0, 16))
        ctk.CTkLabel(badge, text=f"Suscripción {status}", font=self.fonts["badge"], text_color=badge_color).pack(padx=14, pady=6)

        # Plan name and pricing
        plan_frame = ctk.CTkFrame(card, fg_color="transparent")
        plan_frame.grid(row=2, column=0, sticky="w", padx=24, pady=(0, 16))
        
        plan_name_label = ctk.CTkLabel(
            plan_frame,
            text=plan_name,
            font=self.fonts["card_title"],
            text_color=COLOR_TEXT_PRIMARY
        )
        plan_name_label.grid(row=0, column=0, sticky="w")
        
        if plan_price > 0:
            price_label = ctk.CTkLabel(
                plan_frame,
                text=f"${plan_price}/{currency.lower()}",
                font=self.fonts["body"],
                text_color=COLOR_TEXT_MUTED
            )
            price_label.grid(row=1, column=0, sticky="w", pady=(4, 0))
        else:
            free_label = ctk.CTkLabel(
                plan_frame,
                text="Gratis",
                font=self.fonts["body"],
                text_color=COLOR_SUCCESS
            )
            free_label.grid(row=1, column=0, sticky="w", pady=(4, 0))

        description = ctk.CTkLabel(
            card,
            text=(
                "Tu plan incluye almacenamiento cifrado, monitoreo básico de filtraciones "
                "y soporte prioritario. Cambia de plan o actualiza tus datos cuando lo necesites."
            ),
            font=self.fonts["body"],
            text_color=COLOR_TEXT_SECONDARY,
            wraplength=340,
            justify="left",
        )
        description.grid(row=3, column=0, sticky="w", padx=24)

        progress_label = ctk.CTkLabel(card, text="Uso estimado de bóveda", font=self.fonts["muted"], text_color=COLOR_TEXT_MUTED)
        progress_label.grid(row=4, column=0, sticky="w", padx=24, pady=(20, 6))

        progress = ctk.CTkProgressBar(card, fg_color=COLOR_CARD_SOFT, progress_color=COLOR_ACCENT, corner_radius=10, height=14)
        progress.grid(row=5, column=0, sticky="ew", padx=24)
        progress.set(0.65)

        progress_hint = ctk.CTkLabel(
            card,
            text="65% de tus registros están sincronizados en este dispositivo.",
            font=self.fonts["stat_hint"],
            text_color=COLOR_TEXT_MUTED,
        )
        progress_hint.grid(row=6, column=0, sticky="w", padx=24, pady=(6, 20))

        manage_button = ctk.CTkButton(
            card,
            text="Actualizar plan",
            command=self._open_subscription_web,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_DARK,
            text_color=COLOR_CARD,
            font=self.fonts["button"],
            corner_radius=20,
        )
        manage_button.grid(row=7, column=0, sticky="ew", padx=24, pady=(0, 24))

    def _build_quick_actions_card(self, parent: ctk.CTkFrame):
        card = self._create_card(parent, "Accesos rápidos", row=1, pady=(24, 0))
        card.grid_columnconfigure(0, weight=1)

        description = ctk.CTkLabel(
            card,
            text="Accede rápidamente a las secciones clave de EncryptU.",
            font=self.fonts["body"],
            text_color=COLOR_TEXT_SECONDARY,
            wraplength=360,
            justify="left",
        )
        description.grid(row=1, column=0, sticky="w", padx=24, pady=(0, 16))

        buttons = ctk.CTkFrame(card, fg_color="transparent")
        buttons.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 24))
        buttons.grid_columnconfigure(0, weight=1)
        buttons.grid_columnconfigure(1, weight=1)

        vault_button = ctk.CTkButton(
            buttons,
            text="Bóveda de contraseñas",
            command=lambda: self.controller.show_vault_view(self.username),
            fg_color=COLOR_CARD_SOFT,
            hover_color="#EEF2FF",
            text_color=COLOR_TEXT_PRIMARY,
            font=self.fonts["button"],
            corner_radius=18,
            height=44,
        )
        vault_button.grid(row=0, column=0, sticky="ew", padx=(0, 12))

        support_button = ctk.CTkButton(
            buttons,
            text="Soporte prioritario",
            command=lambda: self.controller.show_support_view(self.username),
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_DARK,
            text_color=COLOR_CARD,
            font=self.fonts["button"],
            corner_radius=18,
            height=44,
        )
        support_button.grid(row=0, column=1, sticky="ew")

    def _build_checklist_card(self, parent: ctk.CTkFrame):
        card = self._create_card(parent, "Checklist de seguridad", row=2, pady=(24, 0))

        for idx, item in enumerate(self.security_checklist, start=1):
            row = ctk.CTkFrame(card, fg_color=COLOR_CARD_SOFT, corner_radius=16, border_width=1, border_color=COLOR_BORDER)
            row.grid(row=idx, column=0, sticky="ew", padx=24, pady=(0, 12))
            row.grid_columnconfigure(1, weight=1)

            check = ctk.CTkLabel(row, text="✓", font=self.fonts["section"], text_color=COLOR_ACCENT)
            check.grid(row=0, column=0, sticky="nw", padx=18, pady=14)

            text = ctk.CTkLabel(
                row,
                text=item,
                font=self.fonts["body"],
                text_color=COLOR_TEXT_PRIMARY,
                wraplength=300,
                justify="left",
            )
            text.grid(row=0, column=1, sticky="w", padx=(0, 18), pady=14)

    # ------------------------------------------------------------------
    # Navegación y helpers
    # ------------------------------------------------------------------
    def _go_home(self):
        controller = getattr(self, "controller", None)
        if not controller or not hasattr(controller, "show_main_view"):
            self._show_notification("No se puede volver al inicio en este momento.")
            return

        username = getattr(controller, "current_username", None) or self.username
        try:
            controller.show_main_view(username)
        except Exception:
            self._show_notification("Ocurrió un error al volver al inicio.")

    def _show_notification(self, message: str):
        toplevel = self.winfo_toplevel()
        if not isinstance(toplevel, ctk.CTk):
            return

        popup = ctk.CTkToplevel(toplevel)
        popup.title("EncryptU")
        popup.geometry("380x190")
        popup.resizable(False, False)
        popup.configure(fg_color=COLOR_CARD)

        label = ctk.CTkLabel(
            popup,
            text=message,
            font=self.fonts["body"],
            text_color=COLOR_TEXT_PRIMARY,
            wraplength=320,
            justify="center",
        )
        label.pack(expand=True, fill="both", padx=28, pady=(28, 12))

        popup.after(2600, popup.destroy)

    def _load_logo_image(self) -> ctk.CTkImage:
        try:
            logo = Image.open(BLACK_LOGO_PATH)
            target_height = 168
            aspect_ratio = logo.width / logo.height if logo.height else 1
            size = (int(target_height * aspect_ratio), target_height)
            return ctk.CTkImage(light_image=logo, dark_image=logo, size=size)
        except Exception:
            placeholder = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
            return ctk.CTkImage(light_image=placeholder, dark_image=placeholder, size=(1, 1))

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

    def _open_subscription_web(self):
        """Abre la página web de suscripciones en el navegador."""
        try:
            import webbrowser
            # URL de la página de planes/suscripciones
            subscription_url = "https://encryptu-web.onrender.com/marketing/planes"
            webbrowser.open(subscription_url)
            self._show_notification("Abriendo página de suscripciones en tu navegador...")
        except Exception as e:
            self._show_notification(f"No se pudo abrir la página web: {str(e)}")

    def _get_subscription_info(self) -> Optional[Dict[str, Any]]:
        """Obtiene información de suscripción desde la API."""
        try:
            if hasattr(self.controller, 'api_client') and self.controller.api_client:
                return self.controller.api_client.get_subscription()
        except Exception as e:
            print(f"Error obteniendo suscripción: {e}")
        return None
