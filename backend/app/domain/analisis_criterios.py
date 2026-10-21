"""Contraste documentado de seis criterios, independiente del rendimiento del modelo."""

from dataclasses import asdict, dataclass

from app.domain.carrera import Carrera, normalizar
from app.domain.institucion import etiqueta_carrera


@dataclass(frozen=True)
class AnalisisCriterio:
    clave: str
    etiqueta: str
    etiqueta_izquierda: str
    etiqueta_derecha: str
    valor_izquierda: str
    valor_derecha: str
    relacion: str
    explicacion: str
    recomendacion: str
    motivo: str
    advertencias: tuple[str, ...]


def analizar_criterios(izquierda: Carrera, derecha: Carrera) -> list[dict]:
    etiqueta_izquierda, etiqueta_derecha = etiqueta_carrera(izquierda), etiqueta_carrera(derecha)

    def presentar(valor):
        return (
            str(valor).strip() if valor is not None and str(valor).strip() else "Dato no disponible"
        )

    def criterio(clave, etiqueta, a, b, recomendacion, unidad="", adicionales=()):
        faltante = a is None or b is None or not presentar(a).strip() or not presentar(b).strip()
        faltante = (
            faltante or presentar(a) == "Dato no disponible" or presentar(b) == "Dato no disponible"
        )
        iguales = not faltante and normalizar(str(a)) == normalizar(str(b))
        av, bv = presentar(a), presentar(b)
        numerico = clave in ("duration", "cost")
        if numerico:
            av = (
                "Dato no disponible"
                if a is None
                else f"{a:,.2f} {unidad}"
                if clave == "cost"
                else f"{a} {unidad}"
            )
            bv = (
                "Dato no disponible"
                if b is None
                else f"{b:,.2f} {unidad}"
                if clave == "cost"
                else f"{b} {unidad}"
            )
        if faltante:
            explicacion = (
                f"No se puede completar el contraste de {etiqueta.lower()}: "
                "falta información en una o ambas alternativas."
            )
        elif iguales:
            explicacion = f"Ambas alternativas registran el mismo dato de {etiqueta.lower()}: {av}."
        elif numerico:
            diferencia = b - a
            diferencia_absoluta = (
                f"{abs(diferencia):,.2f}" if clave == "cost" else str(abs(diferencia))
            )
            explicacion = (
                f"{etiqueta_izquierda} registra {av}; {etiqueta_derecha} registra {bv}. "
                f"{etiqueta_derecha} tiene {diferencia_absoluta} {unidad} "
                f"{'más' if diferencia > 0 else 'menos'} "
                f"que {etiqueta_izquierda}."
            )
        else:
            explicacion = f"{etiqueta_izquierda} indica «{av}»; {etiqueta_derecha} indica «{bv}»."
        advertencias = list(adicionales)
        for prefijo, carrera in [(etiqueta_izquierda, izquierda), (etiqueta_derecha, derecha)]:
            campo = {
                "duration": "Duración",
                "modality": "Modalidad",
                "location": "Ubicación",
                "cost": "Costo",
                "requirements": "Requisitos",
                "employment": "Campo laboral",
            }[clave]
            fuente = next((s for s in carrera.fuentes if s.campo == campo), None)
            if fuente:
                advertencias.append(f"{prefijo}: {fuente.estado}")
        return asdict(
            AnalisisCriterio(
                clave,
                etiqueta,
                etiqueta_izquierda,
                etiqueta_derecha,
                av,
                bv,
                "missing" if faltante else "same" if iguales else "different",
                explicacion,
                recomendacion,
                {
                    "duration": "La duración afecta el tiempo de formación; la carga semanal "
                    "y los requisitos de egreso pueden cambiar la fecha real de finalización.",
                    "modality": "La modalidad determina condiciones de asistencia y recursos "
                    "que deben ser compatibles con tu disponibilidad.",
                    "location": "Los traslados consumen tiempo y presupuesto; la sede debe "
                    "confirmarse para la modalidad y carrera elegidas.",
                    "cost": "El importe mensual condiciona tu presupuesto, pero no incluye "
                    "necesariamente matrícula, materiales ni otros gastos.",
                    "requirements": "Los documentos y plazos de admisión determinan si puedes "
                    "postular; una descripción resumida no confirma elegibilidad.",
                    "employment": "Las actividades profesionales permiten contrastar tus "
                    "intereses; estas fichas no demuestran demanda laboral ni salarios.",
                }[clave],
                tuple(advertencias),
            )
        )

    consejo_duracion = (
        "Si necesitas terminar antes, revisa la opción de menor duración "
        "junto con su carga semanal y requisitos de egreso."
    )
    if izquierda.duracion_meses == derecha.duracion_meses:
        consejo_duracion = (
            "Con duración informada igual, compara horarios, carga semanal, "
            "prácticas y requisitos de egreso."
        )
    consejo_costo = (
        "Confirma matrícula, número de cuotas, materiales y gastos de "
        "traslado antes de calcular tu presupuesto total."
    )
    if izquierda.costo_mensual_soles is None or derecha.costo_mensual_soles is None:
        consejo_costo = (
            "Solicita el costo mensual de enseñanza que falta y su periodo; "
            "todavía no puedes comparar el presupuesto con este dato."
        )
    elif izquierda.costo_mensual_soles != derecha.costo_mensual_soles:
        menor_costo = (
            etiqueta_izquierda
            if izquierda.costo_mensual_soles < derecha.costo_mensual_soles
            else etiqueta_derecha
        )
        consejo_costo = (
            f"Si priorizas el presupuesto, {menor_costo} registra menor enseñanza mensual. "
            "Confirma condiciones, matrícula y gastos adicionales; "
            "menor importe no determina calidad."
        )
    return [
        criterio(
            "duration",
            "Duración",
            izquierda.duracion_meses,
            derecha.duracion_meses,
            consejo_duracion,
            "meses",
        ),
        criterio(
            "modality",
            "Modalidad",
            izquierda.modalidad,
            derecha.modalidad,
            (
                "Contrasta asistencia obligatoria, horarios y acceso a equipos e "
                "internet con tu disponibilidad."
            ),
        ),
        criterio(
            "location",
            "Ubicación / sede",
            izquierda.ubicacion,
            derecha.ubicacion,
            (
                "Para una sede física, estima tiempo y gasto de traslado; para una"
                " oferta virtual, confirma actividades presenciales y recursos "
                "necesarios."
            ),
        ),
        criterio(
            "cost",
            "Costo mensual de enseñanza",
            izquierda.costo_mensual_soles,
            derecha.costo_mensual_soles,
            consejo_costo,
            "PEN por mes",
            (
                (
                    "Se comparan importes mensuales de enseñanza, no el costo total de"
                    " estudiar. Las estimaciones no son tarifas oficiales."
                ),
            ),
        ),
        criterio(
            "requirements",
            "Requisitos de ingreso",
            izquierda.requisitos,
            derecha.requisitos,
            (
                "Haz una lista de documentos, fechas y proceso de admisión de cada"
                " institución; identifica qué requisitos ya cumples."
            ),
            adicionales=(
                (
                    "Se contrasta el texto registrado; una redacción distinta no "
                    "demuestra requisitos incompatibles."
                ),
            ),
        ),
        criterio(
            "employment",
            "Campo laboral",
            izquierda.campo_laboral,
            derecha.campo_laboral,
            (
                "Revisa la malla y las prácticas relacionadas con las actividades "
                "que te interesan; consulta egresados y evidencia de inserción "
                "laboral."
            ),
            adicionales=(
                (
                    "Las descripciones no permiten inferir salarios, demanda laboral "
                    "ni una garantía de empleo."
                ),
            ),
        ),
    ]
