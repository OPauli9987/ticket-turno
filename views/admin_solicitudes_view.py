"""Administradores: consulta por CURP o nombre + alta/edición/baja/estatus."""
import tkinter as tk
from tkinter import messagebox, ttk

from app.config import Config
from app.exceptions import TicketTurnoError, ValidationError
from app.views.base import ObserverView
from app.views.comprobante_dialog import ComprobanteDialog
from app.views.solicitud_form import SolicitudForm


class SolicitudDialog(tk.Toplevel):
    """Alta o edición de una solicitud por parte del administrador."""

    def __init__(self, parent, app, solicitud=None):
        super().__init__(parent)
        self.app = app
        self.solicitud = solicitud
        self.title("Editar solicitud" if solicitud else "Nueva solicitud")
        self.transient(parent)
        self.form = SolicitudForm(self, app, mostrar_estatus=True)
        self.form.pack(padx=14, pady=14)
        if solicitud:
            self.form.cargar(solicitud)
            self.form.bloquear_curp()
        botones = ttk.Frame(self)
        botones.pack(pady=(0, 14))
        ttk.Button(botones, text="Guardar", command=self._guardar).pack(
            side="left", padx=4)
        ttk.Button(botones, text="Cancelar", command=self.destroy).pack(
            side="left", padx=4)
        self.grab_set()

    def _guardar(self):
        datos = self.form.obtener_datos()
        try:
            if self.solicitud:
                datos["curp"] = self.solicitud.curp
                self.app.solicitudes.actualizar_admin(datos)
            else:
                self.app.solicitudes.crear_admin(datos)
        except ValidationError as e:
            messagebox.showwarning("Datos inválidos",
                                   "\n".join("• " + x for x in e.errores), parent=self)
            return
        except TicketTurnoError as e:
            messagebox.showerror("Error", str(e), parent=self)
            return
        self.destroy()


