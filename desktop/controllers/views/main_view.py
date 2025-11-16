import customtkinter as ctk
from datetime import datetime
from typing import Dict, Optional, Any

from desktop.controllers.views.base_view import BaseView, COLOR_BACKGROUND

COLOR_CARD = "#FFFFFF"
COLOR_CARD_SOFT = "#FBFCFF"
COLOR_BORDER = "#E2E8F0"
COLOR_TEXT_PRIMARY = "#0F172A"
COLOR_TEXT_MUTED = "#94A3B8"
COLOR_ACCENT = "#EE5A72"
COLOR_ACCENT_DARK = "#D9435C"
COLOR_PRIMARY = "#2563EB"
COLOR_PRIMARY_DARK = "#1D4ED8"
COLOR_SUCCESS = "#16A34A"


class MainView(BaseView):
    """Vista principal con el mismo estilo accesible de support_view."""

    def __init__(self, master, controller, username: str):
        super().__init__(master, fg_color=COLOR_BACKGROUND)
        self.controller = controller
        self.username = username or "Usuario"
        self.display_name = self._format_username(self.username)
        self.last_login = datetime.now().strftime("%d/%m/%Y")
        self.fonts = self._build_fonts()
        
        # Obtener datos reales de la API
        self.subscription_info = self._get_subscription_info()
        self.ticket_stats = self._get_ticket_stats()
        
        self._build_layout()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def _build_fonts(self) -> Dict[str, ctk.CTkFont]:
        fonts = dict(self.base_fonts)
        fonts.update(
            {
                "section": ctk.CTkFont(size=20, weight="bold"),
                "card_title": ctk.CTkFont(size=16, weight="bold"),
                "body": ctk.CTkFont(size=13),
                "muted": ctk.CTkFont(size=12),
                "stat": ctk.CTkFont(size=26, weight="bold"),
            }
        )
        return fonts

    def _build_layout(self):
        header = self.build_header(
            title=f"Hola, {self.display_name}",
            subtitle="Administra tu perfil, credenciales y soporte desde un solo lugar.",
            badge="Inicio - Desktop",
        )
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(20, 12))

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        scroll.grid_columnconfigure(0, weight=1)

        body = ctk.CTkFrame(scroll, fg_color=COLOR_CARD_SOFT, corner_radius=32)
        body.grid(row=0, column=0, sticky="ew", pady=4)
        body.grid_columnconfigure(0, weight=1)

        row = 0
        row = self._build_overview_card(body, row)
        row = self._build_navigation_card(body, row)
        row = self._build_activity_card(body, row)
        self._build_support_card(body, row)

    # ------------------------------------------------------------------
    # Tarjetas
    # ------------------------------------------------------------------
    def _create_card(self, parent: ctk.CTkFrame, title: str, row: int, pady: tuple[int, int] = (0, 0)) -> ctk.CTkFrame:
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.grid(row=row, column=0, sticky="ew", padx=24, pady=(pady[0], pady[1] + 8))
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

        shadow = ctk.CTkLabel(container, text="", fg_color="#CBD3EA", corner_radius=26)
        shadow.place(relx=0, rely=0, relwidth=1, relheight=1, x=6, y=9)

        card = ctk.CTkFrame(
            container,
            fg_color=COLOR_CARD,
            corner_radius=24,
            border_width=1,
            border_color=COLOR_ACCENT,
        )
        card.grid(row=0, column=0, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        card.lift(shadow)

        ctk.CTkLabel(card, text=title, font=self.fonts["section"], text_color=COLOR_TEXT_PRIMARY).grid(
            row=0, column=0, sticky="w", padx=24, pady=(24, 10)
        )

        return card

    def _build_overview_card(self, parent: ctk.CTkFrame, row_index: int) -> int:
        card = self._create_card(parent, "Resumen de cuenta", row=row_index)

        user_row = ctk.CTkFrame(card, fg_color="transparent")
        user_row.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 16))
        user_row.grid_columnconfigure(1, weight=1)

        avatar = ctk.CTkFrame(user_row, fg_color="#E0E7FF", width=82, height=82, corner_radius=41)
        avatar.grid(row=0, column=0, sticky="w")
        avatar.grid_propagate(False)
        ctk.CTkLabel(
            avatar,
            text=self._user_initials(self.username),
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        ).place(relx=0.5, rely=0.5, anchor="center")

        info = ctk.CTkFrame(user_row, fg_color="transparent")
        info.grid(row=0, column=1, sticky="nsew", padx=(16, 0))
        info.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(info, text=self.display_name, font=self.fonts["card_title"], text_color=COLOR_TEXT_PRIMARY).grid(
            row=0, column=0, sticky="w"
        )
        ctk.CTkLabel(info, text=self.username, font=self.fonts["muted"], text_color=COLOR_TEXT_MUTED).grid(
            row=1, column=0, sticky="w", pady=(4, 0)
        )

        stats_row = ctk.CTkFrame(card, fg_color="transparent")
        stats_row.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 24))
        stats_row.grid_columnconfigure((0, 1, 2), weight=1, uniform="stats")

        # Mostrar información real de suscripción
        plan_name = self.subscription_info.get("plan_name", "Gratuito") if self.subscription_info else "Gratuito"
        status = self.subscription_info.get("status", "Activa") if self.subscription_info else "Activa"
        
        self._build_stat_tile(stats_row, 0, "Estado", status)
        self._build_stat_tile(stats_row, 1, "Ultimo acceso", self.last_login)
        self._build_stat_tile(stats_row, 2, "Plan", plan_name)
        return row_index + 1

    def _build_stat_tile(self, parent: ctk.CTkFrame, column: int, label: str, value: str):
        tile = ctk.CTkFrame(parent, fg_color=COLOR_CARD_SOFT, corner_radius=18, border_width=1, border_color=COLOR_BORDER)
        tile.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 12, 0))
        tile.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(tile, text=value, font=self.fonts["stat"], text_color=COLOR_TEXT_PRIMARY).grid(
            row=0, column=0, sticky="w", padx=18, pady=(16, 2)
        )
        ctk.CTkLabel(tile, text=label, font=self.fonts["muted"], text_color=COLOR_TEXT_MUTED).grid(
            row=1, column=0, sticky="w", padx=18, pady=(0, 12)
        )

    def _build_activity_card(self, parent: ctk.CTkFrame, row_index: int) -> int:
        card = self._create_card(parent, "Actividad reciente", row=row_index, pady=(24, 0))

        entries = [
            ("Perfil actualizado", "Datos sincronizados correctamente."),
            ("Credencial guardada", "Se agrego una credencial en la boveda."),
            ("Ticket resuelto", "Tu ultima conversacion de soporte finalizo."),
        ]
        for idx, (title, desc) in enumerate(entries, start=1):
            row = ctk.CTkFrame(card, fg_color=COLOR_CARD_SOFT, corner_radius=16, border_width=1, border_color=COLOR_BORDER)
            row.grid(row=idx, column=0, sticky="ew", padx=24, pady=(0, 10))
            ctk.CTkLabel(row, text=title, font=self.fonts["card_title"], text_color=COLOR_TEXT_PRIMARY).grid(
                row=0, column=0, sticky="w", padx=18, pady=(14, 2)
            )
            ctk.CTkLabel(row, text=desc, font=self.fonts["body"], text_color=COLOR_TEXT_MUTED).grid(
                row=1, column=0, sticky="w", padx=18, pady=(0, 14)
            )
        return row_index + 1

    def _build_navigation_card(self, parent: ctk.CTkFrame, row_index: int) -> int:
        card = self._create_card(parent, "Secciones principales", row=row_index, pady=(24, 0))

        buttons = ctk.CTkFrame(card, fg_color="transparent")
        buttons.grid(row=1, column=0, sticky="ew", padx=24, pady=(10, 24))
        buttons.grid_columnconfigure((0, 1, 2), weight=1, uniform="nav")

        self._nav_button(
            buttons,
            column=0,
            title="Mi Perfil",
            desc="Actualiza tus datos personales y preferencias.",
            command=self._open_profile,
        )
        self._nav_button(
            buttons,
            column=1,
            title="Credenciales",
            desc="Gestiona tu boveda segura de contrasenas.",
            command=self._open_vault,
            accent=COLOR_PRIMARY,
            hover=COLOR_PRIMARY_DARK,
        )
        self._nav_button(
            buttons,
            column=2,
            title="Soporte",
            desc="Chatea con el equipo y revisa tus tickets.",
            command=self._open_support,
            accent=COLOR_ACCENT,
            hover=COLOR_ACCENT_DARK,
        )
        return row_index + 1

    def _nav_button(
        self,
        parent: ctk.CTkFrame,
        column: int,
        title: str,
        desc: str,
        command,
        accent: str | None = None,
        hover: str | None = None,
    ):
        card = ctk.CTkFrame(parent, fg_color=COLOR_CARD_SOFT, corner_radius=20, border_width=1, border_color=COLOR_BORDER)
        card.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 12, 0))
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text=title, font=self.fonts["card_title"], text_color=COLOR_TEXT_PRIMARY).grid(
            row=0, column=0, sticky="w", padx=16, pady=(16, 4)
        )
        ctk.CTkLabel(card, text=desc, font=self.fonts["body"], text_color=COLOR_TEXT_MUTED, wraplength=200).grid(
            row=1, column=0, sticky="w", padx=16
        )

        if accent is None:
            fg_color = "#EEF2FF"
            hover_color = "#E2E8F0"
            text_color = COLOR_TEXT_PRIMARY
        else:
            fg_color = accent
            hover_color = hover or accent
            text_color = COLOR_CARD

        ctk.CTkButton(
            card,
            text="Abrir",
            command=command,
            fg_color=fg_color,
            hover_color=hover_color,
            text_color=text_color,
            font=self.fonts["button"],
            height=36,
            corner_radius=16,
        ).grid(row=2, column=0, sticky="ew", padx=16, pady=(12, 16))

    def _build_support_card(self, parent: ctk.CTkFrame, row_index: int):
        card = self._create_card(parent, "Estado de soporte", row=row_index, pady=(24, 24))

        description = (
            "Consulta respuestas pendientes, crea nuevas solicitudes y recibe ayuda prioritaria "
            "cuando la necesites."
        )
        ctk.CTkLabel(card, text=description, font=self.fonts["body"], text_color=COLOR_TEXT_MUTED, wraplength=420).grid(
            row=1, column=0, sticky="w", padx=24, pady=(0, 18)
        )

        status_row = ctk.CTkFrame(card, fg_color="transparent")
        status_row.grid(row=2, column=0, sticky="ew", padx=24)
        status_row.grid_columnconfigure((0, 1), weight=1)

        self._status_chip(status_row, 0, "Tickets abiertos", "2", COLOR_ACCENT)
        self._status_chip(status_row, 1, "Resueltos esta semana", "4", COLOR_SUCCESS)

        # Mostrar estadísticas reales de tickets
        open_count = self.ticket_stats.get("open", 0) if self.ticket_stats else 0
        resolved_count = self.ticket_stats.get("resolved", 0) if self.ticket_stats else 0
        
        self._status_chip(status_row, 0, "Tickets abiertos", str(open_count), COLOR_ACCENT)
        self._status_chip(status_row, 1, "Resueltos", str(resolved_count), COLOR_SUCCESS)

        ctk.CTkButton(
            card,
            text="Ir a soporte",
            command=self._open_support,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_DARK,
            text_color=COLOR_CARD,
            font=self.fonts["button"],
            height=40,
            corner_radius=20,
        ).grid(row=3, column=0, sticky="ew", padx=24, pady=(18, 24))

    def _status_chip(self, parent: ctk.CTkFrame, column: int, label: str, value: str, color: str):
        chip = ctk.CTkFrame(parent, fg_color=COLOR_CARD_SOFT, corner_radius=18, border_width=1, border_color=COLOR_BORDER)
        chip.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 12, 0))
        ctk.CTkLabel(chip, text=label, font=self.fonts["muted"], text_color=COLOR_TEXT_MUTED).grid(
            row=0, column=0, sticky="w", padx=16, pady=(12, 0)
        )
        ctk.CTkLabel(chip, text=value, font=self.fonts["stat"], text_color=color).grid(
            row=1, column=0, sticky="w", padx=16, pady=(0, 12)
        )

    # ------------------------------------------------------------------
    # NavegaciÃ³n
    # ------------------------------------------------------------------
    def _open_profile(self):
        self.controller.show_profile_view(self.username)

    def _open_vault(self):
        self.controller.show_vault_view(self.username)

    def _open_support(self):
        self.controller.show_support_view(self.username)

    # ------------------------------------------------------------------
    # API Integration
    # ------------------------------------------------------------------
    def _get_subscription_info(self) -> Optional[Dict[str, Any]]:
        """Obtiene información de suscripción desde la API."""
        try:
            if hasattr(self.controller, 'api_client') and self.controller.api_client:
                return self.controller.api_client.get_subscription()
        except Exception as e:
            print(f"Error obteniendo suscripción: {e}")
        return None

    def _get_ticket_stats(self) -> Optional[Dict[str, int]]:
        """Obtiene estadísticas de tickets desde la API."""
        try:
            if hasattr(self.controller, 'api_client') and self.controller.api_client:
                return self.controller.api_client.get_user_ticket_stats()
        except Exception as e:
            print(f"Error obteniendo estadísticas de tickets: {e}")
        return {"open": 0, "resolved": 0}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
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

