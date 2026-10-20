"""Run from backend: python -m app.infrastructure.import_excel path.xlsx [--snapshot path]."""

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from app.adapters.output.excel import read_careers
from app.adapters.output.importer import import_workbook
from app.infrastructure.database import session_factory
from app.infrastructure.settings import Settings


def main():
    parser = argparse.ArgumentParser(description="Importar catálogo PoC validado")
    parser.add_argument("workbook", type=Path)
    parser.add_argument("--snapshot", type=Path, help="Exportar solo una demo; no escribe en BD")
    args = parser.parse_args()
    if args.snapshot:
        careers = read_careers(args.workbook)
        args.snapshot.parent.mkdir(parents=True, exist_ok=True)
        args.snapshot.write_text(
            json.dumps([asdict(c) for c in careers], ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        print(f"Demo: {len(careers)} ofertas; no se escribió en PostgreSQL")
    else:
        with session_factory(Settings())() as session:
            print(import_workbook(args.workbook, session))


if __name__ == "__main__":
    main()
