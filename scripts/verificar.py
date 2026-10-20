#!/usr/bin/env python3
"""Verificador del sitio publicado (spec 0001). Solo librería estándar.

    python3 scripts/verificar.py              # revisa el sitio construido (y que esté al día con src/)
    python3 scripts/verificar.py --publicar   # además exige dominio e indexación definidos

Es la «prueba» de las specs: nada se publica si devuelve errores. Revisa lo que se SIRVE (HTML, CSS, JS,
datos), no src/, docs/ ni tests/.
"""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parent.parent
IGNORAR = {"src", "docs", "tests", "scripts", ".git", "node_modules", "__pycache__", "dist"}
CLAVES_PROHIBIDAS = {"telefono", "teléfono", "email", "correo", "nota", "notas", "usuario", "username", "token",
                     "password", "contrasena", "contacto", "anunciante", "whatsapp"}
CLAVES_COORDENADAS = {"lat", "lon", "lng", "latitud", "longitud", "latitude", "longitude"}
PATRONES_SECRETO = [
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "llave privada"),
    (re.compile(r"""(?i)\b(api[_-]?key|secret|passw(?:or)?d|token|authorization)\b\s*[:=]\s*['"][^'"\s]{4,}['"]"""), "asignación de credencial"),
    (re.compile(r"(?i)postgres(?:ql)?://"), "cadena de conexión a Postgres"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "llave de AWS"),
]
PATRON_AUREX = re.compile(r"(?i)localhost|127\.0\.0\.1|\[::1\]|:8000\b|03_dev_Aurex|/inmuebles/|/oportunidades/\d|postgres")
TOPE_DATOS_KB = 200
PARES_CONTRASTE = [("--text", "--bg"), ("--text", "--bg-elev"), ("--text-muted", "--bg"), ("--text-muted", "--bg-elev"),
                   ("--text-faint", "--bg"), ("--accent-on", "--accent"), ("--success", "--success-bg"),
                   ("--danger", "--danger-bg"), ("--warn", "--warn-bg")]


