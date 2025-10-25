import customtkinter as ctk
from PIL import Image
import os
import secrets # Importamos la librería para generar claves seguras

from .base_view import BaseView

class RegisterView(BaseView):
    """
    Frame para el registro de un nuevo usuario, con generación automática de Clave Maestra.
    """
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.configure(fg_color="transparent")

        # --- Lógica de la imagen de fondo ---
        self.original_bg_image = None
        self.image_path = ""
        try:
            current_dir = os.path.dirname(__file__)
            desktop_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
            self.image_path = os.path.join(desktop_dir, "controllers", "img", "bg.png")
            self.original_bg_image = Image.open(self.image_path)
            self.bg_label = ctk.CTkLabel(self, text="")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.bind("<Configure>", self._resize_image)
        except Exception as e:
            print(f"Error al cargar la imagen de fondo: {e}")
            self.configure(fg_color=("#E0E0E0", "#1E1E1E"))

        # --- Contenedor Central ---
        self.center_frame = ctk.CTkFrame(self, width=320, height=480, corner_radius=15)
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        self.register_form_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        self.register_form_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.title_label = ctk.CTkLabel(self.register_form_frame, text="Crear Cuenta", font=ctk.CTkFont(size=28, weight="bold"))
        self.title_label.pack(pady=(20, 10))
        
        self.subtitle_label = ctk.CTkLabel(self.register_form_frame, text="Completa tus datos y guarda tu Clave Maestra.", wraplength=280)
        self.subtitle_label.pack(pady=(0, 20), padx=10)

        self.name_entry = ctk.CTkEntry(self.register_form_frame, placeholder_text="Nombre Completo", width=250, height=40)
        self.name_entry.pack(pady=5)

        self.email_entry = ctk.CTkEntry(self.register_form_frame, placeholder_text="Correo Electrónico", width=250, height=40)
        self.email_entry.pack(pady=5)
        
        # --- SECCIÓN DE CLAVE MAESTRA AUTOMÁTICA ---
        self.master_key_label = ctk.CTkLabel(self.register_form_frame, text="Tu Clave Maestra (¡Guárdala!)", font=ctk.CTkFont(size=12, weight="bold"))
        self.master_key_label.pack(pady=(10, 0))

        # Contenedor para la clave y el botón de copiar
        key_container = ctk.CTkFrame(self.register_form_frame, fg_color="transparent")
        key_container.pack(pady=5)

        # Generamos la clave maestra segura
        self.generated_master_key = secrets.token_hex(16)

        self.password_entry = ctk.CTkEntry(key_container, width=200, height=40)
        self.password_entry.insert(0, self.generated_master_key)
        self.password_entry.configure(state="readonly") # Hacemos el campo no editable
        self.password_entry.pack(side="left", padx=(0, 5))

        self.copy_button = ctk.CTkButton(key_container, text="Copiar", width=45, command=self.copy_to_clipboard)
        self.copy_button.pack(side="left")

        self.warning_label = ctk.CTkLabel(self.register_form_frame, text="⚠️ Es la única vez que verás esta clave.", font=ctk.CTkFont(size=11), text_color="orange")
        self.warning_label.pack(pady=(0, 10))
        # --- FIN DE LA SECCIÓN ---

        self.register_button = ctk.CTkButton(self.register_form_frame, text="Registrarme y Confirmar Clave", command=self.register_action, width=250, height=40)
        self.register_button.pack(pady=10)

        self.go_to_login_link = ctk.CTkButton(self.register_form_frame, text="Ya tengo una cuenta", fg_color="transparent", text_color=("gray10", "#DCE4EE"), hover=False, command=self.go_to_login, font=ctk.CTkFont(size=12))
        self.go_to_login_link.pack(pady=(0, 20))
        
        self.error_label = ctk.CTkLabel(self.register_form_frame, text="", text_color="red")
        self.error_label.pack(pady=(0, 10))
        
        self.success_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")

    def copy_to_clipboard(self):
        self.clipboard_clear()
        self.clipboard_append(self.generated_master_key)
        self.update() # Necesario para que el portapapeles se actualice
        print("Clave Maestra copiada al portapapeles.")
        # Opcional: Cambiar texto del botón temporalmente
        self.copy_button.configure(text="¡Ok!")
        self.copy_button.after(2000, lambda: self.copy_button.configure(text="Copiar"))


    def _resize_image(self, event):
        if not self.original_bg_image: return
        new_width, new_height = event.width, event.height
        img_ratio = self.original_bg_image.width / self.original_bg_image.height
        frame_ratio = new_width / new_height
        if frame_ratio > img_ratio:
            resize_width = new_width
            resize_height = int(resize_width / img_ratio)
        else:
            resize_height = new_height
            resize_width = int(resize_height * img_ratio)
        resized_img = self.original_bg_image.resize((resize_width, resize_height), Image.Resampling.LANCZOS)
        new_bg_image = ctk.CTkImage(light_image=resized_img, dark_image=resized_img, size=(resize_width, resize_height))
        self.bg_label.configure(image=new_bg_image)
        self.bg_label.place(relx=0.5, rely=0.5, anchor="center")

    def go_to_login(self):
        self.controller.show_login_view()

    def register_action(self):
        self.error_label.configure(text="")
        name = self.name_entry.get()
        email = self.email_entry.get()
        # La contraseña es la que generamos automáticamente
        password = self.generated_master_key
        
        if not name or not email:
            self.show_error("El nombre y el correo son requeridos.")
            return
            
        self.register_button.configure(state="disabled", text="Registrando...")
        self.controller.handle_register(name, email, password)

    def show_registration_success(self):
        self.register_form_frame.pack_forget()
        self.success_frame.pack(pady=20, padx=20, fill="both", expand=True)

        info_title = ctk.CTkLabel(self.success_frame, text="¡Registro Exitoso!", font=ctk.CTkFont(size=24, weight="bold"))
        info_title.pack(pady=(20, 10))
        
        info_label = ctk.CTkLabel(self.success_frame, text="Tu cuenta ha sido creada.\nYa puedes iniciar sesión con tu Clave Maestra.", wraplength=280)
        info_label.pack(pady=(0, 20))
        
        login_button = ctk.CTkButton(self.success_frame, text="Continuar a Iniciar Sesión", width=250, height=40, command=self.go_to_login)
        login_button.pack(pady=20)

    def show_error(self, message):
        self.error_label.configure(text=message)
        self.register_button.configure(state="normal", text="Registrarme y Confirmar Clave")