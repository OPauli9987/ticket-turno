#Generacion del comprobante de datos basicos con el turno asignado
from app.config import Config


class ComprobanteService:
    @staticmethod
    def lineas(s):
        return [
            ("COMPROBANTE DE SOLICITUD", None),
            (Config.APP_NAME.upper(), None),
            ("", None),
            ("Municipio", s.municipio_nombre),
            ("NÚMERO DE TURNO", str(s.numero_turno)),
            ("", None),
            ("CURP del alumno", s.curp),
            ("Alumno", s.nombre_completo),
            ("Nivel que cursa", s.nivel_nombre),
            ("Asunto a tratar", s.asunto_nombre),
            ("Trámite realizado por", s.nombre_tramitante),
            ("Teléfono", s.telefono + (f" / {s.telefono_alterno}"
                                       if s.telefono_alterno else "")),
            ("Correo", s.correo),
            ("Estatus", s.estatus),
            ("Fecha de registro", s.fecha_registro),
            ("Última modificación", s.fecha_modificacion),
            ("", None),
            ("Conserve este comprobante: para modificar su solicitud", None),
            ("necesitará la CURP y el número de turno.", None),
        ]

    @classmethod
    def texto(cls, s):
        salida = []
        for etiqueta, valor in cls.lineas(s):
            salida.append(etiqueta if valor is None else f"{etiqueta + ':':<24}{valor}")
        return "\n".join(salida)

    @classmethod
    def guardar_txt(cls, s, ruta):
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(cls.texto(s))

    @classmethod
    def pdf_disponible(cls):
        try:
            import reportlab  # noqa: F401
            return True
        except ImportError:
            return False

    @classmethod
    def guardar_pdf(cls, s, ruta):
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(ruta, pagesize=letter)
        ancho, alto = letter
        y = alto - 70
        for etiqueta, valor in cls.lineas(s):
            if valor is None:
                c.setFont("Helvetica-Bold", 14 if y > alto - 100 else 10)
                c.drawString(60, y, etiqueta)
            else:
                c.setFont("Helvetica-Bold", 11)
                c.drawString(60, y, etiqueta + ":")
                c.setFont("Helvetica", 11)
                c.drawString(230, y, valor)
            y -= 22
        c.rect(45, y + 10, ancho - 90, alto - 70 - y + 40)
        c.save()
