import customtkinter as ctk
from datetime import datetime
import re
from typing import Callable, Dict, List, Optional

import pyperclip
import requests
import io
from PIL import Image

from desktop.controllers.views.base_view import BaseView
from desktop.config import resource_path

# ----------------------------------------------------------------------
# Paleta compartida con la vista de soporte
# ----------------------------------------------------------------------
COLOR_BACKGROUND = "#F4F6FB"
COLOR_CARD = "#FFFFFF"
COLOR_CARD_SOFT = "#FBFCFF"
COLOR_BORDER = "#E2E8F0"
COLOR_TEXT_PRIMARY = "#0F172A"
COLOR_TEXT_MUTED = "#94A3B8"
COLOR_ACCENT = "#EE5A72"
COLOR_ACCENT_DARK = "#D9435C"
COLOR_SUCCESS = "#16A34A"
COLOR_DANGER = "#DC2626"
COLOR_WHITE = "#FFFFFF"

BLACK_LOGO_PATH = None

BADGE_COLOR_MAP = {
    "instagram": "#F472B6",
    "gmail": "#FB7185",
    "twitter": "#60A5FA",
    "figma": "#34D399",
    "facebook": "#3B82F6",
    "slack": "#A855F7",
}
BADGE_FALLBACK_COLORS = ["#60A5FA", "#FBBF24", "#34D399", "#F472B6"]

ICON_TARGET_SIZE = (52, 52)


