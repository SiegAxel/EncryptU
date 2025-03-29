from crypto.encryption import encriptar_contraseña

def main():
    print("=== EncryptU ===")
    password = input("Introduce tu contraseña: ")
    domain = input("Introduce el dominio (ej. youtube.com): ")

    encrypted = encriptar_contraseña(password, domain)
    print("\nContraseña encriptada:")
    print(encrypted)

if __name__ == "__main__":
    main()