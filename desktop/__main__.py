import customtkinter as ctk
from .controllers.app_controller import AppController

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("EncryptU Desktop")
        self.geometry("800x600")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.controller = AppController(self)
        self.controller.start_app() # <--- Cambio Clave

    def on_closing(self):
        self.controller.on_closing()

if __name__ == "__main__":
    app = App()
    app.mainloop()
