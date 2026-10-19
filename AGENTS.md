# AGENTS.md

Guía para Claude Code en este repo. **Propio Web** es el sitio público de Propio (antes «Aurex Web»): una página **estática**, liviana, con la misma marca que la app, que **solo habla con las rutas públicas `/publico/*` de la API de Propio** y **nunca tiene acceso a la base de datos, a sesiones ni a credenciales de Propio**. La app y su arquitectura viven en `../03_dev_Propio` (ver su `AGENTS.md` y `docs/publico-despliegue.md`, donde está el contrato de esas rutas); este proyecto es independiente.

> El usuario tiene bases de programación pero no domina Python/JS ni frameworks: explica en lenguaje sencillo, sin jerga innecesaria. Responde y comenta en español.

> **Nombre:** la plataforma se llama **Propio** (spec 0017 de la app). «Aurex» sobrevive solo en nombres técnicos antiguos (como el nombre del repo principal en GitHub); todo lo que ve una persona dice Propio.
## Qué se construye

El alcance, las cinco intenciones (vender/arrendar, conocer el precio, invertir por cuenta propia, empezar a invertir, comprar/arrendar para uso propio), las páginas, los formularios, los textos obligatorios de transparencia y los criterios de aceptación salieron del **brief de desarrollo del sitio**, que se retiró del repositorio y **se volverá a construir**; mientras tanto rige lo aprobado en `docs/specs/` (las citas «brief §N» de las specs apuntan a ese documento y quedan pendientes de revalidar cuando exista de nuevo). Esta guía fija CÓMO se construye: las reglas técnicas y de seguridad mandan sobre el brief cuando chocan (p. ej. el brief habla de componentes TypeScript y `/rutas`; aquí se traducen a HTML/JS vanilla y carpetas con `index.html`). **Decisiones del usuario que cambian el brief (spec 0010):** los formularios envían directo a la API pública de Propio; el catálogo y las cifras salen de ella; publicar un inmueble es gratis y la comisión se cobra solo si se vende. Las «decisiones que el agente no debe asumir» (§16 del brief) siguen abiertas salvo las anteriores: **preguntar al usuario, no suponer** (número de WhatsApp, analítica, casos autorizados, textos legales definitivos, hosting y dominio).
## Regla de oro: el sitio solo conoce `/publico/*`

Es la razón de que sea un proyecto aparte. Mientras se cumpla, aunque el sitio público sea atacado no hay nada interno a su alcance.

- **Sin base de datos y sin servidor propio.** Solo archivos (HTML, CSS, JS, JSON, imágenes) servidos por un hosting estático.
- **Sin secretos en este repo.** Nada de `.env`, contraseñas, tokens, llaves de API, cadenas de conexión. `assets/js/config.js` solo lleva valores PÚBLICOS: la dirección de la API y la llave PÚBLICA de Turnstile (`turnstileSiteKey`).
- **La única puerta a Propio son las rutas públicas** `POST /publico/contacto|busqueda|busqueda/pdf|valorar|vender` y `GET /publico/inmuebles|cifras` (lista cerrada, sin sesión, con límites y anti-bot del lado de Propio; contrato en `../03_dev_Propio/docs/publico-despliegue.md`). Ningún otro `fetch` a Propio: ni la API normal, ni la base, ni "aunque sea de solo lectura". `tests/test_verificar.py` falla si el JS llama a otra ruta.
- **No se importa código de `../03_dev_Propio`** (ni `frontend/`, ni `core/`, nada). Lo que se necesite se copia una vez (marca, fuentes, tokens).
- **Todo lo que está en el sitio es público**, incluido el historial de git si el repo es público. Escribir y revisar cada archivo con esa idea.
- **Lo que viene de la API es dato no confiable:** entra al DOM solo con `textContent` / `setAttribute` de enlaces `http(s)` (nunca `innerHTML`), y los enlaces externos llevan `rel="noopener noreferrer"`.
- **Con la API caída el sitio no se rompe:** catálogo y cifras degradan a su texto fijo; los formularios muestran un error recuperable y conservan lo escrito.
## Datos de Propio hacia el sitio (spec 0010)

