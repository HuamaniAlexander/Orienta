"""Grounded six-criterion contrast, independent of probabilistic model performance."""

from dataclasses import asdict, dataclass

from app.domain.career import Career, normalize
from app.domain.institution import career_label


@dataclass(frozen=True)
class CriterionAnalysis:
    key: str
    label: str
    left_label: str
    right_label: str
    left_value: str
    right_value: str
    relationship: str
    explanation: str
    recommendation: str
    reason: str
    caveats: tuple[str, ...]


def analyze_criteria(left: Career, right: Career) -> list[dict]:
    left_label, right_label = career_label(left), career_label(right)

    def present(value):
        return (
            str(value).strip() if value is not None and str(value).strip() else "Dato no disponible"
        )

    def criterion(key, label, a, b, recommendation, unit="", extra=()):
        missing = a is None or b is None or not present(a).strip() or not present(b).strip()
        missing = (
            missing or present(a) == "Dato no disponible" or present(b) == "Dato no disponible"
        )
        same = not missing and normalize(str(a)) == normalize(str(b))
        av, bv = present(a), present(b)
        numeric = key in ("duration", "cost")
        if numeric:
            av = (
                "Dato no disponible"
                if a is None
                else f"{a:,.2f} {unit}"
                if key == "cost"
                else f"{a} {unit}"
            )
            bv = (
                "Dato no disponible"
                if b is None
                else f"{b:,.2f} {unit}"
                if key == "cost"
                else f"{b} {unit}"
            )
        if missing:
            explanation = (
                f"No se puede completar el contraste de {label.lower()}: "
                "falta información en una o ambas alternativas."
            )
        elif same:
            explanation = f"Ambas alternativas registran el mismo dato de {label.lower()}: {av}."
        elif numeric:
            delta = b - a
            difference = f"{abs(delta):,.2f}" if key == "cost" else str(abs(delta))
            explanation = (
                f"{left_label} registra {av}; {right_label} registra {bv}. "
                f"{right_label} tiene {difference} {unit} {'más' if delta > 0 else 'menos'} "
                f"que {left_label}."
            )
        else:
            explanation = f"{left_label} indica «{av}»; {right_label} indica «{bv}»."
        caveats = list(extra)
        for prefix, career in [(left_label, left), (right_label, right)]:
            field = {
                "duration": "Duración",
                "modality": "Modalidad",
                "location": "Ubicación",
                "cost": "Costo",
                "requirements": "Requisitos",
                "employment": "Campo laboral",
            }[key]
            source = next((s for s in career.sources if s.field == field), None)
            if source:
                caveats.append(f"{prefix}: {source.status}")
        return asdict(
            CriterionAnalysis(
                key,
                label,
                left_label,
                right_label,
                av,
                bv,
                "missing" if missing else "same" if same else "different",
                explanation,
                recommendation,
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
                }[key],
                tuple(caveats),
            )
        )

    duration_tip = (
        "Si necesitas terminar antes, revisa la opción de menor duración "
        "junto con su carga semanal y requisitos de egreso."
    )
    if left.duration_months == right.duration_months:
        duration_tip = (
            "Con duración informada igual, compara horarios, carga semanal, "
            "prácticas y requisitos de egreso."
        )
    cost_tip = (
        "Confirma matrícula, número de cuotas, materiales y gastos de "
        "traslado antes de calcular tu presupuesto total."
    )
    if left.monthly_cost_pen is None or right.monthly_cost_pen is None:
        cost_tip = (
            "Solicita el costo mensual de enseñanza que falta y su periodo; "
            "todavía no puedes comparar el presupuesto con este dato."
        )
    elif left.monthly_cost_pen != right.monthly_cost_pen:
        cheaper = left_label if left.monthly_cost_pen < right.monthly_cost_pen else right_label
        cost_tip = (
            f"Si priorizas el presupuesto, {cheaper} registra menor enseñanza mensual. "
            "Confirma condiciones, matrícula y gastos adicionales; "
            "menor importe no determina calidad."
        )
    return [
        criterion(
            "duration",
            "Duración",
            left.duration_months,
            right.duration_months,
            duration_tip,
            "meses",
        ),
        criterion(
            "modality",
            "Modalidad",
            left.modality,
            right.modality,
            (
                "Contrasta asistencia obligatoria, horarios y acceso a equipos e "
                "internet con tu disponibilidad."
            ),
        ),
        criterion(
            "location",
            "Ubicación / sede",
            left.location,
            right.location,
            (
                "Para una sede física, estima tiempo y gasto de traslado; para una"
                " oferta virtual, confirma actividades presenciales y recursos "
                "necesarios."
            ),
        ),
        criterion(
            "cost",
            "Costo mensual de enseñanza",
            left.monthly_cost_pen,
            right.monthly_cost_pen,
            cost_tip,
            "PEN por mes",
            (
                (
                    "Se comparan importes mensuales de enseñanza, no el costo total de"
                    " estudiar. Las estimaciones no son tarifas oficiales."
                ),
            ),
        ),
        criterion(
            "requirements",
            "Requisitos de ingreso",
            left.requirements,
            right.requirements,
            (
                "Haz una lista de documentos, fechas y proceso de admisión de cada"
                " institución; identifica qué requisitos ya cumples."
            ),
            extra=(
                (
                    "Se contrasta el texto registrado; una redacción distinta no "
                    "demuestra requisitos incompatibles."
                ),
            ),
        ),
        criterion(
            "employment",
            "Campo laboral",
            left.employment,
            right.employment,
            (
                "Revisa la malla y las prácticas relacionadas con las actividades "
                "que te interesan; consulta egresados y evidencia de inserción "
                "laboral."
            ),
            extra=(
                (
                    "Las descripciones no permiten inferir salarios, demanda laboral "
                    "ni una garantía de empleo."
                ),
            ),
        ),
    ]
