"""EncryptU desktop app (ttkbootstrap + tray)"""

from __future__ import annotations
import threading
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as tb
from ttkbootstrap.constants import LEFT, RIGHT, BOTH, X, Y
import tkinter.simpledialog as simpledialog
import os
import json
import secrets

try:
    import pystray
    from PIL import Image, ImageDraw
except ImportError:
    pystray = None
    Image = None
    ImageDraw = None
    print("Advertencia: pystray o PIL no disponibles, tray deshabilitado")

import requests
import io
ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT / 'src'))
from crypto.encryption import encriptar_bytes, desencriptar_bytes

API_URL = 'http://127.0.0.1:8000'

# Local config: store master key and associated email in user home
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
    # generate a URL-safe 32-byte-like secret
    return secrets.token_urlsafe(32)


class LoginModal(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title('Iniciar sesión')
        self.resizable(False, False)
        self.geometry('380x220')
        self.transient(parent)
        self.grab_set()

        frm = ttk.Frame(self, padding=12)
        frm.pack(fill='both', expand=True)

        ttk.Label(frm, text='Usuario').pack(anchor='w')
        self.user = ttk.Entry(frm)
        self.user.pack(fill='x', pady=4)

        ttk.Label(frm, text='Contraseña').pack(anchor='w')
        self.password = ttk.Entry(frm, show='*')
        self.password.pack(fill='x', pady=4)

        ttk.Label(frm, text='Clave maestra (opcional)').pack(anchor='w', pady=(8, 0))
        self.master = ttk.Entry(frm, show='*')
        self.master.pack(fill='x', pady=4)

        btns = ttk.Frame(frm)
        btns.pack(fill='x', pady=(8, 0))
        tb.Button(btns, text='Ingresar', command=self._submit).pack(side='left', expand=True, fill='x', padx=4)
        tb.Button(btns, text='Cancelar', command=self.destroy).pack(side='left', expand=True, fill='x', padx=4)

    def _submit(self):
        username = getattr(self.user, 'get')().strip()
        password = getattr(self.password, 'get')().strip()
        master_val = getattr(self.master, 'get')()
        master = master_val.encode() if master_val else None
        if not username or not password:
            messagebox.showwarning('Aviso', 'Usuario y contraseña requeridos')
            return
        # call dashboard login
        try:
            self.parent._do_login(username, password, master)
        except Exception:
            # ensure dialog doesn't crash the app
            messagebox.showerror('Error', 'Error during login')
        finally:
            self.destroy()


class EncryptUDashboard(tb.Window):
    def __init__(self):
        super().__init__(themename='flatly')
        self.title('EncryptU')
        self.geometry('1100x700')
        self.minsize(900, 600)
        self.token: str | None = None
        self.master_password: bytes | None = None
        self._build_ui()
        # Ensure identity/config: may auto-register or auto-login
        try:
            self._ensure_identity()
        except Exception:
            # non-fatal; user can still login manually
            pass

    def _build_ui(self):
        # Hero header
        header = ttk.Frame(self, height=220, style='primary.TFrame')
        header.pack(fill='x')
        hero = ttk.Frame(header)
        hero.place(relx=0.5, rely=0.35, anchor='center')
        ttk.Label(hero, text='BIENVENIDO', font=('Segoe UI', 40, 'bold')).pack()
        ttk.Label(hero, text='A ENCRYPTU', font=('Segoe UI', 40, 'bold')).pack()

        # Main content
        content = ttk.Frame(self, padding=20)
        content.pack(fill='both', expand=True)

        left = ttk.Frame(content)
        left.pack(side='left', fill='both', expand=True)
        right = ttk.Frame(content, width=360)
        right.pack(side='right', fill='y')

        # Cards container
        cards_frame = ttk.Frame(left)
        cards_frame.pack(fill='both', expand=True, pady=(10, 0))
        self.cards_canvas = tk.Canvas(cards_frame, borderwidth=0)
        self.cards_scroll = ttk.Scrollbar(cards_frame, orient='vertical', command=self.cards_canvas.yview)
        self.cards_inner = ttk.Frame(self.cards_canvas)
        self.cards_inner.bind('<Configure>', lambda e: self.cards_canvas.configure(scrollregion=self.cards_canvas.bbox('all')))
        self.cards_canvas.create_window((0, 0), window=self.cards_inner, anchor='nw')
        self.cards_canvas.configure(yscrollcommand=self.cards_scroll.set)
        self.cards_canvas.pack(side='left', fill='both', expand=True)
        self.cards_scroll.pack(side='right', fill='y')

        # Right panel: profile + add password
        profile = ttk.Frame(right, padding=12)
        profile.pack(fill='x')
        ttk.Label(profile, text='John Doe', font=('Segoe UI', 14, 'bold')).pack()
        ttk.Label(profile, text='TheFather32@gmail.com').pack()
        ttk.Separator(right).pack(fill='x', pady=8)

        add_card = ttk.LabelFrame(right, text='Nueva Contraseña', padding=12)
        add_card.pack(fill='x', pady=8)

        self.entry_date = ttk.Entry(add_card)
        self.entry_date.insert(0, 'Fecha')
        self.entry_date.pack(fill='x', pady=4)

        self.entry_web = ttk.Entry(add_card)
        self.entry_web.insert(0, 'Web')
        self.entry_web.pack(fill='x', pady=4)

        self.entry_email = ttk.Entry(add_card)
        self.entry_email.insert(0, 'Correo')
        self.entry_email.pack(fill='x', pady=4)

        self.entry_pass = ttk.Entry(add_card)
        self.entry_pass.insert(0, 'Contraseña')
        self.entry_pass.pack(fill='x', pady=4)

        ttk.Button(add_card, text='Añadir Contraseña', command=self._on_add).pack(fill='x', pady=6)

        # Floating add button
        fab = ttk.Button(self, text='+', width=3, command=self._focus_add)
        fab.place(relx=0.92, rely=0.78)

        # Toolbar (login / list / upload / download)
        toolbar = ttk.Frame(self)
        toolbar.place(relx=0.01, rely=0.3)
        self.login_btn = tb.Button(toolbar, text='Login', command=lambda: LoginModal(self))
        self.login_btn.pack(side='left', padx=4)
        self.list_btn = tb.Button(toolbar, text='Listar', command=self._list_files)
        self.list_btn.pack(side='left', padx=4)
        self.upload_btn = tb.Button(toolbar, text='Subir', command=self._upload_file)
        self.upload_btn.pack(side='left', padx=4)
        self.download_btn = tb.Button(toolbar, text='Descargar', command=self._download_selected)
        self.download_btn.pack(side='left', padx=4)
        self.view_btn = tb.Button(toolbar, text='Ver', command=self._view_selected)
        self.view_btn.pack(side='left', padx=4)
        self.delete_btn = tb.Button(toolbar, text='Eliminar', command=self._delete_selected)
        self.delete_btn.pack(side='left', padx=4)
        self.ticket_btn = tb.Button(toolbar, text='Soporte', command=self._open_ticket_dialog)
        self.ticket_btn.pack(side='left', padx=8)

        # Table at bottom
        table_frame = ttk.Frame(left)
        table_frame.pack(fill='both', expand=True, pady=(8, 0))
        self.table = ttk.Treeview(table_frame, columns=('id', 'fecha', 'web', 'correo', 'contraseña'), show='headings')
        for c in ('id', 'fecha', 'web', 'correo', 'contraseña'):
            self.table.heading(c, text=c.title())
            self.table.column(c, width=100)
        self.table.pack(fill='both', expand=True)

        self._populate_sample()

    def _populate_sample(self):
        sample = [
            ('Instagram', 'TheFather32@gmail.com'),
            ('Gmail', 'TheFather32@gmail.com'),
            ('Figma', 'TheFather32@gmail.com'),
            ('Twitter', 'TheFather32@gmail.com'),
        ]
        for i, (site, email) in enumerate(sample, start=1):
            f = ttk.Frame(self.cards_inner, relief='raised', padding=10)
            f.grid(row=(i-1)//2, column=(i-1)%2, padx=8, pady=8, sticky='nsew')
            ttk.Label(f, text=site, font=('Segoe UI', 12, 'bold')).pack(anchor='w')
            ttk.Label(f, text=email).pack(anchor='w')

        # populate table with sample rows
        for i in range(1, 10):
            self.table.insert('', 'end', values=(i, '01/05/2023', 'URL', 'marifm1986@gmail.com', '********'))

    def _focus_add(self):
        self.entry_web.focus_set()

    def _add_card(self, site: str, email: str, row: int = 0, col: int = 0):
        """Add a small card widget to the cards_inner area."""
        f = ttk.Frame(self.cards_inner, relief='raised', padding=10)
        f.grid(row=row, column=col, padx=8, pady=8, sticky='n')

        ttk.Label(f, text=site, font=('Segoe UI', 12, 'bold')).pack(anchor='w')
        ttk.Label(f, text=email).pack(anchor='w')

    def _on_add(self):
        web = self.entry_web.get()
        correo = self.entry_email.get()
        contr = self.entry_pass.get()
        if not web or not correo:
            messagebox.showwarning('Aviso', 'Web y correo son requeridos')
            return
        # client-side encryption and upload
        sitio_key = f"{web}::{correo}"
        try:
            payload_bytes = contr.encode()
            if self.master_password:
                payload_bytes = encriptar_bytes(contr.encode(), sitio_key, self.master_password)

            filename = f"pw::{web}::{correo}.bin"
            files = {'file': (filename, io.BytesIO(payload_bytes))}
            if not self.token:
                # still add locally but warn
                messagebox.showwarning('No autenticado', 'Se añadirá localmente pero debes iniciar sesión para subir')
                next_id = len(self.table.get_children()) + 1
                self.table.insert('', 'end', values=(next_id, 'Hoy', web, correo, '********'))
                self._add_card(web, correo)
                return
            resp = requests.post(f"{API_URL}/upload", headers=self._headers(), files=files)
            resp.raise_for_status()
        except Exception as exc:
            messagebox.showerror('Error', f'No se pudo subir la contraseña: {exc}')
            return

        # On success, add to UI
        next_id = len(self.table.get_children()) + 1
        self.table.insert('', 'end', values=(next_id, 'Hoy', web, correo, '********'))
        self._add_card(web, correo)

    def _show_master_key_window(self, master_key: str):
            """Muestra la ventana con la master key y permite copiarla."""
            dlg = tk.Toplevel(self)
            dlg.title('Clave Maestra')
            dlg.geometry('420x200')

            # Etiquetas y campo para mostrar la master key
            ttk.Label(dlg, text="Tu clave maestra es:", anchor='w', padding=12).pack(fill='x')
            
            master_key_entry = ttk.Entry(dlg, show='*', state='readonly', width=40)
            master_key_entry.pack(padx=12, pady=6)
            master_key_entry.insert(0, master_key)  # Insertar la master key en el campo

            def _copy_master_key():
                """Función para copiar la master key al portapapeles."""
                self.clipboard_clear()
                self.clipboard_append(master_key)
                messagebox.showinfo('Copiado', 'Clave maestra copiada al portapapeles')

            # Botón para copiar al portapapeles
            copy_button = ttk.Button(dlg, text='Copiar Clave Maestra', command=_copy_master_key)
            copy_button.pack(pady=10)

            # Cerrar el cuadro de diálogo cuando se haga clic en el botón de "Cerrar"
            close_button = ttk.Button(dlg, text='Cerrar', command=dlg.destroy)
            close_button.pack()

    # ------------------ API integration ------------------
    def _do_login(self, username: str, password: str, master: bytes | None, show_master_key: bool = False):
        """Perform login against API and store token and master password in memory."""
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
        # Persist config: save email and master key locally
        try:
            cfg = load_config() or {}
            cfg.setdefault('email', username)
            if master and not cfg.get('master_key'):
                # store master_key as string
                cfg['master_key'] = master.decode() if isinstance(master, (bytes, bytearray)) else str(master)
            save_config(cfg)
        except Exception:
            pass
        messagebox.showinfo('Login', 'Ingreso exitoso')
        
        # Nueva ventana para mostrar la master key con la opción de copiar
        if show_master_key:
            self._show_master_key_window(master.decode() if isinstance(master, (bytes, bytearray)) else str(master))

        # Refresh file list
        self._list_files()
        # disable login button to prevent logout
        try:
            self.login_btn.configure(state='disabled')
        except Exception:
            pass

    def _headers(self):
        if not self.token:
            return {}
        return {'Authorization': f'Bearer {self.token}'}

    def _list_files(self):
        if not self.token:
            messagebox.showwarning('No autorizado', 'Primero inicia sesión')
            return
        try:
            resp = requests.get(f"{API_URL}/files", headers=self._headers())
            resp.raise_for_status()
        except Exception as exc:
            messagebox.showerror('Error', f'No se pudo listar archivos: {exc}')
            return
        files = resp.json()
        # Clear table
        for item in self.table.get_children():
            self.table.delete(item)
        for f in files:
            file_id = f['id']
            fecha = f['created_at']
            filename = f['filename']
            
            web = ''
            correo = ''
            if filename.startswith("pw::"):
                parts = filename.split("::")
                if len(parts) >= 3:
                    web = parts[1]
                    correo = parts[2].replace('.bin', '')
                else:
                    web = filename  # fallback si no tiene formato esperado

            self.table.insert('', 'end', values=(file_id, fecha, web, correo, '********'))

    def _upload_file(self):
        if not self.token:
            messagebox.showwarning('No autorizado', 'Primero inicia sesión')
            return
        path = filedialog.askopenfilename(title='Seleccionar archivo')
        if not path:
            return
        try:
            with open(path, 'rb') as fh:
                content = fh.read()
            # If master password exists, encrypt bytes before upload
            if self.master_password:
                enc = encriptar_bytes(content, Path(path).name, self.master_password)
                files = {'file': (Path(path).name, io.BytesIO(enc))}
            else:
                files = {'file': (Path(path).name, io.BytesIO(content))}
            resp = requests.post(f"{API_URL}/upload", headers=self._headers(), files=files)
            resp.raise_for_status()
        except Exception as exc:
            messagebox.showerror('Upload failed', f'Error: {exc}')
            return
        messagebox.showinfo('Upload', 'Archivo subido')
        self._list_files()

    def _download_selected(self):
        if not self.token:
            messagebox.showwarning('No autorizado', 'Primero inicia sesión')
            return
        sel = self.table.selection()
        if not sel:
            messagebox.showwarning('Selecciona', 'Selecciona un archivo de la tabla')
            return
        file_id = self.table.item(sel[0])['values'][0]
        try:
            resp = requests.get(f"{API_URL}/download/{file_id}", headers=self._headers(), stream=True)
            resp.raise_for_status()
            data = resp.content
            cd = resp.headers.get('Content-Disposition', '')
            # try to extract filename from header: attachment; filename="name"
            filename = ''
            if 'filename=' in cd:
                try:
                    filename = cd.split('filename=')[-1].strip().strip('"')
                except Exception:
                    filename = ''
            if not filename:
                # fallback to table stored filename
                filename = self.table.item(sel[0])['values'][2]
        except Exception as exc:
            messagebox.showerror('Download failed', f'Error: {exc}')
            return
        # If master_password present, try to decrypt
        save_path = filedialog.asksaveasfilename(initialfile=f"file_{file_id}")
        if not save_path:
            return
        try:
            if self.master_password:
                # if filename matches our pw::web::correo.bin pattern, derive sitio_key
                sitio_key = None
                if isinstance(filename, str) and filename.startswith('pw::'):
                    parts = filename.split('::')
                    if len(parts) >= 3:
                        web = parts[1]
                        correo = parts[2]
                        # strip possible .bin suffix
                        if correo.endswith('.bin'):
                            correo = correo[:-4]
                        sitio_key = f"{web}::{correo}"
                if sitio_key is None:
                    sitio_key = filename or str(file_id)
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

    # ------------------ View / manage entries UI ------------------
    def _view_selected(self):
        sel = self.table.selection()
        if not sel:
            messagebox.showwarning('Selecciona', 'Selecciona un archivo de la tabla')
            return
        item = self.table.item(sel[0])['values']
        file_id = item[0]
        # Determine where the actual data is: if row came from server filename is in column 2
        filename_or_site = item[2]
        correo = item[3] if len(item) > 3 else ''

        # If we have a token, fetch the data from server and attempt decrypt
        if self.token:
            try:
                resp = requests.get(f"{API_URL}/download/{file_id}", headers=self._headers(), stream=True)
                resp.raise_for_status()
                data = resp.content
                cd = resp.headers.get('Content-Disposition', '')
                filename = ''
                if 'filename=' in cd:
                    try:
                        filename = cd.split('filename=')[-1].strip().strip('"')
                    except Exception:
                        filename = ''
                if not filename:
                    filename = filename_or_site
                # derive sitio_key
                sitio_key = None
                if isinstance(filename, str) and filename.startswith('pw::'):
                    parts = filename.split('::')
                    if len(parts) >= 3:
                        web = parts[1]
                        correo = parts[2].rstrip('.bin')
                        sitio_key = f"{web}::{correo}"
                if sitio_key is None:
                    sitio_key = filename or str(file_id)

                if self.master_password:
                    try:
                        plain = desencriptar_bytes(data, sitio_key, self.master_password).decode()
                    except Exception:
                        plain = '<Error descifrando con la master key>'
                else:
                    plain = '<No hay master key en memoria>'

                # show modal with decrypted password
                dlg = tk.Toplevel(self)
                dlg.title('Ver contraseña')
                dlg.geometry('420x200')
                ttk.Label(dlg, text=f'Sitio: {filename_or_site}').pack(anchor='w', padx=12, pady=6)
                ttk.Label(dlg, text=f'Usuario: {correo}').pack(anchor='w', padx=12, pady=6)
                ttk.Label(dlg, text='Contraseña:').pack(anchor='w', padx=12, pady=(8, 0))
                pw_entry = ttk.Entry(dlg)
                pw_entry.pack(fill='x', padx=12, pady=4)
                pw_entry.insert(0, plain)
                pw_entry.configure(state='readonly')
                def _copy():
                    self.clipboard_clear()
                    self.clipboard_append(plain)
                    messagebox.showinfo('Copiado', 'Contraseña copiada al portapapeles')
                tb.Button(dlg, text='Copiar', command=_copy).pack(padx=12, pady=8)
            except Exception as exc:
                messagebox.showerror('Error', f'No se pudo obtener el archivo: {exc}')
        else:
            messagebox.showwarning('No autenticado', 'Debes iniciar sesión para ver contraseñas subidas')

    def _delete_selected(self):
        sel = self.table.selection()
        if not sel:
            messagebox.showwarning('Selecciona', 'Selecciona un archivo de la tabla')
            return
        item = self.table.item(sel[0])['values']
        file_id = item[0]
        if messagebox.askyesno('Confirmar', '¿Eliminar este registro?'):
            # attempt server delete if logged in
            if self.token:
                try:
                    resp = requests.delete(f"{API_URL}/files/{file_id}", headers=self._headers())
                    if resp.status_code not in (200, 204):
                        messagebox.showwarning('Eliminar', f'No se pudo eliminar en servidor: {resp.text}')
                except Exception as exc:
                    messagebox.showerror('Eliminar', f'Error al eliminar: {exc}')
            # remove from table
            self.table.delete(sel[0])

    # ------------------ Install / identity helpers ------------------
    def _ensure_identity(self):
        """On first run, create master_key and register; otherwise try auto-login using stored config."""
        cfg = load_config()
        if cfg and cfg.get('email') and cfg.get('master_key'):
            email = cfg['email']
            mkey = cfg['master_key']
            # attempt auto-login
            self._do_login(email, mkey, mkey.encode(), show_master_key=True)
            return

        # No config: prompt to create a new account or login to existing
        res = messagebox.askyesno('Configurar', '¿Deseas crear una nueva cuenta y generar una master key? (Yes = crear, No = iniciar sesión existente)')
        if res:
            email = simpledialog.askstring('Registro', 'Introduce tu correo:')
            if not email:
                return
            # generate master key
            mkey = generate_master_key()
            # send register request
            try:
                # Asegúrate de que los campos username y password no estén vacíos
                if not email or not mkey:
                    messagebox.showwarning('Campos vacíos', 'Usuario y contraseña son requeridos')
                    return
                
                r = requests.post(f"{API_URL}/register", data={'username': email, 'password': mkey})
                if r.status_code == 201:
                    # save config and show master key to user
                    save_config({'email': email, 'master_key': mkey})
                    messagebox.showinfo('Registro', f'Registro completado. Guarda tu master key: {mkey}')
                    self._do_login(email, mkey, mkey.encode())
                    return
                else:
                    # if user exists, ask to login
                    messagebox.showwarning('Registro', f'No se pudo crear la cuenta: {r.text}')
            except Exception as exc:
                messagebox.showerror('Error', f'Error registrando: {exc}')
                return
        else:
            # user chose to login to existing account
            LoginModal(self)

    # ------------------ Tickets / soporte ------------------
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


def _start_tray(window: EncryptUDashboard):
    if not pystray or Image is None:
        return
    img = Image.new('RGB', (64, 64), color=(200, 30, 30))
    if ImageDraw is not None:
        d = ImageDraw.Draw(img)
        d.ellipse((8, 8, 56, 56), fill=(255, 255, 255))

    def on_open(icon, item):
        try:
            window.after(0, lambda: window.deiconify())
        except Exception:
            pass

    def on_quit(icon, item):
        icon.stop()
        try:
            window.after(0, lambda: window.destroy())
        except Exception:
            pass

    menu = pystray.Menu(pystray.MenuItem('Abrir', on_open), pystray.MenuItem('Salir', on_quit))
    icon = pystray.Icon('encryptu', img, 'EncryptU', menu=menu)
    icon.run()


def run_app():
    app = EncryptUDashboard()
    if pystray and Image is not None:
        threading.Thread(target=_start_tray, args=(app,), daemon=True).start()
    app.mainloop()


if __name__ == '__main__':
    run_app()
