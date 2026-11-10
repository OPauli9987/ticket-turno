"""DAO de solicitudes"""
import sqlite3
from datetime import datetime

from app.database.connection import Database, sin_acentos
from app.exceptions import DuplicateError, NotFoundError, ValidationError
from app.models.entities import Solicitud


class SolicitudDAO:
    SELECT = """
        SELECT s.*, m.nombre AS municipio_nombre, n.nombre AS nivel_nombre,
               a.nombre AS asunto_nombre
        FROM solicitud s
        JOIN municipio m       ON m.id = s.municipio_id
        JOIN nivel_educativo n ON n.id = s.nivel_id
        JOIN asunto a          ON a.id = s.asunto_id
    """
    NOMBRE_COMPLETO = ("sin_acentos(s.nombre_alumno || ' ' || "
                       "s.apellido_paterno || ' ' || s.apellido_materno)")

    @property
    def _conn(self):
        return Database.get_instance().connection

    @staticmethod
    def _ahora():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _a_solicitud(fila):
        return Solicitud(**dict(fila))

    # ---------- Turno por municipio (1..n) ----------
    @staticmethod
    def _siguiente_turno(conn, municipio_id):
        conn.execute("INSERT OR IGNORE INTO turno_contador(municipio_id, ultimo) "
                     "VALUES (?, 0)", (municipio_id,))
        conn.execute("UPDATE turno_contador SET ultimo = ultimo + 1 "
                     "WHERE municipio_id = ?", (municipio_id,))
        return conn.execute("SELECT ultimo FROM turno_contador "
                            "WHERE municipio_id = ?", (municipio_id,)).fetchone()[0]

    # ---------- Consultas ----------
    def obtener(self, curp):
        f = self._conn.execute(self.SELECT + " WHERE s.curp = ?", (curp,)).fetchone()
        return self._a_solicitud(f) if f else None

    def listar(self, estatus=None):
        sql, params = self.SELECT, ()
        if estatus:
            sql += " WHERE s.estatus = ?"
            params = (estatus,)
        sql += " ORDER BY s.fecha_registro DESC, s.curp"
        return [self._a_solicitud(f) for f in self._conn.execute(sql, params)]

    def buscar_por_curp(self, texto):
        filas = self._conn.execute(
            self.SELECT + " WHERE s.curp LIKE ? ORDER BY s.curp",
            (f"%{texto}%",)).fetchall()
        return [self._a_solicitud(f) for f in filas]

    def buscar_por_nombre(self, texto):
        palabras = sin_acentos(texto).split()
        where = " AND ".join(f"{self.NOMBRE_COMPLETO} LIKE ?" for _ in palabras)
        filas = self._conn.execute(
            self.SELECT + f" WHERE {where} ORDER BY s.apellido_paterno, s.nombre_alumno",
            [f"%{p}%" for p in palabras]).fetchall()
        return [self._a_solicitud(f) for f in filas]

    def contar_por_estatus(self, municipio_id=None):
        sql = "SELECT estatus, COUNT(*) AS total FROM solicitud"
        params = ()
        if municipio_id is not None:
            sql += " WHERE municipio_id = ?"
            params = (municipio_id,)
        sql += " GROUP BY estatus"
        return {f["estatus"]: f["total"] for f in self._conn.execute(sql, params)}

    # ---------- Escritura ----------
    def insertar(self, s):
        ahora = self._ahora()
        try:
            with self._conn as conn:     # una transacción: turno + registro
                s.numero_turno = self._siguiente_turno(conn, s.municipio_id)
                conn.execute(
                    """INSERT INTO solicitud(curp, nombre_alumno, apellido_paterno,
                       apellido_materno, nombre_tramitante, telefono,
                       telefono_alterno, correo, nivel_id, municipio_id, asunto_id,
                       observaciones, numero_turno, estatus, fecha_registro,
                       fecha_modificacion)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (s.curp, s.nombre_alumno, s.apellido_paterno,
                     s.apellido_materno, s.nombre_tramitante, s.telefono,
                     s.telefono_alterno, s.correo, s.nivel_id, s.municipio_id,
                     s.asunto_id, s.observaciones, s.numero_turno, s.estatus,
                     ahora, ahora))
        except sqlite3.IntegrityError as e:
            raise self._traducir(e)
        return self.obtener(s.curp)

    def actualizar(self, s):
        actual = self.obtener(s.curp)
        if actual is None:
            raise NotFoundError("La solicitud no existe.")
        try:
            with self._conn as conn:
                turno = actual.numero_turno
                if actual.municipio_id != s.municipio_id:   # cambió de municipio
                    turno = self._siguiente_turno(conn, s.municipio_id)
                conn.execute(
                    """UPDATE solicitud SET nombre_alumno=?, apellido_paterno=?,
                       apellido_materno=?, nombre_tramitante=?, telefono=?,
                       telefono_alterno=?, correo=?, nivel_id=?, municipio_id=?,
                       asunto_id=?, observaciones=?, estatus=?, numero_turno=?,
                       fecha_modificacion=? WHERE curp=?""",
                    (s.nombre_alumno, s.apellido_paterno, s.apellido_materno,
                     s.nombre_tramitante, s.telefono, s.telefono_alterno,
                     s.correo, s.nivel_id, s.municipio_id, s.asunto_id,
                     s.observaciones, s.estatus, turno, self._ahora(), s.curp))
        except sqlite3.IntegrityError as e:
            raise self._traducir(e)
        return self.obtener(s.curp)

    def cambiar_estatus(self, curp, estatus):
        with self._conn as conn:
            cur = conn.execute(
                "UPDATE solicitud SET estatus=?, fecha_modificacion=? WHERE curp=?",
                (estatus, self._ahora(), curp))
        if cur.rowcount == 0:
            raise NotFoundError("La solicitud no existe.")

    def eliminar(self, curp):
        with self._conn as conn:
            cur = conn.execute("DELETE FROM solicitud WHERE curp = ?", (curp,))
        if cur.rowcount == 0:
            raise NotFoundError("La solicitud no existe.")

    @staticmethod
    def _traducir(error):
        msg = str(error)
        if "solicitud.curp" in msg or "UNIQUE" in msg:
            return DuplicateError("Ya existe una solicitud con esa CURP.")
        return ValidationError(["Alguno de los catálogos seleccionados no existe."])
