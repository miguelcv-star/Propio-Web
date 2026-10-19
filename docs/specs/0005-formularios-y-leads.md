# 0005 — Formularios de contacto y captura de leads

**Estado:** borrador  ·  **Fecha:** 2026-10-15  ·  **Brief:** §7 (`LeadForm`), §8, §10, §12

> **Actualización (spec 0010):** el destino ya no es un servicio externo: los formularios envían a las rutas públicas `/publico/*` de Propio. Lo de aquí sobre campos, estados y accesibilidad sigue vigente.

## Problema y objetivo
Convertir visitantes en conversaciones calificadas: un formulario por intención (más el del Radar, 0007) que deja un
**lead clasificado** (intención, fuente, consentimiento) en un destino seguro, **sin que el navegador toque la base ni
la API de Aurex**.

**Fuera de alcance:** CRM, correos automáticos de respuesta, crear cuentas Aurex, el destino definitivo (decisión del
usuario, ver abajo), integración de Aurex para traer los leads (spec propia del lado de Aurex).

## Diseño
- **Un solo componente `LeadForm`** (`assets/js/leads.js`) que recibe una configuración por intención
  (`intent`, `fields`, `submitLabel`, `source`, `successMessage`); los campos por intención son los del brief §6.
  No hay cinco formularios con lógica propia.
- **Destino aislado:** `leads.js` envía por una sola función `enviarLead(lead)` a la URL de `assets/js/config.js`.
  Esa URL es de un **servicio de captura aprobado por el usuario** o de un endpoint mínimo aparte que solo guarda
  leads. Nunca la API de Aurex. Sin destino configurado, el formulario muestra «Estamos configurando el envío» y no
  simula éxito.
- **Lead enviado** (brief §8, solo lo que el visitante o la página aporta): `nombre`, `email`, `telefono`, `intencion`,
  `subtipo`, `nivel_acompanamiento`, `representacion_cliente`, `presupuesto_rango`, `zona`, `tipo_inmueble`,
  `operacion`, `horizonte`, `experiencia`, `mensaje`, `fuente`, `utm_source/medium/campaign`,
  `consentimiento_comunicaciones`, `consentimiento_fecha`. `estado`, `id`, `creado_en`, `notas_internas` los pone el
  destino (estado inicial `nuevo`), nunca el navegador.

## Criterios de aceptación
1. **Dado** una intención, **cuando** se abre su formulario, **entonces** muestra exactamente los campos de su
   configuración, cada uno con `label` asociado, y trae la intención (de la página o del parámetro).
2. **Dado** campos obligatorios vacíos o inválidos (contacto sin correo ni WhatsApp válido, sin consentimiento),
   **cuando** se envía, **entonces** no se envía, cada error aparece junto a su campo (`aria-describedby`) y el foco
   va al primero con error.
3. **Dado** un envío válido, **cuando** se pulsa enviar, **entonces** el botón pasa a «Enviando…», se deshabilita (sin
   doble envío) y, al terminar, el resultado se anuncia con `aria-live`: éxito con el `successMessage`, o error
   recuperable con «Reintentar» que conserva lo escrito.
4. **Dado** el envío, **entonces** el lead incluye `intencion`, `fuente` (página/campaña), UTM si existen y
   `consentimiento_comunicaciones = true` con `consentimiento_fecha` (ISO, zona incluida).
5. **Dado** el campo oculto antispam (honeypot) con valor, **entonces** el envío se descarta en silencio sin avisar al
   bot; un envío humano normal no lo ve ni lo rellena.
6. **Dado** el endpoint caído, lento (> 15 s) o con error 4xx/5xx, **entonces** el usuario ve un mensaje accionable
   (reintentar o escribir por WhatsApp) y nada se pierde.
7. **Dado** el formulario, **entonces** no guarda datos personales en `localStorage`, URL, ni los manda a la analítica
   ni a la consola; el mensaje libre se envía como texto (el destino lo sanea al mostrarlo).
8. **Dado** el repositorio y el HTML publicado, **entonces** no hay llaves ni secretos en el código del formulario
   (solo una URL pública de envío).
9. **Dado** que existe un destino real configurado, **cuando** se hace un envío de prueba, **entonces** el lead
   **aparece allí** con intención, fuente y consentimiento. **Hasta verificarlo con un envío real, esta spec no se
   da por implementada.**

## Decisiones y riesgos
- **Pregunta abierta (bloqueante): proveedor/destino de leads.** Hay que elegirlo antes del criterio 9 (ver lista de
  decisiones en `README.md`). El resto se construye detrás de `enviarLead`.
- El sitio **no** valida en servidor: lo hace el destino. Se exige al elegirlo: validación/sanitizado, límite de
  frecuencia (rate limiting), antispam y no registrar datos sensibles en logs; el brief los pide (§12).
- **Datos personales de visitantes** (Ley 1581 de Colombia): la política de privacidad y el aviso de consentimiento
  (0008) deben estar aprobados antes de recibir un solo lead real.
- Aurex jala los leads del destino con sus credenciales; el sitio no conoce Aurex.

## Plan de pruebas
- `node --test tests/leads.test.js` ← criterios 1–5, 7 (validación, estados, honeypot, carga útil sin datos en URL).
- `node --test tests/leads-red.test.js` con `fetch` simulado (OK, 500, timeout, sin destino) ← criterios 3, 6.
- `scripts/verificar.py` ← criterio 8 (patrones de secretos) y que cada `input` tiene `label`.
- A mano ← criterio 9 con el destino real, 320–390 px, teclado, red lenta.
