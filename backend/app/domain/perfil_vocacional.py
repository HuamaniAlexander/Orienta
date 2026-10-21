"""Características simétricas definidas de igual manera al entrenar e inferir."""

import re

from app.domain.carrera import Carrera, normalizar

VERSION_CARACTERISTICAS = "preferencias-pares-1.0"
NOMBRES_FACTORES = {
    "intereses": "Intereses declarados y contenido académico",
    "habilidades": "Habilidades que reconoces",
    "materias": "Materias preferidas",
    "actividades": "Actividades profesionales preferidas",
    "problemas": "Preferencias de formación",
    "costo": "Presupuesto y pensión estimada",
    "duracion": "Duración de estudios",
    "modalidad": "Modalidad preferida",
}
# Correspondencia orientativa RIASEC, no baremos psicométricos ni etiquetas de preferencia.
VOCABULARIO = (
    "mecan|taller|constru|industrial|maquina|robot|practic",
    "analiz|analisis|ciencia|investig|matemat|program|tecnolog|sistema|dato",
    "diseno|arte|creativ|comunic|publicidad|arquitect",
    "salud|enferm|ayud|persona|educa|psicolo|terapia|medic",
    "negocio|empresa|gestion|lider|marketing|administr|proyecto",
    "contab|financ|organiza|presupuest|reporte|control",
)
MAPAS = {
    "p1": (1, 2, 3, 4),
    "p2": (1, 3, 2, 4),
    "p3": (1, 0, 3, 4),
    "p4": (1, 2, 3, 4),
    "p5": (1, 0, 3, 4),
    "p6": (1, 2, 3, 4),
}


def vector_carrera(carrera: Carrera):
    texto = normalizar(
        " ".join(
            [
                carrera.nombre,
                carrera.campo_laboral or "",
                carrera.detalles.get("descripcion", ""),
                *carrera.detalles.get("cursos_principales", []),
                *carrera.detalles.get("actividades_profesionales", []),
            ]
        )
    )
    valores = [len(re.findall(patron, texto)) for patron in VOCABULARIO]
    total = sum(valores) or 1
    return [valor / total for valor in valores]


def extraer_caracteristicas(izquierda, derecha, respuestas, preferencias):
    a, b = vector_carrera(izquierda), vector_carrera(derecha)
    diferencias = [x - y for x, y in zip(a, b, strict=True)]
    intereses = [
        MAPAS[p][int(respuestas[p]) - 1]
        for p in ("p1", "p2", "p3", "p5", "p6")
        if respuestas[p] != "incierto"
    ]
    habilidad = respuestas["p4"]
    resultado = {
        "intereses": sum(diferencias[i] for i in intereses) / (len(intereses) or 1),
        "habilidades": diferencias[MAPAS["p4"][int(habilidad) - 1]]
        if habilidad != "incierto"
        else 0.0,
    }
    for pregunta, campo in [("p7", "materias"), ("p8", "actividades"), ("p9", "problemas")]:
        respuesta = respuestas[pregunta]
        resultado[campo] = float(respuesta == izquierda.id) - float(respuesta == derecha.id)
    prioridad = respuestas["p10"]
    presupuesto = preferencias.get("presupuesto_maximo")
    limite = preferencias.get("duracion_maxima")
    for campo, valor_a, valor_b, tope, seleccion in [
        ("costo", izquierda.costo_mensual_soles, derecha.costo_mensual_soles, presupuesto, "costo"),
        ("duracion", izquierda.duracion_meses, derecha.duracion_meses, limite, "duracion"),
    ]:
        resultado[campo] = 0.0
        if (
            valor_a is not None
            and valor_b is not None
            and (tope is not None or prioridad == seleccion)
        ):
            x, y = float(valor_a), float(valor_b)
            resultado[campo] = (
                (float(x <= tope) - float(y <= tope))
                if tope is not None
                else (y - x) / max(x, y, 1)
            )
    modalidad = normalizar(preferencias.get("modalidad_preferida") or "")
    resultado["modalidad"] = (
        (
            float(normalizar(izquierda.modalidad or "") == modalidad)
            - float(normalizar(derecha.modalidad or "") == modalidad)
        )
        if modalidad
        else 0.0
    )
    return resultado


def hay_informacion(respuestas, preferencias):
    return (
        any(respuestas[p] != "incierto" for p in MAPAS)
        or any(respuestas[p] not in ("incierto", "ninguna", "ambas") for p in ("p7", "p8", "p9"))
        or any(v is not None and v != "" for v in preferencias.values())
        or respuestas["p10"] in ("costo", "duracion")
    )
