#Tablero con graficas de estatus (Resuelto / Pendiente), filtrable
import math
import tkinter as tk
from tkinter import ttk

from app.config import Config
from app.views.base import ObserverView


class DashboardView(ObserverView):
    COLORES = {Config.ESTATUS_PENDIENTE: "#f0a030", Config.ESTATUS_RESUELTO: "#2e9e5b"}
    TODOS = "Todos los municipios (total)"

    def __init__(self, parent, app):
        super().__init__(parent, app, "Dashboard",
                         "Estatus de las solicitudes. Se actualiza solo.")
        self._municipios = {m.nombre: m.id for m in app.catalogos["municipio"].listar()}
        self.filtro = tk.StringVar(value=self.TODOS)

        barra = ttk.Frame(self)
        barra.pack(fill="x", pady=(0, 8))
        ttk.Label(barra, text="Filtrar por municipio:").pack(side="left")
        combo = ttk.Combobox(barra, textvariable=self.filtro, state="readonly",
                             width=32, values=[self.TODOS] + list(self._municipios))
        combo.pack(side="left", padx=6)
        combo.bind("<<ComboboxSelected>>", lambda _e: self.refrescar())
        ttk.Button(barra, text="Actualizar", command=self.refrescar).pack(side="left")

        self.lienzo = tk.Canvas(self, bg="white", highlightthickness=1,
                                highlightbackground="#cccccc")
        self.lienzo.pack(fill="both", expand=True)
        self.lienzo.bind("<Configure>", lambda _e: self._dibujar())
        self._datos = {}
        self.refrescar()

    # ---------- datos ----------
    def refrescar(self):
        municipio_id = self._municipios.get(self.filtro.get())
        self._datos = self.app.dashboard.conteo_por_estatus(municipio_id)
        self._dibujar()

    # ---------- dibujo ----------
    def _dibujar(self):
        c = self.lienzo
        c.delete("all")
        ancho, alto = c.winfo_width(), c.winfo_height()
        if ancho < 50 or alto < 50:
            return
        total = sum(self._datos.values())
        ambito = "todos los municipios" if self.filtro.get() == self.TODOS \
            else self.filtro.get()
        c.create_text(ancho / 2, 24, font=("Segoe UI", 13, "bold"),
                      text=f"Solicitudes por estatus — {ambito}")
        c.create_text(ancho / 2, 48, font=("Segoe UI", 10), fill="#555",
                      text=f"Total de solicitudes: {total}")
        self._pastel(ancho * 0.27, alto * 0.55, min(ancho * 0.2, alto * 0.33), total)
        self._barras(ancho * 0.52, ancho * 0.95, alto - 60, alto * 0.25)
        self._leyenda(ancho / 2, alto - 22, total)

    def _pastel(self, cx, cy, r, total):
        c = self.lienzo
        caja = (cx - r, cy - r, cx + r, cy + r)
        if total == 0:
            c.create_oval(*caja, fill="#eeeeee", outline="#cccccc")
            c.create_text(cx, cy, text="Sin datos", fill="#888")
            return
        activos = [e for e, n in self._datos.items() if n > 0]
        if len(activos) == 1:
            c.create_oval(*caja, fill=self.COLORES[activos[0]], outline="white", width=2)
            c.create_text(cx, cy, text="100%", fill="white", font=("Segoe UI", 14, "bold"))
            return
        inicio = 90
        for estatus, n in self._datos.items():
            if n == 0:
                continue
            extension = -360 * n / total
            c.create_arc(*caja, start=inicio, extent=extension, fill=self.COLORES[estatus],
                         outline="white", width=2)
            medio = math.radians(inicio + extension / 2)
            c.create_text(cx + 0.62 * r * math.cos(medio), cy - 0.62 * r * math.sin(medio),
                          text=f"{100 * n / total:.0f}%", fill="white",
                          font=("Segoe UI", 12, "bold"))
            inicio += extension

    def _barras(self, x0, x1, base, tope):
        c = self.lienzo
        maximo = max(max(self._datos.values()), 1)
        c.create_line(x0, base, x1, base, fill="#999")
        n_barras = len(self._datos)
        espacio = (x1 - x0) / n_barras
        ancho_barra = min(espacio * 0.6, 110)
        for i, (estatus, n) in enumerate(self._datos.items()):
            centro = x0 + espacio * (i + 0.5)
            alto_barra = (base - tope) * n / maximo
            c.create_rectangle(centro - ancho_barra / 2, base - alto_barra,
                               centro + ancho_barra / 2, base,
                               fill=self.COLORES[estatus], outline="")
            c.create_text(centro, base - alto_barra - 12, text=str(n),
                          font=("Segoe UI", 12, "bold"))
            c.create_text(centro, base + 14, text=estatus, font=("Segoe UI", 10))

    def _leyenda(self, cx, y, total):
        c = self.lienzo
        x = cx - 150
        for estatus, n in self._datos.items():
            c.create_rectangle(x, y - 7, x + 14, y + 7, fill=self.COLORES[estatus], outline="")
            c.create_text(x + 20, y, anchor="w", text=f"{estatus}: {n}", font=("Segoe UI", 10))
            x += 170
