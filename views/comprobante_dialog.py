import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from app.utils.comprobante import ComprobanteService


class ComprobanteDialog(tk.Toplevel):
    def __init__(self, parent, solicitud):
        super().__init__(parent)
        self.title("Comprobante de solicitud")
        self.solicitud = solicitud
        self.resizable(False, False)
        self.transient(parent)

        ttk.Label(self, text=f"TURNO {solicitud.numero_turno}  ·  "
                             f"{solicitud.municipio_nombre}",
                  style="Turno.TLabel").pack(padx=20, pady=(16, 6))
        texto = tk.Text(self, width=66, height=21, font=("Courier New", 10),
                        relief="solid", borderwidth=1)
        texto.insert("1.0", ComprobanteService.texto(solicitud))
        texto.config(state="disabled")
        texto.pack(padx=20, pady=6)

        botones = ttk.Frame(self)
        botones.pack(pady=(6, 16))
        ttk.Button(botones, text="Guardar como .txt",
                   command=self._guardar_txt).pack(side="left", padx=4)
        if ComprobanteService.pdf_disponible():
            ttk.Button(botones, text="Guardar como PDF",
                       command=self._guardar_pdf).pack(side="left", padx=4)
        ttk.Button(botones, text="Cerrar", command=self.destroy).pack(
            side="left", padx=4)
        self.grab_set()

    def _guardar(self, extension, escritor, tipo):
        ruta = filedialog.asksaveasfilename(
            parent=self, defaultextension=extension,
            initialfile=f"turno_{self.solicitud.numero_turno}_{self.solicitud.curp}",
            filetypes=[(tipo, "*" + extension)])
        if ruta:
            escritor(self.solicitud, ruta)
            messagebox.showinfo("Comprobante", f"Guardado en:\n{ruta}", parent=self)

    def _guardar_txt(self):
        self._guardar(".txt", ComprobanteService.guardar_txt, "Texto")

    def _guardar_pdf(self):
        self._guardar(".pdf", ComprobanteService.guardar_pdf, "PDF")
