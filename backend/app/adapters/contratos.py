"""Compatibilidad de los contratos JSON existentes en los bordes de la aplicación."""

CAMPOS_EXTERNOS = {
    "nombre": "name",
    "institucion": "institution",
    "tipo_formacion": "training_type",
    "modalidad": "modality",
    "ubicacion": "location",
    "duracion_meses": "duration_months",
    "costo_mensual_soles": "monthly_cost_pen",
    "requisitos": "requirements",
    "campo_laboral": "employment",
    "fecha_revision": "reviewed_on",
    "fuentes": "sources",
    "activa": "active",
    "identidad": "identity",
    "campo": "field",
    "referencia": "reference",
    "estado": "status",
    "izquierda": "left",
    "derecha": "right",
    "diferencia_duracion_meses": "duration_difference_months",
    "diferencia_costo_mensual_soles": "monthly_cost_difference_pen",
    "nombre_busqueda": "search_name",
    "clave_identidad": "identity_key",
    "id_institucion": "institution_id",
    "id_importacion": "import_id",
    "id_oferta": "offer_id",
    "nombre_archivo": "filename",
    "fecha_importacion": "imported_at",
    "cantidad_filas": "row_count",
    "etiqueta_izquierda": "left_label",
    "etiqueta_derecha": "right_label",
    "valor_izquierda": "left_value",
    "valor_derecha": "right_value",
    "clave": "key",
    "etiqueta": "label",
    "relacion": "relationship",
    "explicacion": "explanation",
    "recomendacion": "recommendation",
    "motivo": "reason",
    "advertencias": "caveats",
    "etiqueta_aprendida": "learned_label",
    "ids_carreras": "career_ids",
    "elementos": "items",
    "modo_datos": "data_mode",
    "preferencias": "preferences",
    "presupuesto_soles": "budget_pen",
    "duracion_maxima_meses": "max_duration_months",
    "intereses_laborales": "employment_interests",
    "requisitos_cumplidos": "requirements_met",
    "analisis_criterios": "criteria_analysis",
    "tipo_explicacion": "explanation_kind",
    "umbral_calidad": "quality_target",
    "calidad_aprobada": "quality_approved",
    "evaluaciones_modelos": "model_evaluations",
    "prediccion": "prediction",
    "contraste_catalogo": "catalog_contrast",
    "fuentes_areas": "area_sources",
    "coincide_catalogo": "agrees_with_catalog",
    "nombre_modelo": "model_name",
    "version_modelo": "model_version",
    "metricas": "metrics",
    "exactitud_referencia": "baseline_accuracy",
    "pares_entrenamiento": "training_pairs",
    "pares_prueba": "test_pairs",
    "limitaciones": "limitations",
    "siguientes_pasos": "next_steps",
    "recomendaciones": "recommendations",
    "entrenamiento_recomendaciones": "recommendation_training",
}


def internalizar_registro(registro):
    if isinstance(registro, list):
        return [internalizar_registro(elemento) for elemento in registro]
    if isinstance(registro, dict):
        traducciones = {externo: interno for interno, externo in CAMPOS_EXTERNOS.items()}
        return {
            traducciones.get(clave, clave): internalizar_registro(valor)
            for clave, valor in registro.items()
        }
    return registro


def externalizar_registro(registro):
    if isinstance(registro, list):
        return [externalizar_registro(elemento) for elemento in registro]
    if isinstance(registro, dict):
        return {
            CAMPOS_EXTERNOS.get(clave, clave): externalizar_registro(valor)
            for clave, valor in registro.items()
        }
    return registro