class AdminSolicitudesView(ObserverView):
    COLUMNAS = (("turno", "Turno", 55), ("municipio", "Municipio", 120),
                ("curp", "CURP", 160), ("alumno", "Alumno", 210),
                ("tramitante", "Tramitante", 160), ("telefono", "Teléfono", 95),
                ("nivel", "Nivel", 90), ("asunto", "Asunto", 140),
                ("estatus", "Estatus", 80))

    def __init__(self, parent, app):
        super().__init__(parent, app, "Solicitudes",
                         "Consulta por CURP o nombre y administración de trámites.")
        self.criterio = tk.StringVar(value="curp")
        self.texto = tk.StringVar()
        self.filtro_estatus = tk.StringVar(value="Todos")
        self._construir_barra()
        self._construir_tabla()
        self._construir_acciones()
        self.refrescar()

    def _construir_barra(self):
        barra = ttk.Frame(self)
        barra.pack(fill="x", pady=(0, 8))
        ttk.Label(barra, text="Buscar por:").pack(side="left")
        ttk.Radiobutton(barra, text="CURP", value="curp",
                        variable=self.criterio).pack(side="left", padx=4)
        ttk.Radiobutton(barra, text="Nombre", value="nombre",
                        variable=self.criterio).pack(side="left", padx=4)
        entrada = ttk.Entry(barra, textvariable=self.texto, width=30)
        entrada.pack(side="left", padx=6)
        entrada.bind("<Return>", lambda _e: self.refrescar())
        ttk.Button(barra, text="Buscar", command=self.refrescar).pack(side="left")
        ttk.Button(barra, text="Ver todos", command=self._ver_todos).pack(
            side="left", padx=4)
        ttk.Label(barra, text="   Estatus:").pack(side="left")
        combo = ttk.Combobox(barra, textvariable=self.filtro_estatus, width=11,
                             state="readonly",
                             values=("Todos",) + Config.ESTATUS_VALIDOS)
        combo.pack(side="left", padx=4)
        combo.bind("<<ComboboxSelected>>", lambda _e: self.refrescar())

    def _construir_tabla(self):
        marco = ttk.Frame(self)
        marco.pack(fill="both", expand=True)
        self.tabla = ttk.Treeview(marco, columns=[c[0] for c in self.COLUMNAS],
                                  show="headings", selectmode="browse")
        for clave, titulo, ancho in self.COLUMNAS:
            self.tabla.heading(clave, text=titulo)
            self.tabla.column(clave, width=ancho, anchor="w")
        self.tabla.tag_configure("Pendiente", foreground="#b26a00")
        self.tabla.tag_configure("Resuelto", foreground="#2e7d32")
        sy = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview)
        sx = ttk.Scrollbar(marco, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        self.tabla.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=1, column=0, sticky="ew")
        marco.rowconfigure(0, weight=1)
        marco.columnconfigure(0, weight=1)
        self.tabla.bind("<Double-1>", lambda _e: self._editar())
        self.lbl_total = ttk.Label(self, text="")
        self.lbl_total.pack(anchor="w", pady=(6, 0))

    def _construir_acciones(self):
        acciones = ttk.Frame(self)
        acciones.pack(fill="x", pady=(8, 0))
        for texto, cmd in (("➕ Nueva", self._nueva), ("✏️ Modificar", self._editar),
                           ("🗑 Eliminar", self._eliminar),
                           ("✔ Marcar Resuelto", lambda: self._estatus("Resuelto")),
                           ("⏳ Marcar Pendiente", lambda: self._estatus("Pendiente")),
                           ("🧾 Comprobante", self._comprobante)):
            ttk.Button(acciones, text=texto, command=cmd).pack(side="left", padx=(0, 6))

    # ---------- datos ----------
    def refrescar(self):
        try:
            if self.texto.get().strip():
                filas = self.app.solicitudes.buscar(self.criterio.get(),
                                                    self.texto.get())
            else:
                filas = self.app.solicitudes.listar()
        except TicketTurnoError as e:
            messagebox.showerror("Error", str(e))
            return
        if self.filtro_estatus.get() != "Todos":
            filas = [s for s in filas if s.estatus == self.filtro_estatus.get()]
        self.tabla.delete(*self.tabla.get_children())
        for s in filas:
            self.tabla.insert("", "end", iid=s.curp, tags=(s.estatus,), values=(
                s.numero_turno, s.municipio_nombre, s.curp, s.nombre_completo,
                s.nombre_tramitante, s.telefono, s.nivel_nombre, s.asunto_nombre,
                s.estatus))
        self.lbl_total.config(text=f"{len(filas)} solicitud(es)")

    def _ver_todos(self):
        self.texto.set("")
        self.filtro_estatus.set("Todos")
        self.refrescar()

    def _curp_seleccionada(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showinfo("Seleccione", "Seleccione una solicitud de la tabla.")
            return None
        return sel[0]

    # ---------- acciones ----------
    def _nueva(self):
        SolicitudDialog(self.winfo_toplevel(), self.app)

    def _editar(self):
        curp = self._curp_seleccionada()
        if curp:
            SolicitudDialog(self.winfo_toplevel(), self.app,
                            self.app.solicitudes.obtener(curp))

    def _eliminar(self):
        curp = self._curp_seleccionada()
        if curp and messagebox.askyesno(
                "Eliminar", f"¿Eliminar definitivamente la solicitud de {curp}?"):
            try:
                self.app.solicitudes.eliminar(curp)
            except TicketTurnoError as e:
                messagebox.showerror("Error", str(e))

    def _estatus(self, estatus):
        curp = self._curp_seleccionada()
        if curp:
            try:
                self.app.solicitudes.cambiar_estatus(curp, estatus)
            except TicketTurnoError as e:
                messagebox.showerror("Error", str(e))

    def _comprobante(self):
        curp = self._curp_seleccionada()
        if curp:
            ComprobanteDialog(self.winfo_toplevel(), self.app.solicitudes.obtener(curp))
