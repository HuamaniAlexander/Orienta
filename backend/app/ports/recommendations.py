from typing import Protocol

from app.domain.career import Career


class RecommendationService(Protocol):
    def analyze(self, left: Career, right: Career, preferences: dict) -> tuple[dict, dict]: ...
