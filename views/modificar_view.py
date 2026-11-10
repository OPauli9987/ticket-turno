"""Parte pública: modificar una solicitud con CURP + número de turno."""
import tkinter as tk
from tkinter import messagebox, ttk

from app.exceptions import TicketTurnoError, ValidationError
from app.views.base import BaseView
from app.views.comprobante_dialog import ComprobanteDialog
from app.views.solicitud_form import SolicitudForm


class ModificarView(BaseView):
    def __init__(self, parent, app):
        super().__init__(parent, "Modificar solicitud",
                         "Capture su CURP y el número de turno que se le asignó.")
        self.app = app
        self._verificada = None

        busqueda = ttk.Frame(self)
        busqueda.pack(anchor="w", padx=10, pady=(0, 10))
        self.curp = tk.StringVar()
        self.turno = tk.StringVar()
        ttk.Label(busqueda, text="CURP:").pack(side="left")
        e = ttk.Entry(busqueda, textvariable=self.curp, width=24)
        e.pack(side="left", padx=(4, 14))
        self.curp.trace_add("write", lambda *_: self.curp.set(self.curp.get().upper()))
        ttk.Label(busqueda, text="Núm. de turno:").pack(side="left")
        ttk.Entry(busqueda, textvariable=self.turno, width=8).pack(side="left", padx=4)
        ttk.Button(busqueda, text="Buscar", command=self._buscar).pack(
            side="left", padx=10)
        e.focus_set()

        self.form = SolicitudForm(self, app)
        self.boton = ttk.Button(self, text="Guardar cambios", command=self._guardar,
                                state="disabled")

    def _buscar(self):
        try:
            self._verificada = self.app.solicitudes.verificar_identidad(
                self.curp.get(), self.turno.get())
        except TicketTurnoError as e:
            messagebox.showwarning("No se pudo verificar",
                                   "\n".join(getattr(e, "errores", [str(e)])))
            return
        self.form.pack(anchor="w")
        self.boton.pack(anchor="w", padx=10, pady=14)
        self.boton.config(state="normal")
        self.form.cargar(self._verificada)
        self.form.bloquear_curp()

    def _guardar(self):
        if self._verificada is None:
            return
        try:
            solicitud = self.app.solicitudes.modificar_publico(
                self._verificada.curp, self._verificada.numero_turno,
                self.form.obtener_datos())
        except ValidationError as e:
            messagebox.showwarning("Datos inválidos",
                                   "\n".join("• " + x for x in e.errores))
            return
        except TicketTurnoError as e:
            messagebox.showerror("Error", str(e))
            return
        self._verificada = solicitud
        self.turno.set(str(solicitud.numero_turno))
        messagebox.showinfo("Listo", "Sus datos fueron actualizados.")
        ComprobanteDialog(self.winfo_toplevel(), solicitud)
