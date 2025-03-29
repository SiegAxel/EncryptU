from src.crypto.encryption import encriptar_contraseña

# Pedir datos al usuario
sitio = input("Ingresa el sitio web (ej: facebook.com): ").strip().lower()
password = input("Ingresa tu contraseña común: ").strip()

# Encriptar
try:
    encrypted = encriptar_contraseña(password, sitio)
    print(f"\nContraseña encriptada para {sitio}:")
    print(encrypted.decode())
except Exception as e:
    print(f"Error: {str(e)}")