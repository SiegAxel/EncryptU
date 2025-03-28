# 📚 Documentación Técnica de EncryptU

## 🔧 Arquitectura del Sistema
```plaintext
EncryptU sigue un modelo MVC (Modelo-Vista-Controlador):
- **Modelo**: `crypto_manager.py` (lógica de encriptación) + `database.py` (SQLCipher).
- **Vista**: Interfaz Tkinter (`gui/`) o CLI (`cli/`).
- **Controlador**: `main.py` (orquestación).