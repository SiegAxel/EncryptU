import customtkinter as ctk
from PIL import Image
import os

from .base_view import BaseView

class LoginView(BaseView):
    """
    Frame que contiene la interfaz de usuario para el inicio de sesión
    con una imagen de fondo responsiva.
    """
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.configure(fg_color="transparent")

        # --- Lógica para la imagen de fondo (RUTA CORREGIDA) ---
        self.original_bg_image = None
        self.image_path = "" # Para depuración
        try:
            # 1. Encontrar la carpeta raíz 'desktop'.
            current_dir = os.path.dirname(__file__) # Directorio actual: .../app/views
            desktop_dir = os.path.abspath(os.path.join(current_dir, '..', '..')) # Subimos dos niveles a .../desktop

            # 2. Construimos la ruta correcta hacia tu carpeta de imágenes.
            #    Ahora busca en desktop/controllers/img/bg.png
            self.image_path = os.path.join(desktop_dir, "controllers", "img", "bg.png")
            
            # Guardamos la imagen original de PIL para redimensionarla después
            self.original_bg_image = Image.open(self.image_path)
            
            # Creamos la etiqueta que contendrá la imagen
            self.bg_label = ctk.CTkLabel(self, text="")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

            # Vinculamos el evento <Configure> a la función de redimensionado
            self.bind("<Configure>", self._resize_image)

        except Exception as e:
            print(f"Error al cargar la imagen de fondo: {e}")
            # Imprimimos la ruta que se intentó usar para que sea fácil depurar
            print(f"Buscando en la ruta calculada: {self.image_path}")
            self.configure(fg_color=("#E0E0E0", "#1E1E1E"))
        # --- Fin de la lógica de la imagen de fondo ---

        # Frame contenedor (tarjeta) para centrar los widgets
        self.center_frame = ctk.CTkFrame(self, width=320, height=360, corner_radius=15, fg_color=("#ffffff", "#2b2b2b"))
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # ... (el resto de tus widgets permanecen igual) ...
        self.title_label = ctk.CTkLabel(self.center_frame, text="Iniciar Sesión", font=ctk.CTkFont(size=28, weight="bold"))
        self.title_label.pack(pady=(40, 20))
        self.username_entry = ctk.CTkEntry(self.center_frame, placeholder_text="Usuario", width=250, height=40, corner_radius=8)
        self.username_entry.pack(pady=10, padx=20)
        self.password_entry = ctk.CTkEntry(self.center_frame, placeholder_text="Contraseña", show="*", width=250, height=40, corner_radius=8)
        self.password_entry.pack(pady=10, padx=20)
        self.login_button = ctk.CTkButton(self.center_frame, text="Acceder", command=self.login_action, width=250, height=40, corner_radius=8, fg_color="#d40000", hover_color="#b30000")
        self.login_button.pack(pady=20, padx=20)
        self.error_label = ctk.CTkLabel(self.center_frame, text="", text_color="red")
        self.error_label.pack(pady=(0, 20))


    def _resize_image(self, event):
        """Se ejecuta cada vez que la ventana cambia de tamaño para ajustar el fondo."""
        if not self.original_bg_image:
            return

        new_width = event.width
        new_height = event.height
        
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


    def login_action(self):
        self.error_label.configure(text="")
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.controller.handle_login(username, password)

    def show_error(self, message):
        self.error_label.configure(text=message)

    def clear_fields(self):
        self.username_entry.delete(0, ctk.END)
        self.password_entry.delete(0, ctk.END)
        self.error_label.configure(text="")

