import json
from dataclasses import asdict, replace
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import numpy as np
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.adapters.output.modelos import FilaRegistroPreferencia
from app.adapters.output.motor_preferencias import MotorPreferenciasLocal
from app.adapters.output.registro_preferencias import RegistroPreferenciasSql
from app.adapters.output.repositorios_carreras import RepositorioCarrerasJson
from app.application.catalogo import Catalogo
from app.application.recomendar_preferencia import RecomendarPreferencia, huella_programas
from app.domain.cuestionario import VERSION_CUESTIONARIO, generar_cuestionario
from app.domain.perfil_vocacional import VERSION_CARACTERISTICAS, extraer_caracteristicas
from app.infrastructure.configuracion import Configuracion
from app.infrastructure.entrenar_preferencias import entrenar, separar_participantes
from app.infrastructure.principal import crear_aplicacion


@pytest.fixture
def par():
    carreras = RepositorioCarrerasJson(Path("data/catalogo_lima_norte_2026.json")).carreras
    return carreras[0], carreras[-1]


def respuestas(par):
    return {
        **{f"p{i}": "1" for i in range(1, 7)},
        **{f"p{i}": par[0].id for i in range(7, 10)},
        "p10": "interes",
    }


def test_preguntas_dinamicas_canonicas_y_datos_reales(par):
    a, b = par
    assert huella_programas(par) == huella_programas(
        [
            replace(c, costo_mensual_soles=c.costo_mensual_soles.quantize(Decimal("0.01")))
            for c in par
        ]
    )
    cuestionario = generar_cuestionario(a, b)
    assert len(cuestionario["preguntas"]) == 10
    assert cuestionario == generar_cuestionario(b, a)
    assert a.detalles["cursos_principales"][0] in str(cuestionario["preguntas"][6])
    misma = RepositorioCarrerasJson(Path("data/catalogo_lima_norte_2026.json")).carreras
    opciones = [c for c in misma if c.nombre == "Administración"]
    preguntas = generar_cuestionario(opciones[0], opciones[1])["preguntas"][6:9]
    assert all(p["opciones"][0]["texto"] != p["opciones"][1]["texto"] for p in preguntas)
    assert all("instituci" in p["contexto"] or "catálogo" in p["contexto"] for p in preguntas)


def test_caracteristicas_antisimetricas_inciertas_y_validacion(par):
    a, b = par
    perfil = respuestas(par)
    x = extraer_caracteristicas(a, b, perfil, {"presupuesto_maximo": 500})
    invertido = extraer_caracteristicas(b, a, perfil, {"presupuesto_maximo": 500})
    assert all(np.isclose(x[k], -invertido[k]) for k in x)
    repositorio = Catalogo(RepositorioCarrerasJson(Path("data/catalogo_lima_norte_2026.json")))
    caso = RecomendarPreferencia(repositorio, MotorPreferenciasLocal(Path("models/inexistente")))
    sin_evidencia = {f"p{i}": "incierto" for i in range(1, 11)}
    assert (
        caso.ejecutar([a.id, b.id], sin_evidencia, {}, VERSION_CUESTIONARIO)["estado"]
        == "informacion_insuficiente"
    )
    assert caso.ejecutar([a.id, b.id], perfil, {}, VERSION_CUESTIONARIO)["estado"] == "sin_modelo"
    with pytest.raises(ValueError):
        caso.ejecutar([a.id, b.id], {"p1": "1"}, {}, VERSION_CUESTIONARIO)


def test_api_cuestionario_y_recomendacion_sin_simulacion(par):
    a, b = par
    configuracion = Configuracion(
        modo_datos="demo", ruta_catalogo_json=Path("data/catalogo_lima_norte_2026.json")
    )
    with TestClient(crear_aplicacion(configuracion)) as cliente:
        assert len(cliente.get("/api/v1/cuestionario").json()["preguntas"]) == 6
        ruta = "/api/v1/cuestionario/comparativo"
        consulta = [("idsProgramas", a.id), ("idsProgramas", b.id)]
        cuestionario = cliente.get(ruta, params=consulta).json()
        assert len(cuestionario["preguntas"]) == 10
        cuerpo = {
            "idsProgramas": [a.id, b.id],
            "version": cuestionario["version"],
            "respuestas": respuestas(par),
        }
        resultado = cliente.post("/api/v1/recomendaciones", json=cuerpo)
        assert resultado.status_code == 200, resultado.text
        assert resultado.json()["estado"] == "sin_modelo"
        assert resultado.json()["recomendada"] is None
        assert cliente.get(ruta, params=[("idsProgramas", a.id)]).status_code == 422
        assert cliente.get(ruta, params=[("idsProgramas", a.id)] * 2).status_code == 422
        assert (
            cliente.post(
                "/api/v1/recomendaciones", json=cuerpo | {"preferencias": {"presupuestoMaximo": -1}}
            ).status_code
            == 422
        )
        assert (
            cliente.post(
                "/api/v1/recomendaciones",
                json=cuerpo | {"respuestas": respuestas(par) | {"p7": "otro"}},
            ).status_code
            == 422
        )