El sitio **pide** lo que muestra; no hay instantáneas empujadas:

- `GET /publico/inmuebles` (catálogo de publicaciones de propietarios aprobadas) y `GET /publico/cifras` (números del inicio), solo desde `assets/js/datos.js`.
- Nada de lo que devuelve la API se guarda en `localStorage` ni se manda a analítica. Si la API falla, la sección queda con su texto fijo.
- `data/` y su contrato (`schema_version` + `generado_en`, spec 0009) quedan como referencia: hoy no se usan, pero `verificar.py` los revisa si algún día hay archivos ahí.
- **Jamás se muestra:** datos de contacto del propietario o del anunciante, notas, ids internos ni nada que la API no entregue en su lista cerrada (la limitan del lado de Propio).
## Formularios y leads (spec 0010)

Cada intención tiene su formulario (`form[data-propio-form="invierte|busqueda|valorar|vender"]`), todos manejados por `assets/js/formularios.js` (DOM) y `assets/js/lib.js` (lógica pura, probada con `node --test`):

- **Destino = API pública de Propio** (`apiUrl` de `config.js`). Ahí se crea el lead (origen «Web de Propio») y Propio aplica límites, anti-bot, consentimiento y filtros; **el cliente nunca decide** origen, finalidad ni estado (una prueba lo exige: el cuerpo no puede traer esos campos).
- **Un solo mecanismo**: el HTML de cada formulario usa los parciales de `src/parciales/` (`campos-persona`, `consentimiento`, `campos-ubicacion`, `opciones-*`) con `{{incluir:nombre}}`; las páginas piden sus scripts con la cabecera `scripts: config.js lib.js formularios.js`.
- **Estados** con `aria-live`: inicial, enviando (botón deshabilitado, sin doble envío), éxito y error recuperable que conserva lo escrito. Cada campo con `label` y su error asociado (`aria-describedby`); foco al primer error.
- **Consentimiento** obligatorio (casilla enlazada a `/privacidad/`); en «vende» además la aceptación del acuerdo de comisión. **Honeypot** `sitio_web` (si trae valor se descarta en silencio) y `tiempo_ms` (lo que tardó en llenar). **Turnstile** solo si `turnstileSiteKey` tiene valor (se carga entonces desde `challenges.cloudflare.com`, host aprobado el 2026-10-18 con el plan de la spec 0010).
- **Sin datos personales** en la URL, `localStorage`, consola ni analítica. El PDF del reporte se pide con otra llamada y se descarga como blob.
- **Textos legales (`/privacidad/`, `/terminos/`, `/acuerdo-comision/`):** hoy son BORRADORES con aviso visible, copiados de `../03_dev_Propio/docs/legal/`. El usuario y su abogado los aprueban; `verificar.py --publicar` falla mientras quede el aviso o datos entre corchetes.
- **WhatsApp y analítica:** siguen pendientes (spec 0006): número y herramienta los aprueba el usuario; sin aprobación no se carga nada de terceros.
- **Contenido que no se inventa:** casos solo con evidencia y autorización, nada de rentabilidades prometidas, estimación de mercado ≠ avalúo oficial.
## Proceso (igual que en Propio)

- **Función nueva o cambio que toque qué datos se publican:** spec corta primero (`docs/specs/NNNN-nombre.md`, media página, lenguaje sencillo) y **esperar la aprobación del usuario** antes de implementar. Hay plantilla en `../03_dev_Propio/docs/specs/_plantilla.md`.
- **Cambio mediano:** mini-spec de 3–5 líneas en la conversación. **Trivial** (texto, estilo): sin spec.
- **La API pública vive en Propio, no aquí.** Sus specs (0024–0026) y sus pruebas (lista cerrada de campos, límites, anti-bot, respuestas sin datos internos) van en `../03_dev_Propio`. Aquí se prueba que el sitio solo llama a esas rutas, arma bien el cuerpo y degrada bien si la API falla.
- **Cierre:** probar en local (móvil 375 px, teclado, red lenta/endpoint caído, sin secretos en lo servido), actualizar `CHANGELOG.md` si existe y esta guía si hay gotchas nuevos. **No publicar ni hacer push hasta que el usuario confirme que probó en local.**
- **Antes de publicar:** revisar que ningún archivo nuevo traiga secretos o datos privados (`git diff` completo, y `data/` a ojo).

