"""Pruebas del verificador y del generador (spec 0001). Solo librería estándar:
`python3 -m unittest discover -s tests`. Cada defecto se provoca en una COPIA del sitio ya construido y el
verificador tiene que señalarlo (así se comprueba que de verdad falla cuando debe)."""
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import construir  # noqa: E402
import verificar  # noqa: E402

RUTAS = ["/", "/vender-o-arrendar/", "/conocer-precio/", "/invertir-por-mi-cuenta/", "/empezar-a-invertir/",
         "/comprar-o-arrendar-para-mi/", "/oportunidades/", "/casos/", "/comunidad/", "/contacto/",
         "/privacidad/", "/terminos/", "/acuerdo-comision/"]


def _copiar() -> Path:
    destino = Path(tempfile.mkdtemp(prefix="aurexweb_"))
    for p in RAIZ.iterdir():
        if p.name in {"src", "docs", "tests", "scripts", ".git", "node_modules", "__pycache__"}:
            continue
        if p.is_dir():
            shutil.copytree(p, destino / p.name)
        else:
            shutil.copy2(p, destino / p.name)
    # el verificador lee la configuración (menú, aprobados) de src/sitio.json
    (destino / "src").mkdir()
    shutil.copy2(RAIZ / "src" / "sitio.json", destino / "src" / "sitio.json")
    return destino


def _pagina(raiz: Path, ruta: str) -> Path:
    return raiz / "index.html" if ruta == "/" else raiz / ruta.strip("/") / "index.html"


class Construccion(unittest.TestCase):
    def test_se_generan_todas_las_rutas_la_404_el_sitemap_y_robots(self):
        for ruta in RUTAS:
            self.assertTrue(_pagina(RAIZ, ruta).is_file(), ruta)
        for f in ("404.html", "sitemap.xml", "robots.txt"):
            self.assertTrue((RAIZ / f).is_file(), f)

    def test_lo_generado_esta_al_dia_con_src(self):
        self.assertEqual(construir.comprobar(), [])

    def test_detecta_una_pagina_generada_editada_a_mano(self):
        p = RAIZ / "contacto" / "index.html"
        original = p.read_text(encoding="utf-8")
        try:
            p.write_text(original.replace("<main", "<main data-a-mano", 1), encoding="utf-8")
            self.assertTrue(any("contacto" in e for e in construir.comprobar()))
        finally:
            p.write_text(original, encoding="utf-8")

    def test_el_sitemap_lista_todas_las_rutas_y_no_la_404(self):
        sm = (RAIZ / "sitemap.xml").read_text(encoding="utf-8")
        locs = re.findall(r"<loc>(.*?)</loc>", sm)
        self.assertEqual(len(locs), len(RUTAS))
        self.assertFalse(any("404" in l for l in locs))

    def test_las_intenciones_de_la_portada_llevan_la_intencion_en_la_url(self):
        html = _pagina(RAIZ, "/").read_text(encoding="utf-8")
        for slug in ["/vender-o-arrendar/", "/conocer-precio/", "/empezar-a-invertir/", "/comprar-o-arrendar-para-mi/"]:
            self.assertIn(f'href="{slug}?intencion={slug.strip("/")}"', html)


class SitioReal(unittest.TestCase):
    def test_el_sitio_construido_no_tiene_errores(self):
        self.assertEqual(verificar.verificar(RAIZ), [])

    def test_publicar_exige_dominio_e_indexacion_definidos(self):
        errores = verificar.verificar(RAIZ, publicar=True)
        self.assertTrue(any("url_base" in e for e in errores), errores)
        self.assertTrue(any("indexable" in e for e in errores), errores)

    def test_publicar_frena_si_quedan_textos_legales_en_borrador_o_la_api_sin_definir(self):
        errores = verificar.verificar(RAIZ, publicar=True)
        self.assertTrue(any("BORRADOR" in e for e in errores), errores)
        self.assertTrue(any("[RAZÓN SOCIAL]" in e or "entre corchetes" in e for e in errores), errores)
        self.assertTrue(any("config.js" in e and "por-definir" in e for e in errores), errores)


