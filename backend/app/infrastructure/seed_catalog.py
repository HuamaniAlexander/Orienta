"""Load the documented versioned catalog into PostgreSQL, without requiring Downloads."""

from hashlib import sha256
from pathlib import Path

from app.adapters.output.importer import import_careers
from app.adapters.output.repositories import JsonCareerRepository
from app.infrastructure.database import session_factory
from app.infrastructure.settings import Settings


def main():
    settings = Settings()
    path = Path(__file__).resolve().parents[2] / "data/catalog.json"
    careers = JsonCareerRepository(path).careers
    with session_factory(settings)() as session:
        print(import_careers(careers, sha256(path.read_bytes()).hexdigest(), path.name, session))


if __name__ == "__main__":
    main()
