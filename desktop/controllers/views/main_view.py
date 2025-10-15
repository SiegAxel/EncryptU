import customtkinter as ctk
from typing import cast
import pyperclip
from PIL import Image
import os

# --- Definición de Colores Corporativos y Estilos ---
COLOR_ROJO_PRINCIPAL = "#e53e3e"
COLOR_ROJO_HOVER = "#c53030"
COLOR_BLANCO = "#FFFFFF"
COLOR_GRIS_TEXTO = "#FF0000"
COLOR_FONDO_TARJETA = ("#F7FAFC", "#FFFFFF")
COLOR_FONDO_APP = ("#FFFFFF", "#171923")


class MainView(ctk.CTkFrame):
    """
    Frame principal de la aplicación con un diseño mejorado basado en tarjetas,
    colores corporativos y fondo de imagen.
    """

    def __init__(self, master, controller, username):
        super().__init__(master)
        self.controller = controller
        self.username = username
        self.configure(fg_color="transparent")

        # Variable para mantener una referencia persistente al objeto de imagen
        self.bg_image_object = None

        # Configura las proporciones de las columnas y filas principales
        self.grid_columnconfigure((0, 1), weight=1, uniform="col")
        self.grid_rowconfigure(1, weight=1)  # fila donde están las cards
        self.grid_rowconfigure(0, weight=0)  # header no se expande

        self._setup_background_image()
        self._create_header()
        self._create_save_password_card()
        self._create_view_passwords_card()
        self.refresh_password_list()

    # ------------------------------------------------------------------
    # 🔹 Fondo de imagen redimensionable
    # ------------------------------------------------------------------
    def _setup_background_image(self):
        self.original_bg_image = None
        try:
            current_dir = os.path.dirname(__file__)
            desktop_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
            image_path = os.path.join(desktop_dir, "controllers", "img", "bg_main.png")

            print("\n--- DEBUG IMAGEN DE FONDO ---")
            print(f"Buscando imagen en la ruta absoluta: {image_path}")
            if os.path.exists(image_path):
                print("¡Éxito! El archivo fue encontrado en esa ruta.")
            else:
                print("¡ERROR! El archivo NO fue encontrado. Revisa la ruta y el nombre.")
            print("-----------------------------\n")
            self.original_bg_image = Image.open(image_path)
            self.bg_label = ctk.CTkLabel(self, text="", fg_color="transparent")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.bg_label.lower()  # mantiene el fondo detrás de todo

            self.bind("<Configure>", self._resize_image)
            self.after(10, self._resize_image)
        except Exception as e:
            print(f"Error al cargar imagen de fondo para MainView: {e}")

    def _resize_image(self, event=None):
        if not self.original_bg_image:
            return
        new_width, new_height = self.winfo_width(), self.winfo_height()
        if new_width <= 1 or new_height <= 1:
            return
        
        img_ratio = self.original_bg_image.width / self.original_bg_image.height
        frame_ratio = new_width / new_height
        if frame_ratio > img_ratio:
            resize_width = new_width
            resize_height = int(resize_width / img_ratio)
        else:
            resize_height = new_height
            resize_width = int(resize_height * img_ratio)
            
        resized_img = self.original_bg_image.resize(
            (resize_width, resize_height), Image.Resampling.LANCZOS
        )
        
        # Guardar la imagen en la variable de instancia para evitar que sea eliminada
        self.bg_image_object = ctk.CTkImage(
            light_image=resized_img, dark_image=resized_img, size=(resize_width, resize_height)
        )
        
        self.bg_label.configure(image=self.bg_image_object)
        self.bg_label.place(relx=0.5, rely=0.5, anchor="center")

    # ------------------------------------------------------------------
    # 🔹 Header superior
    # ------------------------------------------------------------------
    def _create_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(
            row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="ew"
        )
        header_frame.grid_columnconfigure(0, weight=1)

        welcome_label = ctk.CTkLabel(
            header_frame,
            text=f"Bienvenido, {self.username}!",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        welcome_label.grid(row=0, column=0, sticky="w")

        logout_button = ctk.CTkButton(
            header_frame,
            text="Cerrar Sesión",
            width=120,
            command=self.logout_action,
            fg_color=COLOR_ROJO_PRINCIPAL,
            hover_color=COLOR_ROJO_HOVER,
        )
        logout_button.grid(row=0, column=1, sticky="e")

    # ------------------------------------------------------------------
    # 🔹 Card: Guardar contraseña
    # ------------------------------------------------------------------
    def _create_save_password_card(self):
        card = ctk.CTkFrame(
            self, corner_radius=15, fg_color=COLOR_FONDO_TARJETA
        )
        card.grid(row=1, column=0, padx=(20, 10), pady=10, sticky="nsew")
        card.grid_propagate(False)
        card.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            card, text="Guardar Nueva Contraseña", font=ctk.CTkFont(size=18, weight="bold"), text_color=COLOR_GRIS_TEXTO
        )
        title.pack(anchor="w", padx=20, pady=(20, 10))

        self.site_entry = ctk.CTkEntry(
            card, placeholder_text="Sitio Web (ej: google.com)", height=40, border_width=0
        )
        self.site_entry.pack(fill="x", padx=20, pady=5)

        self.username_entry_save = ctk.CTkEntry(
            card, placeholder_text="Nombre de Usuario (del sitio)", height=40, border_width=0
        )
        self.username_entry_save.pack(fill="x", padx=20, pady=5)

        self.password_entry = ctk.CTkEntry(
            card, placeholder_text="Contraseña a guardar", show="*", height=40, border_width=0
        )
        self.password_entry.pack(fill="x", padx=20, pady=5)

        self.save_button = ctk.CTkButton(
            card,
            text="Guardar de Forma Segura",
            command=self.save_action,
            height=40,
            fg_color=COLOR_ROJO_PRINCIPAL,
            hover_color=COLOR_ROJO_HOVER,
        )
        self.save_button.pack(anchor="w", padx=20, pady=(20, 10))

        self.status_label_save = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=12))
        self.status_label_save.pack(anchor="w", padx=20, pady=(0, 20))

    # ------------------------------------------------------------------
    # 🔹 Card: Ver contraseñas
    # ------------------------------------------------------------------
    def _create_view_passwords_card(self):
        card = ctk.CTkFrame(
            self, corner_radius=15, fg_color=COLOR_FONDO_TARJETA
        )
        card.grid(row=1, column=1, padx=(10, 20), pady=10, sticky="nsew")
        card.grid_rowconfigure(1, weight=1)
        card.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header, text="Mis Contraseñas Guardadas", font=ctk.CTkFont(size=18, weight="bold"), text_color=COLOR_GRIS_TEXTO
        )
        title.grid(row=0, column=0, sticky="w")

        refresh_button = ctk.CTkButton(
            header,
            text="⟳",
            width=30,
            command=self.refresh_password_list,
            font=ctk.CTkFont(size=20),
        )
        refresh_button.grid(row=0, column=1, sticky="e")

        self.scrollable_frame = ctk.CTkScrollableFrame(card, fg_color="transparent")
        self.scrollable_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    # ------------------------------------------------------------------
    # 🔹 Funciones de lógica
    # ------------------------------------------------------------------
    def save_action(self):
        site = self.site_entry.get()
        username = self.username_entry_save.get()
        password = self.password_entry.get()

        if not site or not password or not username:
            self.show_status("Por favor, completa todos los campos.", "save", "red")
            return

        self.save_button.configure(state="disabled", text="Guardando...")
        self.show_status("Guardando...", "save", COLOR_GRIS_TEXTO)

        success = self.controller.handle_encrypt_and_save(site, username, password)

        if success:
            self.show_status(f"Contraseña para '{site}' guardada.", "save", "green")
            self.site_entry.delete(0, "end")
            self.username_entry_save.delete(0, "end")
            self.password_entry.delete(0, "end")
            self.refresh_password_list()
        else:
            self.show_status("Error al guardar. Inténtalo de nuevo.", "save", "red")

        self.save_button.configure(state="normal", text="Guardar de Forma Segura")

    def refresh_password_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        passwords = self.controller.get_saved_passwords()

        if passwords is None:
            ctk.CTkLabel(
                self.scrollable_frame,
                text="No se pudieron cargar las contraseñas.",
                text_color="red",
            ).pack(pady=20)
            return
        if not passwords:
            ctk.CTkLabel(
                self.scrollable_frame,
                text="Aún no has guardado ninguna contraseña.",
                text_color=COLOR_GRIS_TEXTO,
            ).pack(pady=20, padx=10)
            return

        for p in passwords:
            file_id = p["id"]
            full_filename = p["filename"]

            parts = full_filename.split(" | ", 1)
            site = parts[0]
            username_site = parts[1] if len(parts) > 1 else ""

            item_card = ctk.CTkFrame(
                self.scrollable_frame, corner_radius=10, fg_color=COLOR_FONDO_APP
            )
            item_card.pack(fill="x", padx=5, pady=5)

            info_frame = ctk.CTkFrame(item_card, fg_color="transparent")
            info_frame.pack(side="left", padx=15, pady=10, fill="x", expand=True)

            site_label = ctk.CTkLabel(info_frame, text=site, font=ctk.CTkFont(weight="bold"))
            site_label.pack(anchor="w")

            user_label = ctk.CTkLabel(info_frame, text=username_site, text_color=COLOR_GRIS_TEXTO)
            user_label.pack(anchor="w")

            button_frame = ctk.CTkFrame(item_card, fg_color="transparent")
            button_frame.pack(side="right", padx=10)

            delete_button = ctk.CTkButton(
                button_frame,
                text="Eliminar",
                width=80,
                fg_color=COLOR_ROJO_PRINCIPAL,
                hover_color=COLOR_ROJO_HOVER,
                command=lambda fid=file_id: self.delete_action(fid),
            )
            delete_button.pack(side="right", padx=(5, 0))

            view_button = ctk.CTkButton(
                button_frame,
                text="Ver/Copiar",
                width=100,
                command=lambda fid=file_id, s=site: self.view_copy_action(fid, s),
            )
            view_button.pack(side="right")

    def delete_action(self, file_id: int):
        if self.controller.handle_delete_password(file_id):
            self.refresh_password_list()
        else:
            self.show_temp_popup("Error al eliminar la contraseña.", "red")

    def view_copy_action(self, file_id: int, site: str):
        dialog = ctk.CTkInputDialog(
            text="Para desencriptar, ingresa tu Clave Maestra:", title="Verificación de Seguridad"
        )
        master_key = dialog.get_input()

        if master_key:
            decrypted_pass = self.controller.handle_decrypt_password(file_id, site, master_key)
            if decrypted_pass:
                pyperclip.copy(decrypted_pass)
                self.show_temp_popup("¡Contraseña copiada al portapapeles!")
            else:
                self.show_temp_popup("Clave Maestra incorrecta.", "red")

    def logout_action(self, event=None):
        self.controller.handle_logout()

    def show_status(self, message: str, tab_id: str, color: str):
        if tab_id == "save":
            self.status_label_save.configure(text=message, text_color=color)
            self.status_label_save.after(4000, lambda: self.status_label_save.configure(text=""))

    def show_temp_popup(self, message: str, color: str = "green"):
        toplevel_window = self.winfo_toplevel()
        if isinstance(toplevel_window, ctk.CTk):
            popup = ctk.CTkToplevel(toplevel_window)
            popup.geometry("300x100")
            popup.title("Notificación")
            popup.transient(toplevel_window)
            popup.grab_set()

            label = ctk.CTkLabel(popup, text=message, font=ctk.CTkFont(size=14), text_color=color)
            label.pack(expand=True, padx=20, pady=20)

            popup.after(2000, popup.destroy)