def test_captura_consentida_idempotente_y_no_etiquetas_automaticas(base_datos, par):
    registro = RegistroPreferenciasSql(sessionmaker(base_datos))
    catalogo = Catalogo(RepositorioCarrerasJson(Path("data/catalogo_lima_norte_2026.json")))
    caso = RecomendarPreferencia(
        catalogo, MotorPreferenciasLocal(Path("models/inexistente")), registro
    )
    captura = {
        "id_registro": str(uuid4()),
        "id_participante": str(uuid4()),
        "eleccion": par[1].id,
        "consentimiento": True,
        "mayor_edad": True,
    }
    ids = [c.id for c in par]
    for _ in range(2):
        assert (
            caso.ejecutar(ids, respuestas(par), {}, VERSION_CUESTIONARIO, captura)["id_registro"]
            == captura["id_registro"]
        )
    with Session(base_datos) as sesion:
        assert sesion.scalar(select(func.count()).select_from(FilaRegistroPreferencia)) == 1
        fila = sesion.get(FilaRegistroPreferencia, captura["id_registro"])
        assert fila.estado_revision == "pendiente"
        assert fila.datos["eleccion"] == par[1].id
        assert "eleccion" not in fila.datos["caracteristicas"]
        fila.estado_revision = "aprobado"
        fila.datos = fila.datos | {
            "motivo_revision": "Elección independiente revisada por el equipo"
        }
        sesion.commit()
    assert (
        caso.ejecutar(ids, respuestas(par), {}, VERSION_CUESTIONARIO, captura)["id_registro"]
        == captura["id_registro"]
    )
    with pytest.raises(ValueError):
        caso.ejecutar(
            ids, respuestas(par), {}, VERSION_CUESTIONARIO, captura | {"consentimiento": False}
        )


def test_pipeline_reproducible_y_separacion_solo_con_fixtures_sinteticas(tmp_path, par):
    # Fixtures sintéticas de pruebas: nunca se exportan como datos reales.
    generador = np.random.default_rng(42)
    filas = []
    for indice in range(100):
        perfil = respuestas(par) | {f"p{i}": str(generador.integers(1, 5)) for i in range(1, 7)}
        perfil |= {f"p{i}": par[int(generador.integers(0, 2))].id for i in range(7, 10)}
        filas.append(
            {
                "id_registro": str(indice),
                "id_participante": f"fixture-{indice // 2}",
                "consentimiento": True,
                "mayor_edad": True,
                "estado_revision": "aprobado",
                "origen_eleccion": "previa_inferencia",
                "version_cuestionario": VERSION_CUESTIONARIO,
                "version_caracteristicas": VERSION_CARACTERISTICAS,
                "programas": [c.id for c in par],
                "huella_programas": huella_programas(par),
                "respuestas": perfil,
                "preferencias": {},
                "caracteristicas": extraer_caracteristicas(
                    *sorted(par, key=lambda c: c.id), perfil, {}
                ),
                "eleccion": par[indice % 2].id,
                "instantaneas": [asdict(c) for c in par],
            }
        )
    carreras = {c.id: c for c in par}
    from app.infrastructure.entrenar_preferencias import validar_dataset

    registros = validar_dataset(filas, carreras)
    particiones = separar_participantes(registros)
    grupos = [{registros[i][2] for i in indices} for indices in particiones]
    assert not grupos[0] & grupos[1] and not grupos[0] & grupos[2] and not grupos[1] & grupos[2]
    primero = entrenar(filas, carreras, tmp_path / "uno")
    segundo = entrenar(filas, carreras, tmp_path / "dos")
    assert primero["prueba"] == segundo["prueba"]
    assert primero["validacion"] == segundo["validacion"]
    with pytest.raises(ValueError, match="30 participantes"):
        entrenar(filas[:4], carreras, tmp_path / "fallido")
    with pytest.raises(ValueError, match="consentimiento"):
        entrenar([filas[0] | {"consentimiento": False}], carreras, tmp_path / "fallido")
    # Activar solo este artefacto temporal para comprobar la identidad de contribuciones y simetría.
    ruta = tmp_path / "uno" / "informe.json"
    informe = json.loads(ruta.read_text(encoding="utf-8"))
    informe["habilitado"] = True
    ruta.write_text(json.dumps(informe), encoding="utf-8")
    motor = MotorPreferenciasLocal(tmp_path / "uno")
    x = filas[0]["caracteristicas"]
    a = motor.predecir(x)
    b = motor.predecir({k: -v for k, v in x.items()})
    assert a["estado"] == "disponible"
    assert np.isclose(a["margen"], -b["margen"])
    assert np.isclose(sum(f["contribucion"] for f in a["contribuciones"]), a["margen"])
