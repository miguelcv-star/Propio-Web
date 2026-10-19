# 0003 — Páginas por intención (plantilla + cuatro primeras)

**Estado:** borrador  ·  **Fecha:** 2026-10-15  ·  **Brief:** §6.1–6.4, §11

## Problema y objetivo
Cada intención necesita su propia página con una explicación relevante y su formulario. Se construye **una
plantilla reutilizable** alimentada por un objeto de contenido por intención, para no duplicar lógica ni HTML.
Esta spec cubre la plantilla y cuatro intenciones; **Comprar o arrendar para uso propio** tiene spec aparte (0004)
por su modelo económico.

**Fuera de alcance:** el formulario en sí (0005); la intención 5 (0004); casos/Radar (0007).

## Plantilla
Un solo `h1` (titular de la intención) · subtítulo · secciones del brief como bloques con título y texto ·
**CTA principal** que lleva al formulario de la misma página · formulario `LeadForm` configurado para la intención ·
enlaces internos a casos y comunidad · bloque corto de límites (de 0008). El contenido vive en
`src/intenciones/<ruta>.json` (o equivalente definido en 0001), no en el HTML.

## Contenido por intención
| Ruta | Titular (brief) | Secciones | CTA |
|---|---|---|---|
| `/vender-o-arrendar/` | «Entiende el valor de tu inmueble y define la mejor estrategia para venderlo o arrendarlo.» | análisis de precio · venta vs. arriendo · presentación y remodelación · comercialización · gestión de contactos y visitas | Quiero analizar mi inmueble |
| `/conocer-precio/` | «Conoce un rango de mercado explicado con comparables y supuestos visibles.» | qué analiza Aurex · referencia de mercado vs. informe ampliado · factores que mueven el precio | Quiero conocer el valor de mi inmueble |
| `/invertir-por-mi-cuenta/` | «Busca y compara oportunidades inmobiliarias con datos antes de decidir por tu cuenta.» | reportes Aurex · comparables y score · simulador compra–obra–salida · comunidad · límites del análisis | Quiero explorar oportunidades |
| `/empezar-a-invertir/` | «Pasa de querer invertir a tener un plan inmobiliario concreto.» | diagnóstico de objetivos · definición de estrategia · selección de tipo de activo · análisis de oportunidades · acompañamiento opcional | Quiero comenzar mi plan de inversión |

## Criterios de aceptación
1. **Dado** cada una de las cuatro rutas, **cuando** se abre, **entonces** muestra su titular como único `h1`, todas
   sus secciones del cuadro y su CTA, con `title`/`description` propios (no una palabra cambiada de otra página).
2. **Dado** el CTA principal, **cuando** se pulsa, **entonces** lleva al formulario de esa página (ancla) y el
   formulario ya trae la intención correcta.
3. **Dado** `/conocer-precio/`, **entonces** el texto distingue **referencia de mercado** de **avalúo oficial** y no
   promete un avalúo.
4. **Dado** `/invertir-por-mi-cuenta/` y `/empezar-a-invertir/`, **entonces** no prometen rentabilidad ni
   resultados asegurados y enlazan a los límites del análisis.
5. **Dado** las cuatro páginas, **entonces** salen de la misma plantilla y de contenido en datos: agregar o cambiar
   una sección no exige tocar la plantilla.
6. **Dado** cada página, **entonces** tiene enlaces internos a `/casos/` y `/comunidad/`.
7. **Dado** una página con la intención en la URL (`?intencion=`), **entonces** se usa solo para precargar el
   formulario y la analítica; un valor desconocido se ignora sin error.

## Decisiones y riesgos
- **Redacción:** los titulares son los del brief; el texto de cada sección lo redacta el agente en borrador corto
  y lo **aprueba el usuario** antes de publicar (no se inventan cifras, plazos ni precios).
- «Simulador compra–obra–salida» se **describe** en la página; **no** se incluye un simulador interactivo en esta
  versión (sería otra spec; el cálculo vive en Aurex).
- Riesgo de contenido duplicado para SEO: cada página tiene texto propio suficiente; no se clonan párrafos.

## Plan de pruebas
- `scripts/verificar.py` ← criterios 1, 5 (títulos únicos, un `h1`, secciones presentes) y 6 (enlaces).
- `node --test tests/intencion-param.test.js` ← criterio 7.
- Revisión de texto con el usuario ← criterios 3 y 4 (sin frases prohibidas: «garantizado», «asegurado», «avalúo oficial»
  como oferta); el verificador busca esas palabras.