## Estructura

```
src/sitio.json              # nombre, url_base, indexable, menú, pie, externos aprobados, tope de peso
src/plantilla.html          # esqueleto común (head, SEO, «saltar al contenido», <main>)
src/parciales/              # cabecera (menú) y pie
src/paginas/*.html          # UNA por página: cabecera «ruta/titulo/descripcion» + `---` + el HTML de <main>
index.html, <ruta>/index.html, 404.html, sitemap.xml, robots.txt   # GENERADOS (no editar; ver abajo)
scripts/construir.py        # generador (--comprobar: falla si lo generado no coincide con src/)
scripts/verificar.py        # verificador: es la «prueba» de las specs; nada se publica si falla
tests/                      # pruebas del verificador/generador (unittest) y del JS (node --test)
assets/css/propio.css       # Estilos: tokens de la marca Propio (copia de la app) + componentes del sitio
assets/fonts/               # Plus Jakarta Sans 400/500/600 en woff2 (autoalojada, licencia OFL)
assets/img/                 # favicon, logos, imágenes del sitio
assets/js/                  # JS vanilla: menu.js, contexto.js, config.js (público), lib.js (lógica pura), formularios.js, datos.js
data/                       # (sin uso hoy) contrato de instantáneas públicas, spec 0009. Ver data/README.md
docs/specs/                 # specs de este proyecto
```

## Stack y cómo correrlo

HTML + CSS + JS vanilla, **sin npm y sin dependencias** (menos peso y menos superficie de ataque; mismo enfoque que `../06_dev_Web_Rehabitar`). Las páginas se **generan** con `scripts/construir.py` (solo librería estándar de Python) desde `src/`; lo generado se versiona y **no se edita a mano**. Si una librería llega a hacer falta, discutirlo primero: cada dependencia es peso y riesgo para un sitio público.

```bash
cd 09_dev_Web_Propio
python3 scripts/construir.py            # regenera las páginas desde src/ (hacerlo tras cada cambio en src/)
python3 scripts/verificar.py            # revisa el sitio; con --publicar exige dominio e indexación definidos
python3 -m unittest discover -s tests   # pruebas del verificador y del generador
node --test "tests/*.test.js"           # pruebas del JS (menú, contexto de intención), sin dependencias
python3 -m http.server 8080             # ver el sitio a mano en http://localhost:8080 (lo mismo que ver_sitio.command)
```

**Para ver el sitio:** doble clic en `ver_sitio.command` (regenera, revisa, levanta el servidor solo en este equipo y abre el navegador; Ctrl+C o cerrar la ventana lo detiene). Sin API configurada los formularios muestran «no pudimos conectarnos». **Para probarlo de verdad con la API:** `../03_dev_Propio/scripts/probar_publico_local.sh` levanta una base desechable, la API de Propio y este sitio en `http://localhost:3012/` (usa `scripts/servir_local.py`, que reemplaza `config.js` solo en la respuesta). Nunca apuntar el sitio local a la API real de Propio.

`fetch` de `data/*.json` no funciona abriendo el HTML con doble clic (`file://`): usar el servidor de arriba.

## Identidad visual (igual que Propio)

`assets/css/propio.css` usa una **copia** de los tokens de la marca de la app (`../03_dev_Propio/frontend/app/globals.css`, bloque `:root`), no un enlace. Reglas:

