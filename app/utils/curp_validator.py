#Validacion de la CURP

#Estructura: 4 letras (2ª vocal) + AAMMDD + sexo (H/M/X) + entidad (2 letras)
#+ 3 consonantes internas + 2 caracteres finales (letras y/o numeros).
#Ejemplo valido: PETD800714HCLRNV02

import re
from datetime import date


class CurpValidator:
    ENTIDADES = ("AS|BC|BS|CC|CL|CM|CS|CH|DF|DG|GT|GR|HG|JC|MC|MN|MS|NT|NL|"
                 "OC|PL|QT|QR|SP|SL|SR|TC|TS|TL|VZ|YN|ZS|NE")
    PATRON = re.compile(
        r"^[A-Z][AEIOUX][A-Z]{2}"          # iniciales
        r"(\d{2})(\d{2})(\d{2})"           # AA MM DD
        r"[HMX]"                           # sexo
        r"(?:" + ENTIDADES + r")"          # entidad federativa
        r"[B-DF-HJ-NP-TV-Z]{3}"            # consonantes internas
        r"[A-Z0-9]{2}$"                    # 2 últimos: letras y/o números
    )

    @staticmethod
    def normalizar(curp):
        return (curp or "").strip().upper()

    @classmethod
    def errores(cls, curp):
        curp = cls.normalizar(curp)
        if not curp:
            return ["La CURP es obligatoria."]
        if len(curp) != 18:
            return [f"La CURP debe tener 18 caracteres (tiene {len(curp)})."]
        m = cls.PATRON.match(curp)
        if not m:
            return ["La CURP no tiene un formato válido "
                    "(ejemplo: PETD800714HCLRNV02)."]
        aa, mm, dd = (int(g) for g in m.groups())
        if not cls._fecha_valida(aa, mm, dd):
            return ["La fecha de nacimiento dentro de la CURP no es válida."]
        return []

    @classmethod
    def es_valida(cls, curp):
        return not cls.errores(curp)

    @staticmethod
    def _fecha_valida(aa, mm, dd):
        for siglo in (1900, 2000):
            try:
                date(siglo + aa, mm, dd)
                return True
            except ValueError:
                continue
        return False
