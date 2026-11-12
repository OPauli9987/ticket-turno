"""Componentes base compartidos por las vistas."""
from tkinter import ttk


class BaseView(ttk.Frame):
    def __init__(self, parent, titulo=None, subtitulo=None):
        super().__init__(parent, padding=14)
        if titulo:
            ttk.Label(self, text=titulo, style="Titulo.TLabel").pack(anchor="w")
        if subtitulo:
            ttk.Label(self, text=subtitulo, style="Sub.TLabel").pack(
                anchor="w", pady=(0, 10))


class ObserverView(BaseView):
    """Vista que se suscribe al Subject del SolicitudController (Observer)."""

    def __init__(self, parent, app, titulo=None, subtitulo=None):
        super().__init__(parent, titulo, subtitulo)
        self.app = app
        app.solicitudes.subject.attach(self)

    def update(self, evento, datos=None):
        if self.winfo_exists():
            self.refrescar()

    def refrescar(self):  # pragma: no cover - lo implementan las subclases
        raise NotImplementedError

    def destroy(self):
        self.app.solicitudes.subject.detach(self)
        super().destroy()
