# Propio Web

Sitio público de Propio: inicio, **Invierte**, **Compra o arrienda**, **Vende** (publicar gratis, comisión solo si se vende),
**Conoce el valor** y catálogo de inmuebles publicados. Es una página **estática** (HTML + CSS + JS, sin dependencias) que solo
habla con las rutas públicas `/publico/*` de la API de Propio. Reglas y proceso: `AGENTS.md`; spec de la conexión:
`docs/specs/0010-conexion-con-la-api-publica-de-propio.md`; contrato de la API: `../03_dev_Propio/docs/publico-despliegue.md`.

```bash
python3 scripts/construir.py            # regenera las páginas desde src/
python3 scripts/verificar.py            # revisa el sitio (--publicar: exige dominio, API real y textos legales sin borrador)
python3 -m unittest discover -s tests   # pruebas del verificador y del generador
node --test "tests/*.test.js"           # pruebas del JS
```

Probar con la API de verdad (base desechable, nunca la real): `../03_dev_Propio/scripts/probar_publico_local.sh`
→ el sitio queda en `http://localhost:3012/`.

**Antes de publicar:** dominio real y `indexable: true` en `src/sitio.json`, `apiUrl` (y la llave pública de Turnstile) en
`assets/js/config.js` y en `_headers`, y los textos legales aprobados (hoy son borradores).

## Ver el sitio publicado (hosting estático, Cloudflare Pages)

Abrir `index.html` con doble clic no funciona (los enlaces empiezan con `/`), por eso se publica en un hosting estático:
cada `git push` a `main` lo actualiza solo. `scripts/empaquetar.py` arma `dist/` con **solo** el sitio (sin `src/`, `docs/`,
pruebas, guías ni archivos ocultos).

Una vez, en [dash.cloudflare.com](https://dash.cloudflare.com) → **Workers & Pages → Create → Pages → Connect to Git**:

1. Autoriza GitHub y elige el repositorio `Propio-Web` (privado; Cloudflare lo puede leer).
2. Nombre del proyecto: `propio-web` (la dirección queda `https://propio-web.pages.dev`).
3. Framework preset: **None**. Build command: `python3 scripts/empaquetar.py`. Build output directory: `dist`.
4. **Save and Deploy**. Las siguientes publicaciones salen solas con cada push.

Esta versión de desarrollo **no se indexa** (`noindex` en cada página y `robots.txt` con `Disallow: /`) y cualquiera con el
enlace la puede ver. Los formularios y el catálogo no funcionarán hasta que `apiUrl` (en `assets/js/config.js` y en
`_headers`) apunte a una API de Propio con dirección pública y HTTPS, y esa API acepte el origen del sitio (`CORS_ALLOW_ORIGINS`).
