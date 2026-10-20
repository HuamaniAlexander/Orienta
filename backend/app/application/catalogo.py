from app.ports.repositorio_carreras import ConsultaCatalogo, RepositorioCarreras


class CarreraNoEncontrada(Exception):
    pass


class Catalogo:
    def __init__(self, repositorio: RepositorioCarreras):
        self.repositorio = repositorio

    def buscar(self, consulta: ConsultaCatalogo):
        return self.repositorio.listar(consulta)

    def detalle(self, id: str):
        carrera = self.repositorio.obtener(id)
        if carrera is None or not carrera.activa:
            raise CarreraNoEncontrada(id)
        return carrera

    def filtros(self):
        return self.repositorio.facetas()
