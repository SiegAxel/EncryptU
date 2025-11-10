import customtkinter as ctk
from datetime import datetime
from typing import Any, Dict, List, Optional

from PIL import Image, ImageDraw

try:
    import pywinstyles  # type: ignore
except ImportError:
    pywinstyles = None  # type: ignore

COLOR_BACKGROUND = "#F4F6FB"
COLOR_HERO = "#FFFFFF"
COLOR_TOP_TEXT_PRIMARY = "#0F172A"
COLOR_TOP_TEXT_MUTED = "#64748B"
COLOR_HERO_TEXT_PRIMARY = "#FFFFFF"
COLOR_HERO_TEXT_MUTED = "#B6B6B6"
COLOR_BOTTOM_CARD = "#FFFFFF"
COLOR_BOTTOM_CARD_SOFT = "#FBFCFF"
COLOR_BOTTOM_BORDER = "#E2E8F0"
COLOR_TEXT_PRIMARY = "#0F172A"
COLOR_TEXT_MUTED = "#94A3B8"
COLOR_ACCENT = "#F28AA2"
COLOR_ACCENT_DARK = "#E05D80"
COLOR_PRIMARY = "#EE5A72"
COLOR_PRIMARY_DARK = "#D9435C"
COLOR_SUCCESS = "#34C38F"
COLOR_SUCCESS_DARK = "#1B7B57"
COLOR_AGENT = "#F8F5FF"
COLOR_AGENT_TEXT = "#4C1D95"
COLOR_CLIENT = "#FFF0F3"
COLOR_CLIENT_TEXT = "#9F1239"

SUPPORT_REASONS = ["Soporte", "Consulta"]
GRADIENT_PATH = "desktop/controllers/img/bannerEncryptU.png"
HERO_HEIGHT = 130
TICKETS_REFRESH_MS = 15_000
MESSAGES_REFRESH_MS = 5_000
TAB_PENDING = "pending"
TAB_RESOLVED = "resolved"

STATUS_LABELS = {
    "open": "Abierto",
    "pending": "Pendiente",
    "closed": "Cerrado",
    "resolved": "Resuelto",
}

STATUS_BADGE_COLORS = {
    "open": ("#DDFBEA", "#0F7B4B"),
    "pending": ("#FFF4DB", "#92400E"),
    "closed": ("#FFE4E6", "#9F1239"),
    "resolved": ("#E1E8FF", "#243F8C"),
}

REASON_BADGE_COLORS = {
    "soporte": ("#FFE6EC", "#A31642"),
    "consulta": ("#E4F2FF", "#0F4C81"),
}

 

from .base_view import BaseView

