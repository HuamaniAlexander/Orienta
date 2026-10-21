"""Cuestionario orientativo; no constituye una prueba psicológica validada."""

from dataclasses import asdict, dataclass
from math import isfinite

from app.domain.carrera import Carrera, normalizar

VERSION_CUESTIONARIO = "vocacional-1.0"


@dataclass(frozen=True)
class OpcionVocacional:
    id: str
    texto: str


@dataclass(frozen=True)
class PreguntaVocacional:
    id: str
    seccion: str
    texto: str
    opciones: tuple[OpcionVocacional, ...]
    contexto: str = ""


GENERALES = (
    (
        "¿Qué actividad te gustaría realizar en un proyecto?",
        (
            "Investigar y resolver problemas",
            "Crear diseños o ideas originales",
            "Ayudar y orientar a otras personas",
            "Organizar y dirigir un equipo",
        ),
    ),
    (
        "¿Qué materias te llaman más la atención?",
        (
            "Matemáticas y tecnología",
            "Biología y ciencias de la salud",
            "Comunicación, arte y diseño",
            "Economía y negocios",
        ),
    ),
    (
        "¿En qué entorno preferirías trabajar?",
        (
            "Utilizando computadoras y tecnología",
            "En un laboratorio o taller",
            "Interactuando directamente con personas",
            "En una empresa gestionando proyectos",
        ),
    ),
    (
        "¿Qué habilidad consideras que tienes más desarrollada?",
        (
            "Razonamiento lógico y análisis",
            "Creatividad e imaginación",
            "Comunicación y empatía",
            "Organización y liderazgo",
        ),
    ),
    (
        "Cuando surge un problema, ¿qué prefieres hacer?",
        (
            "Analizar información para encontrar la causa",
            "Experimentar y probar soluciones",
            "Escuchar a los involucrados",
            "Coordinar acciones para solucionarlo",
        ),
    ),
    (
        "¿Qué resultado te produciría mayor satisfacción?",
        (
            "Resolver un problema complejo",
            "Crear algo novedoso",
            "Mejorar la vida de alguien",
            "Conseguir que un proyecto tenga éxito",
        ),
    ),
)


def preguntas_generales():
    return tuple(
        PreguntaVocacional(
            f"p{indice}",
            "Intereses y habilidades",
            texto,
            tuple(OpcionVocacional(str(i + 1), opcion) for i, opcion in enumerate(opciones))
            + (OpcionVocacional("incierto", "Todavía no estoy seguro"),),
        )
        for indice, (texto, opciones) in enumerate(GENERALES, 1)
    )


def generar_cuestionario(izquierda: Carrera, derecha: Carrera):
    # Orden canónico independiente de la posición en el comparador.
    carreras = sorted((izquierda, derecha), key=lambda carrera: carrera.id)
    a, b = carreras
    misma = a.detalles.get("carrera_id", normalizar(a.nombre)) == b.detalles.get(
        "carrera_id", normalizar(b.nombre)
    )
    definiciones = [
        ("¿Qué materias preferirías estudiar?", "cursos_principales"),
        ("¿Qué actividades profesionales te gustaría realizar?", "actividades_profesionales"),
        ("¿Qué tipo de problemas preferirías resolver?", "habilidades_recomendadas"),
    ]
    dinamicas = []
    for indice, (texto, campo) in enumerate(definiciones, 7):
        valores = [", ".join(c.detalles.get(campo, [])) for c in carreras]
        iguales = not all(valores) or normalizar(valores[0]) == normalizar(valores[1])
        if misma or iguales:
            textos = [
                f"{c.nombre} · {c.institucion}: "
                + (
                    f"modalidad {c.modalidad}; sede {c.ubicacion}"
                    if indice == 7
                    else f"formación {c.tipo_formacion}; duración {c.duracion_meses} meses"
                    if indice == 8
                    else (
                        f"pensión estimada S/ {c.costo_mensual_soles}; "
                        f"institución {c.detalles.get('gestion', 'sin gestión registrada')}"
                    )
                )
                for c in carreras
            ]
            texto = {
                7: "¿Qué entorno de formación prefieres?",
                8: "¿Qué propuesta de formación quieres revisar primero?",
                9: "¿Qué condiciones institucionales se ajustan mejor a tus prioridades?",
            }[indice]
            contexto = (
                "El catálogo no distingue contenidos suficientes para esta "
                "pregunta; se contrastan condiciones registradas. Confirma la "
                "oferta y la malla oficial."
            )
        else:
            textos = [
                f"{c.nombre} · {c.institucion}: {valor}"
                for c, valor in zip(carreras, valores, strict=True)
            ]
            contexto = "Contenido sintetizado del catálogo; consulta las fuentes de ambas fichas."
        opciones = tuple(
            OpcionVocacional(c.id, valor) for c, valor in zip(carreras, textos, strict=True)
        ) + (
            OpcionVocacional("ambas", "Ambas me interesan"),
            OpcionVocacional("ninguna", "Ninguna me interesa"),
            OpcionVocacional("incierto", "No estoy seguro"),
        )
        dinamicas.append(
            PreguntaVocacional(f"p{indice}", "Comparación personalizada", texto, opciones, contexto)
        )
    prioridad = PreguntaVocacional(
        "p10",
        "Tu prioridad",
        "¿Qué es lo más importante para ti al elegir una carrera?",
        tuple(
            OpcionVocacional(clave, texto)
            for clave, texto in [
                ("interes", "Estudiar algo que realmente me guste"),
                ("empleo", "Tener buenas oportunidades laborales"),
                ("costo", "Que el costo esté dentro de mi presupuesto"),
                ("duracion", "Terminar mis estudios en menos tiempo"),
                ("incierto", "Todavía no estoy seguro"),
            ]
        ),
    )
    return {
        "version": VERSION_CUESTIONARIO,
        "programas": [
            {"id": c.id, "nombre": c.nombre, "institucion": c.institucion} for c in carreras
        ],
        "preguntas": [asdict(p) for p in (*preguntas_generales(), *dinamicas, prioridad)],
        "aviso": (
            "Orientación comparativa, no un instrumento psicológico validado. "
            "No garantiza resultados académicos ni laborales."
        ),
    }


def validar_respuestas(cuestionario, respuestas, preferencias):
    if set(respuestas) != {f"p{i}" for i in range(1, 11)}:
        raise ValueError("Responde exactamente las 10 preguntas")
    for pregunta in cuestionario["preguntas"]:
        if respuestas[pregunta["id"]] not in {opcion["id"] for opcion in pregunta["opciones"]}:
            raise ValueError("Respuesta no válida para el cuestionario actual")
    for campo in ("presupuesto_maximo", "duracion_maxima"):
        valor = preferencias.get(campo)
        if valor is not None and (
            isinstance(valor, bool)
            or not isinstance(valor, (float, int))
            or not isfinite(valor)
            or valor < (1 if campo == "duracion_maxima" else 0)
        ):
            raise ValueError("Preferencia numérica fuera de rango")
