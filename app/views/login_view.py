import tkinter as tk
from tkinter import ttk

from app.exceptions import AuthenticationError
from app.views.base import BaseView


class LoginView(BaseView):
    def __init__(self, parent, app, al_ingresar):
        super().__init__(parent)
        self.app = app
        self.al_ingresar = al_ingresar
        marco = ttk.LabelFrame(self, text=" Acceso administradores ", padding=24)
        marco.place(relx=0.5, rely=0.42, anchor="center")

        self.usuario = tk.StringVar()
        self.password = tk.StringVar()
        ttk.Label(marco, text="Usuario:").grid(row=0, column=0, sticky="e", pady=6)
        entrada = ttk.Entry(marco, textvariable=self.usuario, width=26)
        entrada.grid(row=0, column=1, padx=8)
        ttk.Label(marco, text="Contraseña:").grid(row=1, column=0, sticky="e", pady=6)
        pw = ttk.Entry(marco, textvariable=self.password, show="●", width=26)
        pw.grid(row=1, column=1, padx=8)
        self.mensaje = ttk.Label(marco, text="", foreground="#c62828")
        self.mensaje.grid(row=2, column=0, columnspan=2, pady=(4, 0))
        ttk.Button(marco, text="Ingresar", command=self._ingresar).grid(
            row=3, column=0, columnspan=2, pady=(10, 0), ipadx=18)
        entrada.focus_set()
        for w in (entrada, pw):
            w.bind("<Return>", lambda _e: self._ingresar())

    def _ingresar(self):
        try:
            self.app.auth.login(self.usuario.get(), self.password.get())
        except AuthenticationError as e:
            self.mensaje.config(text=str(e))
            self.password.set("")
            return
        self.password.set("")
        self.al_ingresar()
