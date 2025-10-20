import customtkinter as ctk
from tkinter import messagebox

# Configurar apariencia
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

def centrar_ventana(win, ancho=500, alto=600):
    ancho_pantalla = win.winfo_screenwidth()
    alto_pantalla = win.winfo_screenheight()
    x = (ancho_pantalla // 2) - (ancho // 2)
    y = (alto_pantalla // 2) - (alto // 2)
    win.geometry(f"{ancho}x{alto}+{x}+{y}")

# Crear ventana
app = ctk.CTk()
app.title("EncryptU")
app.resizable(False, False)

# Centrar la ventana al abrir
centrar_ventana(app, 500, 600)


# Función para validar inicio de sesión
def login():
    user = entry_user.get()
    pwd = entry_pass.get()
    if user == "admin" and pwd == "judas123":
        messagebox.showinfo("Bienvenido", "Inicio de sesión exitoso ✅")
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos ❌")

def olvidar_contrasena(event):
    messagebox.showinfo("EncryptU","Se le ha enviado un correo para restablecer la contraseña")  # Falta agregar lógica jej

#Título
label_inicio = ctk.CTkLabel(app, text="Inicio de Sesión", font=ctk.CTkFont(size=30, weight="bold"), text_color="black")
label_inicio.pack(pady=20)

#Usuario
entry_user = ctk.CTkEntry(app, placeholder_text="Ingrese su Usuario", width=250, height=40)
entry_user.pack(pady=10)

#Contraseña
entry_pass = ctk.CTkEntry(app, placeholder_text="Ingrese su Contraseña", show="*", width=250, height=40)
entry_pass.pack(pady=10)

#Botón acceso
btn_login = ctk.CTkButton(app, text="Iniciar Sesión", width=200, height=35, command=login)
btn_login.pack(pady=20)

#Olvidar contraseña
label_olvide = ctk.CTkLabel(
    app,
    text="Olvidé mi contraseña",
    font=ctk.CTkFont(size=12, underline=True),
    text_color="blue",
    cursor="hand2"
)
label_olvide.pack(pady=20)
label_olvide.bind("<Button-1>", olvidar_contrasena)

#Footer
label_footer = ctk.CTkLabel(app, text="Protege tus claves con EncryptU, Todos los derechos reservados.", font=ctk.CTkFont(size=10, slant="italic"))
label_footer.pack(side="bottom", pady=10)

app.mainloop()
