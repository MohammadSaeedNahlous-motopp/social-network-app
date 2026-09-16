import os

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.fernet import Fernet


def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    public_key = private_key.public_key()

    return public_key, private_key


def encrypt_private_key(private_key: str) -> str:
    master_key = os.getenv("MASTER_KEY")

    fernet = Fernet(master_key)

    encrypted = fernet.encrypt(private_key.encode("utf-8"))

    return encrypted.decode("utf-8")
