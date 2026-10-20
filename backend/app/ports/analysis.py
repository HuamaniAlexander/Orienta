from typing import Protocol

from app.domain.career import Career


class AnalysisUnavailable(Exception):
    pass


class AnalysisService(Protocol):
    def analyze(self, left: Career, right: Career) -> dict: ...
