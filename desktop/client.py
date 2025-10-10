from customtkinter import CTk, CTkLabel, CTkButton, CTkFrame, CTkImage
from PIL import Image, ImageTk
import os
# ------------------------------
# Colores
# ------------------------------
APP_BG = "#1e1e1e"
MENU_BG = "#ffffff"
BUTTON_BG = "#c1121f"
BUTTON_FG = "#ffffff"
TEXT_COLOR = "#000000"
MAIN_BG = "#f5f5f5"
CARD_BG = "#ffffff"

# ------------------------------
# Variables de animación
# ------------------------------
menu_width_expanded = 150
menu_width_collapsed = 50
menu_animation_speed = 10
menu_expanded = True
padding_between_menu = 10

# ------------------------------
# Crear app
# ------------------------------
app = CTk()
app.title("EncryptU Client")
app.geometry("700x450")
app.resizable(True, True)
app.configure(fg_color=APP_BG)

# ------------------------------
# Menú lateral
# ------------------------------
menu_frame = CTkFrame(app, width=menu_width_expanded, corner_radius=0, fg_color=MENU_BG)
menu_frame.place(x=0, y=0, relheight=1)  
# ------------------------------
# Área principal (card)
# ------------------------------
# Se define width y height al crear el frame
main_frame = CTkFrame(app, width=700 - menu_width_expanded - padding_between_menu, fg_color=MAIN_BG)
main_frame.place(x=menu_width_expanded + padding_between_menu, y=0, relheight=1)  

# ------------------------------
# Background image CTKImage
# ------------------------------
script_dir = os.path.dirname(os.path.abspath(__file__))  # carpeta del script
bg_path = os.path.join(script_dir, "bg.jpg")
bg_photo = None
try:
    bg_image = Image.open(bg_path)
    bg_image = bg_image.resize((700, 450), Image.Resampling.LANCZOS)
    bg_photo = CTkImage(light_image=bg_image, dark_image=bg_image, size=(700, 450))
    bg_label = CTkLabel(main_frame, image=bg_photo, text="")
    bg_label.place(relx=0.5, rely=0.5, anchor="center")
except Exception as e:
    print(f"Error loading background image: {e}")
    bg_label = CTkLabel(main_frame, text="Error loading background image", font=("Arial", 16), text_color=TEXT_COLOR, fg_color=MAIN_BG)
    bg_label.place(relx=0.5, rely=0.5, anchor="center")


# ------------------------------
# Animación del menú
# ------------------------------
def toggle_menu():
    global menu_expanded
    target_width = menu_width_collapsed if menu_expanded else menu_width_expanded
    animate_menu(menu_frame.winfo_width(), target_width)
    menu_expanded = not menu_expanded

def animate_menu(current_width, target_width):
    if current_width == target_width:
        if target_width == menu_width_collapsed:
            for widget in menu_frame.winfo_children():
                if widget != toggle_btn:
                    widget.grid_remove()
        else:
            for widget in menu_frame.winfo_children():
                widget.grid()
        return
    
    step = 5 if target_width > current_width else -5
    next_width = current_width + step
    if (step > 0 and next_width > target_width) or (step < 0 and next_width < target_width):
        next_width = target_width

    menu_frame.configure(width=next_width)
    main_frame.place_configure(x=next_width + padding_between_menu,
                               width=app.winfo_width() - next_width - padding_between_menu)
    for btn in [encrypt_button, view_button, help_button, exit_button]:
        if next_width <= menu_width_collapsed + 5:
            btn.configure(text="")  # mostrar solo icono o vacío
        else:
            if btn == encrypt_button:
                btn.configure(text="Encriptar contraseña")
            elif btn == view_button:
                btn.configure(text="Ver contraseñas")
            elif btn == help_button:
                btn.configure(text="Ayuda")
            elif btn == exit_button:
                btn.configure(text="Salir")
    
    is_collapsed = next_width <= menu_width_collapsed + 5
    encrypt_button.configure(text="" if is_collapsed else "Encriptar contraseña")
    view_button.configure(text="" if is_collapsed else "Ver contraseñas")
    help_button.configure(text="" if is_collapsed else "Ayuda")
    exit_button.configure(text="" if is_collapsed else "Salir")
    app.after(10, lambda: animate_menu(next_width, target_width))

