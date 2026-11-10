"""Validacion y normalizacion de los datos de una solicitud."""
import re

from app.config import Config
from app.utils.curp_validator import CurpValidator


class SolicitudValidator:
    NOMBRE_RE = re.compile(r"^[A-ZÁÉÍÓÚÜÑ][A-ZÁÉÍÓÚÜÑ .'\-]{0,59}$")
    CORREO_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")

    @classmethod
    def normalizar(cls, datos):
        d = dict(datos)
        d["curp"] = CurpValidator.normalizar(d.get("curp"))
        for campo in ("nombre_alumno", "apellido_paterno", "apellido_materno",
                      "nombre_tramitante"):
            d[campo] = " ".join(str(d.get(campo) or "").split()).upper()
        for campo in ("telefono", "telefono_alterno"):
            d[campo] = re.sub(r"[\s\-()]", "", str(d.get(campo) or ""))
        d["correo"] = str(d.get("correo") or "").strip().lower()
        d["observaciones"] = str(d.get("observaciones") or "").strip()
        d["estatus"] = d.get("estatus") or Config.ESTATUS_PENDIENTE
        for campo in ("nivel_id", "municipio_id", "asunto_id"):
            try:
                d[campo] = int(d.get(campo))
            except (TypeError, ValueError):
                d[campo] = None
        return d

    @classmethod
    def validar(cls, d):
        """Recibe datos YA normalizados y devuelve la lista de errores."""
        errores = CurpValidator.errores(d["curp"])
        if not cls.NOMBRE_RE.match(d["nombre_alumno"]):
            errores.append("Nombre del alumno obligatorio (solo letras).")
        if not cls.NOMBRE_RE.match(d["apellido_paterno"]):
            errores.append("Apellido paterno obligatorio (solo letras).")
        if d["apellido_materno"] and not cls.NOMBRE_RE.match(d["apellido_materno"]):
            errores.append("Apellido materno inválido (solo letras).")
        if not cls.NOMBRE_RE.match(d["nombre_tramitante"]):
            errores.append("Nombre de quien realiza el trámite obligatorio "
                           "(solo letras).")
        if not re.fullmatch(r"\d{10}", d["telefono"]):
            errores.append("El teléfono debe tener 10 dígitos.")
        if d["telefono_alterno"] and not re.fullmatch(r"\d{10}", d["telefono_alterno"]):
            errores.append("El teléfono alterno debe tener 10 dígitos.")
        if not cls.CORREO_RE.match(d["correo"]):
            errores.append("El correo electrónico no es válido.")
        if d["nivel_id"] is None:
            errores.append("Seleccione el nivel que cursa.")
        if d["municipio_id"] is None:
            errores.append("Seleccione el municipio donde estudia.")
        if d["asunto_id"] is None:
            errores.append("Seleccione el asunto a tratar.")
        if d["estatus"] not in Config.ESTATUS_VALIDOS:
            errores.append("Estatus inválido.")
        if len(d["observaciones"]) > 300:
            errores.append("Las observaciones no pueden pasar de 300 caracteres.")
        return errores
