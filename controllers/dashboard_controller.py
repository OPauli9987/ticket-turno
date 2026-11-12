from app.config import Config
from app.dao.solicitud_dao import SolicitudDAO


class DashboardController:
    def __init__(self):
        self._dao = SolicitudDAO()

    def conteo_por_estatus(self, municipio_id=None):
        """Devuelve {'Pendiente': n, 'Resuelto': m}; municipio None = total."""
        crudo = self._dao.contar_por_estatus(municipio_id)
        return {e: crudo.get(e, 0) for e in Config.ESTATUS_VALIDOS}
