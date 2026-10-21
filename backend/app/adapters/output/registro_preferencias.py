import json
from dataclasses import asdict
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError

from app.adapters.output.modelos import FilaDefinicionCuestionario, FilaRegistroPreferencia
from app.domain.cuestionario import VERSION_CUESTIONARIO, preguntas_generales


def registrar_definicion(sesion):
    if sesion.get(FilaDefinicionCuestionario, VERSION_CUESTIONARIO) is None:
        sesion.add(
            FilaDefinicionCuestionario(
                version=VERSION_CUESTIONARIO,
                contenido={
                    "generales": [asdict(p) for p in preguntas_generales()],
                    "dinamicas": ["p7", "p8", "p9"],
                    "prioridad": "p10",
                    "cantidad": 10,
                    "instrumento_validado": False,
                },
            )
        )
        sesion.flush()


class RegistroPreferenciasSql:
    def __init__(self, sesiones):
        self.sesiones = sesiones

    def guardar(self, registro):
        if registro.get("consentimiento") is not True or registro.get("mayor_edad") is not True:
            raise ValueError("La captura requiere consentimiento y mayorÃ­a de edad declarada")
        datos = json.loads(json.dumps(registro, default=str, ensure_ascii=False))
        try:
            with self.sesiones() as sesion, sesion.begin():
                anterior = sesion.get(FilaRegistroPreferencia, registro["id_registro"])
                if anterior:
                    if {k: v for k, v in anterior.datos.items() if k != "motivo_revision"} != datos:
                        raise ValueError(
                            "El identificador de captura ya corresponde a otra elecciÃ³n"
                        )
                    return anterior.id
                registrar_definicion(sesion)
                sesion.add(
                    FilaRegistroPreferencia(
                        id=registro["id_registro"],
                        id_participante=registro["id_participante"],
                        version_cuestionario=registro["version_cuestionario"],
                        fecha_captura=datetime.now(timezone.utc),
                        estado_revision="pendiente",
                        datos=datos,
                    )
                )
            return registro["id_registro"]
        except IntegrityError as error:
            raise ValueError("La captura ya estÃ¡ registrada; reintenta sin duplicarla") from error
