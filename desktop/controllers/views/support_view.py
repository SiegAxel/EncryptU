import customtkinter as ctk
from datetime import datetime
from typing import Any, Dict, List, Optional

from PIL import Image

COLOR_BACKGROUND = "#F3F5F9"
COLOR_SURFACE = "#FFFFFF"
COLOR_SURFACE_ALT = "#F8FAFC"
COLOR_TEXT = "#1F2933"
COLOR_TEXT_MUTED = "#6B7280"
COLOR_ACCENT = "#F43F5E"
COLOR_ACCENT_DARK = "#DC1F45"
COLOR_PRIMARY = "#2563EB"
COLOR_PRIMARY_DARK = "#1D4ED8"
COLOR_AGENT = "#7C3AED"
COLOR_AGENT_TEXT = "#F9FAFB"
COLOR_CLIENT = "#E5E7EB"
COLOR_CLIENT_TEXT = "#1F2933"

SUPPORT_REASONS = ["Soporte", "Consulta"]
GRADIENT_PATH = "desktop/controllers/img/bg_main.png"
HERO_HEIGHT = 240


from .base_view import BaseView

class SupportView(BaseView):
    """Vista dedicada para la gestion de soporte y tickets de EncryptU."""

    def __init__(self, master, controller, username: str):
        super().__init__(master, fg_color=COLOR_BACKGROUND)
        self.controller = controller
        self.username = username or "Usuario"

        self.fonts = self._build_fonts()
        self.hero_source = self._load_gradient()
        self.hero_image: Optional[ctk.CTkImage] = None
        self.hero_label: Optional[ctk.CTkLabel] = None
        self._hero_image_ref: Optional[ctk.CTkImage] = None

        self.support_tickets: List[Dict[str, Any]] = []
        self.messages_cache: Dict[int, List[Dict[str, Any]]] = {}
        self.active_ticket_id: Optional[int] = None

        self.tickets_container: Optional[ctk.CTkScrollableFrame] = None
        self.chat_messages_container: Optional[ctk.CTkScrollableFrame] = None
        self.message_input: Optional[ctk.CTkTextbox] = None
        self.send_button: Optional[ctk.CTkButton] = None
        self.status_label: Optional[ctk.CTkLabel] = None

        self.chat_title_var = ctk.StringVar(value="Selecciona un ticket")
        self.chat_meta_var = ctk.StringVar(value="")
        self.status_var = ctk.StringVar(value="")

        self._build_layout()
        self.bind("<Configure>", self._handle_resize)
        self.after(200, self.refresh_tickets)

    # ------------------------------------------------------------------
    # Construccion
    # ------------------------------------------------------------------
    def _build_fonts(self) -> Dict[str, ctk.CTkFont]:
        return {
            "hero_title": ctk.CTkFont(size=34, weight="bold"),
            "hero_sub": ctk.CTkFont(size=16),
            "section": ctk.CTkFont(size=18, weight="bold"),
            "badge": ctk.CTkFont(size=13, weight="bold"),
            "body": ctk.CTkFont(size=13),
            "small": ctk.CTkFont(size=12),
            "button": ctk.CTkFont(size=14, weight="bold"),
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
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_hero()
        self._build_body()

    def _build_hero(self):
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

        title = ctk.CTkLabel(
            content,
            text="Centro de soporte",
            font=self.fonts["hero_title"],
            text_color="#F8FAFC",
        )
        title.grid(row=1, column=0, sticky="w")

        subtitle = ctk.CTkLabel(
            content,
            text="Consulta tus tickets, conversa con el equipo y crea nuevas solicitudes.",
            font=self.fonts["hero_sub"],
            text_color="#E2E8F0",
        )
        subtitle.grid(row=2, column=0, sticky="w", pady=(8, 0))

    def _build_body(self):
        body = ctk.CTkFrame(self, fg_color=COLOR_BACKGROUND)
        body.grid(row=1, column=0, sticky="nsew", padx=36, pady=(0, 32))
        body.grid_columnconfigure(0, weight=1, uniform="col")
        body.grid_columnconfigure(1, weight=2, uniform="col")
        body.grid_rowconfigure(0, weight=1)

        self._build_ticket_panel(body)
        self._build_chat_panel(body)

    def _build_ticket_panel(self, parent: ctk.CTkFrame):
        panel = ctk.CTkFrame(parent, fg_color=COLOR_SURFACE, corner_radius=24)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(2, weight=1)

        header = ctk.CTkLabel(panel, text="Mis tickets", font=self.fonts["section"], text_color=COLOR_TEXT)
        header.grid(row=0, column=0, sticky="w", padx=24, pady=(24, 8))

        actions = ctk.CTkFrame(panel, fg_color="transparent")
        actions.grid(row=1, column=0, sticky="ew", padx=24)
        actions.grid_columnconfigure(0, weight=1)

        refresh_button = ctk.CTkButton(
            actions,
            text="Actualizar",
            command=self.refresh_tickets,
            fg_color="transparent",
            hover_color="#EEF2FF",
            text_color=COLOR_PRIMARY,
            font=self.fonts["button"],
        )
        refresh_button.grid(row=0, column=0, sticky="w")

        new_ticket_button = ctk.CTkButton(
            actions,
            text="Nuevo ticket",
            command=self._open_new_ticket_modal,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_DARK,
            text_color="#F8FAFC",
            font=self.fonts["button"],
        )
        new_ticket_button.grid(row=0, column=1, sticky="e")

        self.tickets_container = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        self.tickets_container.grid(row=2, column=0, sticky="nsew", padx=16, pady=(12, 24))

    def _build_chat_panel(self, parent: ctk.CTkFrame):
        panel = ctk.CTkFrame(parent, fg_color=COLOR_SURFACE, corner_radius=24)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.grid_rowconfigure(2, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(panel, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 12))
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(header, textvariable=self.chat_title_var, font=self.fonts["section"], text_color=COLOR_TEXT)
        title.grid(row=0, column=0, sticky="w")

        meta = ctk.CTkLabel(header, textvariable=self.chat_meta_var, font=self.fonts["small"], text_color=COLOR_TEXT_MUTED)
        meta.grid(row=1, column=0, sticky="w", pady=(4, 0))

        self.chat_messages_container = ctk.CTkScrollableFrame(panel, fg_color=COLOR_SURFACE_ALT, corner_radius=18)
        self.chat_messages_container.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 12))

        editor = ctk.CTkFrame(panel, fg_color="transparent")
        editor.grid(row=3, column=0, sticky="ew", padx=24, pady=(0, 24))
        editor.grid_columnconfigure(0, weight=1)

        self.message_input = ctk.CTkTextbox(editor, height=80, corner_radius=16, fg_color=COLOR_SURFACE_ALT, border_width=0)
        self.message_input.grid(row=0, column=0, sticky="ew")
        self.message_input.bind("<Control-Return>", self._send_message_event)

        button_row = ctk.CTkFrame(editor, fg_color="transparent")
        button_row.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        button_row.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(button_row, textvariable=self.status_var, font=self.fonts["small"], text_color=COLOR_TEXT_MUTED)
        self.status_label.grid(row=0, column=0, sticky="w")

        self.send_button = ctk.CTkButton(
            button_row,
            text="Enviar",
            command=self._send_message,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_DARK,
            text_color="#F8FAFC",
            font=self.fonts["button"],
            width=120,
        )
        self.send_button.grid(row=0, column=1, sticky="e")

        self._set_composer_enabled(False)

    # ------------------------------------------------------------------
    # Datos
    # ------------------------------------------------------------------
    def refresh_tickets(self):
        data = self.controller.get_support_tickets(force_refresh=True)
        if data is None:
            self._show_status("No se pudieron cargar los tickets. Intenta nuevamente.", error=True)
            return

        self.support_tickets = [self._normalize_ticket(item) for item in data if item]
        if self.tickets_container:
            for widget in self.tickets_container.winfo_children():
                widget.destroy()

            if not self.support_tickets:
                ctk.CTkLabel(
                    self.tickets_container,
                    text="Aun no tienes tickets abiertos.",
                    font=self.fonts["body"],
                    text_color=COLOR_TEXT_MUTED,
                ).pack(padx=12, pady=24)
            else:
                for ticket in self.support_tickets:
                    self._render_ticket_card(ticket)

        if self.active_ticket_id:
            if not any(t["id"] == self.active_ticket_id for t in self.support_tickets):
                self.active_ticket_id = None
                self.chat_title_var.set("Selecciona un ticket")
                self.chat_meta_var.set("")
                self._render_messages(None)

    def _render_ticket_card(self, ticket: Dict[str, Any]):
        card = ctk.CTkFrame(self.tickets_container, fg_color=COLOR_SURFACE_ALT, corner_radius=18)
        card.pack(fill="x", padx=8, pady=6)

        header = ctk.CTkLabel(
            card,
            text=f"Ticket #{ticket.get('id', '--')}",
            font=self.fonts["body"],
            text_color=COLOR_TEXT,
        )
        header.pack(anchor="w", padx=16, pady=(14, 4))

        reason = ctk.CTkLabel(
            card,
            text=f"Motivo: {ticket.get('reason', 'soporte').title()}",
            font=self.fonts["small"],
            text_color=COLOR_TEXT_MUTED,
        )
        reason.pack(anchor="w", padx=16)

        created = ticket.get("created_at")
        if isinstance(created, datetime):
            created_str = created.strftime("%d/%m/%Y %H:%M")
        elif isinstance(created, str) and created:
            try:
                parsed = datetime.fromisoformat(created.replace("Z", "+00:00")) if created.endswith("Z") else datetime.fromisoformat(created)
                created_str = parsed.strftime("%d/%m/%Y %H:%M")
            except Exception:
                created_str = created
        else:
            created_str = "--"

        meta = ctk.CTkLabel(
            card,
            text=f"Estado: {ticket.get('status', 'pendiente').title()}  -  {created_str}",
            font=self.fonts["small"],
            text_color=COLOR_TEXT_MUTED,
        )
        meta.pack(anchor="w", padx=16, pady=(0, 14))

        card.bind("<Button-1>", lambda _e, tid=ticket.get("id"): self._handle_select_ticket(tid))
        for child in card.winfo_children():
            child.bind("<Button-1>", lambda _e, tid=ticket.get("id"): self._handle_select_ticket(tid))

    def _handle_select_ticket(self, ticket_id: Optional[int]):
        if ticket_id is None:
            return
        self.active_ticket_id = ticket_id
        ticket = self._get_ticket(ticket_id)
        if ticket:
            self.chat_title_var.set(f"Ticket #{ticket_id}")
            self.chat_meta_var.set(f"{ticket['reason'].title()} - Estado {ticket['status'].title()}")
        else:
            self.chat_title_var.set(f"Ticket #{ticket_id}")
            self.chat_meta_var.set("")
        self._load_messages(ticket_id)

    def _load_messages(self, ticket_id: int):
        if ticket_id in self.messages_cache:
            self._render_messages(self.messages_cache[ticket_id])
            return

        messages = self.controller.get_support_ticket_messages(ticket_id)
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

        if not messages:
            self._set_composer_enabled(False)
            ctk.CTkLabel(
                self.chat_messages_container,
                text="Selecciona un ticket para ver la conversacion.",
                font=self.fonts["body"],
                text_color=COLOR_TEXT_MUTED,
                wraplength=420,
                justify="center",
            ).pack(expand=True, fill="both", padx=24, pady=60)
            return

        self._set_composer_enabled(True)
        for message in messages:
            author_role = str(message.get("author") or "user").lower()
            is_agent = author_role == "agent"
            body = message.get("body") or ""
            timestamp = self._format_timestamp(message.get("timestamp"))
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
        else:
            self._show_status("No se pudo enviar el mensaje.", error=True)

        self.send_button.configure(state="normal")

    def _open_new_ticket_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Nuevo ticket de soporte")
        modal.geometry("520x520")
        modal.resizable(False, False)

        form = ctk.CTkFrame(modal, fg_color=COLOR_SURFACE, corner_radius=20)
        form.pack(expand=True, fill="both", padx=18, pady=18)
        form.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(form, text="Crear ticket", font=self.fonts["section"], text_color=COLOR_TEXT).grid(row=0, column=0, sticky="w", pady=(12, 4))
        ctk.CTkLabel(form, text="Cuentanos en que podemos ayudarte.", font=self.fonts["small"], text_color=COLOR_TEXT_MUTED).grid(row=1, column=0, sticky="w", pady=(0, 12))

        first_name_entry = ctk.CTkEntry(form, placeholder_text="Nombre", fg_color=COLOR_SURFACE_ALT, border_width=0)
        first_name_entry.grid(row=2, column=0, sticky="ew", pady=6)

        last_name_entry = ctk.CTkEntry(form, placeholder_text="Apellido", fg_color=COLOR_SURFACE_ALT, border_width=0)
        last_name_entry.grid(row=3, column=0, sticky="ew", pady=6)

        email_entry = ctk.CTkEntry(form, placeholder_text="Correo", fg_color=COLOR_SURFACE_ALT, border_width=0)
        email_entry.grid(row=4, column=0, sticky="ew", pady=6)
        email_entry.insert(0, self.username)

        phone_entry = ctk.CTkEntry(form, placeholder_text="Telefono (9 digitos)", fg_color=COLOR_SURFACE_ALT, border_width=0)
        phone_entry.grid(row=5, column=0, sticky="ew", pady=6)

        reason_option = ctk.CTkOptionMenu(form, values=SUPPORT_REASONS, fg_color=COLOR_SURFACE_ALT, button_color=COLOR_PRIMARY, button_hover_color=COLOR_PRIMARY_DARK)
        reason_option.grid(row=6, column=0, sticky="ew", pady=6)

        description_box = ctk.CTkTextbox(form, height=120, fg_color=COLOR_SURFACE_ALT, border_width=0)
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
                self.refresh_tickets()
                if ticket_id:
                    self.active_ticket_id = ticket_id
                    self._load_messages(ticket_id)
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
        return {
            "id": raw.get("id"),
            "reason": str(raw.get("reason", "soporte")).lower(),
            "status": str(raw.get("status", "pendiente")).lower(),
            "created_at": self._parse_datetime(created_raw),
        }

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
    def _handle_resize(self, event):
        if event.widget is self and self.hero_label and self.hero_source:
            width = max(event.width, 900)
            resized = self.hero_source.resize((width, HERO_HEIGHT))
            self.hero_image = ctk.CTkImage(resized, size=(width, HERO_HEIGHT))
            self.hero_label.configure(image=self.hero_image)
            # keep a strong reference to the image on the view to avoid GC and
            # avoid assigning to a non-existent 'image' attribute on CTkLabel.
            self._hero_image_ref = self.hero_image
            
