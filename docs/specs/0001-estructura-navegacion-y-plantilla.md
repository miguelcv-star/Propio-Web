# 0001 — Estructura del sitio, navegación y plantilla de página

**Estado:** implementada (pendiente de probar en local)  ·  **Fecha:** 2026-10-15  ·  **Brief:** §4, §10, §11

## Problema y objetivo
No existe el sitio público. Esta spec fija la **base común** sobre la que se montan todas las páginas: rutas,
menú, cabecera/pie, SEO básico, accesibilidad y peso. Las demás specs (0002–0009) dependen de esta.

**Fuera de alcance:** el contenido de cada página (0002–0004, 0007, 0008), formularios (0005), analítica (0006).

## Rutas (una carpeta con `index.html` por página, URL limpia)
`/` · `/vender-o-arrendar/` · `/conocer-precio/` · `/invertir-por-mi-cuenta/` · `/empezar-a-invertir/` ·
`/comprar-o-arrendar-para-mi/` · `/oportunidades/` · `/casos/` · `/comunidad/` · `/contacto/` · `/privacidad/` ·
`/terminos/`. Más `404.html`, `sitemap.xml`, `robots.txt`.

**Menú:** Qué necesitas hacer · Cómo funciona Aurex · Oportunidades · Casos reales · Comunidad · Sobre nosotros ·
Hablar con el equipo. «Qué necesitas hacer» y «Cómo funciona» son anclas de la portada; «Sobre nosotros» es una
sección de la portada hasta que haya contenido para una página propia (no se crea una página vacía).

## Criterios de aceptación
1. **Dado** cualquier página, **cuando** se abre sin sesión, **entonces** carga completa (sin pedir login ni cookies).
2. **Dado** cada página, **entonces** tiene `title` y `meta description` **únicos**, **un solo `h1`**,
   `<html lang="es">`, `canonical`, Open Graph (título, descripción, imagen) y aparece en `sitemap.xml`.
3. **Dado** el menú, **cuando** el ancho es ≤ 768 px, **entonces** se convierte en un menú con botón etiquetado
   («Abrir menú»/«Cerrar menú»), `aria-expanded`, se cierra con Escape y se maneja completo con teclado.
   En escritorio el menú está siempre visible.
4. **Dado** un enlace interno, **entonces** apunta a una ruta que existe (cero enlaces rotos); los externos llevan
   `rel="noopener noreferrer"`.
5. **Dado** cualquier página, **entonces** hay enlace «Saltar al contenido», foco visible, contraste AA, imágenes con
   `alt`, y con `prefers-reduced-motion` no hay animaciones.
6. **Dado** cualquier página, **entonces** pesa ≤ 150 KB sin contar imágenes, usa un solo CSS, JS con `defer` y
   ninguna dependencia externa (ni fuentes, ni scripts de terceros).
7. **Dado** una ruta inexistente, **entonces** se muestra `404.html` con el estilo del sitio y enlace al inicio.
8. **Dado** el repo, **entonces** no contiene secretos, ni referencias a la API/base de Aurex (regla de oro de `AGENTS.md`).
9. **Dado** un intento de elegir una intención (0002), **entonces** esa intención viaja a la página destino
   (`?intencion=…` no personal) para conservar el contexto.

## Decisiones y riesgos
- **Cabecera y pie repetidos en ~12 páginas:** propongo un generador mínimo `scripts/construir.py` (solo librería
  estándar de Python, sin npm) que arma cada página desde `src/` + parciales y escribe los `index.html`; el resultado
  se versiona. Alternativa descartada: copiar el HTML a mano (cambiar el menú = tocar 12 archivos) o inyectarlo con JS
  (sin JS no hay menú y los buscadores no lo ven). **Aprobado por el usuario el 2026-10-15.**
- **Verificador automático** `scripts/verificar.py` (stdlib): revisa criterios 2, 4, 5 (alt/labels), 6 y 8 sobre los
  HTML generados. Es la «prueba» de esta spec; se corre antes de cada publicación.
- Contraste AA: los tokens de Aurex (`--text-muted #767676` sobre `#fafaf7`) rozan el mínimo (≈4,3:1); para texto
  pequeño del sitio se usa `--text` o un gris más oscuro. Se mide, no se supone.
- Riesgo: «Sobre nosotros» sin contenido real. Se escribe con el usuario, no se inventa.

## Plan de pruebas
- `scripts/verificar.py` ← criterios 1, 2, 4, 5, 6, 7, 8.
- `node --test tests/menu.test.js` (sin dependencias) ← criterio 3 (estado abierto/cerrado, Escape).
- A mano: teclado completo, 375/768/1280 px, lector de pantalla básico (VoiceOver), criterio 9.

## Ajustes al implementar
- **Sin JavaScript el menú queda visible y apilado:** el CSS solo lo pliega tras el botón cuando `menu.js` marcó `con-js` en `<html>`.
- **Mientras no haya dominio**, `src/sitio.json` trae `url_base` = `https://por-definir.example` e `indexable: false` (todas las páginas con `noindex` y `robots.txt` que bloquea todo). `verificar.py --publicar` falla hasta que se definan los dos.
- **Contraste:** los grises de texto secundario de Aurex (`#767676`, `#a8a59f`) no llegan a 4,5:1 sobre el crema (4,34 y 2,35). En el sitio se oscurecen (`#666666`, `#6b6b6b`) en un `:root` propio; el verificador mide los pares de tokens.
- `scripts/construir.py --comprobar` falla si una página generada se editó a mano o `src/` cambió sin regenerar.
- El contenido de cada página es un **marcador «en construcción»** con el titular del brief; el real llega con las specs 0002–0008. Imagen Open Graph de marcador (`assets/img/og.png`) hasta tener logo.
- **Pruebas:** 33 de Python (el verificador detecta cada defecto provocado en una copia del sitio) y 10 de JS; todas en verde. Menú móvil comprobado a mano en un marco de 390 px (abre, Escape cierra y devuelve el foco).
- Pendiente a mano: lector de pantalla (VoiceOver) y Safari.
