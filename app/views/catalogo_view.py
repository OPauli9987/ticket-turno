"""CRUD genérico de un catálogo."""
import tkinter as tk
from tkinter import messagebox, ttk

from app.exceptions import TicketTurnoError, ValidationError
from app.views.base import BaseView


class CatalogoView(BaseView):
    def __init__(self, parent, controlador):
        super().__init__(parent, f"Catálogo: {controlador.titulo}",
                         "Agregue, renombre o elimine registros del catálogo.")
        self.controlador = controlador
        self._seleccionado = None
        self.nombre = tk.StringVar()

        formulario = ttk.Frame(self)
        formulario.pack(fill="x", pady=(0, 8))
        ttk.Label(formulario, text="Nombre:").pack(side="left")
        entrada = ttk.Entry(formulario, textvariable=self.nombre, width=36)
        entrada.pack(side="left", padx=6)
        entrada.bind("<Return>", lambda _e: self._guardar())
        ttk.Button(formulario, text="➕ Agregar", command=self._agregar).pack(
            side="left", padx=2)
        ttk.Button(formulario, text="💾 Guardar cambio",
                   command=self._guardar).pack(side="left", padx=2)
        ttk.Button(formulario, text="🗑 Eliminar", command=self._eliminar).pack(
            side="left", padx=2)
        ttk.Button(formulario, text="Limpiar", command=self._limpiar).pack(
            side="left", padx=2)

        marco = ttk.Frame(self)
        marco.pack(fill="both", expand=True)
        self.tabla = ttk.Treeview(marco, columns=("id", "nombre"), show="headings",
                                  selectmode="browse")
        self.tabla.heading("id", text="ID")
        self.tabla.heading("nombre", text="Nombre")
        self.tabla.column("id", width=70, anchor="center")
        self.tabla.column("nombre", width=420)
        sy = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=sy.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        sy.pack(side="left", fill="y")
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)
        self._cargar()

    def _cargar(self):
        self.tabla.delete(*self.tabla.get_children())
        for item in self.controlador.listar():
            self.tabla.insert("", "end", iid=str(item.id), values=(item.id, item.nombre))

    def _al_seleccionar(self, _evento=None):
        sel = self.tabla.selection()
        if sel:
            self._seleccionado = int(sel[0])
            self.nombre.set(self.tabla.item(sel[0], "values")[1])

    def _limpiar(self):
        self._seleccionado = None
        self.nombre.set("")
        self.tabla.selection_remove(self.tabla.selection())

    def _ejecutar(self, accion):
        try:
            accion()
        except ValidationError as e:
            messagebox.showwarning("Dato inválido", "\n".join(e.errores))
            return
        except TicketTurnoError as e:
            messagebox.showerror("No se pudo completar", str(e))
            return
        self._limpiar()
        self._cargar()

    def _agregar(self):
        self._ejecutar(lambda: self.controlador.crear(self.nombre.get()))

    def _guardar(self):
        if self._seleccionado is None:
            messagebox.showinfo("Seleccione", "Seleccione un registro para modificar.")
            return
        self._ejecutar(lambda: self.controlador.actualizar(self._seleccionado,
                                                           self.nombre.get()))

    def _eliminar(self):
        if self._seleccionado is None:
            messagebox.showinfo("Seleccione", "Seleccione un registro para eliminar.")
            return
        if messagebox.askyesno("Eliminar", f"¿Eliminar '{self.nombre.get()}'?"):
            self._ejecutar(lambda: self.controlador.eliminar(self._seleccionado))
