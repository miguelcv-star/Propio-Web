# Propio Web

Sitio público de Propio: inicio, **Invierte**, **Compra o arrienda**, **Vende** (publicar gratis, comisión solo si se vende),
**Conoce el valor** y catálogo de inmuebles publicados. Es una página **estática** (HTML + CSS + JS, sin dependencias) que solo
habla con las rutas públicas `/publico/*` de la API de Propio. Reglas y proceso: `AGENTS.md`; spec de la conexión:
`docs/specs/0010-conexion-con-la-api-publica-de-propio.md`; contrato de la API: `../03_dev_Propio/docs/publico-despliegue.md`.

```bash
python3 scripts/construir.py            # regenera las páginas desde src/
python3 scripts/verificar.py            # revisa el sitio (--publicar: exige dominio, API real y textos legales sin borrador)
python3 -m unittest discover -s tests   # pruebas del verificador y del generador
node --test "tests/*.test.js"           # pruebas del JS
```

Probar con la API de verdad (base desechable, nunca la real): `../03_dev_Propio/scripts/probar_publico_local.sh`
→ el sitio queda en `http://localhost:3012/`.

**Antes de publicar:** dominio real y `indexable: true` en `src/sitio.json`, `apiUrl` (y la llave pública de Turnstile) en
`assets/js/config.js` y en `_headers`, y los textos legales aprobados (hoy son borradores).
