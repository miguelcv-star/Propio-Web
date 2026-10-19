#!/usr/bin/env python3
"""Generador del sitio (spec 0001). Solo librería estándar.

Lee `src/` (sitio.json, plantilla.html, parciales/, paginas/*.html) y escribe en la raíz las páginas
`<ruta>/index.html`, `404.html`, `sitemap.xml` y `robots.txt`. Lo generado se versiona; NO se edita a mano:
`python3 scripts/construir.py --comprobar` falla si no coincide con `src/`.

Cada archivo de `src/paginas/` empieza con una cabecera `clave: valor` terminada en una línea `---`:
    ruta: /vender-o-arrendar/        (o /404.html)
    titulo: ...
    descripcion: ...
    sitemap: no                      (opcional; la 404 lo lleva)
    scripts: config.js lib.js        (opcional; archivos de assets/js/ que la página carga con defer, además de menu.js)
y sigue con el HTML de la página (el contenido de <main>). En el contenido, `{{incluir:nombre}}` se reemplaza por
el parcial `src/parciales/nombre.html` (campos repetidos de los formularios).
"""
import html
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SRC = RAIZ / "src"
MANIFIESTO = RAIZ / ".construido.json"


def _leer_pagina(ruta_archivo: Path) -> dict:
    texto = ruta_archivo.read_text(encoding="utf-8")
    cabecera, sep, cuerpo = texto.partition("\n---\n")
    if not sep:
        raise SystemExit(f"{ruta_archivo.name}: falta la línea «---» que cierra la cabecera")
    datos = {}
    for linea in cabecera.splitlines():
        if linea.strip():
            clave, _, valor = linea.partition(":")
            datos[clave.strip()] = valor.strip()
    for obligatoria in ("ruta", "titulo", "descripcion"):
        if not datos.get(obligatoria):
            raise SystemExit(f"{ruta_archivo.name}: falta «{obligatoria}»")
    datos["contenido"] = cuerpo.strip("\n")
    return datos


def _destino(ruta: str) -> str:
    if ruta.endswith(".html"):
        return ruta.lstrip("/")
    return "index.html" if ruta == "/" else ruta.strip("/") + "/index.html"


def _incluir(contenido: str, parciales: Path) -> str:
    """Reemplaza `{{incluir:nombre}}` por el parcial src/parciales/nombre.html (sin salto de línea final)."""
    def reemplazo(m):
        archivo = parciales / f"{m.group(1)}.html"
        if not archivo.is_file():
            raise SystemExit(f"{{{{incluir:{m.group(1)}}}}}: no existe src/parciales/{m.group(1)}.html")
        return archivo.read_text(encoding="utf-8").rstrip("\n")
    return re.sub(r"\{\{incluir:([a-z0-9-]+)\}\}", reemplazo, contenido)


def _scripts(nombres: str) -> str:
    """Etiquetas <script defer> de los archivos de assets/js/ que pide la página (cada uno validado)."""
    filas = []
    for n in nombres.split():
        if not re.fullmatch(r"[A-Za-z0-9._-]+\.js", n) or not (RAIZ / "assets" / "js" / n).is_file():
            raise SystemExit(f"scripts: «{n}» no existe en assets/js/")
        filas.append(f'<script src="/assets/js/{n}" defer></script>')
    return "\n".join(filas)


def _esc(s: str) -> str:
    return html.escape(s, quote=True)


def _menu(items: list, ruta_actual: str, sangria: str) -> str:
    filas = []
    for it in items:
        actual = it["href"] == ruta_actual
        extra = ' class="activo" aria-current="page"' if actual else ""
        filas.append(f'{sangria}<a href="{_esc(it["href"])}"{extra}>{_esc(it["etiqueta"])}</a>')
    return "\n".join(filas)


