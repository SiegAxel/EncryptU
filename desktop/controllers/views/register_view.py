import customtkinter as ctk
from PIL import Image
import os

class RegisterView(ctk.CTkFrame):
    """
    Frame para el registro de un nuevo usuario, con fondo responsivo y enlace a login.
    """
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.configure(fg_color="transparent")

        # --- Lógica para la imagen de fondo responsiva ---
        self.original_bg_image = None
        self.image_path = "" # Para depuración
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
            print(f"Buscando en la ruta calculada: {self.image_path}")
            self.configure(fg_color=("#E0E0E0", "#1E1E1E"))
        # --- Fin de la lógica de la imagen de fondo ---

        # --- Contenedor Central (Tarjeta) ---
        self.center_frame = ctk.CTkFrame(self, width=320, height=400, corner_radius=15)
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # --- Contenedor para el Formulario de Registro ---
        # Usamos un frame interno para poder ocultar/mostrar todo a la vez
        self.register_form_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        self.register_form_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.title_label = ctk.CTkLabel(self.register_form_frame, text="Crear Cuenta", font=ctk.CTkFont(size=28, weight="bold"))
        self.title_label.pack(pady=(20, 10))
        
        self.subtitle_label = ctk.CTkLabel(self.register_form_frame, text="Regístrate para obtener tu Clave Maestra.", wraplength=280)
        self.subtitle_label.pack(pady=(0, 20), padx=10)

        self.email_entry = ctk.CTkEntry(self.register_form_frame, placeholder_text="Correo Electrónico", width=250, height=40)
        self.email_entry.pack(pady=10)

        self.register_button = ctk.CTkButton(self.register_form_frame, text="Registrarme", command=self.register_action, width=250, height=40)
        self.register_button.pack(pady=20)

        # Enlace para ir a Login
        self.go_to_login_link = ctk.CTkButton(
            self.register_form_frame, 
            text="Ya poseo Clave Maestra",
            fg_color="transparent",
            text_color=("gray10", "#DCE4EE"),
            hover=False,
            command=self.go_to_login,
            font=ctk.CTkFont(size=12)
        )
        self.go_to_login_link.pack(pady=(0, 20))
        self.go_to_login_link.bind("<Enter>", self._on_enter_link)
        self.go_to_login_link.bind("<Leave>", self._on_leave_link)
        
        self.error_label = ctk.CTkLabel(self.register_form_frame, text="", text_color="red")
        self.error_label.pack(pady=(0, 10))
        
        # --- Contenedor para mostrar la Clave Maestra (inicialmente oculto) ---
        self.key_display_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        # Este frame se mostrará con .pack() en show_master_key

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

    def _on_enter_link(self, event):
        self.go_to_login_link.configure(font=ctk.CTkFont(size=12, underline=True))

    def _on_leave_link(self, event):
        self.go_to_login_link.configure(font=ctk.CTkFont(size=12, underline=False))

    def go_to_login(self):
        self.controller.show_login_view()

    def register_action(self):
        self.error_label.configure(text="")
        email = self.email_entry.get()
        if not email:
            self.show_error("Por favor, ingresa un correo.")
            return
        self.register_button.configure(state="disabled", text="Registrando...")
        self.controller.handle_register(email)

    def show_master_key(self, master_key):
        self.register_form_frame.pack_forget()
        self.key_display_frame.pack(pady=20, padx=20, fill="both", expand=True)

        info_title = ctk.CTkLabel(self.key_display_frame, text="¡Registro Exitoso!", font=ctk.CTkFont(size=24, weight="bold"))
        info_title.pack(pady=(20, 10))
        
        info_label = ctk.CTkLabel(self.key_display_frame, text="Guarda tu Clave Maestra en un lugar seguro.\nEs la única vez que la verás.", wraplength=280)
        info_label.pack(pady=(0, 20))

        key_entry = ctk.CTkEntry(self.key_display_frame, width=250, height=40, font=ctk.CTkFont(family="Courier New", size=14))
        key_entry.insert(0, master_key)
        key_entry.configure(state="readonly")
        key_entry.pack(pady=10)

        copy_button = ctk.CTkButton(self.key_display_frame, text="Copiar Clave", width=250, height=40, command=lambda: self.copy_to_clipboard(master_key))
        copy_button.pack(pady=10)
        
        login_button = ctk.CTkButton(self.key_display_frame, text="Continuar a Iniciar Sesión", width=250, height=40, command=self.go_to_login)
        login_button.pack(pady=20)

    def copy_to_clipboard(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()
        print("Clave copiada al portapapeles.")

    def show_error(self, message):
        self.error_label.configure(text=message)
        self.register_button.configure(state="normal", text="Registrarme")