- **Usar siempre las variables** (`--bg`, `--text`, `--border`, `--accent`, `--radius-xs`…), nunca colores sueltos. Marca Propio: Azul Petróleo `#0F3D4E` (primario y títulos), Verde Oportunidad `#A7E3C1` (solo detalles, nunca texto sobre blanco), Arena para bordes, Blanco Roto `#FAF9F6` de fondo, Grafito para el texto; **bordes sutiles y sin sombras**, una sola fuente (**Plus Jakarta Sans** 400/500/600), jerarquía por tamaño/peso, no por familias. Los grises de texto secundario son más oscuros que en la app para cumplir contraste AA (lo vigila el verificador).
- Componentes ya disponibles: `.btn-primario`/`.btn-secundario` (en `<a>` o `<button>`), `.badge` (`.alta`/`.media`/`.mercado`/`.sobre`), `.chip`, `.etq`, `.meta`, `.tarjeta`, tablas, `.nav`. Lo propio del sitio (`.web-*`) está al final del archivo, bajo «Sitio público». Antes de inventar una clase, mirar si ya existe.
- **Si la app cambia sus tokens o un componente, el sitio NO se entera solo:** copiar el cambio a mano (los dos proyectos son independientes a propósito). La sección «Tokens» (`:root`) es lo que más importa mantener igual.
- Fuente autoalojada (`assets/fonts`), sin Google Fonts: más rápida y sin avisar a terceros. Se generó desde los TTF estáticos de `../03_dev_Propio/services/fuentes/` (`fontTools`, `flavor="woff2"`; ya vienen en subconjunto latino).
- Móvil primero en lo posible: el menú es corto y se queda visible en filas (sin hamburguesa); probar a 375 px.

## Rendimiento y buenas prácticas (es público)

- **Liviano:** páginas de decenas de KB, sin frameworks, imágenes en WebP/AVIF (o SVG) con `width`/`height` y `loading="lazy"`; un solo CSS; JS mínimo y con `defer`.
- **Texto en español, con tildes**; `<html lang="es">`, `<title>` y `meta description` por página, HTML semántico (`header`, `main`, `nav`, `footer`), contraste y `alt` en imágenes.
- **Nada de terceros sin aprobar** (analítica, proveedor de formularios, mapas, fuentes, chat): cada uno es una vía de entrada y un aviso de privacidad. Cuando el usuario apruebe uno, anotarlo aquí con su fecha.
- **Cabeceras de seguridad** al publicar (las pone el hosting; el archivo `_headers` de la raíz las trae listas para Cloudflare Pages —CSP estricta con `connect-src` hacia la API pública, `script-src`/`frame-src` solo para Turnstile—; al definir el dominio, cambiar `api.por-definir.example` por el real): `Content-Security-Policy` estricta (`default-src 'self'`), `X-Content-Type-Options: nosniff`, `Referrer-Policy`. Anotar aquí el hosting elegido y cómo se configuran cuando se decida.
- **Enlaces externos** con `rel="noopener noreferrer"`.

## Cómo se añade o cambia una página

1. Crear/editar `src/paginas/<nombre>.html` (cabecera con `ruta`, `titulo`, `descripcion` únicos + el contenido de `<main>`, con **un solo `h1`**).
2. Si va en el menú o el pie, agregarla a `src/sitio.json`.
3. `python3 scripts/construir.py` y luego `python3 scripts/verificar.py`. Hasta que el dominio esté definido, `url_base` es `https://por-definir.example` y `indexable` es `false` (el sitio lleva `noindex` y `robots.txt` bloquea todo): **al publicar hay que poner el dominio real, `indexable: true` y correr `verificar.py --publicar`**.
4. Enlaces internos siempre desde la raíz (`/casos/`, `/#como-funciona`); lo externo lleva `rel="noopener noreferrer"`.
5. Sin scripts en línea (la CSP los bloquearía): todo JS va en `assets/js/` con `defer`.

## Lo que NO hay que hacer

- Llamar a cualquier ruta de Propio que no sea `/publico/*`, conectar el sitio a su base, o poner un proxy hacia la API normal.
- Guardar credenciales o URLs internas en este repo (la dirección de la API pública va en `config.js` porque es pública).
- Importar archivos de `../03_dev_Propio` en tiempo de ejecución o de build (se copian una vez).
- Editar a mano un `index.html` generado: el siguiente `construir.py` lo pisaría y `--comprobar` lo marca.
- Mostrar o guardar datos personales que vengan de la API, o insertar texto de la API con `innerHTML`.
- Reemplazar la tipografía, la paleta o los bordes sutiles por otro estilo "porque se ve más moderno": la idea es que se vea como Propio.
