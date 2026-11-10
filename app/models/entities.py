"""Modelo de clases (entidades del dominio)"""

class Catalogo:

    def __init__(self, id=None, nombre=""):
        self.id = id
        self.nombre = nombre

    def __str__(self):
        return self.nombre

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, nombre={self.nombre!r})"


class Municipio(Catalogo):
    pass


class NivelEducativo(Catalogo):
    pass


class Asunto(Catalogo):
    pass


class Administrador:
    def __init__(self, id=None, usuario="", nombre="", salt="", password_hash=""):
        self.id = id
        self.usuario = usuario
        self.nombre = nombre
        self.salt = salt
        self.password_hash = password_hash


class Solicitud:
    CAMPOS = ("curp", "nombre_alumno", "apellido_paterno", "apellido_materno",
              "nombre_tramitante", "telefono", "telefono_alterno", "correo",
              "nivel_id", "municipio_id", "asunto_id", "observaciones",
              "estatus")

    def __init__(self, curp="", nombre_alumno="", apellido_paterno="",
                 apellido_materno="", nombre_tramitante="", telefono="",
                 telefono_alterno="", correo="", nivel_id=None,
                 municipio_id=None, asunto_id=None, observaciones="",
                 estatus="Pendiente", numero_turno=None, fecha_registro="",
                 fecha_modificacion="", municipio_nombre="", nivel_nombre="",
                 asunto_nombre=""):
        self.curp = curp
        self.nombre_alumno = nombre_alumno
        self.apellido_paterno = apellido_paterno
        self.apellido_materno = apellido_materno
        self.nombre_tramitante = nombre_tramitante
        self.telefono = telefono
        self.telefono_alterno = telefono_alterno
        self.correo = correo
        self.nivel_id = nivel_id
        self.municipio_id = municipio_id
        self.asunto_id = asunto_id
        self.observaciones = observaciones
        self.estatus = estatus
        self.numero_turno = numero_turno
        self.fecha_registro = fecha_registro
        self.fecha_modificacion = fecha_modificacion
        # Campos de solo lectura traídos con JOIN
        self.municipio_nombre = municipio_nombre
        self.nivel_nombre = nivel_nombre
        self.asunto_nombre = asunto_nombre

    @classmethod
    def from_dict(cls, datos):
        return cls(**{c: datos.get(c) for c in cls.CAMPOS if c in datos})

    @property
    def nombre_completo(self):
        return " ".join(p for p in (self.nombre_alumno, self.apellido_paterno,
                                    self.apellido_materno) if p)

    def a_dict(self):
        return {c: getattr(self, c) for c in self.CAMPOS}
