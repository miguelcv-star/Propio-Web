# 0007 — Casos reales y comunidad (Radar Aurex)

**Estado:** borrador  ·  **Fecha:** 2026-10-15  ·  **Brief:** §5.4, §5.5, §7 (`CaseStudyCard`, `RadarSignup`)

## Problema y objetivo
Dar prueba (casos) sin engañar, y captar a quienes quieren el reporte quincenal («Radar Aurex»). Un caso mal
presentado (proyección vendida como resultado) daña la confianza y puede ser un problema legal, así que la
**honestidad del dato** manda sobre el diseño.

**Fuera de alcance:** enviar el Radar (se hace fuera del sitio); páginas de detalle largas por caso; cuentas de
miembros.

## Casos (`CaseStudyCard`)
Campos: `title`, `locationLabel` (sin dirección sensible: barrio o zona), `category`, `coverImage`, `resultType`
(**realizado / proyectado / histórico**), `summary`, `href`; y por tarjeta: contexto, inversión inicial,
intervención, resultado, aprendizaje. Los casos viven en `data/casos.json` (a mano o desde Aurex, ver 0009), no en el
HTML. Se muestran **2 o 3** en la portada y todos en `/casos/`.

## Comunidad (`RadarSignup`)
Mensaje: «Recibe cada 15 días un reporte privado con oportunidades inmobiliarias filtradas, casos de estudio y
aprendizajes de operaciones reales.» CTA: «Quiero recibir el Radar Aurex». Formulario mínimo: nombre, WhatsApp o
correo, intención de interés, consentimiento (mismo motor que 0005, con la fuente `radar`).

## Criterios de aceptación
1. **Dado** un caso, **entonces** muestra una etiqueta visible con texto («Resultado realizado», «Proyección»,
   «Caso histórico») además del color, y una proyección nunca usa el estilo ni las palabras de un resultado realizado.
2. **Dado** un caso sin evidencia fotográfica o económica suficiente (`evidencia` incompleta en el dato), **entonces**
   no se muestra como éxito comercial: solo como «aprendizaje del proceso», claramente etiquetado.
3. **Dado** un caso sin `autorizado = true` (o sin `anonimizado = true`), **entonces** no se publica; el verificador
   rechaza el `casos.json` si algún caso publicado no cumple.
4. **Dado** un caso, **entonces** ninguna foto ni texto incluye dirección exacta, nombres de terceros ni datos
   personales (lista de chequeo antes de publicar).
5. **Dado** `casos.json` ausente, vacío o inválido, **entonces** la sección de casos se oculta o muestra «Pronto
   publicaremos casos» sin romper la página.
6. **Dado** la sección Comunidad, **cuando** se envía el formulario, **entonces** se comporta como en 0005
   (validación, consentimiento, estados, sin doble envío) y se emite `radar_signup_submitted`.
7. **Dado** una tarjeta de caso, **cuando** se abre, **entonces** se emite `case_study_opened` y la tarjeta entera es
   un enlace con foco visible.

## Decisiones y riesgos
- **Pendiente del usuario:** qué casos existen, cuáles están **autorizados**, con qué fotos y qué cifras. Mientras no
  haya ninguno aprobado, se publica el esqueleto con «Pronto publicaremos casos» (no se inventan casos de ejemplo).
- El dato del caso incluye las banderas `resultType`, `autorizado`, `anonimizado` y `evidencia` precisamente para que
  el verificador pueda hacer cumplir las reglas en lugar de depender de la memoria de quien edite.
- El Radar crea una lista de datos personales: mismo destino y mismas exigencias de privacidad que 0005.

## Plan de pruebas
- `node --test tests/casos.test.js` ← criterios 1, 2, 5 (etiqueta por `resultType`, degradación).
- `scripts/verificar.py` ← criterio 3 (todo caso publicado autorizado y anonimizado) y alt/labels.
- `node --test tests/leads.test.js` (caso Radar) ← criterio 6.
- A mano ← criterios 4 y 7 con teclado y 320 px.