class SupportView(BaseView):
    """Vista dedicada para la gestion de soporte y tickets de EncryptU."""

    def __init__(self, master, controller, username: str):
        super().__init__(master, fg_color=COLOR_BACKGROUND)
        self.controller = controller
        self.username = username or "Usuario"

        self.fonts = self._build_fonts()
        self.transparent_color = "#000001"
        self._transparent_widgets = []
        self.hero_source = self._load_gradient()
        self.hero_image: Optional[ctk.CTkImage] = None
        self.hero_label: Optional[ctk.CTkLabel] = None
        self._hero_image_ref: Optional[ctk.CTkImage] = None

        self.support_tickets: List[Dict[str, Any]] = []
        self.pending_tickets: List[Dict[str, Any]] = []
        self.resolved_tickets: List[Dict[str, Any]] = []
        self.messages_cache: Dict[int, List[Dict[str, Any]]] = {}
        self.active_ticket_id: Optional[int] = None

        self.filter_var = ctk.StringVar(value="")
        self.tab_var = ctk.StringVar(value=TAB_PENDING)
        self.total_count_var = ctk.StringVar(value="0 tickets")

        self._tickets_refresh_job: Optional[str] = None
        self._messages_refresh_job: Optional[str] = None

        self.tickets_container: Optional[ctk.CTkScrollableFrame] = None
        self.chat_messages_container: Optional[ctk.CTkScrollableFrame] = None
        self.message_input: Optional[ctk.CTkTextbox] = None
        self.send_button: Optional[ctk.CTkButton] = None
        self.status_label: Optional[ctk.CTkLabel] = None
        self.search_entry: Optional[ctk.CTkEntry] = None
        self.tab_buttons: Dict[str, ctk.CTkButton] = {}

        self.chat_title_var = ctk.StringVar(value="Selecciona un ticket")
        self.chat_meta_var = ctk.StringVar(value="")
        self.chat_email_var = ctk.StringVar(value="")
        self.chat_date_var = ctk.StringVar(value="")
        self.status_var = ctk.StringVar(value="")
        self.chat_reason_label: Optional[ctk.CTkLabel] = None
        self.chat_status_label: Optional[ctk.CTkLabel] = None
        self.chat_email_label: Optional[ctk.CTkLabel] = None
        self.chat_date_label: Optional[ctk.CTkLabel] = None
        self.close_button: Optional[ctk.CTkButton] = None

        self._build_layout()
        self.filter_var.trace_add("write", lambda *_: self._render_ticket_list())
        self.tab_var.trace_add("write", lambda *_: self._handle_tab_change())
        self.bind("<Configure>", self._handle_resize)
        self.after(200, self.refresh_tickets)
        self.after(100, self._apply_transparencies)

    # ------------------------------------------------------------------
    # Construccion
    # ------------------------------------------------------------------
    def _build_fonts(self) -> Dict[str, ctk.CTkFont]:
        return {
            "hero_title": ctk.CTkFont(family="Arial", size=40, weight="bold"),
            "hero_sub": ctk.CTkFont(family="Arial", size=20),
            "logo": ctk.CTkFont(family="Arial", size=28, weight="bold"),
            "section": ctk.CTkFont(size=20, weight="bold"),
            "badge": ctk.CTkFont(size=13, weight="bold"),
            "body": ctk.CTkFont(size=14),
            "small": ctk.CTkFont(size=13),
            "button": ctk.CTkFont(size=15, weight="bold"),
        }

    def _make_transparent(self, widget):
        if pywinstyles is None or widget is None:
            return

        # Avoid forcing Windows color-key transparency on widgets that render
        # text directly, otherwise ClearType is lost and the font looks jagged.
        try:
            if isinstance(widget, ctk.CTkButton):
                return
            if isinstance(widget, ctk.CTkLabel):
                has_text = bool(widget.cget("text"))
                has_image = bool(widget.cget("image"))
                if has_text and not has_image:
                    return
        except Exception:
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
        for widget in self._transparent_widgets:
            if hasattr(widget, "winfo_id"):
                try:
                    pywinstyles.set_opacity(widget.winfo_id(), color=self.transparent_color)
                except Exception as exc:
                    print(f"Error al aplicar transparencia: {exc}")

    def _load_gradient(self) -> Image.Image:
        width = 1600
        height = HERO_HEIGHT
        try:
            base = Image.open(GRADIENT_PATH).convert("RGBA")
            base = base.resize((width, height))
        except Exception:
            base = Image.new("RGBA", (width, height), "#FFFFFF")

        overlay = Image.new("RGBA", (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        draw.ellipse(
            (-220, -180, 420, height + 220),
            fill=(242, 138, 162, 90),
        )
        draw.ellipse(
            (width - 520, -200, width + 80, height + 240),
            fill=(184, 215, 255, 110),
        )
        draw.rectangle((0, height - 40, width, height), fill=(255, 255, 255, 180))
        combined = Image.alpha_composite(base, overlay)
        return combined.convert("RGB")

    def _build_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build_hero()
        self._build_body()

    def _build_hero(self):
        hero = ctk.CTkFrame(self, fg_color=COLOR_HERO)
        hero.grid(row=0, column=0, sticky="nsew")
        hero.grid_propagate(False)
        hero.configure(height=HERO_HEIGHT)
        hero.grid_columnconfigure(0, weight=1)
        self._make_transparent(hero)

        self.hero_image = ctk.CTkImage(self.hero_source, size=(self.hero_source.width, HERO_HEIGHT))
        self.hero_label = ctk.CTkLabel(hero, text="", image=self.hero_image)
        self.hero_label.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)
        self._make_transparent(self.hero_label)

        content = ctk.CTkFrame(hero, fg_color="transparent")
        content.pack(expand=True, fill="both", padx=36, pady=18)
        content.grid_columnconfigure(0, weight=1)
        self._make_transparent(content)

        header_row = ctk.CTkFrame(content, fg_color="transparent")
        header_row.grid(row=0, column=0, sticky="ew")
        header_row.grid_columnconfigure(0, weight=1)
        self._make_transparent(header_row)

        brand = ctk.CTkFrame(header_row, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="w")
        brand_label = ctk.CTkLabel(brand, text="Encrypt", font=self.fonts["logo"], text_color=COLOR_HERO_TEXT_PRIMARY)
        brand_label.pack(side="left")
        brand_accent = ctk.CTkLabel(brand, text="U", font=self.fonts["logo"], text_color=COLOR_PRIMARY)
        brand_accent.pack(side="left", padx=(2, 0))
        self._make_transparent(brand)
        self._make_transparent(brand_label)
        self._make_transparent(brand_accent)

        back_button = ctk.CTkButton(
            header_row,
            text="Volver al inicio",
            command=lambda: self.controller.show_main_view(self.username),
            fg_color="#FFFFFF",
            hover_color="#FFE6EC",
            text_color=COLOR_PRIMARY,
            font=self.fonts["button"],
            corner_radius=18,
            border_width=1,
            border_color=COLOR_PRIMARY,
            height=38,
            width=150,
        )
        back_button.grid(row=0, column=1, sticky="e")
        self._make_transparent(back_button)

        badge = ctk.CTkLabel(
            header_row,
            text="Soporte · Desktop",
            font=self.fonts["small"],
            text_color=COLOR_HERO_TEXT_MUTED,
        )
        badge.grid(row=1, column=0, sticky="w", pady=(4, 0))
        self._make_transparent(badge)

        title = ctk.CTkLabel(
            content,
            text="Centro de soporte",
            font=self.fonts["hero_title"],
            text_color=COLOR_HERO_TEXT_PRIMARY,
        )
        title.grid(row=1, column=0, sticky="w", pady=(4, 2))
        self._make_transparent(title)

        subtitle = ctk.CTkLabel(
            content,
            text="Consulta tus tickets, conversa con el equipo y crea nuevas solicitudes.",
            font=self.fonts["hero_sub"],
            text_color=COLOR_HERO_TEXT_MUTED,
        )
        subtitle.grid(row=2, column=0, sticky="w")
        self._make_transparent(subtitle)

        divider = ctk.CTkFrame(hero, fg_color=COLOR_BOTTOM_BORDER, height=1)
        divider.pack(fill="x", side="bottom")

    def _build_body(self):
        wrapper = ctk.CTkFrame(self, fg_color=COLOR_BACKGROUND)
        wrapper.grid(row=1, column=0, sticky="nsew", padx=28, pady=(0, 28))
        wrapper.grid_columnconfigure(0, weight=1)
        wrapper.grid_rowconfigure(0, weight=1)

        body = ctk.CTkFrame(
            wrapper,
            fg_color=COLOR_BOTTOM_CARD,
            corner_radius=28,
            border_width=1,
            border_color=COLOR_BOTTOM_BORDER,
        )
        body.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        body.grid_columnconfigure(0, weight=38)
        body.grid_columnconfigure(1, weight=62)
        body.grid_rowconfigure(0, weight=1)

        self._build_ticket_panel(body)
        self._build_chat_panel(body)

    def _build_ticket_panel(self, parent: ctk.CTkFrame):
        panel = ctk.CTkFrame(
            parent,
            fg_color=COLOR_BOTTOM_CARD_SOFT,
            corner_radius=24,
            border_width=1,
            border_color=COLOR_BOTTOM_BORDER,
        )
        panel.grid(row=0, column=0, sticky="nsew", padx=(24, 12), pady=24)
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(4, weight=1)

        header_row = ctk.CTkFrame(panel, fg_color="transparent")
        header_row.grid(row=0, column=0, sticky="ew", padx=24, pady=(18, 4))
        header_row.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(
            header_row,
            text="Tickets",
            font=self.fonts["section"],
            text_color=COLOR_TEXT_PRIMARY,
        )
        header.grid(row=0, column=0, sticky="w")

        total_label = ctk.CTkLabel(
            header_row,
            textvariable=self.total_count_var,
            font=self.fonts["small"],
            text_color=COLOR_TEXT_MUTED,
        )
        total_label.grid(row=0, column=1, sticky="e")

        search_holder = ctk.CTkFrame(
            panel,
            fg_color=COLOR_BOTTOM_CARD,
            corner_radius=20,
            border_width=1,
            border_color="#EDF2F7",
        )
        search_holder.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 10))
        search_holder.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            search_holder,
            placeholder_text="Buscar por nombre, mail, #id...",
            textvariable=self.filter_var,
            fg_color="transparent",
            border_width=0,
            font=self.fonts["body"],
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=16, pady=10)

        tabs = ctk.CTkFrame(panel, fg_color="transparent")
        tabs.grid(row=2, column=0, sticky="ew", padx=24, pady=(2, 4))
        tabs.grid_columnconfigure(0, weight=1)
        tabs.grid_columnconfigure(1, weight=1)

        self.tab_buttons = {}
        pending_btn = ctk.CTkButton(
            tabs,
            text="Pendientes (0)",
            command=lambda: self._set_tab(TAB_PENDING),
            fg_color="#E6F6EE",
            hover_color="#D4F0E4",
            text_color=COLOR_SUCCESS_DARK,
            font=self.fonts["button"],
            corner_radius=20,
        )
        pending_btn.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.tab_buttons[TAB_PENDING] = pending_btn

        resolved_btn = ctk.CTkButton(
            tabs,
            text="Resueltos (0)",
            command=lambda: self._set_tab(TAB_RESOLVED),
            fg_color=COLOR_BOTTOM_CARD,
            hover_color="#F5F6FB",
            text_color=COLOR_TEXT_MUTED,
            font=self.fonts["button"],
            corner_radius=20,
        )
        resolved_btn.grid(row=0, column=1, sticky="ew")
        self.tab_buttons[TAB_RESOLVED] = resolved_btn

        chip_strip = ctk.CTkFrame(panel, fg_color="transparent")
        chip_strip.grid(row=3, column=0, sticky="ew", padx=24, pady=(0, 6))
        chip_strip.grid_columnconfigure(0, weight=1)
        chip_strip.grid_columnconfigure(1, weight=1)

        refresh_button = ctk.CTkButton(
            chip_strip,
            text="Actualizar",
            command=self.refresh_tickets,
            fg_color="transparent",
            hover_color="#EEF3FF",
            text_color=COLOR_ACCENT_DARK,
            font=self.fonts["button"],
            width=80,
        )
        refresh_button.grid(row=0, column=0, sticky="w")

        new_ticket_button = ctk.CTkButton(
            chip_strip,
            text="Nuevo ticket",
            command=self._open_new_ticket_modal,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_DARK,
            text_color="#FFFFFF",
            font=self.fonts["button"],
            width=110,
        )
        new_ticket_button.grid(row=0, column=1, sticky="e")

        self.tickets_container = ctk.CTkScrollableFrame(
            panel,
            fg_color="transparent",
        )
        self.tickets_container.grid(row=4, column=0, sticky="nsew", padx=16, pady=(0, 20))

    def _build_chat_panel(self, parent: ctk.CTkFrame):
        panel = ctk.CTkFrame(
            parent,
            fg_color=COLOR_BOTTOM_CARD_SOFT,
            corner_radius=24,
            border_width=1,
            border_color=COLOR_BOTTOM_BORDER,
        )
        panel.grid(row=0, column=1, sticky="nsew", padx=(0, 24), pady=24)
        panel.grid_rowconfigure(2, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(panel, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(20, 10))
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0)

        title_block = ctk.CTkFrame(header, fg_color="transparent")
        title_block.grid(row=0, column=0, sticky="w")

        title = ctk.CTkLabel(
            title_block,
            textvariable=self.chat_title_var,
            font=self.fonts["section"],
            text_color=COLOR_TEXT_PRIMARY,
        )
        title.pack(anchor="w")

        badge_row = ctk.CTkFrame(title_block, fg_color="transparent")
        badge_row.pack(anchor="w", pady=(6, 0))

        self.chat_reason_label = ctk.CTkLabel(
            badge_row,
            text="",
            font=self.fonts["badge"],
            text_color="#A31642",
            fg_color="#FFE6EC",
            corner_radius=999,
        )
        self.chat_reason_label.pack(side="left", padx=(0, 6))

        self.chat_status_label = ctk.CTkLabel(
            badge_row,
            text="",
            font=self.fonts["badge"],
            text_color=COLOR_SUCCESS_DARK,
            fg_color="#DDFBEA",
            corner_radius=999,
        )
        self.chat_status_label.pack(side="left")

        meta_block = ctk.CTkFrame(header, fg_color="transparent")
        meta_block.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(4, 0))
        meta_block.grid_columnconfigure(0, weight=1)
        meta_block.grid_columnconfigure(1, weight=0)

        self.chat_email_label = ctk.CTkLabel(
            meta_block,
            textvariable=self.chat_email_var,
            font=self.fonts["small"],
            text_color=COLOR_TEXT_MUTED,
        )
        self.chat_email_label.grid(row=0, column=0, sticky="w")

        right_meta = ctk.CTkFrame(header, fg_color="transparent")
        right_meta.grid(row=0, column=1, rowspan=2, sticky="ne", padx=(12, 0))

        self.chat_date_label = ctk.CTkLabel(
            right_meta,
            textvariable=self.chat_date_var,
            font=self.fonts["small"],
            text_color=COLOR_TEXT_MUTED,
        )
        self.chat_date_label.pack(anchor="e")

        self.close_button = ctk.CTkButton(
            right_meta,
            text="Cerrar ticket",
            command=self._handle_close_ticket,
            state="disabled",
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_DARK,
            text_color="#FFFFFF",
            font=self.fonts["button"],
            width=120,
        )
        self.close_button.pack(anchor="e", pady=(6, 0))

        self.chat_messages_container = ctk.CTkScrollableFrame(
            panel,
            fg_color=COLOR_BOTTOM_CARD,
            corner_radius=18,
        )
        self.chat_messages_container.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 12))

        editor = ctk.CTkFrame(panel, fg_color="transparent")
        editor.grid(row=3, column=0, sticky="ew", padx=28, pady=(8, 24))
        editor.grid_columnconfigure(0, weight=1)

        self.message_input = ctk.CTkTextbox(
            editor,
            height=78,
            corner_radius=18,
            fg_color=COLOR_BOTTOM_CARD,
            border_width=1,
            border_color="#E2E8F0",
        )
        self.message_input.grid(row=0, column=0, sticky="ew")
        self.message_input.bind("<Control-Return>", self._send_message_event)
        self.message_input.bind("<Command-Return>", self._send_message_event)

        button_row = ctk.CTkFrame(editor, fg_color="transparent")
        button_row.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        button_row.grid_columnconfigure(0, weight=1)

        hint = ctk.CTkLabel(
            button_row,
            text="Escribe un mensaje...  (Ctrl/⌘ + Enter para enviar)",
            font=self.fonts["small"],
            text_color=COLOR_TEXT_MUTED,
        )
        hint.grid(row=0, column=0, sticky="w")

        self.status_label = ctk.CTkLabel(
            button_row,
            textvariable=self.status_var,
            font=self.fonts["small"],
            text_color=COLOR_TEXT_MUTED,
        )
        self.status_label.grid(row=1, column=0, sticky="w", pady=(2, 0))

        self.send_button = ctk.CTkButton(
            button_row,
            text="Enviar",
            command=self._send_message,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_DARK,
            text_color="#FFFFFF",
            font=self.fonts["button"],
            width=120,
        )
        self.send_button.grid(row=0, column=1, rowspan=2, sticky="e")

        self._set_composer_enabled(False)

    # ------------------------------------------------------------------
    # Controles de tickets
    # ------------------------------------------------------------------
    def _set_tab(self, tab: str):
        if tab not in (TAB_PENDING, TAB_RESOLVED):
            return
        if self.tab_var.get() != tab:
            self.tab_var.set(tab)

    def _handle_tab_change(self, *_):
        self._update_tab_styles()
        self._render_ticket_list()
        self._ensure_active_ticket()

    def _update_tab_styles(self):
        current = self.tab_var.get()
        for key, button in self.tab_buttons.items():
            if key == current:
                if key == TAB_PENDING:
                    button.configure(
                        fg_color="#DDFBEA",
                        hover_color="#C7F2DA",
                        text_color=COLOR_SUCCESS_DARK,
                    )
                else:
                    button.configure(
                        fg_color="#FFE5EC",
                        hover_color="#FFD9E4",
                        text_color="#A31642",
                    )
            else:
                button.configure(
                    fg_color=COLOR_BOTTOM_CARD,
                    hover_color="#F3F4F6",
                    text_color=COLOR_TEXT_MUTED,
                )

    def _render_ticket_list(self):
        if self.tickets_container is None:
            return

        for widget in self.tickets_container.winfo_children():
            widget.destroy()

        tickets_to_show = self._get_displayed_tickets()
        if not tickets_to_show:
            empty_text = (
                "No hay tickets pendientes por ahora."
                if self.tab_var.get() == TAB_PENDING
                else "No hay tickets resueltos para mostrar."
            )
            state = ctk.CTkFrame(
                self.tickets_container,
                fg_color=COLOR_BOTTOM_CARD,
                corner_radius=18,
                border_width=1,
                border_color=COLOR_BOTTOM_BORDER,
            )
            state.pack(expand=True, fill="both", padx=24, pady=32)
            ctk.CTkLabel(
                state,
                text=empty_text,
                font=self.fonts["body"],
                text_color=COLOR_TEXT_MUTED,
                wraplength=240,
                justify="center",
            ).pack(expand=True, padx=16, pady=20)
            return

        for ticket in tickets_to_show:
            self._render_ticket_card(ticket)

    def _get_displayed_tickets(self) -> List[Dict[str, Any]]:
        base = self.pending_tickets if self.tab_var.get() == TAB_PENDING else self.resolved_tickets
        query = self.filter_var.get().strip().lower()
        if not query:
            return base

        result: List[Dict[str, Any]] = []
        for ticket in base:
            haystack = " ".join(
                [
                    str(ticket.get("id") or ""),
                    ticket.get("full_name") or "",
                    ticket.get("email") or "",
                    ticket.get("reason") or "",
                    ticket.get("status") or "",
                ]
            ).lower()
            if query in haystack:
                result.append(ticket)
        return result

    def _update_ticket_counts(self):
        total = len(self.support_tickets)
        pending = len(self.pending_tickets)
        resolved = len(self.resolved_tickets)

        def pluralize(value: int, singular: str, plural: str) -> str:
            return f"{value} {singular if value == 1 else plural}"

        self.total_count_var.set(pluralize(total, "ticket", "tickets"))

        if TAB_PENDING in self.tab_buttons:
            self.tab_buttons[TAB_PENDING].configure(text=f"Pendientes ({pending})")
        if TAB_RESOLVED in self.tab_buttons:
            self.tab_buttons[TAB_RESOLVED].configure(text=f"Resueltos ({resolved})")

    def _ensure_active_ticket(self):
        if not self.support_tickets:
            self.active_ticket_id = None
            self._update_chat_header(None)
            self._render_messages(None)
            self._schedule_message_refresh()
            return

        if self.active_ticket_id and any(t.get("id") == self.active_ticket_id for t in self.support_tickets):
            ticket = self._get_ticket(self.active_ticket_id)
            self._update_chat_header(ticket)
            return

        displayed = self._get_displayed_tickets()
        target = displayed[0] if displayed else self.support_tickets[0]
        if target:
            self._handle_select_ticket(target.get("id"))
        else:
            self.active_ticket_id = None
            self._update_chat_header(None)
            self._render_messages(None)
            self._schedule_message_refresh()

    def _update_chat_header(self, ticket: Optional[Dict[str, Any]], ticket_id: Optional[int] = None):
        if not ticket:
            target_id = ticket_id or "--"
            self.chat_title_var.set(f"Ticket #{target_id}")
            self.chat_email_var.set("")
            self.chat_date_var.set("")
            if self.chat_reason_label:
                self.chat_reason_label.configure(text="", fg_color="transparent")
            if self.chat_status_label:
                self.chat_status_label.configure(text="", fg_color="transparent")
            if self.close_button:
                self.close_button.configure(state="disabled")
            return

        display_name = ticket.get("full_name") or ticket.get("email") or self.username
        identifier = ticket.get("id", ticket_id or "--")
        status_raw = ticket.get("status", "")
        status = STATUS_LABELS.get(status_raw.lower(), status_raw.title())
        reason = str(ticket.get("reason", "soporte")).title()

        self.chat_title_var.set(f"Ticket #{identifier} — {display_name}")
        self.chat_email_var.set(ticket.get("email") or "")
        self.chat_date_var.set(self._format_date(ticket.get("created_at")))

        reason_colors = self._get_reason_badge_colors(ticket.get("reason"))
        if self.chat_reason_label:
            self.chat_reason_label.configure(
                text=f"  {reason}  ",
                fg_color=reason_colors[0],
                text_color=reason_colors[1],
            )

        status_colors = self._get_status_badge_colors(status_raw)
        if self.chat_status_label:
            self.chat_status_label.configure(
                text=f"  {status}  ",
                fg_color=status_colors[0],
                text_color=status_colors[1],
            )

        if self.close_button:
            self.close_button.configure(state="normal" if status_raw != "closed" else "disabled")

    def refresh_tickets(self):
        data = self.controller.get_support_tickets(force_refresh=True)
        if data is None:
            self._show_status("No se pudieron cargar los tickets. Intenta nuevamente.", error=True)
            self._schedule_ticket_refresh()
            return

        self.support_tickets = [self._normalize_ticket(item) for item in data if item]
        self.pending_tickets = [ticket for ticket in self.support_tickets if ticket.get("status") != "closed"]
        self.resolved_tickets = [ticket for ticket in self.support_tickets if ticket.get("status") == "closed"]

        self._update_ticket_counts()
        self._render_ticket_list()
        self._ensure_active_ticket()
        self._schedule_ticket_refresh()

    def _render_ticket_card(self, ticket: Dict[str, Any]):
        is_active = ticket.get("id") == self.active_ticket_id
        card = ctk.CTkFrame(
            self.tickets_container,
            fg_color=COLOR_BOTTOM_CARD,
            corner_radius=18,
            border_width=2 if is_active else 1,
            border_color=COLOR_ACCENT if is_active else COLOR_BOTTOM_BORDER,
        )
        card.pack(fill="x", padx=10, pady=6)

        full_name = ticket.get("full_name") or "Sin nombre"
        header_row = ctk.CTkFrame(card, fg_color="transparent")
        header_row.pack(fill="x", padx=14, pady=(12, 0))
        header_row.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header_row,
            text=f"#{ticket.get('id', '--')} — {full_name}",
            font=self.fonts["body"],
            text_color=COLOR_TEXT_PRIMARY,
        )
        title.grid(row=0, column=0, sticky="w")

        email = ticket.get("email") or "Sin correo registrado"
        ctk.CTkLabel(
            card,
            text=email,
            font=self.fonts["small"],
            text_color=COLOR_TEXT_MUTED,
        ).pack(anchor="w", padx=16, pady=(0, 6))

        badges = ctk.CTkFrame(card, fg_color="transparent")
        badges.pack(fill="x", padx=12, pady=(0, 8))
        badges.grid_columnconfigure(0, weight=1)
        badges.grid_columnconfigure(1, weight=1)

        reason_colors = self._get_reason_badge_colors(ticket.get("reason"))
        reason_badge = ctk.CTkLabel(
            badges,
            text=f"  {ticket.get('reason', 'soporte').title()}  ",
            font=self.fonts["badge"],
            text_color=reason_colors[1],
            fg_color=reason_colors[0],
            corner_radius=999,
        )
        reason_badge.grid(row=0, column=0, sticky="w", padx=(4, 6))

        status_text = STATUS_LABELS.get(ticket.get("status", "").lower(), ticket.get("status", "Pendiente").title())
        status_colors = self._get_status_badge_colors(ticket.get("status"))
        status_badge = ctk.CTkLabel(
            badges,
            text=f"  {status_text}  ",
            font=self.fonts["badge"],
            text_color=status_colors[1],
            fg_color=status_colors[0],
            corner_radius=999,
        )
        status_badge.grid(row=0, column=1, sticky="e", padx=(6, 4))

        footer = ctk.CTkFrame(card, fg_color="transparent")
        footer.pack(fill="x", padx=16, pady=(0, 12))
        footer.grid_columnconfigure(0, weight=1)

        created_str = self._format_timestamp(ticket.get("created_at"))
        ctk.CTkLabel(
            footer,
            text=created_str,
            font=self.fonts["small"],
            text_color=COLOR_TEXT_MUTED,
        ).grid(row=0, column=0, sticky="w")

        messages_count = ticket.get("messages_count")
        if isinstance(messages_count, int):
            ctk.CTkLabel(
                footer,
                text=f"{messages_count} msgs",
                font=self.fonts["small"],
                text_color=COLOR_TEXT_MUTED,
            ).grid(row=0, column=1, sticky="e")

        card.bind("<Button-1>", lambda _e, tid=ticket.get("id"): self._handle_select_ticket(tid))
        for child in card.winfo_children():
            child.bind("<Button-1>", lambda _e, tid=ticket.get("id"): self._handle_select_ticket(tid))

    def _handle_select_ticket(self, ticket_id: Optional[int]):
        if ticket_id is None:
            return
        self.active_ticket_id = ticket_id
        ticket = self._get_ticket(ticket_id)
        self._update_chat_header(ticket, ticket_id)

        is_closed = bool(ticket and ticket.get("status") == "closed")
        self._set_composer_enabled(not is_closed)

        self._load_messages(ticket_id)
        self._schedule_message_refresh()

    def _load_messages(self, ticket_id: int, use_cache: bool = True):
        if use_cache and ticket_id in self.messages_cache:
            self._render_messages(self.messages_cache[ticket_id])
            return

        messages = self.controller.get_support_ticket_messages(ticket_id, force_refresh=not use_cache)
        if messages is None:
            self._show_status("No se pudieron cargar los mensajes.", error=True)
            return

        self.messages_cache[ticket_id] = messages
        self._render_messages(messages)

    def _render_messages(self, messages: Optional[List[Dict[str, Any]]]):
        if not self.chat_messages_container:
            return

        for widget in self.chat_messages_container.winfo_children():
            widget.destroy()

        ticket = self._get_ticket(self.active_ticket_id) if self.active_ticket_id else None
        composer_allowed = bool(self.active_ticket_id and ticket and ticket.get("status") != "closed")

        if messages is None:
            self._set_composer_enabled(False)
            ghost = ctk.CTkFrame(
                self.chat_messages_container,
                fg_color=COLOR_BOTTOM_CARD,
                corner_radius=24,
                border_width=1,
                border_color=COLOR_BOTTOM_BORDER,
            )
            ghost.pack(expand=True, fill="both", padx=24, pady=40)
            ctk.CTkLabel(
                ghost,
                text="Selecciona un ticket para ver la conversacion.",
                font=self.fonts["body"],
                text_color=COLOR_TEXT_MUTED,
                wraplength=420,
                justify="center",
            ).pack(expand=True, padx=24, pady=32)
            return

        if not messages:
            self._set_composer_enabled(composer_allowed)
            empty_card = ctk.CTkFrame(
                self.chat_messages_container,
                fg_color=COLOR_BOTTOM_CARD,
                corner_radius=24,
                border_width=2,
                border_color="#CBD5F5",
            )
            empty_card.pack(expand=True, fill="both", padx=24, pady=30)
            ctk.CTkLabel(
                empty_card,
                text="Aun no hay mensajes en este ticket.",
                font=self.fonts["body"],
                text_color=COLOR_TEXT_MUTED,
                wraplength=460,
                justify="center",
            ).pack(expand=True, padx=32, pady=40)
            return

        self._set_composer_enabled(composer_allowed)
        for message in messages:
            author_role = str(message.get("author") or "user").lower()
            is_agent = author_role == "agent"
            body = message.get("body") or ""
            timestamp = self._format_timestamp(
                message.get("created_at") or message.get("createdAt") or message.get("timestamp")
            )
            author = message.get("name") or ("Equipo EncryptU" if is_agent else "Tu")

            wrapper = ctk.CTkFrame(self.chat_messages_container, fg_color="transparent")
            wrapper.pack(fill="x", pady=6)

            bubble = ctk.CTkFrame(
                wrapper,
                fg_color=COLOR_AGENT if is_agent else COLOR_CLIENT,
                corner_radius=18,
            )
            bubble.pack(anchor="e" if is_agent else "w", padx=14)

            header = ctk.CTkLabel(
                bubble,
                text=f"{author} - {timestamp}",
                font=self.fonts["small"],
                text_color=COLOR_AGENT_TEXT if is_agent else COLOR_TEXT_MUTED,
            )
            header.pack(anchor="w", padx=16, pady=(12, 4))

            body_label = ctk.CTkLabel(
                bubble,
                text=body,
                font=self.fonts["body"],
                text_color=COLOR_AGENT_TEXT if is_agent else COLOR_CLIENT_TEXT,
                wraplength=380,
                justify="left",
            )
            body_label.pack(anchor="w", padx=16, pady=(0, 12))

        canvas = getattr(self.chat_messages_container, "_parent_canvas", None)
        if canvas is not None:
            canvas.after(50, lambda: canvas.yview_moveto(1.0))

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------
    def _send_message_event(self, event):
        self._send_message()
        return "break"

    def _send_message(self):
        if not self.active_ticket_id:
            self._show_status("Selecciona un ticket para enviar mensajes.", error=True)
            return
        if not self.message_input or not self.send_button:
            return

        ticket = self._get_ticket(self.active_ticket_id)
        if ticket and ticket.get("status") == "closed":
            self._show_status("Este ticket ya esta cerrado.", error=True)
            self._set_composer_enabled(False)
            return

        message = self.message_input.get("0.0", "end").strip()
        if not message:
            self._show_status("Escribe un mensaje antes de enviar.", error=True)
            return

        self.send_button.configure(state="disabled")
        self._show_status("Enviando mensaje...", pending=True)

        success = self.controller.handle_send_support_message(self.active_ticket_id, message)

        if success:
            self.message_input.delete("0.0", "end")
            self._show_status("Mensaje enviado al equipo de soporte.", success=True)
            self.messages_cache.pop(self.active_ticket_id, None)
            self._load_messages(self.active_ticket_id)
            self._schedule_message_refresh()
        else:
            self._show_status("No se pudo enviar el mensaje.", error=True)

        self.send_button.configure(state="normal")

    def _open_new_ticket_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Nuevo ticket de soporte")
        modal.geometry("520x520")
        modal.resizable(False, False)

        form = ctk.CTkFrame(modal, fg_color=COLOR_BOTTOM_CARD, corner_radius=20)
        form.pack(expand=True, fill="both", padx=18, pady=18)
        form.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(form, text="Crear ticket", font=self.fonts["section"], text_color=COLOR_TEXT_PRIMARY).grid(row=0, column=0, sticky="w", pady=(12, 4))
        ctk.CTkLabel(form, text="Cuentanos en que podemos ayudarte.", font=self.fonts["small"], text_color=COLOR_TEXT_MUTED).grid(row=1, column=0, sticky="w", pady=(0, 12))

        first_name_entry = ctk.CTkEntry(form, placeholder_text="Nombre", fg_color=COLOR_BOTTOM_CARD, border_width=0)
        first_name_entry.grid(row=2, column=0, sticky="ew", pady=6)

        last_name_entry = ctk.CTkEntry(form, placeholder_text="Apellido", fg_color=COLOR_BOTTOM_CARD, border_width=0)
        last_name_entry.grid(row=3, column=0, sticky="ew", pady=6)

        email_entry = ctk.CTkEntry(form, placeholder_text="Correo", fg_color=COLOR_BOTTOM_CARD, border_width=0)
        email_entry.grid(row=4, column=0, sticky="ew", pady=6)
        email_entry.insert(0, self.username)

        phone_entry = ctk.CTkEntry(form, placeholder_text="Telefono (9 digitos)", fg_color=COLOR_BOTTOM_CARD, border_width=0)
        phone_entry.grid(row=5, column=0, sticky="ew", pady=6)

        reason_option = ctk.CTkOptionMenu(form, values=SUPPORT_REASONS, fg_color=COLOR_BOTTOM_CARD, button_color=COLOR_PRIMARY, button_hover_color=COLOR_PRIMARY_DARK)
        reason_option.grid(row=6, column=0, sticky="ew", pady=6)

        description_box = ctk.CTkTextbox(form, height=120, fg_color=COLOR_BOTTOM_CARD, border_width=0)
        description_box.grid(row=7, column=0, sticky="ew", pady=12)

        status_label = ctk.CTkLabel(form, text="", font=self.fonts["small"], text_color=COLOR_TEXT_MUTED)
        status_label.grid(row=8, column=0, sticky="w", pady=(0, 8))

        button_row = ctk.CTkFrame(form, fg_color="transparent")
        button_row.grid(row=9, column=0, sticky="ew", pady=(0, 12))
        button_row.grid_columnconfigure(0, weight=1)

        cancel_button = ctk.CTkButton(
            button_row,
            text="Cancelar",
            command=modal.destroy,
            fg_color="transparent",
            hover_color="#F3F4F6",
            text_color=COLOR_TEXT_MUTED,
            font=self.fonts["button"],
        )
        cancel_button.grid(row=0, column=0, sticky="w")

        def submit():
            first_name = first_name_entry.get().strip()
            last_name = last_name_entry.get().strip()
            email = email_entry.get().strip()
            phone = "".join(ch for ch in phone_entry.get() if ch.isdigit())
            reason_label = reason_option.get().strip().lower()
            description = description_box.get("0.0", "end").strip()

            if reason_label.startswith("soporte"):
                reason = "soporte"
            elif reason_label.startswith("consulta"):
                reason = "consulta"
            else:
                reason = ""

            if not all([first_name, last_name, email, reason, phone, description]):
                status_label.configure(text="Completa todos los campos para crear tu ticket.", text_color=COLOR_ACCENT)
                return

            if len(phone) != 9:
                status_label.configure(text="El telefono debe tener 9 digitos.", text_color=COLOR_ACCENT)
                return

            payload = {
                "firstName": first_name,
                "lastName": last_name,
                "email": email,
                "reason": reason,
                "phone": phone,
                "description": description,
            }

            status_label.configure(text="Enviando ticket...", text_color=COLOR_TEXT_MUTED)
            ok, ticket_id, feedback = self.controller.handle_create_support_ticket(payload)

            if ok:
                status_label.configure(text=feedback or "Ticket creado correctamente.", text_color=COLOR_PRIMARY)
                self.messages_cache.clear()
                self.tab_var.set(TAB_PENDING)
                self.refresh_tickets()
                if ticket_id:
                    self.active_ticket_id = ticket_id
                    self._load_messages(ticket_id)
                    self._schedule_message_refresh()
                modal.after(1200, modal.destroy)
            else:
                status_label.configure(text=feedback or "No pudimos crear el ticket.", text_color=COLOR_ACCENT)

        submit_button = ctk.CTkButton(
            button_row,
            text="Enviar ticket",
            command=submit,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_DARK,
            text_color="#F8FAFC",
            font=self.fonts["button"],
        )
        submit_button.grid(row=0, column=1, sticky="e")

        modal.grab_set()

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
    def _normalize_ticket(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        created_raw = raw.get("created_at") or raw.get("createdAt")
        first = str(raw.get("firstName") or raw.get("first_name") or "").strip()
        last = str(raw.get("lastName") or raw.get("last_name") or "").strip()
        email = str(raw.get("email") or raw.get("contactEmail") or "").strip()
        full_name = " ".join(part for part in [first, last] if part).strip()

        messages_count: Optional[int] = None
        counter = raw.get("_count") or {}
        if isinstance(counter, dict):
            candidate = counter.get("messages") or counter.get("messages_count")
            try:
                messages_count = int(candidate) if candidate is not None else None
            except (TypeError, ValueError):
                messages_count = None

        return {
            "id": raw.get("id"),
            "reason": str(raw.get("reason", "soporte")).lower(),
            "status": str(raw.get("status", "pendiente")).lower(),
            "first_name": first or None,
            "last_name": last or None,
            "full_name": full_name or None,
            "email": email or None,
            "messages_count": messages_count,
            "created_at": self._parse_datetime(created_raw),
        }

    def _get_status_badge_colors(self, status: Optional[str]) -> tuple[str, str]:
        default = ("#E5E7EB", COLOR_PRIMARY)
        if not status:
            return default
        return STATUS_BADGE_COLORS.get(status.lower(), default)

    def _get_reason_badge_colors(self, reason: Optional[str]) -> tuple[str, str]:
        default = ("#E0F2FE", "#075985")
        if not reason:
            return default
        return REASON_BADGE_COLORS.get(reason.lower(), default)

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

    def _format_timestamp(self, value: Any) -> str:
        if isinstance(value, datetime):
            return value.strftime("%d/%m/%Y %H:%M")
        if isinstance(value, str) and value:
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00") if value.endswith("Z") else value)
                return parsed.strftime("%d/%m/%Y %H:%M")
            except ValueError:
                return value
        return "--"

    def _format_date(self, value: Any) -> str:
        if isinstance(value, datetime):
            return value.strftime("%d-%m-%Y")
        if isinstance(value, str) and value:
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00") if value.endswith("Z") else value)
                return parsed.strftime("%d-%m-%Y")
            except ValueError:
                return value
        return ""

    def _get_ticket(self, ticket_id: int) -> Optional[Dict[str, Any]]:
        for ticket in self.support_tickets:
            if ticket.get("id") == ticket_id:
                return ticket
        return None

    def _set_composer_enabled(self, enabled: bool):
        if self.message_input:
            if enabled:
                self.message_input.configure(state="normal")
            else:
                self.message_input.configure(state="disabled")
        if self.send_button:
            self.send_button.configure(state="normal" if enabled else "disabled")

    # ------------------------------------------------------------------
    # Refrescos automaticos
    # ------------------------------------------------------------------
    def _schedule_ticket_refresh(self):
        if self._tickets_refresh_job:
            try:
                self.after_cancel(self._tickets_refresh_job)
            except Exception:
                pass
        self._tickets_refresh_job = self.after(TICKETS_REFRESH_MS, self.refresh_tickets)

    def _schedule_message_refresh(self):
        if self._messages_refresh_job:
            try:
                self.after_cancel(self._messages_refresh_job)
            except Exception:
                pass
            self._messages_refresh_job = None

        if not self.active_ticket_id:
            return
        self._messages_refresh_job = self.after(MESSAGES_REFRESH_MS, self._refresh_active_messages)

    def _refresh_active_messages(self):
        if not self.active_ticket_id:
            return
        self._load_messages(self.active_ticket_id, use_cache=False)
        self._schedule_message_refresh()

    def _cancel_refresh_jobs(self):
        for job_attr in ("_tickets_refresh_job", "_messages_refresh_job"):
            job_id = getattr(self, job_attr, None)
            if job_id:
                try:
                    self.after_cancel(job_id)
                except Exception:
                    pass
                setattr(self, job_attr, None)

    def _show_status(self, message: str, error: bool = False, success: bool = False, pending: bool = False):
        if error:
            color = COLOR_ACCENT
        elif success:
            color = COLOR_PRIMARY
        elif pending:
            color = COLOR_TEXT_MUTED
        else:
            color = COLOR_TEXT_MUTED
        self.status_var.set(message)
        if self.status_label is not None:
            self.status_label.configure(text_color=color)

    def _handle_close_ticket(self):
        self._show_status("Cerrar ticket aun no esta disponible en la app de escritorio.", error=True)

    def destroy(self):
        self._cancel_refresh_jobs()
        super().destroy()

    def _handle_resize(self, event):
        if event.widget is self and self.hero_label and self.hero_source:
            width = max(event.width, 900)
            resized = self.hero_source.resize((width, HERO_HEIGHT))
            self.hero_image = ctk.CTkImage(resized, size=(width, HERO_HEIGHT))
            self.hero_label.configure(image=self.hero_image)
            # keep a strong reference to the image on the view to avoid GC and
            # avoid assigning to a non-existent 'image' attribute on CTkLabel.
            self._hero_image_ref = self.hero_image
            
