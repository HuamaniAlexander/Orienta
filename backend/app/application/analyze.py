from app.application.catalog import CareerNotFound, Catalog
from app.application.compare import CompareCareers
from app.domain.criterion_analysis import analyze_criteria
from app.ports.analysis import AnalysisService
from app.ports.recommendations import RecommendationService


class AnalyzeComparison:
    def __init__(
        self,
        catalog: Catalog,
        service: AnalysisService,
        recommender: RecommendationService | None = None,
    ):
        self.catalog, self.service = catalog, service
        self.recommender = recommender

    def execute(self, ids: list[str], preferences=None):
        comparison = CompareCareers(self.catalog).execute(ids)
        result = self.service.analyze(comparison.left, comparison.right)
        related = []
        for id in result.pop("related_ids"):
            if id in ids:
                continue
            try:
                related.append(self.catalog.detail(id))
                if len(related) == 3:
                    break
            except CareerNotFound:
                continue
        criteria = analyze_criteria(comparison.left, comparison.right)
        status = {
            "status": "awaiting_reviewed_labels",
            "quality_target": 0.90,
            "quality_approved": False,
            "message": "Recomendaciones aprendidas pendientes de revisión y evaluación; "
            "las orientaciones actuales se basan en los datos de las fichas.",
        }
        if self.recommender:
            status, predictions = self.recommender.analyze(
                comparison.left, comparison.right, preferences or {}
            )
            for item in criteria:
                label = predictions.get(item["key"])
                item["learned_label"] = label
                if label:
                    item["recommendation"] = (
                        {
                            "favor_left": f"Según tus preferencias: {item['left_label']}.",
                            "favor_right": f"Según tus preferencias: {item['right_label']}.",
                            "equivalent": "El modelo no identifica una ventaja en este criterio.",
                            "needs_preference": "Indica la preferencia que falta "
                            "para valorar este criterio.",
                            "insufficient_data": "Confirma la información que falta.",
                        }[label]
                        + " "
                        + item["recommendation"]
                    )
        return result | {
            "recommendations": related[:3],
            "criteria_analysis": criteria,
            "next_steps": [item["recommendation"] for item in criteria],
            "explanation_kind": "learned_with_grounded_explanation"
            if status["quality_approved"]
            else "structured",
            "recommendation_training": status,
        }
