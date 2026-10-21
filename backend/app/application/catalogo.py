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

    def instituciones(self):
        agrupadas = {}
        pagina = 1
        while True:
            carreras, total = self.buscar(ConsultaCatalogo(pagina=pagina, limite=100))
            for carrera in carreras:
                datos = agrupadas.setdefault(
                    carrera.institucion,
                    {
                        "nombre": carrera.institucion,
                        "ofertas": 0,
                        "gestion": carrera.detalles.get("gestion", ""),
                        "tipo": carrera.detalles.get("tipo_institucion", ""),
                        "distritos": set(),
                        "sitio_web": carrera.detalles.get("sitio_web", ""),
                    },
                )
                datos["ofertas"] += 1
                if carrera.ubicacion:
                    datos["distritos"].add(carrera.ubicacion)
            if pagina * 100 >= total:
                break
            pagina += 1
        return [
            datos | {"distritos": sorted(datos["distritos"])}
            for _, datos in sorted(agrupadas.items())
        ]
