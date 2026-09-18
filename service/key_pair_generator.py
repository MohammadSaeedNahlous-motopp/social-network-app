import os

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from dotenv import load_dotenv

load_dotenv()

def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    public_key = private_key.public_key()

    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    return (
        public_key_pem.decode("utf-8"),
        private_key_pem.decode("utf-8"),
    )


def encrypt_private_key(private_key: str) -> str:
    master_key = os.getenv("MASTER_KEY")

    if not master_key:
        raise RuntimeError("MASTER_KEY is not configured.")

    fernet = Fernet(master_key)

    encrypted_private_key = fernet.encrypt(private_key.encode("utf-8"))

    return encrypted_private_key.decode("utf-8")
