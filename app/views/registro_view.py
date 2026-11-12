"""Parte pública: registrar una solicitud y obtener comprobante."""
from tkinter import messagebox, ttk

from app.exceptions import DuplicateError, TicketTurnoError, ValidationError
from app.views.base import BaseView
from app.views.comprobante_dialog import ComprobanteDialog
from app.views.solicitud_form import SolicitudForm


class RegistroView(BaseView):
    def __init__(self, parent, app):
        super().__init__(parent, "Solicitar turno",
                         "Capture los datos del alumno para agendar su trámite.")
        self.app = app
        self.form = SolicitudForm(self, app)
        self.form.pack(anchor="w")
        botones = ttk.Frame(self)
        botones.pack(anchor="w", padx=10, pady=14)
        ttk.Button(botones, text="Registrar solicitud",
                   command=self._registrar).pack(side="left", padx=(0, 8))
        ttk.Button(botones, text="Limpiar", command=self.form.limpiar).pack(side="left")
        self.form.enfocar()

    def _registrar(self):
        try:
            solicitud = self.app.solicitudes.registrar(self.form.obtener_datos())
        except ValidationError as e:
            messagebox.showwarning("Datos incompletos o inválidos",
                                   "\n".join("• " + x for x in e.errores))
            return
        except DuplicateError as e:
            messagebox.showwarning("Solicitud duplicada", str(e))
            return
        except TicketTurnoError as e:
            messagebox.showerror("Error", str(e))
            return
        self.form.limpiar()
        ComprobanteDialog(self.winfo_toplevel(), solicitud)
