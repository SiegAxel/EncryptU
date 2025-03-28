# 📌 EncryptU 🔒
Sistema de Encriptación Automática de Contraseñas para Usuarios no Técnicos

📋 Tabla de Contenidos
🔍 Problema

💡 Solución

✨ Características Principales

🛠️ Instalación

🚀 Uso

🔐 Seguridad

🔄 Flujo de Trabajo

🧠 Tecnologías

📅 Roadmap

🤝 Contribuir

📜 Licencia

❓ Preguntas Frecuentes




[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Code Style: PEP8](https://img.shields.io/badge/code%20style-PEP8-brightgreen.svg)](https://peps.python.org/pep-0008/)

----------------------------------------------------------------------------------------------------------------------------------------------------------------------


🔍 Problema
La seguridad de contraseñas es crítica, especialmente para usuarios mayores o con dificultades técnicas. Muchos:

Reutilizan contraseñas simples (ej: "pepito123").

Almacenan contraseñas en lugares inseguros.

No gestionan claves únicas por sitio web.

----------------------------------------------------------------------------------------------------------------------------------------------------------------------

💡 Solución
EncryptU es una herramienta local que:
✅ Encripta automáticamente contraseñas comunes en claves únicas por sitio web.
✅ Guarda credenciales en una base de datos encriptada.
✅ Simplifica el registro/login con un solo clic.
✅ Funciona offline para máxima privacidad.

----------------------------------------------------------------------------------------------------------------------------------------------------------------------

✨ Características Principales
Funcionalidad	Descripción
🔄 Encriptación Simétrica	Usa AES-256 con claves derivadas de una contraseña maestra.
🌐 Claves Únicas por Sitio	Mismo password + dominio web = encriptación única.
💾 Almacenamiento Seguro	Base de datos cifrada con SQLCipher.
🖥️ Interfaz Sencilla	Diseñada para usuarios no técnicos (GUI/CLI).
🔄 Autocompletado	Integración con navegadores para login automático.

----------------------------------------------------------------------------------------------------------------------------------------------------------------------

🛠️ Instalación

# 1. Clona el repositorio
git clone https://github.com/SiegAxel/EncryptU.git
cd EncryptU

# 2. Configura el entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 3. Instala dependencias
pip install -r requirements.txt

# 4. Genera el ejecutable (opcional)
pyinstaller --onefile --windowed encryptu.py  # Para .exe


----------------------------------------------------------------------------------------------------------------------------------------------------------------------

🔐 Seguridad

Algoritmos: AES-256 + PBKDF2 (310,000 iteraciones).

Derivación de Claves:

# clave = PBKDF2(master_password, salt=sitio_web, iterations=310000)

Base de Datos: Encriptada con SQLCipher (AES-256-CBC).

----------------------------------------------------------------------------------------------------------------------------------------------------------------------

📜 Licencia
MIT License © 2023 SiegAxel.

----------------------------------------------------------------------------------------------------------------------------------------------------------------------


❓ Preguntas Frecuentes
¿Cómo recupero mis contraseñas si olvido la clave maestra?
❌ No es posible (por diseño). La clave maestra nunca se almacena.

¿Es compatible con móviles?
⚠️ Actualmente solo para desktop. Versión móvil en roadmap.

¿Cómo garantizan la seguridad?
🔒 Todo el código es auditable, y usamos estándares NIST.