class Defectos(unittest.TestCase):
    """Cada caso rompe UNA cosa en una copia y el verificador debe nombrarla."""

    def setUp(self):
        self.raiz = _copiar()
        self.addCleanup(shutil.rmtree, self.raiz, True)

    def editar(self, ruta, f):
        p = _pagina(self.raiz, ruta)
        p.write_text(f(p.read_text(encoding="utf-8")), encoding="utf-8")

    def errores(self):
        return verificar.verificar(self.raiz)

    def assertDetecta(self, fragmento):
        errores = self.errores()
        self.assertTrue(any(fragmento in e for e in errores), f"no se detectó «{fragmento}»: {errores}")

    def test_estilo_en_linea(self):
        self.editar("/", lambda h: h.replace("<main", '<main style="color:red"', 1))
        self.assertDetecta("style en línea")

    def test_dos_h1(self):
        self.editar("/contacto/", lambda h: h.replace("</main>", "<h1>otro</h1></main>"))
        self.assertDetecta("h1")

    def test_sin_h1(self):
        self.editar("/contacto/", lambda h: re.sub(r"<h1.*?</h1>", "<p>x</p>", h, flags=re.S))
        self.assertDetecta("h1")

    def test_sin_description(self):
        self.editar("/casos/", lambda h: re.sub(r'<meta name="description"[^>]*>', "", h))
        self.assertDetecta("description")

    def test_title_duplicado(self):
        titulo = re.search(r"<title>(.*?)</title>", _pagina(self.raiz, "/").read_text(encoding="utf-8")).group(1)
        self.editar("/casos/", lambda h: re.sub(r"<title>.*?</title>", f"<title>{titulo}</title>", h))
        self.assertDetecta("duplicado")

    def test_sin_canonical(self):
        self.editar("/casos/", lambda h: re.sub(r'<link rel="canonical"[^>]*>', "", h))
        self.assertDetecta("canonical")

    def test_sin_open_graph(self):
        self.editar("/casos/", lambda h: re.sub(r'<meta property="og:image"[^>]*>', "", h))
        self.assertDetecta("og:image")

    def test_sin_lang_es(self):
        self.editar("/casos/", lambda h: h.replace('lang="es"', 'lang="en"'))
        self.assertDetecta("lang")

    def test_enlace_interno_roto(self):
        self.editar("/casos/", lambda h: h.replace("</main>", '<a href="/no-existe/">x</a></main>'))
        self.assertDetecta("enlace roto")

    def test_ancla_inexistente(self):
        self.editar("/casos/", lambda h: h.replace("</main>", '<a href="/#no-hay-esta-ancla">x</a></main>'))
        self.assertDetecta("ancla")

    def test_enlace_externo_sin_rel(self):
        self.editar("/casos/", lambda h: h.replace("</main>", '<a href="https://ejemplo.org">x</a></main>'))
        self.assertDetecta("noopener")

    def test_imagen_sin_alt(self):
        self.editar("/casos/", lambda h: h.replace("</main>", '<img src="/assets/img/favicon.ico" width="16" height="16"></main>'))
        self.assertDetecta("alt")

    def test_campo_sin_label(self):
        self.editar("/casos/", lambda h: h.replace("</main>", '<input type="text" id="solo"></main>'))
        self.assertDetecta("label")

    def test_script_externo(self):
        self.editar("/casos/", lambda h: h.replace("</body>", '<script src="https://cdn.ejemplo.com/a.js" defer></script></body>'))
        self.assertDetecta("externo")

    def test_script_sin_defer(self):
        self.editar("/casos/", lambda h: h.replace("</body>", '<script src="/assets/js/menu.js"></script></body>'))
        self.assertDetecta("defer")

    def test_script_en_linea(self):
        self.editar("/casos/", lambda h: h.replace("</body>", "<script>var a=1</script></body>"))
        self.assertDetecta("en línea")

    def test_dos_hojas_de_estilo(self):
        self.editar("/casos/", lambda h: h.replace("</head>", '<link rel="stylesheet" href="/assets/css/propio.css"></head>'))
        self.assertDetecta("hoja de estilo")

    def test_sin_enlace_saltar_al_contenido(self):
        self.editar("/casos/", lambda h: re.sub(r'<a class="saltar".*?</a>', "", h, flags=re.S))
        self.assertDetecta("saltar")

    def test_pagina_fuera_del_sitemap(self):
        sm = self.raiz / "sitemap.xml"
        sm.write_text(re.sub(r"<url><loc>[^<]*casos/</loc></url>\s*", "", sm.read_text(encoding="utf-8")), encoding="utf-8")
        self.assertDetecta("sitemap")

    def test_falta_la_404(self):
        (self.raiz / "404.html").unlink()
        self.assertDetecta("404")

    def test_pagina_demasiado_pesada(self):
        css = self.raiz / "assets" / "css" / "propio.css"
        css.write_text(css.read_text(encoding="utf-8") + "/*" + "x" * 200_000 + "*/", encoding="utf-8")
        self.assertDetecta("pesa")

    def test_secreto_en_el_codigo(self):
        js = self.raiz / "assets" / "js" / "menu.js"
        js.write_text(js.read_text(encoding="utf-8") + '\nconst api_key = "abc123";\n', encoding="utf-8")
        self.assertDetecta("secreto")

    def test_referencia_a_la_api_de_aurex(self):
        js = self.raiz / "assets" / "js" / "menu.js"
        js.write_text(js.read_text(encoding="utf-8") + '\nfetch("http://localhost:8000/inmuebles");\n', encoding="utf-8")
        self.assertDetecta("Aurex")

    def test_sin_respeto_a_reduced_motion(self):
        css = self.raiz / "assets" / "css" / "propio.css"
        css.write_text(css.read_text(encoding="utf-8").replace("prefers-reduced-motion", "prefers-otra-cosa"), encoding="utf-8")
        self.assertDetecta("reduced-motion")

    def test_contraste_insuficiente_en_los_tokens(self):
        css = self.raiz / "assets" / "css" / "propio.css"
        css.write_text(re.sub(r"--text-muted:\s*#[0-9a-fA-F]{6}", "--text-muted: #bbbbbb", css.read_text(encoding="utf-8")), encoding="utf-8")
        self.assertDetecta("contraste")

    def test_json_de_datos_con_clave_prohibida(self):
        (self.raiz / "data" / "x.json").write_text(json.dumps({"schema_version": 1, "generado_en": "2026-10-15T00:00:00-05:00", "telefono": "300"}), encoding="utf-8")
        self.assertDetecta("telefono")


