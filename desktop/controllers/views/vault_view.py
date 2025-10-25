import customtkinter as ctk
from datetime import datetime
from typing import Dict, List, Optional

import pyperclip
from PIL import Image

# --- Colores base para replicar el estilo de los mockups ---
COLOR_BACKGROUND = "#F3F5F9"
COLOR_WHITE = "#FFFFFF"
COLOR_MUTED = "#6B7280"
COLOR_TEXT_DARK = "#1F2933"
COLOR_TEXT_LIGHT = "#F9FAFB"
COLOR_ACCENT = "#F43F5E"
COLOR_ACCENT_DARK = "#DC1F45"
COLOR_FAB = "#2563EB"
COLOR_FAB_HOVER = "#1D4ED8"
COLOR_CARD_BORDER = "#E2E8F0"
COLOR_HIGHLIGHT = "#C7D2FE"
COLOR_SUCCESS = "#047857"
COLOR_ERROR = "#B91C1C"

GRADIENT_START = "#FF5A5F"
GRADIENT_END = "#2D2A87"
HERO_HEIGHT = 240

BADGE_COLOR_MAP = {
    "instagram": "#F472B6",
    "gmail": "#F87171",
    "twitter": "#60A5FA",
    "figma": "#34D399",
    "facebook": "#3B82F6",
    "slack": "#A855F7",
}
BADGE_FALLBACK_COLORS = ["#60A5FA", "#FBBF24", "#34D399", "#F472B6"]


from .base_view import BaseView

