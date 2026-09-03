from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


class Hash:
    @staticmethod
    def hash(password: str) -> str:
        return password_hash.hash(password)

    @staticmethod
    def verify(hashed_password: str, plain_password: str) -> bool:
        return password_hash.verify(plain_password, hashed_password)