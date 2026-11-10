"""Sesion global de la aplicacion (Singleton)

Guarda las "variables globales de sesion": al cerrar el sistema se destruyen.
"""
import threading


class Session:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._datos = {}
        return cls._instance

    @classmethod
    def get_instance(cls):
        return cls()

    def iniciar(self, administrador):
        self._datos = {"admin_id": administrador.id,
                       "usuario": administrador.usuario,
                       "nombre": administrador.nombre}

    @property
    def autenticado(self):
        return "admin_id" in self._datos

    @property
    def usuario(self):
        return self._datos.get("usuario")

    @property
    def nombre(self):
        return self._datos.get("nombre")

    def clear(self):
        """Destruye todas las variables de sesión."""
        self._datos.clear()
