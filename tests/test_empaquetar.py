"""Pruebas del empaquetado para el hosting (solo librería estándar): `python3 -m unittest discover -s tests`.
Lo publicado debe ser el sitio y NADA más: ni el código fuente, ni las guías internas, ni las pruebas."""
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import empaquetar  # noqa: E402


class Empaquetar(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="empaquetar_"))
        self.origen = self.tmp / "sitio"
        self.destino = self.tmp / "dist"
        for ruta, texto in {
            "index.html": "i", "404.html": "x", "robots.txt": "r", "sitemap.xml": "s", "_headers": "h",
            "contacto/index.html": "c", "assets/css/propio.css": "a", "assets/js/config.js": "j",
            # lo que NO debe publicarse
            "AGENTS.md": "a", "README.md": "r", "ver_sitio.command": "v", ".gitignore": "g", ".env": "secreto",
            "src/sitio.json": "{}", "docs/specs/0001.md": "d", "tests/test_x.py": "t", "scripts/construir.py": "c",
            "data/README.md": "d", "node_modules/x/index.js": "n", "__pycache__/a.pyc": "p", ".git/config": "g",
            "dist/viejo.txt": "v",
        }.items():
            f = self.origen / ruta
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(texto)

    def publicados(self):
        return sorted(str(p.relative_to(self.destino)) for p in self.destino.rglob("*") if p.is_file())

    def test_publica_solo_el_sitio(self):
        empaquetar.empaquetar(self.origen, self.destino)
        self.assertEqual(self.publicados(), [
            "404.html", "_headers", "assets/css/propio.css", "assets/js/config.js",
            "contacto/index.html", "index.html", "robots.txt", "sitemap.xml"])

    def test_vuelve_a_empezar_limpio(self):
        self.destino.mkdir()
        (self.destino / "sobrante.html").write_text("de una publicación anterior")
        empaquetar.empaquetar(self.origen, self.destino)
        self.assertNotIn("sobrante.html", self.publicados())

    def test_falla_si_falta_el_inicio(self):
        (self.origen / "index.html").unlink()
        with self.assertRaises(SystemExit):
            empaquetar.empaquetar(self.origen, self.destino)


if __name__ == "__main__":
    unittest.main()