def construir() -> dict:
    """Devuelve {ruta_relativa: texto} de todo lo que genera (sin escribir nada)."""
    sitio = json.loads((SRC / "sitio.json").read_text(encoding="utf-8"))
    plantilla = (SRC / "plantilla.html").read_text(encoding="utf-8")
    cabecera_t = (SRC / "parciales" / "cabecera.html").read_text(encoding="utf-8")
    pie_t = (SRC / "parciales" / "pie.html").read_text(encoding="utf-8")
    base = sitio["url_base"].rstrip("/")
    paginas = [_leer_pagina(p) for p in sorted((SRC / "paginas").glob("*.html"))]
    salida, sitemap = {}, []
    for pag in paginas:
        ruta = pag["ruta"]
        es_404 = ruta.endswith(".html")
        url_pagina = base + ruta
        sin_indexar = (not sitio["indexable"]) or es_404
        cabecera = cabecera_t.replace("{{menu}}", _menu(sitio["menu"], ruta, "      ")).replace("{{nombre}}", _esc(sitio["nombre"]))
        pie = pie_t.replace("{{pie_enlaces}}", _menu(sitio["pie"], ruta, "      ")).replace("{{nombre}}", _esc(sitio["nombre"]))
        valores = {
            "idioma": sitio["idioma"], "nombre": _esc(sitio["nombre"]),
            "titulo": _esc(pag["titulo"]), "descripcion": _esc(pag["descripcion"]),
            "robots": '<meta name="robots" content="noindex, nofollow">' if sin_indexar else "",
            "canonical": "" if es_404 else f'<link rel="canonical" href="{_esc(url_pagina)}">',
            "url_pagina": _esc(url_pagina), "og_imagen": _esc(base + sitio["og_imagen"]),
            "cabecera": cabecera.rstrip("\n"), "pie": pie.rstrip("\n"),
            "contenido": _incluir(pag["contenido"], SRC / "parciales"), "scripts": _scripts(pag.get("scripts", "")),
        }
        texto = plantilla
        for k, v in valores.items():
            texto = texto.replace("{{" + k + "}}", v)
        texto = "\n".join(l for l in texto.split("\n") if l.strip() != "")  # sin renglones vacíos por campos opcionales
        salida[_destino(ruta)] = texto + "\n"
        if pag.get("sitemap", "si") != "no" and not es_404:
            sitemap.append(url_pagina)
    filas = "".join(f"<url><loc>{_esc(u)}</loc></url>\n" for u in sitemap)
    salida["sitemap.xml"] = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + filas + "</urlset>\n")
    if sitio["indexable"]:
        salida["robots.txt"] = f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n"
    else:
        salida["robots.txt"] = "User-agent: *\nDisallow: /\n"
    return salida


def comprobar() -> list:
    """Lista de diferencias entre lo generado en disco y lo que produciría `src/` (vacía = al día)."""
    esperado, errores = construir(), []
    for rel, texto in esperado.items():
        p = RAIZ / rel
        if not p.is_file():
            errores.append(f"{rel}: falta (correr scripts/construir.py)")
        elif p.read_text(encoding="utf-8") != texto:
            errores.append(f"{rel}: no coincide con src/ (¿editado a mano? correr scripts/construir.py)")
    return errores


def escribir() -> list:
    esperado = construir()
    anteriores = set(json.loads(MANIFIESTO.read_text(encoding="utf-8"))) if MANIFIESTO.is_file() else set()
    for rel, texto in esperado.items():
        p = RAIZ / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(texto, encoding="utf-8")
    for viejo in sorted(anteriores - set(esperado)):  # páginas que ya no existen en src/
        p = RAIZ / viejo
        if p.is_file():
            p.unlink()
            try:
                p.parent.rmdir()
            except OSError:
                pass
    MANIFIESTO.write_text(json.dumps(sorted(esperado), indent=1) + "\n", encoding="utf-8")
    return sorted(esperado)


if __name__ == "__main__":
    if "--comprobar" in sys.argv:
        errs = comprobar()
        print("\n".join(errs) if errs else "Lo generado está al día con src/.")
        sys.exit(1 if errs else 0)
    archivos = escribir()
    print(f"Generado: {len(archivos)} archivos.")
