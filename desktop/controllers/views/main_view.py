import customtkinter as ctk
from typing import cast
import pyperclip

# --- Definición de Colores Corporativos ---
COLOR_ROJO_PRINCIPAL = "#c50000"
COLOR_ROJO_HOVER = "#a50000"
COLOR_TEXTO_PRINCIPAL = "#FFFFFF"
COLOR_FONDO_FRAME = "#242424"
COLOR_FONDO_TAB = "#2D2D2D"
COLOR_ENTRADA = "#343638"

class MainView(ctk.CTkFrame):
    """
    Frame que contiene la interfaz principal de la aplicación después del login.
    Organizada con pestañas para las funcionalidades de encriptar y ver contraseñas.
    """
    def __init__(self, master, controller, username):
        super().__init__(master)
        self.controller = controller
        self.username = username
        self.configure(fg_color="transparent")

        # --- ESTRUCTURA GENERAL ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- CABECERA ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="ew")
        
        self.welcome_label = ctk.CTkLabel(header_frame, text=f"Bienvenido, {self.username}!", font=ctk.CTkFont(size=20, weight="bold"), text_color=COLOR_TEXTO_PRINCIPAL)
        self.welcome_label.pack(side="left")

        self.logout_button = ctk.CTkButton(header_frame, text="Cerrar Sesión", width=120, command=self.logout_action, fg_color=COLOR_ROJO_PRINCIPAL, hover_color=COLOR_ROJO_HOVER)
        self.logout_button.pack(side="right")

        # --- PESTAÑAS DE FUNCIONALIDADES ---
        self.tab_view = ctk.CTkTabview(self, fg_color=COLOR_FONDO_FRAME)
        self.tab_view.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.tab_view.add("Guardar Contraseña")
        self.tab_view.add("Mis Contraseñas")

        self._create_save_password_tab(self.tab_view.tab("Guardar Contraseña"))
        self._create_view_passwords_tab(self.tab_view.tab("Mis Contraseñas"))
        
        self.refresh_password_list()

    def _create_save_password_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)
        
        container = ctk.CTkFrame(tab, fg_color="transparent")
        container.pack(padx=20, pady=20, fill="x")

        title = ctk.CTkLabel(container, text="Guardar Nueva Contraseña", font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(anchor="w")

        self.site_entry = ctk.CTkEntry(container, placeholder_text="Sitio Web (ej: google.com)", height=40, fg_color=COLOR_ENTRADA, border_width=0)
        self.site_entry.pack(fill="x", pady=(10, 5))

        # --- NUEVO CAMPO PARA EL NOMBRE DE USUARIO ---
        self.username_entry_save = ctk.CTkEntry(container, placeholder_text="Nombre de Usuario (del sitio)", height=40, fg_color=COLOR_ENTRADA, border_width=0)
        self.username_entry_save.pack(fill="x", pady=5)
        # --- FIN DEL NUEVO CAMPO ---

        self.password_entry = ctk.CTkEntry(container, placeholder_text="Contraseña a guardar", show="*", height=40, fg_color=COLOR_ENTRADA, border_width=0)
        self.password_entry.pack(fill="x", pady=5)

        self.save_button = ctk.CTkButton(container, text="Guardar de forma segura", command=self.save_action, height=40, fg_color=COLOR_ROJO_PRINCIPAL, hover_color=COLOR_ROJO_HOVER)
        self.save_button.pack(anchor="w", pady=(20, 10))

        self.status_label_save = ctk.CTkLabel(container, text="", font=ctk.CTkFont(size=12))
        self.status_label_save.pack(anchor="w")

    def _create_view_passwords_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(tab, fg_color="transparent")
        header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        title = ctk.CTkLabel(header, text="Mis Contraseñas Guardadas", font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(side="left")
        
        refresh_button = ctk.CTkButton(header, text="Refrescar", width=100, command=self.refresh_password_list)
        refresh_button.pack(side="right")

        self.scrollable_frame = ctk.CTkScrollableFrame(tab, fg_color=COLOR_FONDO_TAB)
        self.scrollable_frame.grid(row=1, column=0, padx=20, pady=5, sticky="nsew")

    def save_action(self):
        site = self.site_entry.get()
        username = self.username_entry_save.get()
        password = self.password_entry.get()
        
        if not site or not password or not username:
            self.show_status("Por favor, completa todos los campos.", "save", "red")
            return

        self.save_button.configure(state="disabled", text="Guardando...")
        self.show_status("Guardando...", "save", "white")
        
        success = self.controller.handle_encrypt_and_save(site, username, password)
        
        if success:
            self.show_status(f"Contraseña para '{site}' guardada con éxito.", "save", "green")
            self.site_entry.delete(0, "end")
            self.username_entry_save.delete(0, "end")
            self.password_entry.delete(0, "end")
            self.refresh_password_list()
        else:
            self.show_status("Error al guardar. Inténtalo de nuevo.", "save", "red")
        
        self.save_button.configure(state="normal", text="Guardar de forma segura")

    def refresh_password_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        passwords = self.controller.get_saved_passwords()
        
        if passwords is None:
            ctk.CTkLabel(self.scrollable_frame, text="No se pudieron cargar las contraseñas.", text_color="red").pack(pady=20)
            return
        if not passwords:
            ctk.CTkLabel(self.scrollable_frame, text="Aún no has guardado ninguna contraseña.").pack(pady=20)
            return

        # Cabecera de la lista
        header_list = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        header_list.pack(fill="x", padx=5, pady=(0,5))
        header_list.grid_columnconfigure(0, weight=1)
        header_list.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(header_list, text="Sitio Web", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(header_list, text="Usuario", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, sticky="w")


        for p in passwords:
            file_id = p["id"]
            full_filename = p["filename"]
            
            # --- LÓGICA PARA SEPARAR SITIO Y USUARIO ---
            parts = full_filename.split(" | ", 1)
            site = parts[0]
            username = parts[1] if len(parts) > 1 else ""
            # --- FIN DE LA LÓGICA ---

            item_frame = ctk.CTkFrame(self.scrollable_frame, fg_color=("gray85", COLOR_ENTRADA))
            item_frame.pack(fill="x", padx=5, pady=5)
            item_frame.grid_columnconfigure(0, weight=1)
            item_frame.grid_columnconfigure(1, weight=1)
            
            ctk.CTkLabel(item_frame, text=site).grid(row=0, column=0, sticky="w", padx=10, pady=10)
            ctk.CTkLabel(item_frame, text=username, text_color="gray").grid(row=0, column=1, sticky="w", padx=10, pady=10)
            
            button_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            button_frame.grid(row=0, column=2, sticky="e")

            delete_button = ctk.CTkButton(button_frame, text="Eliminar", width=80, fg_color=COLOR_ROJO_PRINCIPAL, hover_color=COLOR_ROJO_HOVER,
                                          command=lambda fid=file_id: self.delete_action(fid))
            delete_button.pack(side="right", padx=(5,10), pady=5)

            view_button = ctk.CTkButton(button_frame, text="Ver/Copiar", width=100,
                                        command=lambda fid=file_id, s=site: self.view_copy_action(fid, s))
            view_button.pack(side="right", pady=5)

    def delete_action(self, file_id: int):
        success = self.controller.handle_delete_password(file_id)
        if success:
            self.refresh_password_list()
        else:
            self.show_temp_popup("Error al eliminar la contraseña.", "red")

    def view_copy_action(self, file_id: int, site: str):
        dialog = ctk.CTkInputDialog(text="Para desencriptar, ingresa tu Clave Maestra:", title="Verificación de Seguridad")
        master_key = dialog.get_input()

        if master_key:
            decrypted_pass = self.controller.handle_decrypt_password(file_id, site, master_key)
            if decrypted_pass:
                pyperclip.copy(decrypted_pass)
                self.show_temp_popup("¡Contraseña copiada al portapapeles!")
            else:
                self.show_temp_popup("Clave Maestra incorrecta.", "red")
                
    def logout_action(self):
        self.controller.handle_logout()

    def show_status(self, message: str, tab: str, color: str):
        if tab == "save":
            self.status_label_save.configure(text=message, text_color=color)
            self.status_label_save.after(3000, lambda: self.status_label_save.configure(text=""))

    def show_temp_popup(self, message: str, color: str = "green"):
        popup = ctk.CTkToplevel(self)
        popup.geometry("300x100")
        popup.title("Notificación")
        popup.transient(cast(ctk.CTk, self.winfo_toplevel()))
        popup.grab_set()
        
        label = ctk.CTkLabel(popup, text=message, font=ctk.CTkFont(size=14), text_color=color)
        label.pack(expand=True, padx=20, pady=20)
        
        popup.after(2000, popup.destroy)

