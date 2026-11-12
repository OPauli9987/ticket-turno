"""Formulario reutilizable de solicitud (público y administrador)."""
import tkinter as tk
from tkinter import ttk

from app.config import Config
from app.utils.curp_validator import CurpValidator


class SolicitudForm(ttk.Frame):
    def __init__(self, parent, app, mostrar_estatus=False):
        super().__init__(parent)
        self.app = app
        self._vars = {}
        self._mapas = {}
        self._combos = {}
        self._mostrar_estatus = mostrar_estatus
        self._construir()

    # ---------- construcción ----------
    def _fila(self, fila, columna, etiqueta, clave, ancho=30, obligatorio=True):
        ttk.Label(self, text=etiqueta + (" *" if obligatorio else "")).grid(
            row=fila, column=columna * 2, sticky="e", padx=(10, 6), pady=5)
        var = tk.StringVar()
        entry = ttk.Entry(self, textvariable=var, width=ancho)
        entry.grid(row=fila, column=columna * 2 + 1, sticky="w", pady=5)
        self._vars[clave] = var
        return entry

    def _combo(self, fila, columna, etiqueta, clave, opciones):
        ttk.Label(self, text=etiqueta + " *").grid(
            row=fila, column=columna * 2, sticky="e", padx=(10, 6), pady=5)
        self._mapas[clave] = {o.nombre: o.id for o in opciones}
        var = tk.StringVar()
        combo = ttk.Combobox(self, textvariable=var, state="readonly", width=28,
                             values=[o.nombre for o in opciones])
        combo.grid(row=fila, column=columna * 2 + 1, sticky="w", pady=5)
        self._vars[clave] = var
        self._combos[clave] = combo

    def _construir(self):
        self.curp_entry = self._fila(0, 0, "CURP del alumno", "curp", 24)
        self.lbl_curp = ttk.Label(self, text="", width=34)
        self.lbl_curp.grid(row=0, column=2, columnspan=2, sticky="w")
        self._vars["curp"].trace_add("write", self._validar_curp_en_vivo)

        self._fila(1, 0, "Nombre del alumno", "nombre_alumno")
        self._fila(1, 1, "Apellido paterno", "apellido_paterno")
        self._fila(2, 0, "Apellido materno", "apellido_materno", obligatorio=False)
        self._fila(2, 1, "Quién realiza el trámite", "nombre_tramitante")
        self._fila(3, 0, "Teléfono (10 dígitos)", "telefono")
        self._fila(3, 1, "Teléfono alterno", "telefono_alterno", obligatorio=False)
        self._fila(4, 0, "Correo electrónico", "correo")

        catalogos = self.app.catalogos
        self._combo(5, 0, "Nivel que cursa", "nivel_id", catalogos["nivel"].listar())
        self._combo(5, 1, "Municipio donde estudia", "municipio_id",
                    catalogos["municipio"].listar())
        self._combo(6, 0, "Asunto a tratar", "asunto_id", catalogos["asunto"].listar())
        if self._mostrar_estatus:
            ttk.Label(self, text="Estatus *").grid(
                row=6, column=2, sticky="e", padx=(10, 6), pady=5)
            self._vars["estatus"] = tk.StringVar(value=Config.ESTATUS_PENDIENTE)
            ttk.Combobox(self, textvariable=self._vars["estatus"], state="readonly",
                         values=Config.ESTATUS_VALIDOS, width=28).grid(
                row=6, column=3, sticky="w", pady=5)
        self._fila(7, 0, "Observaciones", "observaciones", 30, obligatorio=False)
        ttk.Label(self, text="* Campo obligatorio", style="Sub.TLabel").grid(
            row=8, column=0, columnspan=4, sticky="w", padx=10, pady=(8, 0))

    # ---------- CURP en vivo ----------
    def _validar_curp_en_vivo(self, *_):
        curp = self._vars["curp"].get()
        if curp != curp.upper():
            self._vars["curp"].set(curp.upper())
            return
        if not curp:
            self.lbl_curp.config(text="", foreground="black")
        elif CurpValidator.es_valida(curp):
            self.lbl_curp.config(text="✔ CURP válida", foreground="#2e7d32")
        else:
            self.lbl_curp.config(text="✘ " + CurpValidator.errores(curp)[0][:48],
                                 foreground="#c62828")

    # ---------- datos ----------
    def obtener_datos(self):
        datos = {k: v.get() for k, v in self._vars.items()
                 if k not in self._mapas}
        for clave, mapa in self._mapas.items():
            datos[clave] = mapa.get(self._vars[clave].get())
        return datos

    def cargar(self, s):
        for clave, var in self._vars.items():
            if clave in self._mapas:
                continue
            var.set(getattr(s, clave, "") or "")
        nombres = {"nivel_id": s.nivel_nombre, "municipio_id": s.municipio_nombre,
                   "asunto_id": s.asunto_nombre}
        for clave, nombre in nombres.items():
            self._vars[clave].set(nombre)

    def limpiar(self):
        for clave, var in self._vars.items():
            var.set(Config.ESTATUS_PENDIENTE if clave == "estatus" else "")

    def bloquear_curp(self, bloquear=True):
        self.curp_entry.config(state="disabled" if bloquear else "normal")

    def enfocar(self):
        self.curp_entry.focus_set()