class VaultView(BaseView):
    """Vista dedicada para guardar, encriptar y listar credenciales del usuario."""

    def __init__(self, master, controller, username: str):
        super().__init__(master, fg_color=COLOR_BACKGROUND)

        self.controller = controller
        self.username = username or "Usuario"

        self.fonts = self._build_fonts()
        self.password_count_var = ctk.StringVar(value="0")
        self.status_label_save: Optional[ctk.CTkLabel] = None
        self.status_message = ""
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self._on_search_change)

        self.credentials: List[Dict[str, str]] = []
        self.filtered_credentials: List[Dict[str, str]] = []

        self.scrollable_frame: Optional[ctk.CTkScrollableFrame] = None
        self.hero_bg_label: Optional[ctk.CTkLabel] = None
        self.hero_bg_image: Optional[ctk.CTkImage] = None
        self.hero_bg_source = self._load_background_image()
        self._hero_bg_width = 0

        # Referencias para el modal de nueva credencial
        self.add_modal: Optional[ctk.CTkToplevel] = None
        self.site_entry: Optional[ctk.CTkEntry] = None
        self.username_entry_save: Optional[ctk.CTkEntry] = None
        self.password_entry: Optional[ctk.CTkEntry] = None
        self.save_button: Optional[ctk.CTkButton] = None


        self._build_layout()
        self.bind("<Configure>", self._on_resize)

        # Se espera un corto tiempo antes de cargar datos para asegurar que la UI este lista.
        self.after(150, self.refresh_password_list)

    # ------------------------------------------------------------------
    # Construccion de UI
    # ------------------------------------------------------------------
    def _build_fonts(self) -> Dict[str, ctk.CTkFont]:
        return {
            "hero_title": ctk.CTkFont(size=46, weight="bold"),
            "hero_sub": ctk.CTkFont(size=16),
            "search": ctk.CTkFont(size=14),
            "section": ctk.CTkFont(size=20, weight="bold"),
            "card_title": ctk.CTkFont(size=16, weight="bold"),
            "card_sub": ctk.CTkFont(size=13),
            "card_icon": ctk.CTkFont(size=15, weight="bold"),
            "body": ctk.CTkFont(size=13),
            "button": ctk.CTkFont(size=14, weight="bold"),
            "brand": ctk.CTkFont(size=22, weight="bold"),
        }

    def _load_background_image(self) -> Image.Image:
        try:
            return Image.open("desktop/controllers/img/bg_main.png")
        except Exception:
            return self._create_gradient_image(1200, HERO_HEIGHT)

    def _create_gradient_image(self, width: int, height: int) -> Image.Image:
        base = Image.new("RGB", (width, height), color=GRADIENT_START)
        top = Image.new("RGB", (width, height), color=GRADIENT_END)
        mask = Image.new("L", (1, height))
        for y in range(height):
            mask.putpixel((0, y), int(255 * (y / max(height - 1, 1))))
        mask = mask.resize((width, height))
        return Image.composite(top, base, mask)

    def _build_layout(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_hero_section()
        self._build_content_section()

    def _build_hero_section(self):
        hero_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        hero_frame.grid(row=0, column=0, sticky="nsew")
        hero_frame.grid_propagate(False)
        hero_frame.configure(height=HERO_HEIGHT)

        self.hero_bg_image = ctk.CTkImage(self.hero_bg_source, size=(self.hero_bg_source.width, HERO_HEIGHT))
        self.hero_bg_label = ctk.CTkLabel(hero_frame, text="", image=self.hero_bg_image)
        self.hero_bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)

        hero_content = ctk.CTkFrame(hero_frame, fg_color="transparent")
        hero_content.pack(expand=True, fill="both", padx=36, pady=24)
        hero_content.grid_columnconfigure(0, weight=3)
        hero_content.grid_columnconfigure(1, weight=2)
        hero_content.grid_columnconfigure(2, weight=1)
        hero_content.grid_rowconfigure((0, 1, 2, 3), weight=0)

        back_button = ctk.CTkButton(
            hero_content,
            text="<- Volver al inicio",
            command=self._go_home,
            fg_color="transparent",
            hover_color="#2B2B2B",
            text_color=COLOR_TEXT_LIGHT,
            font=self.fonts["button"],
        )
        back_button.grid(row=0, column=0, sticky="w", pady=(0, 12))

        title = ctk.CTkLabel(
            hero_content,
            text="Tu boveda segura",
            font=self.fonts["hero_title"],
            text_color=COLOR_TEXT_LIGHT,
            justify="left",
        )
        title.grid(row=1, column=0, sticky="w")

        subtitle = ctk.CTkLabel(
            hero_content,
            text="Gestiona, almacena y encripta tus credenciales confidenciales.",
            font=self.fonts["hero_sub"],
            text_color=COLOR_TEXT_LIGHT,
        )
        subtitle.grid(row=2, column=0, sticky="w", pady=(12, 0))

        self._build_search_box(hero_content)
        self._build_user_card(hero_content)

    def _build_search_box(self, parent: ctk.CTkFrame):
        search_box = ctk.CTkFrame(parent, fg_color="#1A1A1A", corner_radius=24)
        search_box.grid(row=1, column=1, sticky="ew", padx=(24, 12), pady=(0, 12))
        search_box.grid_columnconfigure(1, weight=1)

        search_label = ctk.CTkLabel(search_box, text="Search", font=self.fonts["search"], text_color=COLOR_TEXT_LIGHT)
        search_label.grid(row=0, column=0, padx=(20, 12), pady=18)

        search_entry = ctk.CTkEntry(
            search_box,
            textvariable=self.search_var,
            placeholder_text="Buscar credenciales",
            font=self.fonts["search"],
            border_width=0,
            fg_color="transparent",
            text_color=COLOR_TEXT_LIGHT,
        )
        search_entry.grid(row=0, column=1, sticky="ew", pady=18)

        search_button = ctk.CTkButton(
            search_box,
            text="Buscar",
            command=self._on_search_submit,
            width=90,
            fg_color="#3F4868",
            hover_color="#2D3450",
            text_color=COLOR_TEXT_LIGHT,
            font=self.fonts["button"],
        )
        search_button.grid(row=0, column=2, padx=(0, 20), pady=12)

        self.status_label_save = ctk.CTkLabel(
            parent,
            text="",
            font=self.fonts["search"],
            text_color=COLOR_TEXT_LIGHT,
        )
        self.status_label_save.grid(row=2, column=1, sticky="w", padx=(24, 12))

        sync_label = ctk.CTkLabel(
            parent,
            text=f"Ultima sincronizacion: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            font=self.fonts["search"],
            text_color=COLOR_TEXT_LIGHT,
        )
        sync_label.grid(row=3, column=1, sticky="w", padx=(24, 12))

    def _build_user_card(self, parent: ctk.CTkFrame):
        card = ctk.CTkFrame(parent, fg_color="#FFFFFF", corner_radius=20)
        card.grid(row=1, column=2, rowspan=2, sticky="ne", padx=(12, 0))
        card.grid_columnconfigure(1, weight=1)

        avatar = ctk.CTkButton(
            card,
            text=self._get_initials(self.username),
            width=54,
            height=54,
            fg_color=COLOR_WHITE,
            text_color=COLOR_ACCENT,
            font=self.fonts["card_title"],
            corner_radius=26,
            hover_color=COLOR_HIGHLIGHT,
            command=self._go_profile,
        )
        avatar.grid(row=0, column=0, padx=16, pady=16)

        name_label = ctk.CTkLabel(card, text=self._format_username(self.username), font=self.fonts["card_title"], text_color=COLOR_TEXT_LIGHT)
        name_label.grid(row=0, column=1, sticky="e", padx=(0, 18), pady=(18, 0))

        email_label = ctk.CTkLabel(card, text=self.username, font=self.fonts["card_sub"], text_color=COLOR_TEXT_LIGHT)
        email_label.grid(row=1, column=1, sticky="e", padx=(0, 18))

        profile_button = ctk.CTkButton(
            card,
            text="Ver perfil",
            command=self._go_profile,
            fg_color="transparent",
            hover_color="#2B2B2B",
            text_color=COLOR_TEXT_LIGHT,
            font=self.fonts["button"],
        )
        profile_button.grid(row=2, column=0, columnspan=2, padx=16, pady=(0, 16))

    def _build_content_section(self):
        content_frame = ctk.CTkFrame(self, fg_color=COLOR_BACKGROUND)
        content_frame.grid(row=1, column=0, sticky="nsew")
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=0)
        content_frame.grid_columnconfigure(0, weight=1)

        self._build_recent_credentials(content_frame)
        self._build_footer(content_frame)

    def _build_recent_credentials(self, parent: ctk.CTkFrame):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.grid(row=0, column=0, sticky="nsew", padx=36, pady=(24, 0))
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(header, text="Agregadas Recientemente", font=self.fonts["section"], text_color=COLOR_TEXT_DARK)
        title.grid(row=0, column=0, sticky="w")

        count_label = ctk.CTkLabel(
            header,
            textvariable=self.password_count_var,
            font=self.fonts["card_title"],
            text_color=COLOR_MUTED,
        )
        count_label.grid(row=0, column=1, sticky="e")

        self.scrollable_frame = ctk.CTkScrollableFrame(container, fg_color="transparent")
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", pady=(16, 0))
        self.scrollable_frame.grid_columnconfigure(0, weight=1, uniform="cards")
        self.scrollable_frame.grid_columnconfigure(1, weight=1, uniform="cards")

    def _build_footer(self, parent: ctk.CTkFrame):
        footer = ctk.CTkFrame(parent, fg_color="transparent")
        footer.grid(row=1, column=0, sticky="ew", padx=36, pady=(24, 32))
        footer.grid_columnconfigure(0, weight=1)
        footer.grid_columnconfigure(1, weight=0)

        brand_frame = ctk.CTkFrame(footer, fg_color="transparent")
        brand_frame.grid(row=0, column=0, sticky="w")

        logo_label = ctk.CTkLabel(
            brand_frame,
            text="EU",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COLOR_ACCENT,
        )
        logo_label.pack(side="left")

        brand_text = ctk.CTkLabel(
            brand_frame,
            text="EncryptU",
            font=self.fonts["brand"],
            text_color=COLOR_TEXT_DARK,
        )
        brand_text.pack(side="left", padx=(12, 0))

        logout_button = ctk.CTkButton(
            brand_frame,
            text="Cerrar Sesion",
            command=self.logout_action,
            fg_color="transparent",
            hover_color="#E5E7EB",
            text_color=COLOR_ACCENT,
            font=self.fonts["button"],
        )
        logout_button.pack(side="left", padx=(24, 0))

        fab_button = ctk.CTkButton(
            footer,
            text="+",
            width=64,
            height=64,
            corner_radius=32,
            fg_color=COLOR_FAB,
            hover_color=COLOR_FAB_HOVER,
            text_color=COLOR_TEXT_LIGHT,
            font=ctk.CTkFont(size=34, weight="bold"),
            command=self._open_add_credential_modal,
        )
        fab_button.grid(row=0, column=1, sticky="e")

    # ------------------------------------------------------------------
    # Datos y renderizado
    # ------------------------------------------------------------------
    def refresh_password_list(self):
        if not self.scrollable_frame:
            return

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        passwords = self.controller.get_saved_passwords()

        if passwords is None:
            self.password_count_var.set("--")
            self._show_empty_state("No se pudieron obtener las credenciales. Inicia sesion nuevamente.")
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
        self.password_count_var.set(str(len(parsed)))
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
                cred
                for cred in self.credentials
                if query in cred["site"].lower() or query in cred["username"].lower()
            ]
        if force_render or self.scrollable_frame:
            self._render_credential_cards()

    def _render_credential_cards(self):
        if not self.scrollable_frame:
            return

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not self.filtered_credentials:
            self._show_empty_state("No encontramos resultados para tu busqueda.")
            return

        columns = 2
        for index, cred in enumerate(self.filtered_credentials):
            row = index // columns
            column = index % columns
            card = ctk.CTkFrame(self.scrollable_frame, fg_color=COLOR_WHITE, corner_radius=18, border_width=1, border_color=COLOR_CARD_BORDER)
            card.grid(row=row, column=column, padx=12, pady=10, sticky="nsew")
            card.grid_columnconfigure(1, weight=1)

            badge = ctk.CTkFrame(card, width=54, height=54, corner_radius=16, fg_color=self._badge_color_for_site(cred["site"]))
            badge.grid(row=0, column=0, rowspan=2, padx=16, pady=16)
            badge.grid_propagate(False)
            badge_label = ctk.CTkLabel(badge, text=self._badge_initials(cred["site"]), font=self.fonts["card_icon"], text_color=COLOR_TEXT_LIGHT)
            badge_label.place(relx=0.5, rely=0.5, anchor="center")

            title = ctk.CTkLabel(card, text=cred["site"], font=self.fonts["card_title"], text_color=COLOR_TEXT_DARK)
            title.grid(row=0, column=1, sticky="w", pady=(18, 0))

            subtitle = ctk.CTkLabel(card, text=cred["username"], font=self.fonts["card_sub"], text_color=COLOR_MUTED)
            subtitle.grid(row=1, column=1, sticky="w", pady=(0, 18))

            actions = ctk.CTkFrame(card, fg_color="transparent")
            actions.grid(row=0, column=2, rowspan=2, padx=16, pady=16, sticky="e")

            view_button = ctk.CTkButton(
                actions,
                text="Ver",
                width=72,
                fg_color="transparent",
                hover_color="#F3F4FF",
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
                width=72,
                fg_color=COLOR_ACCENT,
                hover_color=COLOR_ACCENT_DARK,
                text_color=COLOR_TEXT_LIGHT,
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
        if not self.scrollable_frame:
            return
        label = ctk.CTkLabel(self.scrollable_frame, text=message, font=self.fonts["body"], text_color=COLOR_MUTED, justify="center")
        label.grid(row=0, column=0, columnspan=2, padx=24, pady=40)

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
            self.show_status("Completa todos los campos para continuar.", "save", COLOR_ERROR)
            return

        self.save_button.configure(state="disabled", text="Guardando...")  # type: ignore[union-attr]
        self.show_status("Guardando...", "save", COLOR_MUTED)

        success = self.controller.handle_encrypt_and_save(site, username, password)

        if success:
            self.show_status(f"Credencial para '{site}' almacenada.", "save", COLOR_SUCCESS)
            self.refresh_password_list()
            self._close_add_modal()
        else:
            self.show_status("Ocurrio un error al guardar. Intenta de nuevo.", "save", COLOR_ERROR)

        if self.save_button:
            self.save_button.configure(state="normal", text="Guardar")

    def delete_action(self, file_id: int):
        if self.controller.handle_delete_password(file_id):
            self.show_temp_popup("Credencial eliminada correctamente.", "green")
            self.refresh_password_list()
        else:
            self.show_temp_popup("No fue posible eliminar la credencial.", COLOR_ERROR)

    def view_copy_action(self, file_id: int, site: str):
        dialog = ctk.CTkInputDialog(text="Para desencriptar ingresa tu clave maestra:", title="Verificacion de seguridad")
        master_key = dialog.get_input()

        if master_key:
            decrypted = self.controller.handle_decrypt_password(file_id, site, master_key)
            if decrypted:
                pyperclip.copy(decrypted)
                self.show_temp_popup("Contrasena copiada al portapapeles.", COLOR_SUCCESS)
            else:
                self.show_temp_popup("Clave maestra incorrecta.", COLOR_ERROR)

    def logout_action(self, event=None):
        self.controller.handle_logout()

    def show_status(self, message: str, target: str, color):
        if target != "save" or not self.status_label_save:
            return
        label = self.status_label_save  # keep a local strong reference so it's not treated as Optional in callbacks
        label.configure(text=message)
        if isinstance(color, tuple):
            label.configure(text_color=color[0])
        else:
            label.configure(text_color=color)
        label.after(4000, lambda lbl=label: lbl.configure(text=""))

    def show_temp_popup(self, message: str, color: str = "green"):
        toplevel = self.winfo_toplevel()
        if not isinstance(toplevel, ctk.CTk):
            return
        popup = ctk.CTkToplevel(toplevel)
        popup.title("EncryptU")
        popup.geometry("360x140")
        popup.resizable(False, False)
        popup.configure(fg_color=COLOR_WHITE)

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
        modal.geometry("420x360")
        modal.resizable(False, False)

        container = ctk.CTkFrame(modal, fg_color=COLOR_WHITE, corner_radius=18)
        container.pack(expand=True, fill="both", padx=24, pady=24)

        title = ctk.CTkLabel(container, text="Guardar nueva credencial", font=self.fonts["section"], text_color=COLOR_TEXT_DARK)
        title.pack(anchor="w", pady=(0, 12))

        self.site_entry = ctk.CTkEntry(container, placeholder_text="Servicio (ej. Instagram)", fg_color=COLOR_BACKGROUND, border_width=0, font=self.fonts["body"])
        self.site_entry.pack(fill="x", pady=6)

        self.username_entry_save = ctk.CTkEntry(container, placeholder_text="Usuario o correo", fg_color=COLOR_BACKGROUND, border_width=0, font=self.fonts["body"])
        self.username_entry_save.pack(fill="x", pady=6)

        self.password_entry = ctk.CTkEntry(container, placeholder_text="Contrasena", show="*", fg_color=COLOR_BACKGROUND, border_width=0, font=self.fonts["body"])
        self.password_entry.pack(fill="x", pady=6)

        buttons = ctk.CTkFrame(container, fg_color="transparent")
        buttons.pack(fill="x", pady=(18, 0))

        cancel = ctk.CTkButton(buttons, text="Cancelar", command=self._close_add_modal, fg_color="transparent", hover_color="#E5E7EB", text_color=COLOR_MUTED, font=self.fonts["button"])
        cancel.pack(side="left")

        self.save_button = ctk.CTkButton(buttons, text="Guardar", command=self.save_action, fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_DARK, text_color=COLOR_TEXT_LIGHT, font=self.fonts["button"])
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

    def _go_home(self):
        self.controller.show_main_view(self.username)

    def _go_profile(self):
        self.controller.show_profile_view(self.username)

    # ------------------------------------------------------------------
    # Eventos y helpers
    # ------------------------------------------------------------------
    def _on_resize(self, event):
        if event.widget is self:
            width = max(event.width, 800)
            if width != self._hero_bg_width and self.hero_bg_label and self.hero_bg_source:
                self._hero_bg_width = width
                resized = self.hero_bg_source.resize((width, HERO_HEIGHT))
                self.hero_bg_image = ctk.CTkImage(resized, size=(width, HERO_HEIGHT))
                self.hero_bg_label.configure(image=self.hero_bg_image)
                # store a reference to the image to prevent it from being garbage collected
                # use setattr to avoid static type checker errors about unknown attributes
                setattr(self.hero_bg_label, "image", self.hero_bg_image)

    def _on_search_change(self, *_):
        self._filter_credentials()

    def _on_search_submit(self):
        self._filter_credentials()

    def _format_username(self, value: str) -> str:
        if "@" in value:
            value = value.split("@", 1)[0]
        return value.title()

    def _get_initials(self, value: str) -> str:
        if not value:
            return "EU"
        if "@" in value:
            value = value.split("@", 1)[0]
        parts = [part for part in value.replace("_", " ").replace(".", " ").split() if part]
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        return value[:2].upper()
