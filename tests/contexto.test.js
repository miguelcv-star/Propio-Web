// Criterio 9 de la spec 0001 (y 7 de la 0003): la intención viaja en la URL sin datos personales.
const test = require("node:test");
const assert = require("node:assert/strict");
const c = require("../assets/js/contexto.js");

test("hay exactamente las cinco intenciones del brief", () => {
  assert.deepEqual([...c.INTENCIONES].sort(), [
    "comprar-o-arrendar-para-mi", "conocer-precio", "empezar-a-invertir",
    "invertir-por-mi-cuenta", "vender-o-arrendar"]);
});

test("intencionDesde lee ?intencion= válido", () => {
  assert.equal(c.intencionDesde("?intencion=conocer-precio"), "conocer-precio");
  assert.equal(c.intencionDesde("?utm_source=x&intencion=vender-o-arrendar"), "vender-o-arrendar");
});

test("un valor desconocido, vacío o ausente se ignora (null)", () => {
  assert.equal(c.intencionDesde("?intencion=hackeame"), null);
  assert.equal(c.intencionDesde("?intencion="), null);
  assert.equal(c.intencionDesde(""), null);
  assert.equal(c.intencionDesde("?intencion=%3Cscript%3E"), null);
});

test("urlConIntencion arma la ruta con la intención y rechaza una inválida", () => {
  assert.equal(c.urlConIntencion("/conocer-precio/", "conocer-precio"), "/conocer-precio/?intencion=conocer-precio");
  assert.equal(c.urlConIntencion("/conocer-precio/", "otra"), "/conocer-precio/");
});
