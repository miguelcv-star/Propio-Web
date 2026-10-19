# 0009 — Sincronización de un solo sentido: Aurex → sitio

**Estado:** borrador  ·  **Fecha:** 2026-10-15  ·  **Brief:** §3 (fuera de alcance), §5.3, §14.5

> **Actualización (spec 0010):** el catálogo y las cifras ya no vienen de una instantánea `data/*.json` empujada por Propio: el sitio las lee de `GET /publico/inmuebles` y `GET /publico/cifras`. Esta spec queda como referencia del contrato de `data/` si algún día se vuelve a usar.

## Problema y objetivo
Algunas secciones («Oportunidades», «Aurex en acción», cifras de mercado, casos) pueden alimentarse con información
de Aurex, pero **el sitio no puede tener acceso a Aurex**. Se define el **contrato** de la instantánea que Aurex
genera y empuja, y cómo el sitio la consume y degrada. Es la única vía de datos Aurex → sitio.

**Fuera de alcance:** publicar oportunidades **en tiempo real** (el brief lo excluye en v1); exponer la base de
inmuebles; el exportador en sí, que **es una spec del lado de Aurex** (`03_dev_Aurex/docs/specs/`, a abrir cuando se
apruebe esta); los leads (sentido contrario, 0005).

## Contrato (`data/*.json`)
- Raíz de cada archivo: `schema_version` (entero), `generado_en` (ISO-8601 con zona) y los datos.
- **Archivos previstos:** `oportunidades.json` (selección curada, pocas decenas), `mercado.json` (cifras agregadas por
  zona/tipo), `casos.json` (0007). Cada archivo se pide **solo cuando una página lo usa**.
- **Lista blanca** de campos (la define y prueba el exportador): p. ej. título genérico, barrio/zona (no dirección),
  tipo, precio, área, rango de score, foto autorizada. **Nunca:** contactos o anunciantes, notas, seguimiento,
  simulaciones, usuarios, ids internos, URLs de portales (salvo decisión expresa) ni coordenadas exactas.
- **Instantánea completa** que reemplaza a la anterior, escrita de forma atómica; pocas decenas de KB en total.
- **Publica Aurex** (script o tarea programada suya) en el repo/hosting del sitio con credenciales que viven solo del
  lado de Aurex; el hosting no recibe credenciales de Aurex.

## Criterios de aceptación (lado sitio)
1. **Dado** un archivo con `schema_version` conocido y datos válidos, **cuando** carga la página, **entonces** muestra
   su sección y «Actualizado el <fecha>» a partir de `generado_en`.
2. **Dado** un archivo ausente, vacío, corrupto, con `schema_version` desconocido o con campos fuera de la lista
   blanca, **entonces** esa sección se oculta o muestra su texto fijo y la página sigue funcionando sin errores visibles.
3. **Dado** un `generado_en` de hace más de **N días** (configurable, p. ej. 30), **entonces** la sección muestra un
   aviso de datos desactualizados o se oculta.
4. **Dado** el sitio completo, **entonces** no hay ninguna petición a un dominio de Aurex: el único `fetch` de datos
   es a rutas `data/…` del mismo origen (verificado en el HTML/JS publicados).
5. **Dado** un `data/*.json` publicado, **entonces** `verificar.py` lo valida contra su esquema, rechaza campos no
   listados y claves sospechosas (`telefono`, `email`, `nota`, `usuario`, `token`, coordenadas con más de 3 decimales) y
   mide su tamaño (falla sobre el tope).
6. **Dado** que Aurex esté apagado o caído, **entonces** el sitio sigue sirviendo la última instantánea.
7. **Dado** los datos mostrados, **entonces** cada cifra de precio/score lleva el texto de que es una referencia, no
   un avalúo ni una garantía (0008).

## Criterios del lado Aurex (para su propia spec)
a. El exportador arma cada JSON campo por campo (lista blanca) y una prueba demuestra que un campo nuevo de la base
**no** aparece hasta añadirlo. b. Prueba de que ningún dato de contacto, nota, seguimiento ni simulación sale. c. Escritura
atómica y reintento seguro. d. Registro de qué se publicó y cuándo. e. Un fallo del exportador no toca el último
archivo bueno.

## Decisiones y riesgos
- **Preguntas abiertas:** ¿qué se publica primero? (propongo `mercado.json` con cifras agregadas: el menor riesgo de
  datos de terceros); frecuencia (semanal/quincenal, alineada al Radar); mecanismo de publicación (git push al repo del
  sitio vs. subida al hosting); si habrá fotos de inmuebles (derechos de imagen de los portales: probablemente **no**).
- **Riesgo legal:** los avisos pertenecen a portales y anunciantes; republicarlos con foto/precio puede ser un problema.
  Empezar con cifras agregadas y avisos propios o autorizados.
- Riesgo: publicar por error un campo sensible. Mitigación: lista blanca + prueba en Aurex + verificador aquí (doble
  llave).

## Plan de pruebas
- `node --test tests/datos.test.js` ← criterios 1–3, 6 (carga y degradación con archivos buenos/malos/viejos).
- `scripts/verificar.py` ← criterios 4, 5 (esquema, claves prohibidas, tamaño, sin dominios de Aurex).
- `tests/` de Aurex (su spec) ← criterios a–e. A mano ← criterio 7 y que la sección se ve bien con y sin datos.
