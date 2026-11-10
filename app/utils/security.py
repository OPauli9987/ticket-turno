"""Hash de contraseñas (PBKDF2-HMAC-SHA256 con sal aleatoria)."""
import hashlib
import hmac
import os


class PasswordHasher:
    ITERACIONES = 120_000

    @classmethod
    def hash(cls, password, salt_hex=None):
        salt = bytes.fromhex(salt_hex) if salt_hex else os.urandom(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"),
                                     salt, cls.ITERACIONES)
        return salt.hex(), digest.hex()

    @classmethod
    def verificar(cls, password, salt_hex, hash_hex):
        _, calculado = cls.hash(password, salt_hex)
        return hmac.compare_digest(calculado, hash_hex)
