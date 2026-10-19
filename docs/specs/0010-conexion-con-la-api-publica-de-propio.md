# 0010 — Conexión del sitio con la API pública de Propio

**Estado:** aprobada (decisión del usuario, 2026-10-18)  ·  **Fecha:** 2026-10-18  ·  Cambia la regla «el sitio nunca llama a Propio» de 0005 y 0009.
Del lado de Propio: specs 0024 (captura y búsqueda), 0025 (valoración) y 0026 (publicar tu inmueble), release v2.51.0.

## Problema y objetivo
El sitio debía enviar sus formularios a un servicio externo y esperar a que Propio «jalara» los leads. El usuario decidió
otra cosa: el sitio envía **directo** a una API pública mínima de Propio (`/publico/*`, apagada por defecto, sin sesión,
con lista cerrada de campos, límites y anti-bot) y también le pide el catálogo y las cifras. Objetivo: que cada intención
tenga su formulario funcionando de punta a punta, sin abrir ninguna otra puerta a Propio.

**Fuera de alcance:** subir fotos (van como enlaces); WhatsApp y analítica (0006); casos y comunidad (0007).

## Criterios de aceptación
1. **Dado** una página con formulario, **cuando** se envía, **entonces** el navegador llama SOLO a una de las rutas
   `/publico/contacto|busqueda|busqueda/pdf|valorar|vender|inmuebles|cifras` de la dirección de `assets/js/config.js`
   (una prueba lo verifica sobre todo el JS publicado).
2. **Dado** campos vacíos o inválidos (contacto, consentimiento, obligatorios de cada intención), **entonces** no se envía
   y cada error aparece junto a su campo con el foco en el primero.
3. **Dado** un envío válido, **entonces** el botón pasa a «Enviando…» sin permitir doble envío, el resultado se anuncia con
   `aria-live` y, si falla, el mensaje es accionable y lo escrito se conserva.
4. **Dado** el campo trampa (`sitio_web`) con valor, **entonces** el envío se descarta en silencio; el cuerpo lleva
   `tiempo_ms` y, si hay llave pública, el token de Turnstile.
5. **Dado** «compra o arrienda», **entonces** se muestra el reporte (hasta 20) y se puede bajar en PDF; **dado** «conoce el
   valor», **entonces** se muestra el rango con su confianza y el aviso de «estimación orientativa, no avalúo»; **dado**
   «vende», **entonces** exige aceptar el acuerdo de comisión y la respuesta es la misma pase o no los filtros.
6. **Dado** el catálogo y las cifras, **si la API falla**, **entonces** la página sigue funcionando con su texto fijo.
7. **Dado** el repositorio y lo servido, **entonces** no hay secretos, ni `localhost`, ni datos personales en URL,
   `localStorage` o consola; todo texto que viene de la API entra con `textContent`.
8. **Dado** `verificar.py --publicar`, **entonces** falla si quedan textos legales en BORRADOR, datos entre corchetes o la
   dirección de la API sin definir.

## Decisiones y riesgos
- La frontera sigue siendo de un solo sentido y mínima: el sitio solo conoce `/publico/*`; Propio no le entrega
  credenciales ni lee nada de él. La regla de `AGENTS.md` se reescribe en ese sentido.
- La dirección de la API vive en `assets/js/config.js` (pública); las pruebas locales la reemplazan con
  `scripts/servir_local.py` sin tocar el archivo.
- Turnstile solo se carga si `turnstileSiteKey` tiene valor (el host `challenges.cloudflare.com` está aprobado).
- Los textos legales de `privacidad`, `terminos` y `acuerdo-comision` son BORRADORES (con aviso visible): el usuario y su
  abogado los aprueban antes de publicar. El catálogo no incrusta imágenes de terceros: las fotos van como enlaces.

## Plan de pruebas
- `node --test "tests/*.test.js"` ← 2, 3, 4, 5 (lógica de `lib.js`); `tests/test_verificar.py` ← 1, 7, 8 y el contenido de las páginas.
- A mano (con `03_dev_Propio/scripts/probar_publico_local.sh`): cada formulario contra la API aislada, a 375 px y con teclado.
