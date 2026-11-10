from app.config import Config
from app.controllers.app_controller import AppController
from app.database.connection import Database
from app.database.schema import SchemaInitializer
from app.views.main_window import MainWindow

"""Arranque: BD -> esquema -> controladores -> ventana"""
class Application:

    def run(self):
        Config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        conexion = Database.get_instance().connect()
        SchemaInitializer.inicializar(conexion)
        MainWindow(AppController()).mainloop()
