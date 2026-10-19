# Especificaciones de Aurex Web

Salen de `../../20261015-Brief_Desarrollo_Pagina_Publica_Aurex.md` y siguen el proceso de `../../AGENTS.md`:
spec corta → **aprobación del usuario** → pruebas primero → código → probar en local → recién ahí publicar.
Plantilla: `_plantilla.md`. Estado inicial de todas: `borrador`.

| # | Spec | Depende de | Brief |
|---|---|---|---|
| 0001 | Estructura, navegación y plantilla de página | — | §4, §10, §11 |
| 0002 | Portada | 0001 | §1, §2, §5 |
| 0003 | Páginas por intención (plantilla + 4) | 0001, 0005 | §6.1–6.4 |
| 0004 | Comprar o arrendar para uso propio | 0001, 0005 | §6.5 |
| 0005 | Formularios y captura de leads | 0001, 0008 | §7, §8, §12 |
| 0006 | WhatsApp y analítica | 0001 | §7, §9 |
| 0007 | Casos reales y comunidad (Radar) | 0001, 0005 | §5.4, §5.5 |
| 0008 | Transparencia, privacidad y términos | 0001 | §5.6, §12 |
| 0009 | Sincronización Aurex → sitio (contrato) | 0001 | §3, §5.3 |
| 0010 | Conexión del sitio con la API pública de Propio (reemplaza la regla de 0005/0009) | 0001, 0005 | §7, §8, §12 |

## Orden de ejecución recomendado
1. **0001** (base + verificador) → 2. **0002** (portada) → 3. **0005** con un destino simulado + **0003** con una
intención completa → 4. resto de intenciones y **0004** → 5. **0008** (textos con el usuario) → 6. **0007** y
**0006** → 7. **0009** (y su spec gemela en Aurex).
**Condición para publicar:** 0005 criterio 9 (envío real verificado) y 0008 criterio 5 (textos aprobados).

## Decisiones abiertas (brief §16) — las resuelve el usuario, no se suponen
| Decisión | Afecta | Bloquea |
|---|---|---|
| ~~¿Apruebas el generador `scripts/construir.py`?~~ | 0001 | **Resuelto: aprobado**, implementado |
| Proveedor/destino de leads y quién responde cada categoría | 0005, 0007 | publicar |
| Número oficial de WhatsApp | 0006 | publicar el botón |
| Herramienta de analítica (idealmente sin cookies) | 0006 | medir (no bloquea construir) |
| Logo e identidad definitivos | 0002 | pulido visual |
| Casos autorizados (fotos, cifras) | 0007 | publicar casos |
| Textos legales aprobados / responsable de datos | 0008 | publicar |
| Hosting y dominio | todas | publicar |
| ¿Sitio separado de Aurex? | — | **Resuelto: sitio separado** (ver `AGENTS.md`) |
| Qué datos de Aurex se publican y con qué frecuencia | 0009 | secciones con datos |
| ¿Correo automático al enviar un lead? | 0005 | no (fuera de v1 salvo que se pida) |

## Verificación común
`scripts/verificar.py` (stdlib) y `node --test tests/` (sin dependencias) son las «pruebas» de todas las specs; se
crean con 0001 y crecen con cada una. Nada se publica si fallan.
