# 0008 — Transparencia, privacidad y términos

**Estado:** borrador  ·  **Fecha:** 2026-10-15  ·  **Brief:** §5.6, §12, §13 (contenido)

## Problema y objetivo
El sitio hace afirmaciones sobre precios y oportunidades y recoge datos personales. Debe decir con claridad **qué no
promete** y **qué hace con los datos**. Sin esto no se pueden recibir leads reales.

**Fuera de alcance:** redactar el texto jurídico definitivo (lo aprueba el usuario con su abogado); cookies más allá de
lo que exija la herramienta de analítica elegida (0006).

## Contenido
- **Bloque de transparencia** (portada y páginas por intención, con enlace a `/terminos/`): los análisis dependen de la
  calidad y fecha de los datos · una oportunidad no garantiza rentabilidad · toda compra requiere validación técnica,
  jurídica y financiera · los escenarios son estimaciones, no resultados asegurados · las comisiones o relaciones
  comerciales se informan de forma transparente.
- **`/privacidad/`:** quién es responsable de los datos, qué se recoge (formularios, WhatsApp, analítica), para qué,
  con qué proveedor se procesa, cuánto tiempo se conserva, cómo ejercer derechos de consulta/corrección/supresión y
  contacto. Texto de consentimiento de comunicaciones usado en los formularios.
- **`/terminos/`:** naturaleza informativa del contenido, referencia de mercado ≠ avalúo oficial, no es asesoría
  jurídica ni financiera, alcance del servicio de representación (remite a 0004), propiedad del contenido.

## Criterios de aceptación
1. **Dado** la portada y cada página por intención, **entonces** incluyen el bloque de transparencia con las cinco
   afirmaciones y un enlace funcional a `/terminos/`.
2. **Dado** cualquier formulario, **entonces** el consentimiento muestra el texto aprobado y enlaza a `/privacidad/`;
   no se puede enviar sin marcarlo y la casilla **no** viene premarcada.
3. **Dado** `/privacidad/`, **entonces** nombra al responsable, los datos recogidos, la finalidad, el proveedor que
   los recibe, el tiempo de conservación y el canal para ejercer derechos, y coincide con lo que de verdad hace el
   sitio (revisión contra 0005 y 0006).
4. **Dado** cualquier texto del sitio, **entonces** no contiene promesas de rentabilidad ni «garantizado/asegurado»
   (verificador de palabras prohibidas).
5. **Dado** que los textos legales no están aprobados (`aprobado: false` en su configuración), **entonces** el sitio
   **no recibe leads reales**: los formularios quedan en «Estamos configurando el envío» (0005) y `verificar.py`
   falla si se intenta publicar con envío activo y texto sin aprobar.
6. **Dado** `/privacidad/` y `/terminos/`, **entonces** son indexables, enlazadas desde el pie de todas las páginas.

## Decisiones y riesgos
- **Pendiente del usuario:** razón social/responsable, correo de contacto de privacidad, proveedor de leads, tiempo de
  conservación y aprobación del texto por un abogado (Ley 1581 de 2012 y su reglamento). El agente deja un borrador
  con huecos marcados `[POR DEFINIR]` y **no** lo presenta como definitivo.
- Riesgo: política desfasada de lo que hace el sitio. Mitigación: criterio 3 se revisa cada vez que cambie 0005 o 0006.

## Plan de pruebas
- `scripts/verificar.py` ← criterios 1, 2 (casilla sin `checked`), 4, 5, 6 (y que no queden `[POR DEFINIR]` al publicar).
- Revisión del usuario/abogado ← criterios 3 y 5. A mano: flujo de consentimiento en un formulario.