# ------------------------------
# Widgets del menú
# ------------------------------
toggle_btn = CTkButton(menu_frame, text="≡", width=30, fg_color=BUTTON_BG, text_color=BUTTON_FG, command=toggle_menu)
toggle_btn.grid(row=0, column=0, padx=10, pady=10)

menu_label = CTkLabel(menu_frame, text="EncryptU", font=("Arial", 20), text_color=TEXT_COLOR, fg_color=MENU_BG)
menu_label.grid(row=1, column=0, padx=20, pady=(20, 10))

encrypt_button = CTkButton(menu_frame, text="Encriptar contraseña", fg_color=BUTTON_BG, text_color=BUTTON_FG)
encrypt_button.grid(row=2, column=0, padx=20, pady=10)

view_button = CTkButton(menu_frame, text="Ver contraseñas", fg_color=BUTTON_BG, text_color=BUTTON_FG)
view_button.grid(row=3, column=0, padx=20, pady=10)

help_button = CTkButton(menu_frame, text="Ayuda", fg_color=BUTTON_BG, text_color=BUTTON_FG)
help_button.grid(row=4, column=0, padx=20, pady=10)

exit_button = CTkButton(menu_frame, text="Salir", fg_color=BUTTON_BG, text_color=BUTTON_FG, command=app.quit)
exit_button.grid(row=5, column=0, padx=20, pady=10)

# ------------------------------
# Widgets del área principal (card)
# ------------------------------
card_frame = CTkFrame(main_frame, fg_color=None, corner_radius=15)  # fondo transparente
card_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

bg_label = CTkLabel(card_frame, image=bg_photo, text="")
bg_label.place(relx=0.5, rely=0.5, anchor="center")

# # sombra
# shadow_label = CTkLabel(card_frame, text="Bienvenido a EncryptU",
#                         font=("Montserrat", 28, "bold"),
#                         text_color="black", fg_color=None)
# shadow_label.place(relx=0.5+0.01, rely=0.2+0.01, anchor="center")  # ligero offset

# overlay = CTkFrame(card_frame, fg_color="#00000080", corner_radius=10, width=400, height=60)
# overlay.place(relx=0.5, rely=0.2, anchor="center")
# overlay.configure(fg_color="#0000003E")  # último "80" = transparencia 50%

main_label = CTkLabel(card_frame, text="Bienvenido a EncryptU",
                       font=("Montserrat", 28, "bold"),
                       text_color="#FF2D55",  # rojo más brillante
                       fg_color=None)
main_label.place(relx=0.5, rely=0.2, anchor="center")
main_label.pack(pady=(40, 10), padx=20, fill="x")

main_text = CTkLabel(card_frame, text="Selecciona una opción del menú para comenzar.", font=("Arial", 16), text_color=TEXT_COLOR, fg_color=CARD_BG)
main_text.pack(pady=10, padx=20, fill="x")

# ------------------------------
# Ajustar main_frame al redimensionar ventana
# ------------------------------
def on_resize(event):
    main_frame.configure(width=app.winfo_width() - menu_frame.winfo_width() - padding_between_menu,
                         height=app.winfo_height())
    main_frame.place_configure(x=menu_frame.winfo_width() + padding_between_menu)

app.bind("<Configure>", on_resize)

# ------------------------------
# Ejecutar app
# ------------------------------
app.mainloop()








#Nota: para las funciones de los botones, crear nuevas ventanas o cambiar el contenido del main_frame
#para la ventana de encriptar contraseña, pedir sitio web y contraseña, y mostrar la contraseña encriptada
#para la ventana de ver contraseñas, pedir la clave maestra y mostrar una tabla con las contraseñas guardadas
#para la ventana de ayuda, mostrar un texto con instrucciones de uso
#el boton de salir cierra la app
#usar colores oscuros y fuentes modernas
#usar iconos para los botones del menu (opcional)
#usar tooltips para los botones del menu (opcional)
#usar animaciones para el menu (opcional)
#guardar las contraseñas en un archivo local (opcional)
#usar una base de datos local para guardar las contraseñas (opcional)
#usar una API para guardar las contraseñas en un servidor (opcional)
#usar autenticación para acceder a la API (opcional)
#usar variables de entorno para configurar la API (opcional)
