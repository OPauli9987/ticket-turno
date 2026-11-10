"""PATRON DE DISEÑO Singleton
Una sola conexion a la base de datos para toda la aplicacion
"""
import sqlite3
import threading
import unicodedata

from app.config import Config


def sin_acentos(texto):
    """Quita acentos y pasa a mayúsculas (para búsquedas tolerantes)."""
    if texto is None:
        return ""
    base = unicodedata.normalize("NFD", str(texto))
    return "".join(c for c in base if unicodedata.category(c) != "Mn").upper()


class Database:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._connection = None
        return cls._instance

    @classmethod
    def get_instance(cls):
        return cls()

    def connect(self, path=None):
        if self._connection is None:
            self._connection = sqlite3.connect(path or Config.DB_PATH)
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys = ON")
            self._connection.create_function("sin_acentos", 1, sin_acentos,
                                             deterministic=True)
        return self._connection

    @property
    def connection(self):
        if self._connection is None:
            raise RuntimeError("La base de datos no esta conectada.")
        return self._connection

    @property
    def conectada(self):
        return self._connection is not None

    def close(self):
        if self._connection is not None:
            self._connection.close()
            self._connection = None
