from cryptography.fernet import Fernet

master_key = Fernet.generate_key()

print(master_key.decode())
