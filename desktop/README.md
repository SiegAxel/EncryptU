# EncryptU Desktop

Cliente de escritorio mínimo para probar la API de EncryptU.

Requisitos:
- Python 3.10+
- Instalar dependencias desde `requirements.txt` del proyecto.

Instalación (PowerShell):

```powershell
python -m venv .venv; ; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

Ejecutar API (desde la raíz del repo):

```powershell
# En una terminal
uvicorn api.app:app --reload
```

Ejecutar cliente de escritorio (en otra terminal ya activada):

```powershell
python desktop\client.py
```

Notas:
- Actualmente el cliente usa autenticación simple (username+password) y endpoints básicos.
- El servidor incluido es un scaffold; para producción se debe mejorar la seguridad (secrets, OAuth2, HTTPS, validación de tokens).
