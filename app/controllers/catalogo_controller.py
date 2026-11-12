from app.exceptions import ValidationError


class CatalogoController:
    #CRUD de un catálogo (recibe el DAO correspondiente)

    def __init__(self, dao, titulo):
        self._dao = dao
        self.titulo = titulo

    @staticmethod
    def _limpiar(nombre):
        nombre = " ".join((nombre or "").split())
        if not nombre:
            raise ValidationError(["El nombre es obligatorio."])
        if len(nombre) > 80:
            raise ValidationError(["El nombre no puede pasar de 80 caracteres."])
        return nombre

    def listar(self):
        return self._dao.listar()

    def crear(self, nombre):
        return self._dao.insertar(self._limpiar(nombre))

    def actualizar(self, id_, nombre):
        return self._dao.actualizar(id_, self._limpiar(nombre))

    def eliminar(self, id_):
        self._dao.eliminar(id_)
