// Spec 0010: lógica de los formularios (validación, cuerpo de la API pública, errores, formato). Sin DOM ni red.
const test = require("node:test");
const assert = require("node:assert/strict");
const L = require("../assets/js/lib.js");

const persona = { nombre: "Ana Pérez", telefono: "300 123 4567", email: "", consentimiento: true, sitio_web: "" };

test("sin teléfono ni correo, o sin consentimiento, no valida", () => {
  const e = L.validar("invierte", { nombre: "Ana Pérez", consentimiento: false });
  assert.ok(e.telefono && e.consentimiento);
  assert.deepEqual(L.validar("invierte", persona), {});
});

test("teléfono y correo mal escritos se señalan", () => {
  assert.ok(L.validar("invierte", { ...persona, telefono: "123" }).telefono);
  assert.ok(L.validar("invierte", { ...persona, telefono: "", email: "no-es-correo" }).email);
  assert.deepEqual(L.validar("invierte", { ...persona, telefono: "", email: "a@b.co" }), {});
});

test("valorar exige motivo, tipo, área y ubicación", () => {
  const e = L.validar("valorar", persona);
  assert.ok(e.motivo && e.tipo_inmueble && e.area_construida && e.localidad);
  const ok = { ...persona, motivo: "vender", tipo_inmueble: "casa", area_construida: "80", localidad: "Suba" };
  assert.deepEqual(L.validar("valorar", ok), {});
  assert.ok(L.validar("valorar", { ...ok, area_construida: "5" }).area_construida);
});

test("vender exige el acuerdo de comisión y valida las fotos", () => {
  const base = { ...persona, operacion: "venta", tipo_inmueble: "casa", titulo: "Casa bonita", descripcion: "Casa de dos pisos",
    precio: "500000000", area_construida: "120", barrio: "Chicó" };
  assert.ok(L.validar("vender", base).acepta_comision);
  assert.deepEqual(L.validar("vender", { ...base, acepta_comision: true }), {});
  assert.ok(L.validar("vender", { ...base, acepta_comision: true, fotos: "javascript:alert(1)" }).fotos);
  assert.ok(L.validar("vender", { ...base, acepta_comision: true, fotos: Array(9).fill("https://x.co/a.jpg").join("\n") }).fotos);
});

test("millones a pesos acepta coma decimal y rechaza lo inválido", () => {
  assert.equal(L.millonesAPesos("680"), 680000000);
  assert.equal(L.millonesAPesos("1,5"), 1500000);
  assert.equal(L.millonesAPesos(""), null);
  assert.equal(L.millonesAPesos("abc"), null);
  assert.equal(L.millonesAPesos("-3"), null);
});

test("el plazo se convierte en rango de meses", () => {
  assert.deepEqual(L.plazoDe("3-6"), { plazo_min_meses: 3, plazo_max_meses: 6 });
  assert.deepEqual(L.plazoDe("12+"), { plazo_min_meses: 12, plazo_max_meses: null });
  assert.deepEqual(L.plazoDe(""), {});
});

test("el cuerpo de invierte lleva presupuesto en pesos, plazo, consentimiento y tiempo", () => {
  const c = L.cuerpo("invierte", { ...persona, presupuesto_max: "600", plazo: "1-3", mensaje: "hola" },
    { tiempo_ms: 9000.4, turnstile: "tok", prefijoMensaje: "[Empezar a invertir]" });
  assert.equal(c.presupuesto_max, 600000000);
  assert.equal(c.plazo_min_meses, 1);
  assert.equal(c.consentimiento, true);
  assert.equal(c.tiempo_ms, 9000);
  assert.equal(c.turnstile, "tok");
  assert.equal(c.mensaje, "[Empezar a invertir] hola");
  assert.ok(!("presupuesto_min" in c) && !("email" in c));          // lo vacío no se envía
});

