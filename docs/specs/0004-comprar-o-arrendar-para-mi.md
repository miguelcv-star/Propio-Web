# 0004 — Comprar o arrendar para uso propio (representación del comprador)

**Estado:** borrador  ·  **Fecha:** 2026-10-15  ·  **Brief:** §6.5

## Problema y objetivo
Esta intención no es de inversión: el visitante busca un lugar para vivir o trabajar y paga por **ahorrar tiempo,
evitar errores, validar el precio y negociar mejor**. La página debe explicar el servicio de representación y
acompañamiento y **comunicar con transparencia cómo se cobra**, sin lenguaje de inversión ni promesas de descuento.

**Fuera de alcance:** el contrato real (lo redactan y aprueban el usuario y un abogado); calcular el ahorro de un
cliente concreto; cobros en línea; el formulario en sí (0005).

## Contenido de la página
- **Titular (`h1`):** «Encuentra un inmueble que funcione para tu vida, tu familia o tu negocio.» Propuesta:
  «Tú nos dices qué necesitas. Nosotros buscamos, filtramos, comparamos y te acompañamos hasta cerrar la operación.»
- **Secciones:** búsqueda por necesidades · comparación · validación del precio · shortlist · visitas · estrategia de
  oferta y negociación · acompañamiento del proceso · diseño o remodelación posterior.
- **Proceso en 6 pasos:** definimos la búsqueda → buscamos y filtramos → presentamos una shortlist → acompañamos las
  visitas → preparamos la oferta → negociamos y acompañamos el cierre (textos del brief).
- **Cómo se cobra** (bloque propio, visible, no en letra pequeña): fee inicial de activación (diagnóstico y búsqueda),
  acreditable contra el success fee si se cierra · success fee al cerrar · componente variable sobre el ahorro
  documentado con mínimo y máximo definidos antes · servicios opcionales (revisión técnica, diseño, remodelación,
  gestión). Se incluye el texto de remuneración del brief y la fórmula
  **Ahorro reconocido = referencia acordada − precio de cierre**, aclarando que la referencia se fija y registra
  **antes** de negociar y no se cambia después.
- **CTA principal:** «Quiero encontrar mi próximo inmueble» · **secundario:** «Quiero que me acompañen en la compra».

## Criterios de aceptación
1. **Dado** la página, **entonces** muestra los seis pasos, las ocho secciones de servicio y los dos CTA.
2. **Dado** el bloque «Cómo se cobra», **entonces** nombra los cuatro componentes (fee inicial acreditable, success fee,
   variable con mínimo y máximo, servicios opcionales) y la fórmula del ahorro, **sin cifras** (los valores salen de
   configuración y de la propuesta al cliente, no de la web) a menos que el usuario las apruebe.
3. **Dado** la página, **entonces** declara que Aurex **representa al comprador/arrendatario** y que cualquier comisión,
   relación o incentivo de vendedores, inmobiliarias o terceros se revela.
4. **Dado** la página, **entonces** NO promete descuentos, NO se presenta como asesoría jurídica, avalúo oficial ni
   inspección técnica (salvo profesional habilitado, que debe nombrarse) y NO usa el lenguaje de inversión
   («rentabilidad», «ROI», «oportunidad de inversión») en su texto principal.
5. **Dado** el CTA principal o secundario, **cuando** se pulsa, **entonces** abre el formulario con la intención
   `comprar_arrendar_uso_propio` y, según el CTA, `nivel_acompanamiento` distinto (búsqueda / acompañamiento).
6. **Dado** el formulario de esta intención, **entonces** pide los campos del brief (comprar o arrendar, tipo,
   zona, presupuesto máximo, área y habitaciones, parqueaderos, fecha objetivo, estado deseado, necesidades
   especiales, nivel de acompañamiento, contacto, consentimiento) y el lead queda marcado con
   `representacion_cliente = true`.

## Decisiones y riesgos
- **Es el texto más sensible del sitio (dinero y obligaciones):** el contenido lo escribe el agente como borrador y
  **lo aprueban el usuario y, idealmente, un abogado** antes de publicar. El verificador (0001) busca las palabras
  prohibidas del criterio 4.
- **No se publican porcentajes ni montos** hasta que el modelo económico esté cerrado; mostrar uno equivocado crea una
  expectativa difícil de retirar.
- Pendiente de contrato (no es de la web, pero la página no puede contradecirlo): duración, zonas, número de visitas,
  alcance de la negociación, cuándo nace el success fee y qué pasa si el cliente compra directo algo que Aurex le presentó.

## Plan de pruebas
- `scripts/verificar.py` ← criterios 1, 2 (presencia de bloques y fórmula), 4 (palabras prohibidas ausentes).
- `node --test tests/lead-config.test.js` ← criterios 5 y 6 (la configuración de esa intención).
- Revisión del usuario/abogado ← criterios 2–4 antes de publicar. A mano: ambos CTA con teclado.
