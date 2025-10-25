import customtkinter as ctk
from typing import Dict, Optional

from PIL import Image

COLOR_BACKGROUND = "#F3F5F9"
COLOR_TEXT = "#1F2933"
COLOR_TEXT_MUTED = "#6B7280"
COLOR_ACCENT = "#F43F5E"
COLOR_SURFACE = "#FFFFFF"
COLOR_BADGE = "#7C3AED"

GRADIENT_PATH = "desktop/controllers/img/bg_main.png"
HERO_HEIGHT = 300


from .base_view import BaseView

class ProfileView(BaseView):
    """Vista dedicada para mostrar el perfil del usuario y su suscripcion."""

    def __init__(self, master, controller, username: str):
        super().__init__(master, fg_color=COLOR_BACKGROUND)
        self.controller = controller
        self.username = username or "Usuario"
        self.hero_source = self._load_gradient()
        self.hero_image: Optional[ctk.CTkImage] = None
        self.hero_label: Optional[ctk.CTkLabel] = None
        self.fonts = self._build_fonts()

        self._build_layout()
        self.bind("<Configure>", self._handle_resize)

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def _build_fonts(self) -> Dict[str, ctk.CTkFont]:
        return {
            "title": ctk.CTkFont(size=38, weight="bold"),
            "subtitle": ctk.CTkFont(size=18),
            "body": ctk.CTkFont(size=14),
            "accent": ctk.CTkFont(size=16, weight="bold"),
            "button": ctk.CTkFont(size=15, weight="bold"),
        }

    def _load_gradient(self) -> Image.Image:
        try:
            return Image.open(GRADIENT_PATH)
        except Exception:
            gradient = Image.new("RGB", (1200, HERO_HEIGHT), COLOR_ACCENT)
            overlay = Image.new("RGB", (1200, HERO_HEIGHT), "#2D2A87")
            mask = Image.new("L", (1, HERO_HEIGHT))
            for y in range(HERO_HEIGHT):
                mask.putpixel((0, y), int(255 * (y / max(HERO_HEIGHT - 1, 1))))
            mask = mask.resize((1200, HERO_HEIGHT))
            return Image.composite(overlay, gradient, mask)

    def _build_layout(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_hero_section()
        self._build_body()

    def _build_hero_section(self):
        hero = ctk.CTkFrame(self, fg_color="transparent")
        hero.grid(row=0, column=0, sticky="nsew")
        hero.grid_propagate(False)
        hero.configure(height=HERO_HEIGHT)

        self.hero_image = ctk.CTkImage(self.hero_source, size=(self.hero_source.width, HERO_HEIGHT))
        self.hero_label = ctk.CTkLabel(hero, text="", image=self.hero_image)
        self.hero_label.place(relx=0, rely=0, relwidth=1, relheight=1)

        content = ctk.CTkFrame(hero, fg_color="transparent")
        content.pack(expand=True, fill="both", padx=36, pady=24)
        content.grid_columnconfigure(0, weight=1)

        back_button = ctk.CTkButton(
            content,
            text="<- Volver al inicio",
            command=lambda: self.controller.show_main_view(self.username),
            fg_color="transparent",
            hover_color="#2B2B2B",
            text_color="#F9FAFB",
            font=self.fonts["button"],
        )
        back_button.grid(row=0, column=0, sticky="w", pady=(0, 12))

        avatar_wrapper = ctk.CTkFrame(content, fg_color="#FFFFFF", width=200, height=200, corner_radius=100)
        avatar_wrapper.grid(row=1, column=0, pady=(10, 18))
        avatar_wrapper.grid_propagate(False)

        inner_avatar = ctk.CTkFrame(avatar_wrapper, fg_color="#6D28D9", width=170, height=170, corner_radius=85)
        inner_avatar.place(relx=0.5, rely=0.5, anchor="center")
        inner_avatar.grid_propagate(False)

        initials = ctk.CTkLabel(
            inner_avatar,
            text=self._user_initials(self.username),
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color="#F8FAFC",
        )
        initials.place(relx=0.5, rely=0.5, anchor="center")

    def _build_body(self):
        body = ctk.CTkFrame(self, fg_color=COLOR_BACKGROUND)
        body.grid(row=1, column=0, sticky="nsew", padx=36, pady=(0, 32))
        body.grid_rowconfigure(1, weight=1)
        body.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(body, fg_color=COLOR_SURFACE, corner_radius=24)
        card.grid(row=0, column=0, sticky="nsew", padx=0, pady=(0, 24))
        card.grid_columnconfigure(0, weight=1)

        name_label = ctk.CTkLabel(
            card,
            text=self._format_username(self.username),
            font=self.fonts["title"],
            text_color=COLOR_TEXT,
        )
        name_label.grid(row=0, column=0, pady=(32, 4))

        email_label = ctk.CTkLabel(
            card,
            text=self.username,
            font=self.fonts["subtitle"],
            text_color=COLOR_TEXT_MUTED,
        )
        email_label.grid(row=1, column=0, pady=(0, 24))

        subscription_badge = ctk.CTkFrame(card, fg_color="#F1F3FF", corner_radius=18)
        subscription_badge.grid(row=2, column=0, padx=40, pady=(0, 24), sticky="ew")
        subscription_badge.grid_columnconfigure(1, weight=1)

        badge_icon = ctk.CTkLabel(
            subscription_badge,
            text="*",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLOR_BADGE,
        )
        badge_icon.grid(row=0, column=0, padx=(18, 12), pady=18)

        badge_text = ctk.CTkLabel(
            subscription_badge,
            text="Suscripcion Activa",
            font=self.fonts["accent"],
            text_color=COLOR_TEXT,
        )
        badge_text.grid(row=0, column=1, sticky="w")

        cancel_button = ctk.CTkButton(
            card,
            text="Cancelar Suscripcion",
            command=lambda: self._show_notification("Un asesor se pondra en contacto contigo."),
            fg_color="transparent",
            hover_color="#FFE4E6",
            text_color=COLOR_ACCENT,
            font=self.fonts["button"],
        )
        cancel_button.grid(row=3, column=0, pady=(0, 24))

        logout_button = ctk.CTkButton(
            card,
            text="Cerrar Sesion",
            command=self.controller.handle_logout,
            fg_color="transparent",
            hover_color="#F3F4F6",
            text_color=COLOR_ACCENT,
            font=self.fonts["button"],
        )
        logout_button.grid(row=4, column=0, pady=(0, 32))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _handle_resize(self, event):
        if event.widget is self and self.hero_label and self.hero_source:
            width = max(event.width, 800)
            resized = self.hero_source.resize((width, HERO_HEIGHT))
            self.hero_image = ctk.CTkImage(resized, size=(width, HERO_HEIGHT))
            self.hero_label.configure(image=self.hero_image)

    def _show_notification(self, message: str):
        toplevel = self.winfo_toplevel()
        if not isinstance(toplevel, ctk.CTk):
            return
        popup = ctk.CTkToplevel(toplevel)
        popup.title("EncryptU")
        popup.geometry("360x160")
        popup.resizable(False, False)
        popup.configure(fg_color=COLOR_SURFACE)

        label = ctk.CTkLabel(
            popup,
            text=message,
            font=self.fonts["body"],
            text_color=COLOR_TEXT,
            wraplength=320,
            justify="center",
        )
        label.pack(expand=True, fill="both", padx=24, pady=30)

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

