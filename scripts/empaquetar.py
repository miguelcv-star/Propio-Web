#!/usr/bin/env python3
"""Arma `dist/` con SOLO lo que se publica en el hosting estático (solo librería estándar).

    python3 scripts/empaquetar.py        # deja el sitio listo en dist/

Las páginas ya están generadas y versionadas (`scripts/construir.py`), así que aquí solo se copia. Quedan fuera el
código fuente (`src/`), las guías y especificaciones (`AGENTS.md`, `docs/`), las pruebas, los scripts y todo archivo
oculto: en un hosting público cualquier archivo se puede pedir por su dirección."""
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CARPETAS_FUERA = {"src", "docs", "tests", "scripts", "data", "node_modules", "__pycache__", "dist"}
ARCHIVOS_FUERA = {"AGENTS.md", "README.md"}
EXTENSIONES_FUERA = {".command", ".md", ".py", ".pyc", ".log"}
# Los archivos con punto inicial no se publican, salvo estos (no hay ninguno hoy).
OCULTOS_PERMITIDOS: set[str] = set()


def _publicable(p: Path) -> bool:
    if p.name.startswith(".") and p.name not in OCULTOS_PERMITIDOS:
        return False
    if p.is_dir():
        return p.name not in CARPETAS_FUERA
    return p.name not in ARCHIVOS_FUERA and p.suffix not in EXTENSIONES_FUERA


def empaquetar(origen: Path = RAIZ, destino: Path | None = None) -> Path:
    destino = destino or origen / "dist"
    if not (origen / "index.html").is_file():
        sys.exit("Falta index.html: ¿se generó el sitio? (python3 scripts/construir.py)")
    if destino.exists():
        shutil.rmtree(destino)
    destino.mkdir(parents=True)
    ignorar = lambda carpeta, nombres: [n for n in nombres if not _publicable(Path(carpeta) / n)]  # noqa: E731
    for p in sorted(origen.iterdir()):
        if not _publicable(p):
            continue
        if p.is_dir():
            shutil.copytree(p, destino / p.name, ignore=ignorar)
        else:
            shutil.copy2(p, destino / p.name)
    return destino


if __name__ == "__main__":
    salida = empaquetar()
    n = sum(1 for f in salida.rglob("*") if f.is_file())
    print(f"Listo: {n} archivos en {salida}")
