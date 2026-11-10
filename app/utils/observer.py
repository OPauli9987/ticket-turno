#PATRON DE DISEÑO Observer

#Las vistas (Dashboard, lista de solicitudes) se suscriben al ``Subject`` del SolicitudController y se refrescan automáticamente cuando hay cambios.


class Observer:
    def update(self, evento, datos=None):  # pragma: no cover - interfaz
        raise NotImplementedError


class Subject:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, evento, datos=None):
        for observer in list(self._observers):
            observer.update(evento, datos)
