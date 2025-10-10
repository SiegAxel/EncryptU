from __future__ import annotations
import threading
import sys
from pathlib import Path
import os
import json
import secrets
import io
import requests
import tkinter.ttk as ttk
import customtkinter as ctk
import tkinter.simpledialog as simpledialog
from tkinter import messagebox, filedialog

# --- Crypto utilities ---
ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT / 'src'))
from crypto.encryption import encriptar_bytes, desencriptar_bytes

API_URL = 'http://127.0.0.1:8000'

APP_DIR = Path(os.environ.get('APPDATA') or Path.home()) / '.encryptu'
CONFIG_PATH = APP_DIR / 'config.json'

def ensure_app_dir():
    APP_DIR.mkdir(parents=True, exist_ok=True)

def load_config():
    try:
        if CONFIG_PATH.exists():
            return json.loads(CONFIG_PATH.read_text())
    except Exception:
        return None
    return None

def save_config(data: dict):
    ensure_app_dir()
    CONFIG_PATH.write_text(json.dumps(data))

def generate_master_key() -> str:
    return secrets.token_urlsafe(32)

# ====================== Login Modal ======================
class LoginModal(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title('Iniciar sesión')
        self.geometry('380x220')
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        ctk.CTkLabel(self, text='Usuario').pack(anchor='w', padx=12, pady=(12,0))
        self.user = ctk.CTkEntry(self)
        self.user.pack(fill='x', padx=12, pady=4)

        ctk.CTkLabel(self, text='Contraseña').pack(anchor='w', padx=12)
        self.password = ctk.CTkEntry(self, show='*')
        self.password.pack(fill='x', padx=12, pady=4)

        ctk.CTkLabel(self, text='Clave maestra (opcional)').pack(anchor='w', padx=12, pady=(8,0))
        self.master = ctk.CTkEntry(self, show='*')
        self.master.pack(fill='x', padx=12, pady=4)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill='x', pady=12)
        ctk.CTkButton(btn_frame, text='Ingresar', command=self._submit).pack(side='left', expand=True, padx=4)
        ctk.CTkButton(btn_frame, text='Cancelar', command=self.destroy).pack(side='left', expand=True, padx=4)

    def _submit(self):
        username = self.user.get().strip()
        password = self.password.get().strip()
        master_val = self.master.get() # type: ignore
        master = master_val.encode() if master_val else None

        if not username or not password:
            messagebox.showwarning('Aviso', 'Usuario y contraseña requeridos')
            return

        try:
            self.parent._do_login(username, password, master)
        except Exception:
            messagebox.showerror('Error', 'Error durante login')
        finally:
            self.destroy()