class VaultView(BaseView):
    """Gestor de credenciales con la estética limpia de la vista de soporte."""

    def __init__(self, master, controller, username: str):
        super().__init__(master, fg_color=COLOR_BACKGROUND)

        self.controller = controller
        self.username = username or "Usuario"

        self.fonts = self._build_fonts()
        self.logo_image = self._load_logo_image()

        self.password_count_var = ctk.StringVar(value="0 credenciales")
        self.last_sync_var = ctk.StringVar(value="Sincroniza para comenzar")
        self.status_label_save: Optional[ctk.CTkLabel] = None

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self._on_search_change)

        self.credentials: List[Dict[str, str]] = []
        self.filtered_credentials: List[Dict[str, str]] = []
        self.scrollable_frame: Optional[ctk.CTkScrollableFrame] = None

        # Referencias del modal
        self.icon_cache: Dict[str, Optional[ctk.CTkImage]] = {}
        self.add_modal: Optional[ctk.CTkToplevel] = None
        self.view_modal: Optional[ctk.CTkToplevel] = None
        self.site_entry: Optional[ctk.CTkEntry] = None
        self.username_entry_save: Optional[ctk.CTkEntry] = None
        self.password_entry: Optional[ctk.CTkEntry] = None
        self.save_button: Optional[ctk.CTkButton] = None

        self._build_layout()
        self.after(150, self.refresh_password_list)

    # ------------------------------------------------------------------
    # Construcción de UI
    # ------------------------------------------------------------------
    def _build_fonts(self) -> Dict[str, ctk.CTkFont]:
        return {
            "hero_title": ctk.CTkFont(family="Arial", size=40, weight="bold"),
            "hero_sub": ctk.CTkFont(family="Arial", size=18),
            "section": ctk.CTkFont(size=20, weight="bold"),
            "card_title": ctk.CTkFont(size=16, weight="bold"),
            "card_sub": ctk.CTkFont(size=13),
            "body": ctk.CTkFont(size=14),
            "small": ctk.CTkFont(size=12),
            "button": ctk.CTkFont(size=15, weight="bold"),
            "badge": ctk.CTkFont(size=13, weight="bold"),
        }

    def _load_logo_image(self) -> ctk.CTkImage:
        try:
            path = resource_path("controllers/img/Blacklogo.png")
            logo = Image.open(path)
            target_height = 168
            aspect_ratio = logo.width / logo.height if logo.height else 1
            size = (int(target_height * aspect_ratio), target_height)
            return ctk.CTkImage(light_image=logo, dark_image=logo, size=size)
        except Exception:
            fallback = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
            return ctk.CTkImage(light_image=fallback, dark_image=fallback, size=(1, 1))

    def _build_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

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
            hover_color="#E2E8F0",
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

        badge = ctk.CTkLabel(
            title_block,
            text="Vault · Desktop",
            font=self.fonts["small"],
            text_color=COLOR_TEXT_MUTED,
        )
        badge.grid(row=0, column=0, sticky="w")

        title = ctk.CTkLabel(
            title_block,
            text="Mis credenciales",
            font=self.fonts["hero_title"],
            text_color=COLOR_TEXT_PRIMARY,
        )
        title.grid(row=1, column=0, sticky="w")

        subtitle = ctk.CTkLabel(
            header,
            text="Administra, cifra y comparte de forma segura tus accesos importantes.",
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

        body = ctk.CTkFrame(wrapper, fg_color=COLOR_CARD_SOFT, corner_radius=32)
        body.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=48)
        body.grid_columnconfigure(1, weight=52)

        self._build_credentials_panel(body)
        self._build_summary_panel(body)

    def _build_credentials_panel(self, parent: ctk.CTkFrame):
        panel = ctk.CTkFrame(
            parent,
            fg_color=COLOR_CARD,
            border_width=1,
            border_color=COLOR_BORDER,
            corner_radius=28,
        )
        panel.grid(row=0, column=0, sticky="nsew", padx=(24, 12), pady=24)
        panel.grid_rowconfigure(4, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(panel, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 4))
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(header, text="Credenciales", font=self.fonts["section"], text_color=COLOR_TEXT_PRIMARY)
        title.grid(row=0, column=0, sticky="w")

        count = ctk.CTkLabel(header, textvariable=self.password_count_var, font=self.fonts["small"], text_color=COLOR_TEXT_MUTED)
        count.grid(row=0, column=1, sticky="e")

        search_holder = ctk.CTkFrame(panel, fg_color=COLOR_CARD_SOFT, corner_radius=20, border_width=1, border_color=COLOR_BORDER)
        search_holder.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 8))
        search_holder.grid_columnconfigure(1, weight=1)

        search_icon = ctk.CTkLabel(search_holder, text="🔍", font=self.fonts["body"], text_color=COLOR_TEXT_MUTED)
        search_icon.grid(row=0, column=0, padx=(16, 8), pady=10)

        search_entry = ctk.CTkEntry(
            search_holder,
            placeholder_text="Buscar por servicio o usuario",
            textvariable=self.search_var,
            border_width=0,
            fg_color="transparent",
            font=self.fonts["body"],
        )
        search_entry.grid(row=0, column=1, sticky="ew", pady=10)

        actions = ctk.CTkFrame(panel, fg_color="transparent")
        actions.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 4))
        actions.grid_columnconfigure(0, weight=1)
        actions.grid_columnconfigure(1, weight=1)
        actions.grid_columnconfigure(2, weight=1)

        refresh_btn = ctk.CTkButton(
            actions,
            text="Actualizar",
            command=self.refresh_password_list,
            fg_color="transparent",
            hover_color="#EEF2FF",
            text_color=COLOR_ACCENT,
            font=self.fonts["button"],
        )
        refresh_btn.grid(row=0, column=0, sticky="w")

        export_btn = ctk.CTkButton(
            actions,
            text="Exportar",
            command=self._export_passwords,
            fg_color="transparent",
            hover_color="#EEF2FF",
            text_color=COLOR_SUCCESS,
            font=self.fonts["button"],
        )
        export_btn.grid(row=0, column=1, sticky="e", padx=8)

        new_btn = ctk.CTkButton(
            actions,
            text="Nueva credencial",
            command=self._open_add_credential_modal,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_DARK,
            text_color=COLOR_WHITE,
            font=self.fonts["button"],
        )
        new_btn.grid(row=0, column=2, sticky="e")

        divider = ctk.CTkFrame(panel, fg_color=COLOR_BORDER, height=1)
        divider.grid(row=3, column=0, sticky="ew", padx=24, pady=(8, 4))

        self.scrollable_frame = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        self.scrollable_frame.grid(row=4, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

    def _build_summary_panel(self, parent: ctk.CTkFrame):
        panel = ctk.CTkFrame(
            parent,
            fg_color=COLOR_CARD,
            border_width=1,
            border_color=COLOR_BORDER,
            corner_radius=28,
        )
        panel.grid(row=0, column=1, sticky="nsew", padx=(12, 24), pady=24)
        panel.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(panel, text="Resumen & Acciones", font=self.fonts["section"], text_color=COLOR_TEXT_PRIMARY)
        header.grid(row=0, column=0, sticky="w", padx=24, pady=(20, 8))

        stats_card = ctk.CTkFrame(panel, fg_color=COLOR_CARD_SOFT, corner_radius=20, border_width=1, border_color=COLOR_BORDER)
        stats_card.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 16))
        stats_card.grid_columnconfigure(1, weight=1)

        total_label = ctk.CTkLabel(stats_card, text="Total guardadas", font=self.fonts["small"], text_color=COLOR_TEXT_MUTED)
        total_label.grid(row=0, column=0, sticky="w", padx=20, pady=(16, 0))

        total_value = ctk.CTkLabel(stats_card, textvariable=self.password_count_var, font=self.fonts["hero_sub"], text_color=COLOR_TEXT_PRIMARY)
        total_value.grid(row=1, column=0, sticky="w", padx=20)

        sync_label = ctk.CTkLabel(stats_card, text="Última sincronización", font=self.fonts["small"], text_color=COLOR_TEXT_MUTED)
        sync_label.grid(row=0, column=1, sticky="e", padx=20, pady=(16, 0))

        sync_value = ctk.CTkLabel(stats_card, textvariable=self.last_sync_var, font=self.fonts["body"], text_color=COLOR_TEXT_PRIMARY)
        sync_value.grid(row=1, column=1, sticky="e", padx=20)

        self.status_label_save = ctk.CTkLabel(stats_card, text="", font=self.fonts["small"], text_color=COLOR_TEXT_MUTED)
        self.status_label_save.grid(row=2, column=0, columnspan=2, sticky="w", padx=20, pady=(10, 16))

        tips_card = ctk.CTkFrame(panel, fg_color=COLOR_CARD_SOFT, corner_radius=20, border_width=1, border_color=COLOR_BORDER)
        tips_card.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 16))
        tips_card.grid_columnconfigure(0, weight=1)

        tips_title = ctk.CTkLabel(tips_card, text="Consejos rápidos", font=self.fonts["card_title"], text_color=COLOR_TEXT_PRIMARY)
        tips_title.grid(row=0, column=0, sticky="w", padx=20, pady=(16, 4))

        tips_text = (
            "• Las contraseñas se desencriptan automáticamente.\n"
            "• Copiamos tu contraseña al portapapeles por 1 uso.\n"
            "• Actualiza frecuentemente tus credenciales críticas."
        )
        ctk.CTkLabel(tips_card, text=tips_text, font=self.fonts["body"], text_color=COLOR_TEXT_MUTED, justify="left", wraplength=360).grid(
            row=1, column=0, sticky="w", padx=20, pady=(0, 12)
        )

        action_row = ctk.CTkFrame(tips_card, fg_color="transparent")
        action_row.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))

        quick_add = ctk.CTkButton(
            action_row,
            text="Agregar credencial",
            command=self._open_add_credential_modal,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_DARK,
            text_color=COLOR_WHITE,
            font=self.fonts["button"],
        )
        quick_add.pack(side="left")

        logout_btn = ctk.CTkButton(
            panel,
            text="Cerrar sesión",
            command=self.logout_action,
            fg_color="transparent",
            hover_color="#E2E8F0",
            text_color=COLOR_ACCENT,
            font=self.fonts["button"],
        )
        logout_btn.grid(row=3, column=0, sticky="e", padx=24, pady=(0, 24))

        # Botón flotante para importar
        import_btn = ctk.CTkButton(
            panel,
            text="📥 Importar",
            command=self._import_passwords,
            fg_color=COLOR_SUCCESS,
            hover_color="#15803D",
            text_color=COLOR_WHITE,
            font=self.fonts["button"],
            corner_radius=25,
            width=140,
            height=50,
        )
        import_btn.place(relx=0.1, rely=0.95, anchor="center")

    # ------------------------------------------------------------------
    # Datos y renderizado
    # ------------------------------------------------------------------
    def refresh_password_list(self):
        if not self.scrollable_frame or not self.scrollable_frame.winfo_exists() or not self.winfo_exists():
            return

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        passwords = self.controller.get_saved_passwords()

        if passwords is None:
            self.password_count_var.set("-- credenciales")
            self.last_sync_var.set("Sin conexión")
            self._show_empty_state("No se pudieron obtener las credenciales. Inicia sesión nuevamente.")
            return

        parsed: List[Dict[str, str]] = []
        for item in passwords:
            file_id = item.get("id")
            filename = item.get("filename", "")
            if file_id is None or not filename:
                continue
            site, username = self._split_filename(filename)
            parsed.append({"id": file_id, "site": site, "username": username})

        self.credentials = parsed
        self.password_count_var.set(f"{len(parsed)} credenciales")
        self.last_sync_var.set(datetime.now().strftime("%d/%m/%Y %H:%M"))
        self._filter_credentials(force_render=True)

    def _split_filename(self, filename: str) -> tuple[str, str]:
        parts = filename.split(" | ", 1)
        site = parts[0].strip() if parts and parts[0].strip() else "Servicio"
        username = parts[1].strip() if len(parts) > 1 and parts[1].strip() else "Sin usuario"
        return site, username

    def _filter_credentials(self, force_render: bool = False):
        query = self.search_var.get().strip().lower()
        if not query:
            self.filtered_credentials = list(self.credentials)
        else:
            self.filtered_credentials = [
                cred for cred in self.credentials if query in cred["site"].lower() or query in cred["username"].lower()
            ]
        if force_render or self.scrollable_frame:
            self._render_credential_cards()

    def _render_credential_cards(self):
        if not self.scrollable_frame or not self.scrollable_frame.winfo_exists():
            return

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not self.filtered_credentials:
            self._show_empty_state("No encontramos resultados para tu búsqueda.")
            return

        for index, cred in enumerate(self.filtered_credentials):
            card = ctk.CTkFrame(
                self.scrollable_frame,
                fg_color=COLOR_CARD_SOFT,
                border_width=1,
                border_color=COLOR_BORDER,
                corner_radius=24,
            )
            card.grid(row=index, column=0, sticky="ew", padx=12, pady=6)
            card.grid_columnconfigure(1, weight=1)

            badge_icon = self._get_site_icon(cred["site"])
            if badge_icon:
                badge = ctk.CTkLabel(card, text="", image=badge_icon, width=52, height=52)
                badge.grid(row=0, column=0, rowspan=2, padx=18, pady=18)
            else:
                badge = ctk.CTkFrame(
                    card,
                    width=52,
                    height=52,
                    corner_radius=18,
                    fg_color=self._badge_color_for_site(cred["site"]),
                )
                badge.grid(row=0, column=0, rowspan=2, padx=18, pady=18)
                badge.grid_propagate(False)

                badge_label = ctk.CTkLabel(
                    badge,
                    text=self._badge_initials(cred["site"]),
                    font=self.fonts["badge"],
                    text_color=COLOR_WHITE,
                )
                badge_label.place(relx=0.5, rely=0.5, anchor="center")

            title = ctk.CTkLabel(card, text=cred["site"], font=self.fonts["card_title"], text_color=COLOR_TEXT_PRIMARY)
            title.grid(row=0, column=1, sticky="w", pady=(18, 0))

            subtitle = ctk.CTkLabel(card, text=cred["username"], font=self.fonts["card_sub"], text_color=COLOR_TEXT_MUTED)
            subtitle.grid(row=1, column=1, sticky="w", pady=(0, 18))

            actions = ctk.CTkFrame(card, fg_color="transparent")
            actions.grid(row=0, column=2, rowspan=2, padx=16, pady=12, sticky="e")

            view_button = ctk.CTkButton(
                actions,
                text="Ver",
                width=90,
                fg_color="transparent",
                hover_color="#EEF2FF",
                text_color=COLOR_ACCENT,
                border_width=1,
                border_color=COLOR_ACCENT,
                command=lambda fid=int(cred["id"]), site=cred["site"], user=cred["username"]: self._open_view_modal(
                    fid, site, user
                ),
                font=self.fonts["button"],
            )
            view_button.pack(pady=(0, 8))

            delete_button = ctk.CTkButton(
                actions,
                text="Eliminar",
                width=90,
                fg_color=COLOR_ACCENT,
                hover_color=COLOR_ACCENT_DARK,
                text_color=COLOR_WHITE,
                command=lambda fid=int(cred["id"]): self.delete_action(fid),
                font=self.fonts["button"],
            )
            delete_button.pack()

    def _badge_initials(self, site: str) -> str:
        clean = "".join(ch for ch in site if ch.isalnum())
        if len(clean) >= 2:
            return clean[:2].upper()
        if clean:
            return clean[0].upper()
        return "EU"

    def _badge_color_for_site(self, site: str) -> str:
        key = site.lower()
        for pattern, color in BADGE_COLOR_MAP.items():
            if pattern in key:
                return color
        index = abs(hash(key)) % len(BADGE_FALLBACK_COLORS)
        return BADGE_FALLBACK_COLORS[index]

    def _get_site_icon(self, site: str) -> Optional[ctk.CTkImage]:
        # Clean the site name to get a base domain
        key = site.lower().strip()
        key = re.sub(r"^https?://", "", key)
        key = key.split("/")[0]
        if key.startswith("www."):
            key = key[4:]
        if not key:
            return None
        
        domain = key

        # Check if icon is already cached
        if domain in self.icon_cache:
            return self.icon_cache[domain]

        # If not cached, try to download it
        try:
            # Usar servicio de Google para obtener el favicon en buena resolución
            url = f"https://www.google.com/s2/favicons?domain={domain}&sz=64"
            
            # Short timeout to not block UI
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                # Open image from downloaded bytes
                image_data = response.content
                pil_icon = Image.open(io.BytesIO(image_data)).convert("RGBA")
                
                # Crear CTkImage
                tk_icon = ctk.CTkImage(
                    light_image=pil_icon,
                    dark_image=pil_icon,
                    size=ICON_TARGET_SIZE
                )
                
                # Cache and return
                self.icon_cache[domain] = tk_icon
                return tk_icon
            
        except Exception as e:
            # If there's a network error or image processing error
            print(f"Could not download favicon for {domain}: {e}")

        # If it fails, cache None to avoid retrying
        self.icon_cache[domain] = None
        return None

    def _normalize_site_input(self, raw_site: str) -> str:
        site = raw_site.strip()
        if not site:
            return ""

        site = re.sub(r"^https?://", "", site, flags=re.IGNORECASE)
        site = site.split("/", 1)[0]
        site = site.strip().strip(".")
        site = re.sub(r"\s+", "", site)
        if not site:
            return ""

        body = site
        if body.lower().startswith("www."):
            body = body[4:]
        if not body:
            return ""

        if "." not in body:
            body = f"{body}.com"

        parts = [segment for segment in body.split(".") if segment]
        if not parts:
            return ""

        formatted: list[str] = []
        last_index = len(parts) - 1
        for index, part in enumerate(parts):
            lower_part = part.lower()
            if index == last_index:
                formatted.append(lower_part)
            else:
                formatted.append(lower_part.capitalize())

        formatted_body = ".".join(formatted)
        return f"www.{formatted_body}"

    def _show_empty_state(self, message: str):
        if not self.scrollable_frame or not self.scrollable_frame.winfo_exists() or not self.winfo_exists():
            return
        label = ctk.CTkLabel(
            self.scrollable_frame,
            text=message,
            font=self.fonts["body"],
            text_color=COLOR_TEXT_MUTED,
            justify="center",
        )
        label.grid(row=0, column=0, padx=24, pady=36)

    # ------------------------------------------------------------------
    # Acciones principales
    # ------------------------------------------------------------------
    def save_action(self):
        if not all([self.site_entry, self.username_entry_save, self.password_entry, self.save_button]):
            return

        site_value = self.site_entry.get().strip()  # type: ignore[union-attr]
        username = self.username_entry_save.get().strip()  # type: ignore[union-attr]
        password = self.password_entry.get().strip()  # type: ignore[union-attr]

        normalized_site = self._normalize_site_input(site_value)

        if not normalized_site or not username or not password:
            self.show_status("Completa todos los campos para continuar.", "save", COLOR_DANGER)
            return

        self.save_button.configure(state="disabled", text="Guardando...")  # type: ignore[union-attr]
        self.show_status("Guardando...", "save", COLOR_TEXT_MUTED)

        success = self.controller.handle_encrypt_and_save(normalized_site, username, password)

        if success:
            self.show_status(f"Credencial para '{normalized_site}' almacenada.", "save", COLOR_SUCCESS)
            self.refresh_password_list()
            self._close_add_modal()
        else:
            self.show_status("Ocurrió un error al guardar. Intenta de nuevo.", "save", COLOR_DANGER)

        if self.save_button:
            self.save_button.configure(state="normal", text="Guardar")

    def delete_action(self, file_id: int):
        if self.controller.handle_delete_password(file_id):
            self.show_temp_popup("Credencial eliminada correctamente.", COLOR_SUCCESS)
            self.refresh_password_list()
        else:
            self.show_temp_popup("No fue posible eliminar la credencial.", COLOR_DANGER)

    def _close_view_modal(self):
        if self.view_modal and self.view_modal.winfo_exists():
            self.view_modal.destroy()
        self.view_modal = None

    def _open_view_modal(self, file_id: int, site: str, username: str):
        encrypted_content = self.controller.handle_get_encrypted_password(file_id)
        if not encrypted_content:
            self.show_temp_popup("No pudimos abrir la credencial. Intenta nuevamente.", COLOR_DANGER)
            return

        try:
            encrypted_text = encrypted_content.decode("utf-8").strip()
        except UnicodeDecodeError:
            encrypted_text = encrypted_content.decode("latin-1").strip()

        self._close_view_modal()
        modal, body = self.build_modal_shell(
            title="Detalle de credencial",
            subtitle="Comparte la versión cifrada o desbloquea la original.",
            badge="Vault seguro",
            width=660,
            height=580,
            close_command=self._close_view_modal,
        )
        self.view_modal = modal

        info = ctk.CTkFrame(body, fg_color=COLOR_CARD_SOFT, corner_radius=18)
        info.pack(fill="x", pady=(0, 18))
        info.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(info, text="Servicio", font=self.fonts["small"], text_color=COLOR_TEXT_MUTED).grid(
            row=0, column=0, sticky="w", padx=18, pady=(18, 0)
        )
        ctk.CTkLabel(info, text=site, font=self.fonts["section"], text_color=COLOR_TEXT_PRIMARY).grid(
            row=1, column=0, sticky="w", padx=18
        )

        ctk.CTkLabel(info, text="Usuario", font=self.fonts["small"], text_color=COLOR_TEXT_MUTED).grid(
            row=0, column=1, sticky="w", padx=18, pady=(18, 0)
        )
        ctk.CTkLabel(info, text=username, font=self.fonts["card_sub"], text_color=COLOR_TEXT_PRIMARY).grid(
            row=1, column=1, sticky="w", padx=18
        )

        encrypted_section = ctk.CTkFrame(body, fg_color="transparent")
        encrypted_section.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            encrypted_section,
            text="Clave cifrada",
            font=self.fonts["card_title"],
            text_color=COLOR_TEXT_PRIMARY,
        ).pack(anchor="w", pady=(0, 6))

        encrypted_box = ctk.CTkTextbox(
            encrypted_section,
            height=100,
            fg_color=COLOR_CARD_SOFT,
            border_width=0,
            font=self.fonts["body"],
            wrap="word",
        )
        encrypted_box.pack(fill="x")
        encrypted_box.insert("0.0", encrypted_text)
        encrypted_box.configure(state="disabled")

        def copy_encrypted():
            pyperclip.copy(encrypted_text)
            self.show_temp_popup("Clave cifrada copiada.", COLOR_SUCCESS)

        ctk.CTkButton(
            encrypted_section,
            text="Copiar clave cifrada",
            command=copy_encrypted,
            fg_color="transparent",
            hover_color="#F8FAFC",
            border_width=1,
            border_color=COLOR_BORDER,
            text_color=COLOR_TEXT_PRIMARY,
            font=self.fonts["button"],
        ).pack(anchor="e", pady=(10, 0))

        decrypt_section = ctk.CTkFrame(body, fg_color="transparent")
        decrypt_section.pack(fill="both", expand=True)

        ctk.CTkLabel(
            decrypt_section,
            text="Contraseña desencriptada",
            font=self.fonts["card_title"],
            text_color=COLOR_TEXT_PRIMARY,
        ).pack(anchor="w", pady=(0, 6))

        plain_entry = ctk.CTkEntry(
            decrypt_section,
            placeholder_text="Contraseña protegida",
            show="•",
            fg_color=COLOR_CARD_SOFT,
            border_width=1,
            border_color=COLOR_BORDER,
            corner_radius=14,
            font=self.fonts["body"],
            state="disabled",
        )
        plain_entry.pack(fill="x", pady=(0, 12))

        status_label = ctk.CTkLabel(decrypt_section, text="Desencriptando...", font=self.fonts["small"], text_color=COLOR_TEXT_MUTED)
        status_label.pack(anchor="w", pady=(0, 12))

        controls_row = ctk.CTkFrame(decrypt_section, fg_color="transparent")
        controls_row.pack(fill="x")

        decrypted_value: dict[str, Optional[str]] = {"value": None}
        is_visible = {"value": False}

        def update_plain_entry(value: str):
            plain_entry.configure(state="normal")
            plain_entry.delete(0, "end")
            plain_entry.insert(0, value)
            plain_entry.configure(state="disabled", show="•")

        def toggle_visibility():
            if not decrypted_value["value"]:
                return
            is_visible["value"] = not is_visible["value"]
            plain_entry.configure(state="normal")
            plain_entry.configure(show="" if is_visible["value"] else "•")
            plain_entry.configure(state="disabled")
            toggle_button.configure(text="Ocultar" if is_visible["value"] else "Mostrar")

        def copy_plain():
            if decrypted_value["value"]:
                pyperclip.copy(decrypted_value["value"])
                self.show_temp_popup("Clave original copiada.", COLOR_SUCCESS)

        toggle_button = ctk.CTkButton(
            controls_row,
            text="Mostrar",
            command=toggle_visibility,
            state="disabled",
            fg_color="transparent",
            hover_color="#F8FAFC",
            border_width=1,
            border_color=COLOR_BORDER,
            text_color=COLOR_TEXT_PRIMARY,
            font=self.fonts["button"],
        )
        toggle_button.pack(side="left", padx=(0, 8))

        copy_plain_button = ctk.CTkButton(
            controls_row,
            text="Copiar clave original",
            command=copy_plain,
            state="disabled",
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_DARK,
            text_color=COLOR_WHITE,
            font=self.fonts["button"],
        )
        copy_plain_button.pack(side="left")

        def auto_decrypt():
            # Automatically use master key from session - no user input required
            plaintext = self.controller.handle_decrypt_password(file_id, site, self.controller.master_key)
            if plaintext:
                decrypted_value["value"] = plaintext
                is_visible["value"] = False
                update_plain_entry(plaintext)
                toggle_button.configure(state="normal", text="Mostrar")
                copy_plain_button.configure(state="normal")
                status_label.configure(text="Contraseña desbloqueada.", text_color=COLOR_SUCCESS)
            else:
                decrypted_value["value"] = None
                toggle_button.configure(state="disabled", text="Mostrar")
                copy_plain_button.configure(state="disabled")
                update_plain_entry("")
                status_label.configure(text="Error al desencriptar. Verifica tu sesión.", text_color=COLOR_DANGER)

        # Automatically decrypt when modal opens
        auto_decrypt()

    def logout_action(self, event=None):
        self.controller.handle_logout()

    def show_status(self, message: str, target: str, color):
        if target != "save" or not self.status_label_save:
            return
        label = self.status_label_save
        label.configure(text=message)
        label.configure(text_color=color)
        label.after(4000, lambda lbl=label: lbl.configure(text=""))

    def show_temp_popup(self, message: str, color: str = COLOR_SUCCESS):
        toplevel = self.winfo_toplevel()
        if not isinstance(toplevel, ctk.CTk):
            return
        popup = ctk.CTkToplevel(toplevel)
        popup.title("EncryptU")
        popup.geometry("360x140")
        popup.resizable(False, False)
        popup.configure(fg_color=COLOR_CARD)

        label = ctk.CTkLabel(popup, text=message, font=self.fonts["card_title"], text_color=color, wraplength=320, justify="center")
        label.pack(expand=True, fill="both", padx=24, pady=32)

        popup.after(2400, popup.destroy)

    # ------------------------------------------------------------------
    # Ventanas modales
    # ------------------------------------------------------------------
    def _open_add_credential_modal(self):
        if self.add_modal and self.add_modal.winfo_exists():
            self.add_modal.focus_set()
            return

        modal, body = self.build_modal_shell(
            title="Guardar nueva credencial",
            subtitle="Tus datos se cifran antes de sincronizarse con la nube.",
            badge="Vault seguro",
            width=520,
            height=620,
            close_command=self._close_add_modal,
        )
        self.add_modal = modal

        highlight = ctk.CTkFrame(body, fg_color=COLOR_CARD_SOFT, corner_radius=18)
        highlight.pack(fill="x", pady=(0, 18))
        ctk.CTkLabel(
            highlight,
            text="Mantén tus claves organizadas y protegidas. Puedes editarlas cuando quieras.",
            font=self.fonts["body"],
            text_color=COLOR_TEXT_PRIMARY,
            wraplength=420,
            justify="left",
        ).pack(anchor="w", padx=18, pady=18)

        fields_wrapper = ctk.CTkFrame(body, fg_color="transparent")
        fields_wrapper.pack(fill="both", expand=True)

        def build_entry(*, label_text: str, placeholder: str, **entry_kwargs) -> ctk.CTkEntry:
            field = ctk.CTkFrame(fields_wrapper, fg_color="transparent")
            field.pack(fill="x", pady=(0, 14))

            ctk.CTkLabel(field, text=label_text, font=self.fonts["card_title"], text_color=COLOR_TEXT_PRIMARY).pack(
                anchor="w", pady=(0, 4)
            )

            entry = ctk.CTkEntry(
                field,
                placeholder_text=placeholder,
                fg_color=COLOR_CARD_SOFT,
                text_color=COLOR_TEXT_PRIMARY,
                border_color=COLOR_BORDER,
                border_width=1,
                corner_radius=14,
                height=44,
                font=self.fonts["body"],
                **entry_kwargs,
            )
            entry.pack(fill="x")
            return entry

        self.site_entry = build_entry(label_text="Servicio o app", placeholder="Servicio (ej. Instagram)")
        self.username_entry_save = build_entry(label_text="Usuario o correo", placeholder="Usuario o correo asociado")
        self.password_entry = build_entry(
            label_text="Contraseña cifrada",
            placeholder="Ingresa o pega tu contraseña",
            show="*",
        )

        ctk.CTkLabel(
            fields_wrapper,
            text="Tip: usa combinaciones únicas por servicio. Nosotros las guardamos cifradas.",
            font=self.fonts["small"],
            text_color=COLOR_TEXT_MUTED,
            wraplength=420,
            justify="left",
        ).pack(anchor="w", pady=(4, 0))

        buttons = ctk.CTkFrame(body, fg_color="transparent")
        buttons.pack(fill="x", pady=(18, 0))

        cancel = ctk.CTkButton(
            buttons,
            text="Cancelar",
            command=self._close_add_modal,
            fg_color="#FFFFFF",
            hover_color="#F8FAFC",
            border_width=1,
            border_color=COLOR_BORDER,
            text_color=COLOR_TEXT_MUTED,
            corner_radius=22,
            height=46,
            font=self.fonts["button"],
        )
        cancel.pack(side="left", padx=(0, 8), expand=True, fill="x")

        self.save_button = ctk.CTkButton(
            buttons,
            text="Guardar credencial",
            command=self.save_action,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_DARK,
            text_color=COLOR_WHITE,
            corner_radius=22,
            height=46,
            font=self.fonts["button"],
        )
        self.save_button.pack(side="right", padx=(8, 0), expand=True, fill="x")

    def _close_add_modal(self):
        if self.add_modal and self.add_modal.winfo_exists():
            self.add_modal.destroy()
        self.add_modal = None
        self.site_entry = None
        self.username_entry_save = None
        self.password_entry = None
        self.save_button = None

    # ------------------------------------------------------------------
    # Helpers de navegación y eventos
    # ------------------------------------------------------------------
    def _go_home(self):
        self.controller.show_main_view(self.username)

    def _go_profile(self):
        self.controller.show_profile_view(self.username)

    def _on_search_change(self, *_):
        self._filter_credentials()

    # ------------------------------------------------------------------
    # Exportar/Importar credenciales
    # ------------------------------------------------------------------
    def _export_passwords(self):
        """Exporta las credenciales a un archivo JSON."""
        if not self.credentials:
            self.show_temp_popup("No hay credenciales para exportar.", COLOR_DANGER)
            return

        try:
            # Obtener datos encriptados para cada credencial
            export_data = []
            for cred in self.credentials:
                file_id = cred.get("id")
                if file_id:
                    encrypted_content = self.controller.api_client.download_password_data(int(file_id))
                    if encrypted_content:
                        try:
                            encrypted_text = encrypted_content.decode("utf-8").strip()
                        except UnicodeDecodeError:
                            encrypted_text = encrypted_content.decode("latin-1").strip()
                        
                        export_data.append({
                            "site": cred.get("site", ""),
                            "username": cred.get("username", ""),
                            "encrypted_content": encrypted_text
                        })

            if not export_data:
                self.show_temp_popup("Error al obtener datos encriptados.", COLOR_DANGER)
                return

            # Generar archivo JSON
            from datetime import datetime
            import json
            
            export_dict = {
                "export_timestamp": datetime.now().isoformat(),
                "version": "1.0",
                "credentials": export_data
            }
            
            json_content = json.dumps(export_dict, indent=2, ensure_ascii=False)
            
            # Guardar archivo usando diálogo de guardado
            from tkinter import filedialog, messagebox
            import tkinter as tk
            
            root = self.winfo_toplevel()
            if hasattr(root, 'withdraw'):
                root.withdraw()  # Hide main window temporarily
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Exportar credenciales",
                initialfile=f"encryptu_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            if filename:
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(json_content)
                    self.show_temp_popup(f"Credenciales exportadas a {filename}", COLOR_SUCCESS)
                except Exception as e:
                    self.show_temp_popup(f"Error al guardar archivo: {str(e)}", COLOR_DANGER)
            
            if hasattr(root, 'deiconify'):
                root.deiconify()  # Restore main window
                
        except Exception as e:
            print(f"Error al exportar contraseñas: {e}")
            self.show_temp_popup("Error durante la exportación.", COLOR_DANGER)

    def _import_passwords(self):
        """Importa credenciales desde un archivo JSON."""
        try:
            from tkinter import filedialog, messagebox
            import tkinter as tk
            import json
            
            root = self.winfo_toplevel()
            if hasattr(root, 'withdraw'):
                root.withdraw()  # Hide main window temporarily
            
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Importar credenciales"
            )
            
            if not filename:
                if hasattr(root, 'deiconify'):
                    root.deiconify()  # Restore main window
                return
            
            # Leer archivo
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    file_content = f.read()
            except Exception as e:
                if hasattr(root, 'deiconify'):
                    root.deiconify()  # Restore main window
                self.show_temp_popup(f"Error al leer archivo: {str(e)}", COLOR_DANGER)
                return
            
            # Procesar importación
            try:
                data = json.loads(file_content)
            except json.JSONDecodeError:
                if hasattr(root, 'deiconify'):
                    root.deiconify()  # Restore main window
                self.show_temp_popup("Archivo JSON inválido.", COLOR_DANGER)
                return
            
            if hasattr(root, 'deiconify'):
                root.deiconify()  # Restore main window
            
            # Validar estructura
            if not isinstance(data, dict) or "credentials" not in data:
                self.show_temp_popup("Formato de archivo inválido.", COLOR_DANGER)
                return
            
            credentials = data.get("credentials", [])
            if not isinstance(credentials, list) or not credentials:
                self.show_temp_popup("No se encontraron credenciales en el archivo.", COLOR_DANGER)
                return
            
            # Importar credenciales
            success, errors = self.controller.handle_import_passwords(file_content)
            
            if success:
                self.show_temp_popup(f"Credenciales importadas exitosamente.", COLOR_SUCCESS)
                self.refresh_password_list()
            else:
                error_msg = "\n".join(errors[:3])  # Show first 3 errors
                if len(errors) > 3:
                    error_msg += f"\n... y {len(errors) - 3} errores más."
                self.show_temp_popup(f"Errores en la importación:\n{error_msg}", COLOR_DANGER)
                
        except Exception as e:
            print(f"Error al importar contraseñas: {e}")
            self.show_temp_popup("Error durante la importación.", COLOR_DANGER)