class PropioApi(unittest.TestCase):
    """El sitio solo habla con las rutas públicas de Propio (spec 0010)."""

    def test_los_formularios_solo_llaman_a_rutas_publicas(self):
        rutas = set()
        for js in (RAIZ / "assets" / "js").glob("*.js"):
            rutas |= set(re.findall(r"""["'](/publico/[a-z/_]+)""", js.read_text(encoding="utf-8")))
        self.assertTrue(rutas)
        self.assertEqual(sorted(rutas), sorted({"/publico/contacto", "/publico/busqueda", "/publico/busqueda/pdf",
                                                "/publico/valorar", "/publico/vender", "/publico/inmuebles",
                                                "/publico/cifras"}))

    def test_la_configuracion_no_lleva_secretos_ni_localhost(self):
        cfg = (RAIZ / "assets" / "js" / "config.js").read_text(encoding="utf-8")
        self.assertNotIn("localhost", cfg)
        self.assertEqual(verificar.verificar(RAIZ), [])

    def test_cada_pagina_con_formulario_carga_sus_scripts(self):
        for ruta in ("/empezar-a-invertir/", "/invertir-por-mi-cuenta/", "/comprar-o-arrendar-para-mi/",
                     "/conocer-precio/", "/vender-o-arrendar/"):
            html = _pagina(RAIZ, ruta).read_text(encoding="utf-8")
            for js in ("config.js", "lib.js", "formularios.js"):
                self.assertIn(f'<script src="/assets/js/{js}" defer></script>', html, f"{ruta} {js}")
            self.assertIn('data-propio-form="', html)
            self.assertIn('name="sitio_web"', html)           # honeypot
            self.assertIn('name="consentimiento"', html)

    def test_el_formulario_de_vender_pide_el_acuerdo_de_comision(self):
        html = _pagina(RAIZ, "/vender-o-arrendar/").read_text(encoding="utf-8")
        self.assertIn('name="acepta_comision"', html)
        self.assertIn('href="/acuerdo-comision/"', html)


class Contraste(unittest.TestCase):
    def test_razones_conocidas(self):
        self.assertGreater(verificar.contraste("#1a1a1a", "#fafaf7"), 15)
        self.assertLess(verificar.contraste("#a8a59f", "#fafaf7"), 3)
        self.assertAlmostEqual(verificar.contraste("#000000", "#ffffff"), 21.0, places=1)


if __name__ == "__main__":
    unittest.main()
