import customtkinter as ctk
from PIL import Image
from typing import Callable, Optional, Union
from desktop.config import resource_path

LOGO_PATH = None

COLOR_BACKGROUND = "#F4F6FB"
COLOR_ACCENT = "#EE5A72"
COLOR_ACCENT_DARK = "#D9435C"
COLOR_TEXT_PRIMARY = "#0F172A"
COLOR_TEXT_MUTED = "#94A3B8"


WindowType = Union[ctk.CTk, ctk.CTkToplevel]


class BaseView(ctk.CTkFrame):
    """Base estilizada para todas las vistas EncryptU."""

    MIN_WIDTH = 1200
    MIN_HEIGHT = 720
    MAX_WIDTH = 1200
    MAX_HEIGHT = 1200

    def __init__(self, master, *args, **kwargs):
        kwargs.setdefault("fg_color", COLOR_BACKGROUND)
        super().__init__(master, *args, **kwargs)
        self.base_fonts = self._build_base_fonts()
        self.logo_image = self._load_logo_image()
        self._configure_window_limits()
        self._register_drag_handle(self, direct_only=True)

    # ------------------------------------------------------------------
    # Branding compartido
    # ------------------------------------------------------------------
    def _build_base_fonts(self) -> dict[str, ctk.CTkFont]:
        return {
            "hero_title": ctk.CTkFont(family="Arial", size=40, weight="bold"),
            "hero_sub": ctk.CTkFont(family="Arial", size=18),
            "modal_title": ctk.CTkFont(family="Arial", size=26, weight="bold"),
            "modal_sub": ctk.CTkFont(family="Arial", size=15),
            "badge": ctk.CTkFont(size=12, weight="bold"),
            "button": ctk.CTkFont(size=15, weight="bold"),
        }

    def _load_logo_image(self) -> ctk.CTkImage:
        try:
            path = resource_path("controllers/img/Blacklogo.png")
            logo = Image.open(path)
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
        self._register_drag_handle(header)
        return header

    def build_modal_shell(
        self,
        *,
        title: str,
        subtitle: str = "",
        badge: str | None = None,
        width: int = 520,
        height: int = 520,
        grab_focus: bool = True,
        close_command: Optional[Callable[[], None]] = None,
    ) -> tuple[ctk.CTkToplevel, ctk.CTkFrame]:
        """Crea un modal con el estilo EncryptU y retorna la ventana junto a su contenedor interno."""
        parent_widget = self.winfo_toplevel()
        host = parent_widget if isinstance(parent_widget, ctk.CTk) else self
        transient_master: ctk.CTk | None = parent_widget if isinstance(parent_widget, ctk.CTk) else None

        modal = ctk.CTkToplevel(host)
        modal.title(title)
        modal.geometry(f"{width}x{height}")
        modal.resizable(True, True)
        modal.configure(fg_color=COLOR_BACKGROUND)
        if transient_master:
            modal.transient(transient_master)
        self._make_borderless_window(modal)

        close_action = close_command if callable(close_command) else modal.destroy

        wrapper = ctk.CTkFrame(modal, fg_color=COLOR_BACKGROUND)
        wrapper.pack(expand=True, fill="both", padx=14, pady=14)

        card = ctk.CTkFrame(wrapper, fg_color="#FFFFFF", corner_radius=28, border_width=1, border_color="#E2E8F0")
        card.pack(expand=True, fill="both", padx=6, pady=6)

        header = ctk.CTkFrame(card, fg_color="#FFFFFF")
        header.pack(fill="x", padx=26, pady=(26, 10))
        header.grid_columnconfigure(0, weight=1)

        text_block = ctk.CTkFrame(header, fg_color="#FFFFFF")
        text_block.grid(row=0, column=0, sticky="w")
        text_block.grid_columnconfigure(0, weight=1)

        row_index = 0
        if badge:
            ctk.CTkLabel(text_block, text=badge.upper(), font=self.base_fonts["badge"], text_color=COLOR_ACCENT).grid(
                row=row_index, column=0, sticky="w", pady=(0, 4)
            )
            row_index += 1

        ctk.CTkLabel(
            text_block, text=title, font=self.base_fonts["modal_title"], text_color=COLOR_TEXT_PRIMARY
        ).grid(row=row_index, column=0, sticky="w")
        row_index += 1

        if subtitle:
            ctk.CTkLabel(
                text_block, text=subtitle, font=self.base_fonts["modal_sub"], text_color=COLOR_TEXT_MUTED
            ).grid(row=row_index, column=0, sticky="w", pady=(6, 0))

        close_btn = ctk.CTkButton(
            header,
            text="x",
            width=32,
            height=32,
            fg_color="transparent",
            hover_color="#FFE4E6",
            text_color=COLOR_ACCENT,
            command=close_action,
            font=self.base_fonts["button"],
        )
        close_btn.grid(row=0, column=1, sticky="ne", padx=(12, 0))
        self.register_drag_handle(header, window=modal)

        separator = ctk.CTkFrame(card, fg_color="#EEF2FF", height=2)
        separator.pack(fill="x", padx=26, pady=(0, 18))
        separator.pack_propagate(False)

        content = ctk.CTkFrame(card, fg_color="#FFFFFF")
        content.pack(expand=True, fill="both", padx=26, pady=(0, 26))
        content.grid_columnconfigure(0, weight=1)

        def _ensure_modal_size():
            try:
                modal.update_idletasks()
                req_w = card.winfo_reqwidth() + 56
                req_h = card.winfo_reqheight() + 72
                final_w = max(width, req_w)
                final_h = max(height, req_h)
                modal.geometry(f"{final_w}x{final_h}")
            except Exception:
                pass

        modal.after(60, _ensure_modal_size)

        modal.bind("<Escape>", lambda _=None: close_action())
        modal.protocol("WM_DELETE_WINDOW", close_action)
        if grab_focus:
            modal.grab_set()
            modal.focus_force()

        return modal, content

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

    # ------------------------------------------------------------------
    # Integración con el chrome personalizado del root
    # ------------------------------------------------------------------
    def register_drag_handle(
        self,
        widget: Optional[ctk.CTkBaseClass],
        *,
        window: Optional[WindowType] = None,
        direct_only: bool = False,
    ):
        self._register_drag_handle(widget, window=window, direct_only=direct_only)

    def _register_drag_handle(
        self,
        widget: Optional[ctk.CTkBaseClass],
        *,
        window: Optional[WindowType] = None,
        direct_only: bool = False,
    ):
        if widget is None:
            return
        root = self.winfo_toplevel()
        proxy = getattr(root, "register_drag_handle", None)
        if callable(proxy):
            proxy(widget, window=window, direct_only=direct_only)

    def _make_borderless_window(self, window: WindowType):
        root = self.winfo_toplevel()
        helper = getattr(root, "make_child_borderless", None)
        if callable(helper):
            helper(window)
        else:
            try:
                window.overrideredirect(True)
            except Exception:
                pass
