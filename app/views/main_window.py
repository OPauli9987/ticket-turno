"""Ventana principal: menú de navegación y cambio de pantallas."""
import tkinter as tk
from tkinter import messagebox, ttk

from app.config import Config
from app.views.admin_solicitudes_view import AdminSolicitudesView
from app.views.catalogo_view import CatalogoView
from app.views.dashboard_view import DashboardView
from app.views.home_view import HomeView
from app.views.login_view import LoginView
from app.views.modificar_view import ModificarView
from app.views.registro_view import RegistroView


class MainWindow(tk.Tk):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.title(Config.APP_NAME)
        self.geometry("1150x680")
        self.minsize(960, 600)
        self._estilos()
        self._contenedor = ttk.Frame(self)
        self._contenedor.pack(fill="both", expand=True)
        self._barra = ttk.Label(self, anchor="w", padding=(10, 3), relief="sunken")
        self._barra.pack(fill="x", side="bottom")
        self._actual = None
        self.protocol("WM_DELETE_WINDOW", self.cerrar_sistema)
        self._construir_menu()
        self.mostrar_inicio()

    # ---------- estilos ----------
    def _estilos(self):
        s = ttk.Style(self)
        if "clam" in s.theme_names():
            s.theme_use("clam")
        s.configure("Titulo.TLabel", font=("Segoe UI", 16, "bold"))
        s.configure("Sub.TLabel", foreground="#666666")
        s.configure("Hero.TLabel", font=("Segoe UI", 28, "bold"))
        s.configure("Turno.TLabel", font=("Segoe UI", 18, "bold"), foreground="#1a5fb4")
        s.configure("Treeview", rowheight=24)

    # ---------- menú ----------
    def _construir_menu(self):
        barra = tk.Menu(self)
        publico = tk.Menu(barra, tearoff=False)
        publico.add_command(label="Inicio", command=self.mostrar_inicio)
        publico.add_command(label="Solicitar turno", command=self.mostrar_registro)
        publico.add_command(label="Modificar solicitud", command=self.mostrar_modificar)
        barra.add_cascade(label="Público", menu=publico)

        admin = tk.Menu(barra, tearoff=False)
        if self.app.session.autenticado:
            admin.add_command(label="Solicitudes", command=self.mostrar_solicitudes)
            admin.add_command(label="Dashboard", command=self.mostrar_dashboard)
            catalogos = tk.Menu(admin, tearoff=False)
            for clave, ctrl in self.app.catalogos.items():
                catalogos.add_command(label=ctrl.titulo,
                                      command=lambda k=clave: self.mostrar_catalogo(k))
            admin.add_cascade(label="Catálogos", menu=catalogos)
            admin.add_separator()
            admin.add_command(label="Cerrar sesión", command=self.cerrar_sesion)
        else:
            admin.add_command(label="Iniciar sesión", command=self.mostrar_login)
        barra.add_cascade(label="Administración", menu=admin)

        sistema = tk.Menu(barra, tearoff=False)
        sistema.add_command(label="Cerrar sistema", command=self.cerrar_sistema)
        barra.add_cascade(label="Sistema", menu=sistema)
        self.config(menu=barra)
        self._barra.config(text=f"Sesión: {self.app.session.nombre} "
                                f"({self.app.session.usuario})"
                           if self.app.session.autenticado else "Modo público")

    # ---------- navegación ----------
    def _mostrar(self, fabrica):
        if self._actual is not None:
            self._actual.destroy()
        self._actual = fabrica(self._contenedor)
        self._actual.pack(fill="both", expand=True)

    def _exigir_admin(self):
        if self.app.session.autenticado:
            return True
        messagebox.showinfo("Acceso restringido", "Inicie sesión como administrador.")
        self.mostrar_login()
        return False

    def mostrar_inicio(self):
        self._mostrar(lambda p: HomeView(p, self))

    def mostrar_registro(self):
        self._mostrar(lambda p: RegistroView(p, self.app))

    def mostrar_modificar(self):
        self._mostrar(lambda p: ModificarView(p, self.app))

    def mostrar_login(self):
        self._mostrar(lambda p: LoginView(p, self.app, self._login_correcto))

    def mostrar_solicitudes(self):
        if self._exigir_admin():
            self._mostrar(lambda p: AdminSolicitudesView(p, self.app))

    def mostrar_dashboard(self):
        if self._exigir_admin():
            self._mostrar(lambda p: DashboardView(p, self.app))

    def mostrar_catalogo(self, clave):
        if self._exigir_admin():
            self._mostrar(lambda p: CatalogoView(p, self.app.catalogos[clave]))

    # ---------- sesión / cierre ----------
    def _login_correcto(self):
        self._construir_menu()
        self.mostrar_solicitudes()

    def cerrar_sesion(self):
        self.app.auth.logout()
        self._construir_menu()
        self.mostrar_inicio()

    def cerrar_sistema(self):
        if messagebox.askyesno("Cerrar sistema",
                               "Se cerrará la sesión, la base de datos y la "
                               "aplicación. ¿Desea continuar?"):
            if self._actual is not None:
                self._actual.destroy()
                self._actual = None
            self.app.cerrar_sistema()
            self.destroy()
