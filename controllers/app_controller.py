from app.controllers.auth_controller import AuthController
from app.controllers.catalogo_controller import CatalogoController
from app.controllers.dashboard_controller import DashboardController
from app.controllers.solicitud_controller import SolicitudController
from app.dao.catalogo_dao import AsuntoDAO, MunicipioDAO, NivelEducativoDAO
from app.database.connection import Database
from app.utils.session import Session


class AppController:
    """Punto único que crea y comparte los controladores con las vistas."""

    def __init__(self):
        self.session = Session.get_instance()
        self.auth = AuthController()
        self.solicitudes = SolicitudController()
        self.dashboard = DashboardController()
        self.catalogos = {
            "municipio": CatalogoController(MunicipioDAO(), "Municipios"),
            "nivel": CatalogoController(NivelEducativoDAO(), "Niveles educativos"),
            "asunto": CatalogoController(AsuntoDAO(), "Asuntos / trámites"),
        }

    def cerrar_sistema(self):
        """Seguridad: destruye la sesión y cierra la base de datos."""
        self.session.clear()
        Database.get_instance().close()
