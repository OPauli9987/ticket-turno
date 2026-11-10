from tkinter import ttk

from app.config import Config
from app.views.base import BaseView


class HomeView(BaseView):
    def __init__(self, parent, ventana):
        super().__init__(parent)
        centro = ttk.Frame(self)
        centro.place(relx=0.5, rely=0.45, anchor="center")
        ttk.Label(centro, text=Config.APP_NAME, style="Hero.TLabel").pack(pady=(0, 4))
        ttk.Label(centro, text="Agenda de citas para trámites escolares del "
                               "sector educativo del Estado",
                  style="Sub.TLabel").pack(pady=(0, 24))
        ttk.Button(centro, text="📝  Solicitar un turno", width=32,
                   command=ventana.mostrar_registro).pack(pady=5, ipady=6)
        ttk.Button(centro, text="✏️  Modificar mi solicitud", width=32,
                   command=ventana.mostrar_modificar).pack(pady=5, ipady=6)
        ttk.Button(centro, text="🔒  Acceso administradores", width=32,
                   command=ventana.mostrar_login).pack(pady=5, ipady=6)
