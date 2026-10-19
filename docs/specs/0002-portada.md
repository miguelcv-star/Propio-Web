# 0002 — Portada: la pregunta «¿Qué quieres hacer con un inmueble?»

**Estado:** borrador  ·  **Fecha:** 2026-10-15  ·  **Brief:** §1, §2, §5, §7 (`IntentCard`)

## Problema y objetivo
La portada no debe presentar Aurex como software sino partir de la necesidad del visitante y llevarlo a uno de cinco
recorridos. Que en pocos segundos entienda qué resuelve Aurex y elija.

**Fuera de alcance:** el contenido de las páginas de destino (0003, 0004); los formularios (0005); casos y Radar
(0007); el texto legal (0008).

## Secciones (en este orden)
1. **Hero:** titular «El siguiente paso de tu inmueble empieza con mejores decisiones.», subtítulo de apoyo del
   brief, pregunta «¿Qué quieres hacer con un inmueble?», **cinco tarjetas de intención** y CTA secundario a WhatsApp.
2. **Cómo ayudamos:** tres bloques — Observamos / Analizamos / Acompañamos (pilares Datos / Criterio / Ejecución).
3. **Aurex en acción:** capturas o ilustraciones de análisis de oportunidad, comparables, escenarios de inversión,
   reporte y seguimiento. **Solo material anonimizado** (sin direcciones, personas ni datos de terceros).
4. **Casos reales** (2–3 tarjetas) y **Comunidad / Radar** — se montan con 0007.
5. **Transparencia** (límites del análisis) — texto en 0008.
6. **CTA final:** «Cuéntanos qué quieres hacer con un inmueble.» + las cinco intenciones otra vez.

## Las cinco tarjetas (`IntentCard`)
Vender o arrendar · Conocer el precio · Invertir por mi cuenta · Empezar a invertir · Comprar o arrendar para mí.
Cada una: título, una línea de descripción, ícono con texto accesible y enlace a su ruta (0001). Datos en una sola
lista de configuración, no repetidos en el HTML.

## Criterios de aceptación
1. **Dado** la portada en escritorio, **cuando** carga, **entonces** las cinco tarjetas se ven sin hacer scroll
   (≥ 1280×720) y sin leer más de una línea por tarjeta.
2. **Dado** una tarjeta, **cuando** se hace clic en cualquier parte, **entonces** navega a su ruta con la intención
   conservada; toda la tarjeta es un solo enlace con foco visible y nombre accesible.
3. **Dado** que el color es el único diferenciador, **entonces** no lo es: cada tarjeta se distingue por texto e ícono.
4. **Dado** escritorio, **entonces** las tarjetas tienen la misma altura; en móvil (≤ 768 px) se apilan en una columna
   sin desbordar a 320 px.
5. **Dado** las cinco tarjetas, **entonces** salen de una sola lista (`assets/js/intenciones.js`) que también usan el
   CTA final y el menú de las páginas por intención.
6. **Dado** la sección «Aurex en acción», **entonces** ninguna imagen contiene datos personales, direcciones exactas
   ni información de terceros (revisión manual con lista de chequeo antes de publicar).
7. **Dado** el hero, **entonces** hay exactamente un `h1` y el CTA de WhatsApp usa la configuración de 0006.

## Decisiones y riesgos
- **Sin software en el primer plano:** el brief lo pide; «Aurex en acción» va después de las intenciones.
- Los textos principales son los del brief tal cual; cualquier variante la aprueba el usuario.
- **Pendiente del usuario:** logo e identidad definitiva (por ahora el nombre «Aurex» en el estilo de la app) y las
  imágenes/capturas anonimizadas de «Aurex en acción».
- Riesgo: «Aurex en acción» con capturas reales de la app puede revelar datos. Se usan datos ficticios o recortes
  anonimizados.

## Plan de pruebas
- `scripts/verificar.py` ← criterios 5 y 7 (un `h1`, lista única) y que las cinco rutas existen.
- `node --test tests/intenciones.test.js` ← criterio 5 (la lista tiene 5 elementos y rutas válidas).
- A mano: criterios 1–4 en 320/375/768/1280 px y con teclado; criterio 6 con la lista de chequeo.
