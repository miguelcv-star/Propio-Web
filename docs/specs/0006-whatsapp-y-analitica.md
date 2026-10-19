# 0006 — Botón de WhatsApp y analítica de conversiones

**Estado:** borrador  ·  **Fecha:** 2026-10-15  ·  **Brief:** §7 (`WhatsAppCTA`), §9

## Problema y objetivo
Dar un segundo camino de contacto (WhatsApp) y poder **medir qué intenciones generan conversaciones**, que es el
objetivo de la primera versión, sin recoger datos personales.

**Fuera de alcance:** elegir la herramienta de analítica (decisión del usuario); chatbots; automatizar respuestas.

## Diseño
- **`config.js`** guarda en un solo lugar: número oficial de WhatsApp y un mensaje inicial por intención. Ningún
  componente lo repite.
- **`WhatsAppCTA`:** enlace `https://wa.me/<número>?text=<mensaje por intención>`, en pestaña nueva con
  `rel="noopener noreferrer"`, que emite el evento `whatsapp_clicked`.
- **`track(evento, datos)`** (`assets/js/track.js`): único punto de analítica. **Por defecto no hace nada**; solo
  envía si el usuario aprobó una herramienta y esta está configurada. Eventos: `public_page_view`,
  `intent_selected`, `lead_form_started`, `lead_form_submitted`, `lead_form_error`, `whatsapp_clicked`,
  `radar_signup_submitted`, `case_study_opened`, `report_downloaded`, `cta_clicked`. Cada uno lleva, si existen:
  ruta, intención, fuente, campaña UTM y marca de tiempo.

## Criterios de aceptación
1. **Dado** una intención, **cuando** se pulsa el botón de WhatsApp, **entonces** abre `wa.me` con el número de
   `config.js` y el mensaje de esa intención, en pestaña nueva, y se emite `whatsapp_clicked`.
2. **Dado** `config.js` sin número, **entonces** el botón de WhatsApp no se muestra (no queda un enlace roto).
3. **Dado** el mensaje precargado, **entonces** no contiene datos del visitante ni del formulario (solo un texto
   fijo por intención).
4. **Dado** cada evento de la lista, **cuando** ocurre su acción, **entonces** `track` lo recibe con los campos
   disponibles y **ningún** dato personal ni texto libre (nombre, correo, teléfono, mensaje).
5. **Dado** que no hay herramienta de analítica configurada, **entonces** la página no carga ningún script de
   terceros y `track` no falla ni hace peticiones.
6. **Dado** una herramienta aprobada, **entonces** se carga solo después del consentimiento que la ley o el
   proveedor exijan (si usa cookies) y su dominio queda anotado en `AGENTS.md` y en la política de privacidad.
7. **Dado** los parámetros UTM de la URL, **entonces** se capturan una vez, se pasan a `track` y al lead (0005) y
   no se guardan en el navegador más allá de la sesión.

## Decisiones y riesgos
- **Preguntas abiertas:** número oficial de WhatsApp y herramienta de analítica (se prefiere una que no use cookies
  ni ponga a terceros en el sitio; si se elige una con cookies, hace falta aviso de cookies).
- Sin analítica aprobada, `track` ya está cableado y las pruebas pasan con un destino simulado: encenderla después
  es cambiar `config.js`.
- Riesgo: el número de WhatsApp en un sitio público recibe spam; se acepta y se atiende con la cuenta de empresa.

## Plan de pruebas
- `node --test tests/track.test.js` ← criterios 3, 4, 5, 7 (carga útil sin datos personales, sin red por defecto).
- `node --test tests/whatsapp.test.js` ← criterios 1–3.
- `scripts/verificar.py` ← que no hay scripts externos sin aprobar (criterios 5–6).
- A mano ← eventos en modo de prueba de la herramienta elegida.
