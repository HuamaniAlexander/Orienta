from app.application.catalog import CareerNotFound, Catalog
from app.application.compare import CompareCareers
from app.domain.criterion_analysis import analyze_criteria
from app.ports.analysis import AnalysisService


class AnalyzeComparison:
    def __init__(self, catalog: Catalog, service: AnalysisService):
        self.catalog, self.service = catalog, service

    def execute(self, ids: list[str]):
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
        return result | {
            "recommendations": related[:3],
            "criteria_analysis": criteria,
            "next_steps": [item["recommendation"] for item in criteria],
            "explanation_kind": "structured",
        }
