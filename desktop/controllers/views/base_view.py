import customtkinter as ctk
from PIL import Image

LOGO_PATH = "desktop/controllers/img/Blacklogo.png"

COLOR_BACKGROUND = "#F4F6FB"
COLOR_ACCENT = "#EE5A72"
COLOR_ACCENT_DARK = "#D9435C"
COLOR_TEXT_PRIMARY = "#0F172A"
COLOR_TEXT_MUTED = "#94A3B8"


class BaseView(ctk.CTkFrame):
    """Base estilizada para todas las vistas EncryptU."""

    MIN_WIDTH = 1200
    MIN_HEIGHT = 720
    MAX_WIDTH = 1200
    MAX_HEIGHT = 720

    def __init__(self, master, *args, **kwargs):
        kwargs.setdefault("fg_color", COLOR_BACKGROUND)
        super().__init__(master, *args, **kwargs)
        self.base_fonts = self._build_base_fonts()
        self.logo_image = self._load_logo_image()
        self._configure_window_limits()

    # ------------------------------------------------------------------
    # Branding compartido
    # ------------------------------------------------------------------
    def _build_base_fonts(self) -> dict[str, ctk.CTkFont]:
        return {
            "hero_title": ctk.CTkFont(family="Arial", size=40, weight="bold"),
            "hero_sub": ctk.CTkFont(family="Arial", size=18),
            "badge": ctk.CTkFont(size=12, weight="bold"),
            "button": ctk.CTkFont(size=15, weight="bold"),
        }

    def _load_logo_image(self) -> ctk.CTkImage:
        try:
            logo = Image.open(LOGO_PATH)
            target_height = 110
            aspect_ratio = logo.width / logo.height if logo.height else 1
            size = (int(target_height * aspect_ratio), target_height)
            return ctk.CTkImage(light_image=logo, dark_image=logo, size=size)
        except Exception:
            placeholder = Image.new("RGBA", (360, 110), (0, 0, 0, 0))
            return ctk.CTkImage(light_image=placeholder, dark_image=placeholder, size=(360, 110))

    def build_header(
        self,
        *,
        title: str,
        subtitle: str = "",
        badge: str | None = None,
        back_command=None,
    ) -> ctk.CTkFrame:
        """Construye un encabezado consistente con el diseño de soporte/vault."""
        header = ctk.CTkFrame(self, fg_color=COLOR_BACKGROUND)
        header.grid_columnconfigure(1, weight=1)
        header.grid_columnconfigure(2, weight=0)

        if back_command:
            ctk.CTkButton(
                header,
                text="<",
                command=back_command,
                fg_color="transparent",
                hover_color="#E2E8F0",
                text_color=COLOR_ACCENT,
                font=self.base_fonts["button"],
                width=44,
                height=44,
                corner_radius=16,
                border_width=1,
                border_color=COLOR_ACCENT,
            ).grid(row=0, column=0, rowspan=2, sticky="w")

        title_block = ctk.CTkFrame(header, fg_color="transparent")
        title_block.grid(row=0, column=1, sticky="w", padx=(16, 0))
        title_block.grid_columnconfigure(0, weight=1)

        if badge:
            ctk.CTkLabel(title_block, text=badge, font=self.base_fonts["badge"], text_color=COLOR_TEXT_MUTED).grid(
                row=0, column=0, sticky="w"
            )

        ctk.CTkLabel(title_block, text=title, font=self.base_fonts["hero_title"], text_color=COLOR_TEXT_PRIMARY).grid(
            row=1, column=0, sticky="w"
        )

        if subtitle:
            ctk.CTkLabel(header, text=subtitle, font=self.base_fonts["hero_sub"], text_color=COLOR_TEXT_MUTED).grid(
                row=1, column=1, sticky="w", padx=(16, 0)
            )

        ctk.CTkLabel(header, text="", image=self.logo_image).grid(row=0, column=2, rowspan=2, sticky="e")
        return header

    # ------------------------------------------------------------------
    # Control de ventana
    # ------------------------------------------------------------------
    def _configure_window_limits(self):
        root = self.winfo_toplevel()
        if not isinstance(root, ctk.CTk):
            return

        if getattr(root, "_size_limits_configured", False):
            return
        setattr(root, "_size_limits_configured", True)

        current_width = root.winfo_width() or self.MIN_WIDTH
        current_height = root.winfo_height() or self.MIN_HEIGHT

        width = max(self.MIN_WIDTH, min(current_width, self.MAX_WIDTH))
        height = max(self.MIN_HEIGHT, min(current_height, self.MAX_HEIGHT))
        root.geometry(f"{width}x{height}")

        try:
            root.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)
            root.maxsize(self.MAX_WIDTH, self.MAX_HEIGHT)
        except Exception:
            pass

        def enforce_limits():
            w, h = root.winfo_width(), root.winfo_height()
            clamped_w = max(self.MIN_WIDTH, min(w, self.MAX_WIDTH))
            clamped_h = max(self.MIN_HEIGHT, min(h, self.MAX_HEIGHT))
            if clamped_w != w or clamped_h != h:
                root.geometry(f"{clamped_w}x{clamped_h}")
            root.after(120, enforce_limits)

        root.after(120, enforce_limits)
