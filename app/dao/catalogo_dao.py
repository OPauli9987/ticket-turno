"""DAO generico de catalogos (municipio, nivel educativo, asunto)."""
import sqlite3

from app.database.connection import Database
from app.exceptions import DuplicateError, IntegrityViolation, NotFoundError
from app.models.entities import Asunto, Catalogo, Municipio, NivelEducativo


class CatalogoDAO:
    TABLA = None          # definido por las subclases (nunca viene del usuario)
    ENTIDAD = Catalogo

    @property
    def _conn(self):
        return Database.get_instance().connection

    def listar(self):
        filas = self._conn.execute(
            f"SELECT id, nombre FROM {self.TABLA} ORDER BY nombre COLLATE NOCASE"
        ).fetchall()
        return [self.ENTIDAD(f["id"], f["nombre"]) for f in filas]

    def obtener(self, id_):
        f = self._conn.execute(
            f"SELECT id, nombre FROM {self.TABLA} WHERE id = ?", (id_,)).fetchone()
        return self.ENTIDAD(f["id"], f["nombre"]) if f else None

    def insertar(self, nombre):
        try:
            with self._conn:
                cur = self._conn.execute(
                    f"INSERT INTO {self.TABLA}(nombre) VALUES (?)", (nombre,))
        except sqlite3.IntegrityError:
            raise DuplicateError(f"Ya existe un registro llamado '{nombre}'.")
        return self.ENTIDAD(cur.lastrowid, nombre)

    def actualizar(self, id_, nombre):
        try:
            with self._conn:
                cur = self._conn.execute(
                    f"UPDATE {self.TABLA} SET nombre = ? WHERE id = ?", (nombre, id_))
        except sqlite3.IntegrityError:
            raise DuplicateError(f"Ya existe un registro llamado '{nombre}'.")
        if cur.rowcount == 0:
            raise NotFoundError("El registro ya no existe.")
        return self.ENTIDAD(id_, nombre)

    def eliminar(self, id_):
        try:
            with self._conn:
                cur = self._conn.execute(
                    f"DELETE FROM {self.TABLA} WHERE id = ?", (id_,))
        except sqlite3.IntegrityError:
            raise IntegrityViolation(
                "No se puede eliminar: hay solicitudes que usan este registro.")
        if cur.rowcount == 0:
            raise NotFoundError("El registro ya no existe.")


class MunicipioDAO(CatalogoDAO):
    TABLA = "municipio"
    ENTIDAD = Municipio


class NivelEducativoDAO(CatalogoDAO):
    TABLA = "nivel_educativo"
    ENTIDAD = NivelEducativo


class AsuntoDAO(CatalogoDAO):
    TABLA = "asunto"
    ENTIDAD = Asunto