test("el cuerpo nunca trae campos que decide el servidor", () => {
  for (const tipo of ["invierte", "busqueda", "valorar", "vender"]) {
    const c = L.cuerpo(tipo, { ...persona, operacion: "venta", motivo: "vender", area_construida: "80" }, {});
    for (const prohibido of ["origen", "estado", "finalidad", "responsable_id", "lead_id", "estado_lead"]) {
      assert.ok(!(prohibido in c), `${tipo} trae ${prohibido}`);
    }
  }
});

test("el cuerpo de la búsqueda convierte presupuesto, área y habitaciones", () => {
  const c = L.cuerpo("busqueda", { ...persona, operacion: "arriendo", presupuesto_max: "3,5", area_min: "60", habitaciones_min: "2" }, {});
  assert.equal(c.operacion, "arriendo");
  assert.equal(c.presupuesto_max, 3500000);
  assert.equal(c.area_min, 60);
  assert.equal(c.habitaciones_min, 2);
});

test("el cuerpo de vender separa las fotos por línea y manda la aceptación", () => {
  const c = L.cuerpo("vender", { ...persona, operacion: "venta", tipo_inmueble: "casa", titulo: "Casa bonita",
    descripcion: "Casa de dos pisos", precio: "500000000", area_construida: "120", acepta_comision: true,
    fotos: "https://x.co/1.jpg\n\nhttps://x.co/2.jpg" }, {});
  assert.deepEqual(c.fotos, ["https://x.co/1.jpg", "https://x.co/2.jpg"]);
  assert.equal(c.acepta_comision, true);
  assert.equal(c.precio, 500000000);
});

test("la URL de la API se arma sin dobles barras", () => {
  assert.equal(L.urlApi("https://api.propio.co/", L.RUTAS.busqueda), "https://api.propio.co/publico/busqueda");
});

test("formato de pesos y millones", () => {
  assert.equal(L.formatoPesos(682000000), "$682.000.000");
  assert.equal(L.formatoPesos(null), "—");
  assert.equal(L.formatoMillones(682000000), "$682 M");
  assert.equal(L.formatoMillones(3500000), "$3,5 M");
});

test("los mensajes de error son accionables y no filtran detalles", () => {
  assert.match(L.mensajeDeError(429), /muchas solicitudes/);
  assert.match(L.mensajeDeError(0), /conectarnos/);
  assert.match(L.mensajeDeError(503), /no está disponible/);
  assert.equal(L.mensajeDeError(422, "Debes autorizar el tratamiento de tus datos."), "Debes autorizar el tratamiento de tus datos.");
  assert.doesNotMatch(L.mensajeDeError(500, "Traceback password=secreto"), /secreto/);
});

test("enviar devuelve el error del servidor sin lanzar", async () => {
  const fetchFn = async () => ({ ok: false, status: 429, json: async () => ({ detail: "x" }) });
  const r = await L.enviar(fetchFn, "https://api.propio.co/publico/contacto", { a: 1 });
  assert.equal(r.ok, false);
  assert.equal(r.status, 429);
  assert.match(r.error, /muchas solicitudes/);
});

test("enviar con la red caída responde un error recuperable, no una excepción", async () => {
  const r = await L.enviar(async () => { throw new Error("red"); }, "https://x", {});
  assert.equal(r.ok, false);
  assert.equal(r.status, 0);
});

test("enviar manda JSON sin cookies ni referente", async () => {
  let visto;
  const fetchFn = async (url, init) => { visto = { url, init }; return { ok: true, status: 200, json: async () => ({ ok: true }) }; };
  const r = await L.enviar(fetchFn, "https://api.propio.co/publico/contacto", { nombre: "Ana" });
  assert.equal(r.ok, true);
  assert.equal(visto.init.method, "POST");
  assert.equal(visto.init.credentials, "omit");
  assert.equal(visto.init.referrerPolicy, "no-referrer");
  assert.equal(JSON.parse(visto.init.body).nombre, "Ana");
  assert.ok(!visto.url.includes("Ana"));                            // sin datos personales en la URL
});
