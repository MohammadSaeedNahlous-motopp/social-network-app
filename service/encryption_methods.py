import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import (
    load_pem_public_key,
    load_pem_private_key,
)


# For every message generate a key
def generate_aes_key() -> bytes:
    return AESGCM.generate_key(bit_length=256)


# AES-GCM uses a 12-byte nonce as the standard nonce size.
# The nonce does not need to be secret. We can store/send it alongside the encrypted message.
def encrypt_message(content: str, aes_key: bytes):
    nonce = os.urandom(12)

    aes = AESGCM(aes_key)

    ciphertext = aes.encrypt(
        nonce,
        content.encode("utf-8"),
        None,
    )

    return ciphertext, nonce


# This method takes the raw AES key and the recipient's RSA public key, then encrypts the AES key using RSA-OAEP.
def encrypt_aes_key(
    aes_key: bytes,
    recipient_public_key: str,
) -> bytes:
    # converts your public key from its stored PEM text format back into a Python public-key object
    public_key = load_pem_public_key(recipient_public_key.encode("utf-8"))

    encrypted_aes_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(
                algorithm=hashes.SHA256(),
            ),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    return encrypted_aes_key


# decrypt_private_key() does the opposite of encrypt_private_key().
# We stored the RSA private key encrypted with our server master key using Fernet,
# so now we decrypt it with the same master key.
def decrypt_private_key(encrypted_private_key: str) -> str:
    master_key = os.getenv("MASTER_KEY")

    if not master_key:
        raise RuntimeError("MASTER_KEY is not configured.")

    fernet = Fernet(master_key)

    private_key = fernet.decrypt(encrypted_private_key.encode("utf-8"))

    return private_key.decode("utf-8")


# This is the reverse of encrypt_aes_key().
# We take the encrypted AES key and use the recipient's RSA private key to recover the original AES key.
def decrypt_aes_key(
    encrypted_aes_key: bytes,
    private_key: str,
) -> bytes:
    # converts your private key from its stored PEM text format back into a Python private-key object
    private_key = load_pem_private_key(
        private_key.encode("utf-8"),
        password=None,
    )

    aes_key = private_key.decrypt(
        encrypted_aes_key,
        padding.OAEP(
            mgf=padding.MGF1(
                algorithm=hashes.SHA256(),
            ),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    return aes_key


# we use the same AES key and nonce of the message
def decrypt_message(
    ciphertext: bytes,
    aes_key: bytes,
    nonce: bytes,
) -> str:
    aes = AESGCM(aes_key)

    plaintext = aes.decrypt(
        nonce,
        ciphertext,
        None,
    )

    return plaintext.decode("utf-8")


def decrypt_chat_message(message, encrypted_private_key):
    private_key = decrypt_private_key(encrypted_private_key)

    encrypted_aes_key = base64.b64decode(message.encrypted_aes_key)

    nonce = base64.b64decode(message.nonce)

    ciphertext = base64.b64decode(message.ciphertext)

    aes_key = decrypt_aes_key(
        encrypted_aes_key,
        private_key,
    )

    return decrypt_message(
        ciphertext,
        aes_key,
        nonce,
    )
