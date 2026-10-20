"""Pure recommendation vocabulary, predictors and quality policy."""

CRITERIA = ("duration", "modality", "location", "cost", "requirements", "employment")
LABELS = ("favor_left", "favor_right", "equivalent", "needs_preference", "insufficient_data")


def features(row):
    # Identity, evidence, rationale and reviewer decisions are NOT predictors.
    result = {}
    for side in ("left", "right"):
        value = row[f"{side}_value"]
        result[f"{side}_missing"] = int(value is None or value == "")
        if value is not None:
            if row["criterion"] in ("duration", "cost"):
                result[f"{side}_number"] = float(value)
            else:
                for token in str(value).casefold().split():
                    result[f"{side}_token={token}"] = 1
    for key, value in sorted(row.get("preferences", {}).items()):
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            result[f"preference_{key}"] = float(value)
        elif isinstance(value, str):
            result[f"preference_{key}={value.casefold()}"] = 1
    return result


def approved(scores):
    return all(
        scores[k] > 0.90 for k in ("accuracy", "precision_macro", "recall_macro", "f1_macro")
    )