def _luminancia(hexa: str) -> float:
    h = hexa.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contraste(a: str, b: str) -> float:
    la, lb = sorted((_luminancia(a), _luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


class _Pagina(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang = None; self.title = ""; self.metas = {}; self.links = []; self.enlaces = []
        self.h1 = 0; self.scripts = []; self.estilos = []; self.imgs = []; self.ids = set()
        self.campos = []; self.labels_for = set(); self._en_label = 0; self._en_title = False
        self._en_body = False; self.primer_enlace = None; self.canonical = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a: self.ids.add(a["id"])
        if tag == "html": self.lang = a.get("lang")
        elif tag == "title": self._en_title = True
        elif tag == "body": self._en_body = True
        elif tag == "meta":
            clave = a.get("name") or a.get("property")
            if clave: self.metas[clave] = a.get("content", "")
        elif tag == "link":
            rel = (a.get("rel") or "").lower()
            if rel == "canonical": self.canonical = a.get("href")
            if rel == "stylesheet": self.estilos.append(a.get("href", ""))
            self.links.append((rel, a.get("href", "")))
        elif tag == "h1": self.h1 += 1
        elif tag == "script": self.scripts.append((a.get("src"), "defer" in a, a.get("type", "")))
        elif tag == "img": self.imgs.append((a.get("src", ""), "alt" in a))
        elif tag == "a":
            self.enlaces.append((a.get("href", ""), (a.get("rel") or ""), a.get("target")))
            if self._en_body and self.primer_enlace is None: self.primer_enlace = a
        elif tag == "label":
            self._en_label += 1
            if a.get("for"): self.labels_for.add(a["for"])
        elif tag in ("input", "select", "textarea"):
            if a.get("type", "text") not in ("hidden", "submit", "button", "reset", "image"):
                self.campos.append({"id": a.get("id"), "aria": a.get("aria-label") or a.get("aria-labelledby"), "en_label": self._en_label > 0})

    def handle_endtag(self, tag):
        if tag == "title": self._en_title = False
        elif tag == "label" and self._en_label: self._en_label -= 1

    def handle_data(self, d):
        if self._en_title: self.title += d


def _leer(p: Path) -> _Pagina:
    pg = _Pagina(); pg.feed(p.read_text(encoding="utf-8")); return pg


def _paginas(raiz: Path) -> dict:
    """{ruta: archivo} de las páginas HTML servidas."""
    out = {}
    if (raiz / "index.html").is_file(): out["/"] = raiz / "index.html"
    if (raiz / "404.html").is_file(): out["/404.html"] = raiz / "404.html"
    for d in sorted(raiz.iterdir()):
        if d.is_dir() and d.name not in IGNORAR and d.name not in ("assets", "data") and (d / "index.html").is_file():
            out[f"/{d.name}/"] = d / "index.html"
    return out


def _archivo_de(raiz: Path, ruta: str) -> Path:
    p = raiz / ruta.lstrip("/")
    return p / "index.html" if ruta.endswith("/") or ruta == "" else p


def _servidos(raiz: Path):
    for p in raiz.rglob("*"):
        rel = p.relative_to(raiz)
        if p.is_file() and rel.parts[0] not in IGNORAR and rel.suffix in {".html", ".js", ".css", ".json", ".xml", ".txt"} \
                and p.name != ".construido.json":
            yield p


def _tokens(css: str) -> dict:
    toks = {}
    for bloque in re.findall(r":root\s*\{(.*?)\}", css, flags=re.S):
        for k, v in re.findall(r"(--[\w-]+)\s*:\s*(#[0-9a-fA-F]{6})\b", bloque):
            toks[k] = v
    return toks


def _revisar_datos(raiz: Path, errores: list):
    def recorrer(x, ruta):
        if isinstance(x, dict):
            for k, v in x.items():
                kl = k.lower()
                if kl in CLAVES_PROHIBIDAS:
                    errores.append(f"{ruta}: clave prohibida «{k}» (dato privado en un archivo público)")
                if kl in CLAVES_COORDENADAS and isinstance(v, float) and len(repr(v).split(".")[-1]) > 3:
                    errores.append(f"{ruta}: coordenada «{k}» con más de 3 decimales (revela la ubicación exacta)")
                recorrer(v, ruta)
        elif isinstance(x, list):
            for i in x: recorrer(i, ruta)
    for p in sorted((raiz / "data").glob("*.json")) if (raiz / "data").is_dir() else []:
        rel = f"data/{p.name}"
        if p.stat().st_size > TOPE_DATOS_KB * 1024:
            errores.append(f"{rel}: pesa más de {TOPE_DATOS_KB} KB")
        try:
            datos = json.loads(p.read_text(encoding="utf-8"))
        except ValueError:
            errores.append(f"{rel}: JSON inválido"); continue
        if not isinstance(datos, dict) or "schema_version" not in datos or "generado_en" not in datos:
            errores.append(f"{rel}: falta schema_version o generado_en en la raíz")
        recorrer(datos, rel)


def verificar(raiz: Path = RAIZ, publicar: bool = False) -> list:
    raiz = Path(raiz); errores = []
    sitio = json.loads((raiz / "src" / "sitio.json").read_text(encoding="utf-8"))
    base = sitio["url_base"].rstrip("/"); host_propio = urlparse(base).hostname
    aprobados = set(sitio.get("externos_aprobados", []))
    paginas = _paginas(raiz); leidas = {r: _leer(p) for r, p in paginas.items()}

    if publicar:
        if "por-definir" in base: errores.append("url_base sin definir (src/sitio.json): falta el dominio real")
        if not sitio.get("indexable"): errores.append("indexable es false (src/sitio.json): el sitio sigue oculto a buscadores")
        for ruta_p, arch in paginas.items():
            t = arch.read_text(encoding="utf-8")
            if "web-borrador" in t: errores.append(f"{ruta_p}: texto legal en BORRADOR (pendiente de revisión jurídica)")
            m = re.search(r"\[[A-ZÁÉÍÓÚÑ ]{3,}\]", t)
            if m: errores.append(f"{ruta_p}: dato pendiente entre corchetes {m.group(0)} (completar con la información real)")
        cfg = raiz / "assets" / "js" / "config.js"
        if cfg.is_file() and "por-definir" in cfg.read_text(encoding="utf-8"):
            errores.append("assets/js/config.js: apiUrl sin definir (por-definir): falta la dirección real de la API pública")
    if "/404.html" not in paginas: errores.append("falta 404.html")
    try: sitemap = (raiz / "sitemap.xml").read_text(encoding="utf-8")
    except OSError: sitemap = ""; errores.append("falta sitemap.xml")
    locs = set(re.findall(r"<loc>(.*?)</loc>", sitemap))

    titulos, descripciones = {}, {}
    for ruta, pg in leidas.items():
        e = lambda m: errores.append(f"{ruta}: {m}")
        es_404 = ruta == "/404.html"
        if pg.lang != sitio.get("idioma", "es"): e(f"el atributo lang debe ser «{sitio.get('idioma', 'es')}» (es «{pg.lang}»)")
        if pg.h1 != 1: e(f"debe tener exactamente un h1 (tiene {pg.h1})")
        t = pg.title.strip()
        if not t: e("falta el title")
        elif t in titulos: e(f"title duplicado con {titulos[t]}")
        else: titulos[t] = ruta
        d = pg.metas.get("description", "").strip()
        if not d: e("falta la meta description")
        elif d in descripciones: e(f"description duplicada con {descripciones[d]}")
        else: descripciones[d] = ruta
        for og in ("og:title", "og:description", "og:image", "og:url"):
            if not pg.metas.get(og): e(f"falta {og}")
        if not es_404:
            if not pg.canonical: e("falta el link canonical")
            if base + ruta not in locs: e("no aparece en sitemap.xml")
        if len(pg.estilos) != 1: e(f"debe tener una sola hoja de estilo (tiene {len(pg.estilos)})")
        pe = pg.primer_enlace
        if not pe or "saltar" not in (pe.get("class") or "") or pe.get("href") != "#contenido" or "contenido" not in pg.ids:
            e("el primer enlace debe ser «Saltar al contenido» (class saltar, href #contenido) hacia un id contenido")
        for src, defer, tipo in pg.scripts:
            if src is None:
                if tipo != "application/ld+json": e("script en línea (la CSP lo bloquearía): mover a assets/js/")
            elif urlparse(src).scheme in ("http", "https") and urlparse(src).hostname not in aprobados | {host_propio}:
                e(f"script externo no aprobado: {src}")
            elif not defer: e(f"el script {src} debe llevar defer")
        if re.search(r"""<[^>]+\sstyle\s*=""", paginas[ruta].read_text(encoding="utf-8")):
            e("atributo style en línea (la CSP lo bloquearía): usar una clase en assets/css/")
        for rel, href in pg.links:
            if rel in ("stylesheet", "preload", "icon") and urlparse(href).scheme in ("http", "https") \
                    and urlparse(href).hostname not in aprobados | {host_propio}:
                e(f"recurso externo no aprobado: {href}")
        for src, con_alt in pg.imgs:
            if not con_alt: e(f"imagen sin atributo alt: {src}")
            if urlparse(src).scheme in ("http", "https") and urlparse(src).hostname not in aprobados | {host_propio}:
                e(f"imagen externa no aprobada: {src}")
        for c in pg.campos:
            if not (c["aria"] or c["en_label"] or (c["id"] and c["id"] in pg.labels_for)):
                e(f"campo sin label asociado (id={c['id']})")
        # enlaces y recursos internos
        destinos = [h for h, _, _ in pg.enlaces] + [h for _, h in pg.links if h] + [s for s, _, _ in pg.scripts if s] + [s for s, _ in pg.imgs]
        for href in destinos:
            u = urlparse(href)
            if u.scheme in ("mailto", "tel", "javascript", "data") or (u.scheme in ("http", "https") and u.hostname != host_propio):
                continue
            ruta_dest = ruta if (not u.path and u.fragment) else u.path
            if not ruta_dest.startswith("/"):
                e(f"enlace roto o relativo ({href}): usar rutas desde la raíz"); continue
            arch = _archivo_de(raiz, ruta_dest)
            if not arch.is_file(): e(f"enlace roto: {href}"); continue
            if u.fragment and arch.suffix == ".html":
                destino_pg = leidas.get(ruta_dest) or _leer(arch)
                if u.fragment not in destino_pg.ids: e(f"ancla inexistente: {href}")
        for href, rel, target in pg.enlaces:
            u = urlparse(href)
            if u.scheme in ("http", "https") and u.hostname != host_propio:
                if "noopener" not in rel or "noreferrer" not in rel:
                    e(f"el enlace externo {href} debe llevar rel=\"noopener noreferrer\"")

    # peso por página: HTML + CSS + JS + fuentes (sin imágenes)
    tope = int(sitio.get("peso_max_kb", 150)) * 1024
    for ruta, pg in leidas.items():
        total = paginas[ruta].stat().st_size
        for href in pg.estilos:
            css = _archivo_de(raiz, urlparse(href).path)
            if css.is_file():
                total += css.stat().st_size
                for f in re.findall(r"url\(['\"]?([^)'\"]+\.woff2)", css.read_text(encoding="utf-8")):
                    fp = (css.parent / f).resolve()
                    if fp.is_file(): total += fp.stat().st_size
        for src, _, _ in pg.scripts:
            if src and not urlparse(src).scheme:
                sp = _archivo_de(raiz, src)
                if sp.is_file(): total += sp.stat().st_size
        if total > tope: errores.append(f"{ruta}: pesa {total // 1024} KB sin imágenes (máximo {tope // 1024} KB)")

    # secretos y referencias a Aurex en lo servido
    for p in _servidos(raiz):
        rel = p.relative_to(raiz).as_posix(); texto = p.read_text(encoding="utf-8", errors="replace")
        for patron, que in PATRONES_SECRETO:
            if patron.search(texto): errores.append(f"{rel}: posible secreto ({que})")
        if p.suffix != ".xml" and PATRON_AUREX.search(texto):
            errores.append(f"{rel}: referencia a la API/base de Aurex o a un servicio interno ({PATRON_AUREX.search(texto).group(0)})")
        if p.suffix == ".js":
            for url in re.findall(r"""fetch\(\s*['"](https?://[^'"]+)""", texto):
                if urlparse(url).hostname not in aprobados | {host_propio}:
                    errores.append(f"{rel}: fetch a un dominio no aprobado ({url})")

    # estilos: reduced-motion y contraste de los tokens
    for p in sorted((raiz / "assets" / "css").glob("*.css")) if (raiz / "assets" / "css").is_dir() else []:
        css = p.read_text(encoding="utf-8")
        if "prefers-reduced-motion" not in css: errores.append(f"{p.name}: falta la regla prefers-reduced-motion")
        toks = _tokens(css)
        for fg, bg in PARES_CONTRASTE:
            if fg in toks and bg in toks and contraste(toks[fg], toks[bg]) < 4.5:
                errores.append(f"{p.name}: contraste insuficiente {fg} {toks[fg]} sobre {bg} {toks[bg]} "
                               f"({contraste(toks[fg], toks[bg]):.2f}:1, mínimo 4.5:1)")
    _revisar_datos(raiz, errores)
    return errores


if __name__ == "__main__":
    sys.path.insert(0, str(RAIZ / "scripts"))
    import construir
    errs = construir.comprobar() + verificar(RAIZ, publicar="--publicar" in sys.argv)
    for x in errs: print("✗", x)
    print(f"\n{'FALLÓ' if errs else 'OK'}: {len(errs)} problema(s).")
    sys.exit(1 if errs else 0)
