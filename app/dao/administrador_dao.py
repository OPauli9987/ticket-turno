from app.database.connection import Database
from app.models.entities import Administrador


class AdministradorDAO:
    @property
    def _conn(self):
        return Database.get_instance().connection

    def buscar_por_usuario(self, usuario):
        f = self._conn.execute(
            "SELECT id, usuario, nombre, salt, password_hash "
            "FROM administrador WHERE usuario = ?", (usuario,)).fetchone()
        return Administrador(**dict(f)) if f else None
