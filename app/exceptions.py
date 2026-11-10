"""Excepciones propias del dominio"""


class TicketTurnoError(Exception):
    """Base de todas las excepciones de la aplicacion"""


class ValidationError(TicketTurnoError):
    def __init__(self, errores):
        self.errores = list(errores)
        super().__init__("; ".join(self.errores))


class NotFoundError(TicketTurnoError):
    pass


class DuplicateError(TicketTurnoError):
    pass


class IntegrityViolation(TicketTurnoError):
    """Se intenta borrar un registro que esta siendo usado por otro"""


class AuthenticationError(TicketTurnoError):
    pass
