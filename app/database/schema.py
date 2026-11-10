from app.config import Config
from app.utils.security import PasswordHasher


class SchemaInitializer:
    DDL = """
    CREATE TABLE IF NOT EXISTS municipio (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre  TEXT NOT NULL UNIQUE
    );
    CREATE TABLE IF NOT EXISTS nivel_educativo (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre  TEXT NOT NULL UNIQUE
    );
    CREATE TABLE IF NOT EXISTS asunto (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre  TEXT NOT NULL UNIQUE
    );
    CREATE TABLE IF NOT EXISTS administrador (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario        TEXT NOT NULL UNIQUE,
        nombre         TEXT NOT NULL,
        salt           TEXT NOT NULL,
        password_hash  TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS turno_contador (
        municipio_id  INTEGER PRIMARY KEY
                      REFERENCES municipio(id) ON DELETE CASCADE,
        ultimo        INTEGER NOT NULL DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS solicitud (
        curp                TEXT PRIMARY KEY,
        nombre_alumno       TEXT NOT NULL,
        apellido_paterno    TEXT NOT NULL,
        apellido_materno    TEXT NOT NULL DEFAULT '',
        nombre_tramitante   TEXT NOT NULL,
        telefono            TEXT NOT NULL,
        telefono_alterno    TEXT NOT NULL DEFAULT '',
        correo              TEXT NOT NULL,
        nivel_id            INTEGER NOT NULL
                            REFERENCES nivel_educativo(id) ON DELETE RESTRICT,
        municipio_id        INTEGER NOT NULL
                            REFERENCES municipio(id) ON DELETE RESTRICT,
        asunto_id           INTEGER NOT NULL
                            REFERENCES asunto(id) ON DELETE RESTRICT,
        observaciones       TEXT NOT NULL DEFAULT '',
        numero_turno        INTEGER NOT NULL,
        estatus             TEXT NOT NULL DEFAULT 'Pendiente'
                            CHECK (estatus IN ('Pendiente','Resuelto')),
        fecha_registro      TEXT NOT NULL,
        fecha_modificacion  TEXT NOT NULL,
        UNIQUE (municipio_id, numero_turno)
    );
    CREATE INDEX IF NOT EXISTS idx_solicitud_municipio
        ON solicitud(municipio_id);
    CREATE INDEX IF NOT EXISTS idx_solicitud_estatus
        ON solicitud(estatus);
    """

    @classmethod
    def inicializar(cls, conn):
        with conn:
            conn.executescript(cls.DDL)
        cls._sembrar(conn)

    @classmethod
    def _sembrar(cls, conn):
        with conn:
            for tabla, valores in (("municipio", Config.MUNICIPIOS),
                                   ("nivel_educativo", Config.NIVELES),
                                   ("asunto", Config.ASUNTOS)):
                if conn.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0] == 0:
                    conn.executemany(
                        f"INSERT INTO {tabla}(nombre) VALUES (?)",
                        [(v,) for v in valores])
            if conn.execute("SELECT COUNT(*) FROM administrador").fetchone()[0] == 0:
                salt, h = PasswordHasher.hash(Config.ADMIN_PASSWORD)
                conn.execute(
                    "INSERT INTO administrador(usuario, nombre, salt, password_hash)"
                    " VALUES (?,?,?,?)",
                    (Config.ADMIN_USUARIO, Config.ADMIN_NOMBRE, salt, h))
