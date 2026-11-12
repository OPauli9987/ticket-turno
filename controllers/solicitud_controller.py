from app.config import Config
from app.dao.solicitud_dao import SolicitudDAO
from app.exceptions import DuplicateError, NotFoundError, ValidationError
from app.models.entities import Solicitud
from app.utils.curp_validator import CurpValidator
from app.utils.observer import Subject
from app.utils.validators import SolicitudValidator


class SolicitudController:
    """Casos de uso de solicitudes. Es el *Subject* del patrón Observer."""

    def __init__(self):
        self._dao = SolicitudDAO()
        self.subject = Subject()

    # ---------- util ----------
    @staticmethod
    def _preparar(datos):
        datos = SolicitudValidator.normalizar(datos)
        errores = SolicitudValidator.validar(datos)
        if errores:
            raise ValidationError(errores)
        return datos

    # ---------- parte pública ----------
    def registrar(self, datos):
        datos = self._preparar(datos)
        datos["estatus"] = Config.ESTATUS_PENDIENTE   # el público no fija estatus
        existente = self._dao.obtener(datos["curp"])
        if existente:
            raise DuplicateError(
                f"Ya existe una solicitud con esa CURP (turno "
                f"{existente.numero_turno} de {existente.municipio_nombre}). "
                "Use la opción 'Modificar solicitud' para cambiar sus datos.")
        solicitud = self._dao.insertar(Solicitud.from_dict(datos))
        self.subject.notify("registrada", solicitud)
        return solicitud

    def verificar_identidad(self, curp, turno):
        """CURP + número de turno deben coincidir con una solicitud."""
        curp = CurpValidator.normalizar(curp)
        errores = CurpValidator.errores(curp)
        if errores:
            raise ValidationError(errores)
        try:
            turno = int(str(turno).strip())
        except ValueError:
            raise ValidationError(["El número de turno debe ser numérico."])
        solicitud = self._dao.obtener(curp)
        if solicitud is None or solicitud.numero_turno != turno:
            raise NotFoundError("No se encontró una solicitud con esa CURP "
                                "y número de turno.")
        return solicitud

    def modificar_publico(self, curp, turno, datos):
        actual = self.verificar_identidad(curp, turno)
        datos = dict(datos, curp=actual.curp, estatus=actual.estatus)
        datos = self._preparar(datos)
        solicitud = self._dao.actualizar(Solicitud.from_dict(datos))
        self.subject.notify("modificada", solicitud)
        return solicitud

    # ---------- administradores ----------
    def listar(self, estatus=None):
        return self._dao.listar(estatus)

    def buscar(self, criterio, texto):
        texto = (texto or "").strip()
        if not texto:
            return self._dao.listar()
        if criterio == "curp":
            return self._dao.buscar_por_curp(texto.upper())
        return self._dao.buscar_por_nombre(texto)

    def obtener(self, curp):
        s = self._dao.obtener(curp)
        if s is None:
            raise NotFoundError("La solicitud no existe.")
        return s

    def crear_admin(self, datos):
        datos = self._preparar(datos)
        if self._dao.obtener(datos["curp"]):
            raise DuplicateError("Ya existe una solicitud con esa CURP.")
        solicitud = self._dao.insertar(Solicitud.from_dict(datos))
        self.subject.notify("registrada", solicitud)
        return solicitud

    def actualizar_admin(self, datos):
        datos = self._preparar(datos)
        solicitud = self._dao.actualizar(Solicitud.from_dict(datos))
        self.subject.notify("modificada", solicitud)
        return solicitud

    def cambiar_estatus(self, curp, estatus):
        if estatus not in Config.ESTATUS_VALIDOS:
            raise ValidationError(["Estatus inválido."])
        self._dao.cambiar_estatus(curp, estatus)
        self.subject.notify("estatus", curp)

    def eliminar(self, curp):
        self._dao.eliminar(curp)
        self.subject.notify("eliminada", curp)
