import customtkinter as ctk
from datetime import datetime
from typing import Dict, List, Optional

import pyperclip
from PIL import Image

from .base_view import BaseView

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

BLACK_LOGO_PATH = "desktop/controllers/img/Blacklogo.png"

BADGE_COLOR_MAP = {
    "instagram": "#F472B6",
    "gmail": "#FB7185",
    "twitter": "#60A5FA",
    "figma": "#34D399",
    "facebook": "#3B82F6",
    "slack": "#A855F7",
}
BADGE_FALLBACK_COLORS = ["#60A5FA", "#FBBF24", "#34D399", "#F472B6"]


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
        self.add_modal: Optional[ctk.CTkToplevel] = None
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
            logo = Image.open(BLACK_LOGO_PATH)
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

        new_btn = ctk.CTkButton(
            actions,
            text="Nueva credencial",
            command=self._open_add_credential_modal,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_DARK,
            text_color=COLOR_WHITE,
            font=self.fonts["button"],
        )
        new_btn.grid(row=0, column=1, sticky="e")

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
            "• Usa la clave maestra para desencriptar solo cuando la necesites.\n"
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

            badge = ctk.CTkFrame(
                card,
                width=52,
                height=52,
                corner_radius=18,
                fg_color=self._badge_color_for_site(cred["site"]),
            )
            badge.grid(row=0, column=0, rowspan=2, padx=18, pady=18)
            badge.grid_propagate(False)

            badge_label = ctk.CTkLabel(badge, text=self._badge_initials(cred["site"]), font=self.fonts["badge"], text_color=COLOR_WHITE)
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
                command=lambda fid=int(cred["id"]), site=cred["site"]: self.view_copy_action(fid, site),
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

        site = self.site_entry.get().strip()  # type: ignore[union-attr]
        username = self.username_entry_save.get().strip()  # type: ignore[union-attr]
        password = self.password_entry.get().strip()  # type: ignore[union-attr]

        if not site or not username or not password:
            self.show_status("Completa todos los campos para continuar.", "save", COLOR_DANGER)
            return

        self.save_button.configure(state="disabled", text="Guardando...")  # type: ignore[union-attr]
        self.show_status("Guardando...", "save", COLOR_TEXT_MUTED)

        success = self.controller.handle_encrypt_and_save(site, username, password)

        if success:
            self.show_status(f"Credencial para '{site}' almacenada.", "save", COLOR_SUCCESS)
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

    def view_copy_action(self, file_id: int, site: str):
        dialog = ctk.CTkInputDialog(text="Para desencriptar ingresa tu clave maestra:", title="Verificación de seguridad")
        master_key = dialog.get_input()

        if master_key:
            decrypted = self.controller.handle_decrypt_password(file_id, site, master_key)
            if decrypted:
                pyperclip.copy(decrypted)
                self.show_temp_popup("Contraseña copiada al portapapeles.", COLOR_SUCCESS)
            else:
                self.show_temp_popup("Clave maestra incorrecta.", COLOR_DANGER)

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

        modal = ctk.CTkToplevel(self)
        self.add_modal = modal
        modal.title("Nueva credencial")
        modal.geometry("420x380")
        modal.resizable(False, False)

        container = ctk.CTkFrame(modal, fg_color=COLOR_CARD, corner_radius=18, border_width=1, border_color=COLOR_BORDER)
        container.pack(expand=True, fill="both", padx=24, pady=24)

        title = ctk.CTkLabel(container, text="Guardar nueva credencial", font=self.fonts["section"], text_color=COLOR_TEXT_PRIMARY)
        title.pack(anchor="w", pady=(0, 12))

        self.site_entry = ctk.CTkEntry(container, placeholder_text="Servicio (ej. Instagram)", fg_color=COLOR_CARD_SOFT, border_width=0, font=self.fonts["body"])
        self.site_entry.pack(fill="x", pady=6)

        self.username_entry_save = ctk.CTkEntry(container, placeholder_text="Usuario o correo", fg_color=COLOR_CARD_SOFT, border_width=0, font=self.fonts["body"])
        self.username_entry_save.pack(fill="x", pady=6)

        self.password_entry = ctk.CTkEntry(container, placeholder_text="Contraseña", show="*", fg_color=COLOR_CARD_SOFT, border_width=0, font=self.fonts["body"])
        self.password_entry.pack(fill="x", pady=6)

        buttons = ctk.CTkFrame(container, fg_color="transparent")
        buttons.pack(fill="x", pady=(18, 0))

        cancel = ctk.CTkButton(buttons, text="Cancelar", command=self._close_add_modal, fg_color="transparent", hover_color="#E5E7EB", text_color=COLOR_TEXT_MUTED, font=self.fonts["button"])
        cancel.pack(side="left")

        self.save_button = ctk.CTkButton(buttons, text="Guardar", command=self.save_action, fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_DARK, text_color=COLOR_WHITE, font=self.fonts["button"])
        self.save_button.pack(side="right")

        modal.protocol("WM_DELETE_WINDOW", self._close_add_modal)

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
