"""Vocabulario, predictores y política de calidad de las recomendaciones."""

CRITERIOS = ("duration", "modality", "location", "cost", "requirements", "employment")
ETIQUETAS = ("favor_left", "favor_right", "equivalent", "needs_preference", "insufficient_data")


def caracteristicas(fila):
    # Identidad, evidencia, motivos y decisiones de revisión no son predictores.
    resultado = {}
    for lado in ("left", "right"):
        valor = fila[f"{lado}_value"]
        resultado[f"{lado}_missing"] = int(valor is None or valor == "")
        if valor is not None:
            if fila["criterion"] in ("duration", "cost"):
                resultado[f"{lado}_number"] = float(valor)
            else:
                for token in str(valor).casefold().split():
                    resultado[f"{lado}_token={token}"] = 1
    for clave, valor in sorted(fila.get("preferences", {}).items()):
        if isinstance(valor, (int, float)) and not isinstance(valor, bool):
            resultado[f"preference_{clave}"] = float(valor)
        elif isinstance(valor, str):
            resultado[f"preference_{clave}={valor.casefold()}"] = 1
    return resultado


def cumple_umbral(puntuaciones):
    return all(
        puntuaciones[k] > 0.90 for k in ("accuracy", "precision_macro", "recall_macro", "f1_macro")
    )