# ====================== Dashboard ======================
class EncryptUDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.title('EncryptU')
        self.geometry('1100x700')
        self.minsize(900, 600)

        self.token: str | None = None
        self.master_password: bytes | None = None
        self.entries = []  # almacen de entradas para cards/table
        self.table = ttk.Treeview(self, columns=('id','fecha','web','correo','contraseña'), show='headings')
        for c in ('id','fecha','web','correo','contraseña'):
            self.table.heading(c, text=c.title())
            self.table.column(c, width=100)
        self.table.pack(fill='both', expand=True)

        self._build_ui()
        try:
            self._ensure_identity()
        except Exception:
            pass

    def _list_files(self):
        """Lista archivos del servidor y los muestra en la tabla."""
        if not self.token:
            messagebox.showwarning('No autorizado', 'Primero inicia sesión')
            return
        try:
            resp = requests.get(f"{API_URL}/files", headers={'Authorization': f'Bearer {self.token}'})
            resp.raise_for_status()
            files = resp.json()
        except Exception as exc:
            messagebox.showerror('Error', f'No se pudo listar archivos: {exc}')
            return

        # limpiar tabla
        for item in self.table.get_children():
            self.table.delete(item)

        # agregar archivos
        for f in files:
            file_id = f.get('id', '')
            fecha = f.get('created_at', '')
            filename = f.get('filename', '')
            web, correo = '', ''
            if filename.startswith("pw::"):
                parts = filename.split("::")
                if len(parts) >= 3:
                    web = parts[1]
                    correo = parts[2].replace('.bin', '')
                else:
                    web = filename
            self.table.insert('', 'end', values=(file_id, fecha, web, correo, '********'))


    def _upload_file(self):
        """Sube un archivo seleccionado al servidor."""
        if not self.token:
            messagebox.showwarning('No autorizado', 'Primero inicia sesión')
            return
        path = filedialog.askopenfilename(title='Seleccionar archivo')
        if not path:
            return

        try:
            with open(path, 'rb') as fh:
                content = fh.read()
            if self.master_password:
                enc = encriptar_bytes(content, Path(path).name, self.master_password)
                files = {'file': (Path(path).name, io.BytesIO(enc))}
            else:
                files = {'file': (Path(path).name, io.BytesIO(content))}
            resp = requests.post(f"{API_URL}/upload", headers={'Authorization': f'Bearer {self.token}'}, files=files)
            resp.raise_for_status()
        except Exception as exc:
            messagebox.showerror('Upload failed', f'Error: {exc}')
            return

        messagebox.showinfo('Upload', 'Archivo subido')
        self._list_files()


    def _download_selected(self):
        """Descarga el archivo seleccionado en la tabla."""
        if not self.token:
            messagebox.showwarning('No autorizado', 'Primero inicia sesión')
            return
        sel = self.table.selection()
        if not sel:
            messagebox.showwarning('Selecciona', 'Selecciona un archivo de la tabla')
            return

        file_id = self.table.item(sel[0])['values'][0]
        try:
            resp = requests.get(f"{API_URL}/download/{file_id}", headers={'Authorization': f'Bearer {self.token}'}, stream=True)
            resp.raise_for_status()
            data = resp.content
        except Exception as exc:
            messagebox.showerror('Download failed', f'Error: {exc}')
            return

        save_path = filedialog.asksaveasfilename(initialfile=f"file_{file_id}")
        if not save_path:
            return

        try:
            # descifrado si hay master_password
            if self.master_password:
                filename = self.table.item(sel[0])['values'][2]
                sitio_key = filename
                if filename.startswith("pw::"):
                    parts = filename.split("::")
                    if len(parts) >= 3:
                        sitio_key = f"{parts[1]}::{parts[2].rstrip('.bin')}"
                dec = desencriptar_bytes(data, sitio_key, self.master_password)
                with open(save_path, 'wb') as fh:
                    fh.write(dec)
            else:
                with open(save_path, 'wb') as fh:
                    fh.write(data)
        except Exception as exc:
            messagebox.showerror('Guardar', f'Error escribiendo archivo: {exc}')
            return

        messagebox.showinfo('Descarga', 'Archivo guardado')


    def _view_selected(self):
        """Muestra en un modal la contraseña del archivo seleccionado."""
        sel = self.table.selection()
        if not sel:
            messagebox.showwarning('Selecciona', 'Selecciona un archivo de la tabla')
            return
        item = self.table.item(sel[0])['values']
        file_id, filename, correo = item[0], item[2], item[3]

        if not self.token:
            messagebox.showwarning('No autenticado', 'Debes iniciar sesión para ver contraseñas subidas')
            return

        try:
            resp = requests.get(f"{API_URL}/download/{file_id}", headers={'Authorization': f'Bearer {self.token}'})
            resp.raise_for_status()
            data = resp.content
            sitio_key = filename
            if filename.startswith("pw::"):
                parts = filename.split("::")
                if len(parts) >= 3:
                    sitio_key = f"{parts[1]}::{parts[2].rstrip('.bin')}"
            if self.master_password is None:
                messagebox.showwarning("Error", "No hay clave maestra disponible para descifrar")
                return
            plain = desencriptar_bytes(data, sitio_key, self.master_password).decode()
        except Exception:
            plain = '<Error descifrando>'

        dlg = ctk.CTkToplevel(self)
        dlg.title('Ver contraseña')
        dlg.geometry('420x200')
        ctk.CTkLabel(dlg, text=f'Sitio: {filename}').pack(anchor='w', padx=12, pady=6)
        ctk.CTkLabel(dlg, text=f'Usuario: {correo}').pack(anchor='w', padx=12, pady=6)
        ctk.CTkLabel(dlg, text='Contraseña:').pack(anchor='w', padx=12, pady=(8, 0))
        pw_entry = ctk.CTkEntry(dlg)
        pw_entry.pack(fill='x', padx=12, pady=4)
        pw_entry.insert(0, plain)
        pw_entry.configure(state='readonly')


    def _delete_selected(self):
        """Elimina el archivo seleccionado."""
        sel = self.table.selection()
        if not sel:
            messagebox.showwarning('Selecciona', 'Selecciona un archivo de la tabla')
            return
        file_id = self.table.item(sel[0])['values'][0]

        if messagebox.askyesno('Confirmar', '¿Eliminar este registro?'):
            if self.token:
                try:
                    resp = requests.delete(f"{API_URL}/files/{file_id}", headers={'Authorization': f'Bearer {self.token}'})
                    if resp.status_code not in (200, 204):
                        messagebox.showwarning('Eliminar', f'No se pudo eliminar en servidor: {resp.text}')
                except Exception as exc:
                    messagebox.showerror('Eliminar', f'Error al eliminar: {exc}')
            self.table.delete(sel[0])


    # ------------------ UI BUILD ------------------
    def _build_ui(self):
        # Header Hero
        header = ctk.CTkFrame(self, height=220, fg_color="#1f6aa5")
        header.pack(fill='x')
        hero_frame = ctk.CTkFrame(header, fg_color="transparent")
        hero_frame.place(relx=0.5, rely=0.35, anchor='center')
        ctk.CTkLabel(hero_frame, text='BIENVENIDO', font=ctk.CTkFont(size=40, weight='bold')).pack()
        ctk.CTkLabel(hero_frame, text='A ENCRYPTU', font=ctk.CTkFont(size=40, weight='bold')).pack()

        # Main content
        content = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        content.pack(fill='both', expand=True, pady=(10,0))

        left = ctk.CTkFrame(content)
        left.pack(side='left', fill='both', expand=True, padx=10)

        right = ctk.CTkFrame(content, width=360)
        right.pack(side='right', fill='y', padx=10)

        # Cards Scroll
        cards_frame = ctk.CTkScrollableFrame(left, width=600, height=300)
        cards_frame.pack(fill='both', expand=True, pady=(10,0))
        self.cards_inner = cards_frame

        # Right panel: profile + add password
        profile = ctk.CTkFrame(right, fg_color="#2b2b2b", corner_radius=8)
        profile.pack(fill='x', pady=8, padx=8)
        ctk.CTkLabel(profile, text='John Doe', font=ctk.CTkFont(size=14, weight='bold')).pack()
        ctk.CTkLabel(profile, text='TheFather32@gmail.com').pack()

        add_card = ctk.CTkFrame(right, fg_color="#2b2b2b", corner_radius=8)
        add_card.pack(fill='x', pady=8, padx=8)
        ctk.CTkLabel(add_card, text='Nueva Contraseña', font=ctk.CTkFont(size=12, weight='bold')).pack(anchor='w', pady=(4,2))

        self.entry_date = ctk.CTkEntry(add_card, placeholder_text='Fecha')
        self.entry_date.pack(fill='x', pady=4)
        self.entry_web = ctk.CTkEntry(add_card, placeholder_text='Web')
        self.entry_web.pack(fill='x', pady=4)
        self.entry_email = ctk.CTkEntry(add_card, placeholder_text='Correo')
        self.entry_email.pack(fill='x', pady=4)
        self.entry_pass = ctk.CTkEntry(add_card, placeholder_text='Contraseña')
        self.entry_pass.pack(fill='x', pady=4)
        ctk.CTkButton(add_card, text='Añadir Contraseña', command=self._on_add).pack(fill='x', pady=6)

        # Floating Add Button
        fab = ctk.CTkButton(self, text='+', width=50, height=50, corner_radius=25, command=self._focus_add)
        fab.place(relx=0.92, rely=0.78)

        # Toolbar
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.place(relx=0.01, rely=0.3)
        self.login_btn = ctk.CTkButton(toolbar, text='Login', command=lambda: LoginModal(self))
        self.login_btn.pack(side='left', padx=4)
        self.list_btn = ctk.CTkButton(toolbar, text='Listar', command=self._list_files)
        self.list_btn.pack(side='left', padx=4)
        self.upload_btn = ctk.CTkButton(toolbar, text='Subir', command=self._upload_file)
        self.upload_btn.pack(side='left', padx=4)
        self.download_btn = ctk.CTkButton(toolbar, text='Descargar', command=self._download_selected)
        self.download_btn.pack(side='left', padx=4)
        self.view_btn = ctk.CTkButton(toolbar, text='Ver', command=self._view_selected)
        self.view_btn.pack(side='left', padx=4)
        self.delete_btn = ctk.CTkButton(toolbar, text='Eliminar', command=self._delete_selected)
        self.delete_btn.pack(side='left', padx=4)
        self.ticket_btn = ctk.CTkButton(toolbar, text='Soporte', command=self._open_ticket_dialog)
        self.ticket_btn.pack(side='left', padx=8)

        # Populate sample cards
        sample = [
            ('Instagram', 'TheFather32@gmail.com'),
            ('Gmail', 'TheFather32@gmail.com'),
            ('Figma', 'TheFather32@gmail.com'),
            ('Twitter', 'TheFather32@gmail.com'),
        ]
        for i, (site, email) in enumerate(sample):
            self._add_card(site, email, row=i//2, col=i%2)

    # ------------------ Cards ------------------
    def _add_card(self, site: str, email: str, row: int = 0, col: int = 0):
        f = ctk.CTkFrame(self.cards_inner, corner_radius=8, fg_color="#3a3a3a")
        f.grid(row=row, column=col, padx=8, pady=8, sticky='nsew')
        ctk.CTkLabel(f, text=site, font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w')
        ctk.CTkLabel(f, text=email).pack(anchor='w')

    def _focus_add(self):
        self.entry_web.focus_set()

    # ------------------ Add password ------------------
    def _on_add(self):
        web = self.entry_web.get()
        correo = self.entry_email.get()
        contr = self.entry_pass.get()

        if not web or not correo:
            messagebox.showwarning('Aviso', 'Web y correo son requeridos')
            return

        sitio_key = f"{web}::{correo}"
        try:
            payload_bytes = contr.encode()
            if self.master_password:
                payload_bytes = encriptar_bytes(contr.encode(), sitio_key, self.master_password)
            filename = f"pw::{web}::{correo}.bin"
            files = {'file': (filename, io.BytesIO(payload_bytes))}

            if not self.token:
                messagebox.showwarning('No autenticado', 'Se añadirá localmente pero debes iniciar sesión para subir')
                self.entries.append({'web': web, 'correo': correo, 'contr': contr})
                self._add_card(web, correo)
                return

            resp = requests.post(f"{API_URL}/upload", headers=self._headers(), files=files)
            resp.raise_for_status()
        except Exception as exc:
            messagebox.showerror('Error', f'No se pudo subir la contraseña: {exc}')
            return

        self.entries.append({'web': web, 'correo': correo, 'contr': contr})
        self._add_card(web, correo)
        messagebox.showinfo('Añadido', 'Contraseña añadida exitosamente')

    # ------------------ Helper ------------------
    def _headers(self):
        if not self.token:
            return {}
        return {'Authorization': f'Bearer {self.token}'}

    # =================== LOGIN & CONFIG ===================
    def _do_login(self, username: str, password: str, master: bytes | None, show_master_key: bool = False):
        try:
            resp = requests.post(f"{API_URL}/login", data={'username': username, 'password': password})
            resp.raise_for_status()
        except Exception as exc:
            messagebox.showerror('Login failed', f'Error contacting server: {exc}')
            return
        data = resp.json()
        token = data.get('access_token')
        if not token:
            messagebox.showerror('Login failed', 'No token received')
            return
        self.token = token
        self.master_password = master

        try:
            cfg = load_config() or {}
            cfg.setdefault('email', username)
            if master and not cfg.get('master_key'):
                cfg['master_key'] = master.decode() if isinstance(master, (bytes, bytearray)) else str(master)
            save_config(cfg)
        except Exception:
            pass

        messagebox.showinfo('Login', 'Ingreso exitoso')

        if show_master_key:
            self._show_master_key_window(master.decode() if isinstance(master, (bytes, bytearray)) else str(master))

    def _show_master_key_window(self, master_key: str):
        dlg = ctk.CTkToplevel(self)
        dlg.title('Clave Maestra')
        dlg.geometry('420x200')
        ctk.CTkLabel(dlg, text="Tu clave maestra es:", anchor='w').pack(fill='x', padx=12, pady=6)
        master_key_entry = ctk.CTkEntry(dlg, show='*', state='readonly')
        master_key_entry.pack(padx=12, pady=6)
        master_key_entry.insert(0, master_key)

        def _copy_master_key():
            self.clipboard_clear()
            self.clipboard_append(master_key)
            messagebox.showinfo('Copiado', 'Clave maestra copiada al portapapeles')

        ctk.CTkButton(dlg, text='Copiar Clave Maestra', command=_copy_master_key).pack(pady=10)
        ctk.CTkButton(dlg, text='Cerrar', command=dlg.destroy).pack()

    # ------------------ Ensure identity ------------------
    def _ensure_identity(self):
        cfg = load_config()
        if cfg and cfg.get('email') and cfg.get('master_key'):
            email = cfg['email']
            mkey = cfg['master_key']
            self._do_login(email, mkey, mkey.encode(), show_master_key=True)
            return

        res = messagebox.askyesno('Configurar', '¿Deseas crear una nueva cuenta y generar una master key? (Yes = crear, No = iniciar sesión existente)')
        if res:
            email = simpledialog.askstring('Registro', 'Introduce tu correo:')
            if not email:
                return
            mkey = generate_master_key()
            try:
                if not email or not mkey:
                    messagebox.showwarning('Campos vacíos', 'Usuario y contraseña son requeridos')
                    return
                r = requests.post(f"{API_URL}/register", data={'username': email, 'password': mkey})
                if r.status_code == 201:
                    save_config({'email': email, 'master_key': mkey})
                    messagebox.showinfo('Registro', f'Registro completado. Guarda tu master key: {mkey}')
                    self._do_login(email, mkey, mkey.encode())
                    return
                else:
                    messagebox.showwarning('Registro', f'No se pudo crear la cuenta: {r.text}')
            except Exception as exc:
                messagebox.showerror('Error', f'Error registrando: {exc}')
        else:
            LoginModal(self)

    # ------------------ Cards / Tickets ------------------
    def _open_ticket_dialog(self):
        if not self.token:
            messagebox.showwarning('No autorizado', 'Primero inicia sesión')
            return
        subject = simpledialog.askstring('Soporte', 'Asunto:')
        if not subject:
            return
        body = simpledialog.askstring('Soporte', 'Describe tu problema:')
        if body is None:
            return
        self._send_ticket(subject, body)

    def _send_ticket(self, subject: str, body: str):
        try:
            cfg = load_config() or {}
            payload = {'email': cfg.get('email', ''), 'subject': subject, 'body': body}
            resp = requests.post(f"{API_URL}/tickets", json=payload, headers=self._headers())
            resp.raise_for_status()
        except Exception as exc:
            messagebox.showerror('Soporte', f'Error enviando ticket: {exc}')
            return
        messagebox.showinfo('Soporte', 'Ticket enviado')

# ====================== Run App ======================
def run_app():
    app = EncryptUDashboard()
    app.mainloop()

if __name__ == '__main__':
    run_app()
