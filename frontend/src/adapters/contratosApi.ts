// Traducir únicamente las claves del contrato existente en el borde HTTP.
const camposInternos: Record<string, string> = {
  "name": "nombre",
  "institution": "institucion",
  "training_type": "tipoFormacion",
  "modality": "modalidad",
  "location": "ubicacion",
  "duration_months": "duracionMeses",
  "monthly_cost_pen": "costoMensualSoles",
  "requirements": "requisitos",
  "employment": "campoLaboral",
  "reviewed_on": "fechaRevision",
  "sources": "fuentes",
  "field": "campo",
  "reference": "referencia",
  "status": "estado",
  "left": "izquierda",
  "right": "derecha",
  "duration_difference_months": "diferenciaDuracionMeses",
  "monthly_cost_difference_pen": "diferenciaCostoMensualSoles",
  "items": "elementos",
  "data_mode": "modoDatos",
  "career_ids": "idsCarreras",
  "criteria_analysis": "analisisCriterios",
  "explanation_kind": "tipoExplicacion",
  "quality_target": "umbralCalidad",
  "quality_approved": "calidadAprobada",
  "model_evaluations": "evaluacionesModelos",
  "prediction": "prediccion",
  "catalog_contrast": "contrasteCatalogo",
  "area_sources": "fuentesAreas",
  "agrees_with_catalog": "coincideCatalogo",
  "model_name": "nombreModelo",
  "model_version": "versionModelo",
  "metrics": "metricas",
  "baseline_accuracy": "exactitudReferencia",
  "training_pairs": "paresEntrenamiento",
  "test_pairs": "paresPrueba",
  "limitations": "limitaciones",
  "next_steps": "siguientesPasos",
  "recommendations": "recomendaciones",
  "recommendation_training": "entrenamientoRecomendaciones",
  "left_label": "etiquetaIzquierda",
  "right_label": "etiquetaDerecha",
  "left_value": "valorIzquierda",
  "right_value": "valorDerecha",
  "relationship": "relacion",
  "explanation": "explicacion",
  "recommendation": "recomendacion",
  "reason": "motivo",
  "caveats": "advertencias",
  "key": "clave",
  "label": "etiqueta",
  "preferences": "preferencias"
}
const camposExternos = Object.fromEntries(Object.entries(camposInternos).map(([externo, interno]) => [interno, externo]))
function traducirClaves(valor: unknown, campos: Record<string, string>): unknown {
  if (Array.isArray(valor)) return valor.map(elemento => traducirClaves(elemento, campos))
  if (valor !== null && typeof valor === 'object') return Object.fromEntries(
    Object.entries(valor).map(([clave, contenido]) => [campos[clave] || clave, clave === "detalles" ? contenido : traducirClaves(contenido, campos)]))
  return valor
}
export const internalizarRespuesta = <T,>(valor: unknown): T => traducirClaves(valor, camposInternos) as T
export const externalizarSolicitud = (valor: unknown): unknown => traducirClaves(valor, camposExternos)
