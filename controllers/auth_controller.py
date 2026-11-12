from app.dao.administrador_dao import AdministradorDAO
from app.exceptions import AuthenticationError
from app.utils.security import PasswordHasher
from app.utils.session import Session


class AuthController:
    def __init__(self):
        self._dao = AdministradorDAO()
        self.session = Session.get_instance()

    def login(self, usuario, password):
        usuario = (usuario or "").strip()
        if not usuario or not password:
            raise AuthenticationError("Capture usuario y contraseña.")
        admin = self._dao.buscar_por_usuario(usuario)
        if admin is None or not PasswordHasher.verificar(
                password, admin.salt, admin.password_hash):
            raise AuthenticationError("Usuario o contraseña incorrectos.")
        self.session.iniciar(admin)
        return admin

    def logout(self):
        self.session.clear()
