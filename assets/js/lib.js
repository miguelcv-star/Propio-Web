// Lógica pura de los formularios del sitio (spec 0010): validación, armado del cuerpo que recibe la API pública de
// Propio, formato de resultados y manejo de errores. Sin DOM: se prueba con `node --test`.
(function () {
  "use strict";

  var PLAZOS = {
    "0-1": [0, 1], "1-3": [1, 3], "3-6": [3, 6], "6-12": [6, 12], "12+": [12, null]
  };
  var TIMEOUT_MS = 20000;

  function texto(v) { return v == null ? "" : String(v).trim(); }

  // «680» millones → 680000000. Acepta coma o punto decimal; vacío o inválido → null.
  function millonesAPesos(v) {
    var t = texto(v).replace(/\s/g, "").replace(",", ".");
    if (t === "") { return null; }
    var n = Number(t);
    return isFinite(n) && n >= 0 ? Math.round(n * 1e6) : null;
  }
  function aNumero(v) {
    var t = texto(v).replace(",", ".");
    if (t === "") { return null; }
    var n = Number(t);
    return isFinite(n) ? n : null;
  }
  function aEntero(v) {
    var n = aNumero(v);
    return n == null ? null : Math.round(n);
  }
  function plazoDe(clave) {
    var p = PLAZOS[clave];
    return p ? { plazo_min_meses: p[0], plazo_max_meses: p[1] } : {};
  }
  // Una foto por línea; solo http(s); máximo 8. Devuelve { fotos, invalidas }.
  function fotosDeTexto(t) {
    var lineas = texto(t).split(/\r?\n/).map(texto).filter(Boolean);
    var fotos = [], invalidas = [];
    lineas.forEach(function (l) {
      if (/^https?:\/\/[^\s]+$/i.test(l) && l.length <= 500) { fotos.push(l); } else { invalidas.push(l); }
    });
    return { fotos: fotos.slice(0, 8), invalidas: invalidas, demasiadas: fotos.length > 8 };
  }

  // ── validación ────────────────────────────────────────────────────────────
  var REGLAS = {
    invierte: { obligatorios: [] },
    busqueda: { obligatorios: ["operacion"] },
    valorar: { obligatorios: ["motivo", "tipo_inmueble", "area_construida"], ubicacion: true },
    vender: { obligatorios: ["operacion", "tipo_inmueble", "titulo", "descripcion", "precio", "area_construida"],
              ubicacion: true, acuerdo: true }
  };
  var ETIQUETAS = {
    operacion: "Elige si es venta o arriendo.", motivo: "Cuéntanos el motivo de tu consulta.",
    tipo_inmueble: "Elige el tipo de inmueble.", area_construida: "Escribe el área en metros cuadrados.",
    titulo: "Escribe un título para el aviso.", descripcion: "Escribe una descripción del inmueble.",
    precio: "Escribe el precio que esperas."
  };

  function validar(tipo, v) {
    var e = {}, regla = REGLAS[tipo];
    if (!regla) { return { _form: "Formulario desconocido." }; }
    var nombre = texto(v.nombre);
    if (nombre.length < 2) { e.nombre = "Escribe tu nombre."; }
    var tel = texto(v.telefono), mail = texto(v.email);
    if (!tel && !mail) { e.telefono = "Déjanos un teléfono o un correo para contactarte."; }
    if (tel && (tel.replace(/\D/g, "").length < 7 || tel.replace(/\D/g, "").length > 15)) { e.telefono = "El teléfono no parece válido."; }
    if (mail && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(mail)) { e.email = "El correo no parece válido."; }
    regla.obligatorios.forEach(function (c) {
      if (texto(v[c]) === "") { e[c] = ETIQUETAS[c] || "Este campo es obligatorio."; }
    });
    ["area_construida", "precio"].forEach(function (c) {
      if (v[c] != null && texto(v[c]) !== "" && !(aNumero(v[c]) > 0)) { e[c] = "Escribe un número mayor que cero."; }
    });
    if (regla.obligatorios.indexOf("area_construida") >= 0 && !e.area_construida && aNumero(v.area_construida) <= 9) {
      e.area_construida = "El área debe ser de más de 9 m².";
    }
    if (regla.ubicacion && !texto(v.localidad) && !texto(v.barrio)) { e.localidad = "Elige la localidad o escribe el barrio."; }
    if (tipo === "vender") {
      var f = fotosDeTexto(v.fotos);
      if (f.invalidas.length) { e.fotos = "Cada foto debe ser un enlace que empiece por http:// o https://."; }
      else if (f.demasiadas) { e.fotos = "Máximo 8 fotos."; }
      if (texto(v.titulo) && texto(v.titulo).length < 5) { e.titulo = "El título es muy corto."; }
      if (texto(v.descripcion) && texto(v.descripcion).length < 10) { e.descripcion = "Cuéntanos un poco más del inmueble."; }
    }
    if (!v.consentimiento) { e.consentimiento = "Debes autorizar el tratamiento de tus datos para continuar."; }
    if (regla.acuerdo && !v.acepta_comision) { e.acepta_comision = "Debes aceptar el acuerdo de publicación y comisión."; }
    return e;
  }

  // ── cuerpo de cada ruta de la API pública ─────────────────────────────────
  function limpio(o) {
    var r = {};
    Object.keys(o).forEach(function (k) {
      var x = o[k];
      if (x !== null && x !== undefined && x !== "" && !(Array.isArray(x) && x.length === 0)) { r[k] = x; }
    });
    return r;
  }
  function base(v, ctx) {
    return {
      nombre: texto(v.nombre), telefono: texto(v.telefono), email: texto(v.email).toLowerCase(),
      consentimiento: v.consentimiento === true, sitio_web: texto(v.sitio_web),
      tiempo_ms: ctx && ctx.tiempo_ms != null ? Math.max(0, Math.round(ctx.tiempo_ms)) : null,
      turnstile: ctx && ctx.turnstile ? ctx.turnstile : null
    };
  }
  function cuerpo(tipo, v, ctx) {
    var b = base(v, ctx), extra = {};
    if (tipo === "invierte") {
      var plazo = plazoDe(v.plazo);
      extra = {
        presupuesto_min: millonesAPesos(v.presupuesto_min), presupuesto_max: millonesAPesos(v.presupuesto_max),
        plazo_min_meses: plazo.plazo_min_meses, plazo_max_meses: plazo.plazo_max_meses,
        mensaje: (ctx && ctx.prefijoMensaje ? ctx.prefijoMensaje + " " : "") + texto(v.mensaje)
      };
      extra.mensaje = texto(extra.mensaje).slice(0, 1000);
    } else if (tipo === "busqueda") {
      extra = {
        operacion: v.operacion, tipo_inmueble: v.tipo_inmueble, localidad: texto(v.localidad), barrio: texto(v.barrio),
        presupuesto_min: millonesAPesos(v.presupuesto_min), presupuesto_max: millonesAPesos(v.presupuesto_max),
        area_min: aNumero(v.area_min), area_max: aNumero(v.area_max), habitaciones_min: aEntero(v.habitaciones_min),
        banos_min: aEntero(v.banos_min), estrato: aEntero(v.estrato), mensaje: texto(v.mensaje).slice(0, 1000)
      };
    } else if (tipo === "valorar") {
      extra = {
        motivo: v.motivo, operacion: v.operacion || "venta", tipo_inmueble: v.tipo_inmueble,
        area_construida: aNumero(v.area_construida), estrato: aEntero(v.estrato), habitaciones: aEntero(v.habitaciones),
        banos: aEntero(v.banos), parqueaderos: aEntero(v.parqueaderos), antiguedad_anios: aEntero(v.antiguedad_anios),
        localidad: texto(v.localidad), barrio: texto(v.barrio)
      };
    } else if (tipo === "vender") {
      extra = {
        acepta_comision: v.acepta_comision === true, operacion: v.operacion, tipo_inmueble: v.tipo_inmueble,
        titulo: texto(v.titulo), descripcion: texto(v.descripcion), precio: aNumero(v.precio),
        area_construida: aNumero(v.area_construida), habitaciones: aEntero(v.habitaciones), banos: aEntero(v.banos),
        parqueaderos: aEntero(v.parqueaderos), estrato: aEntero(v.estrato), antiguedad_anios: aEntero(v.antiguedad_anios),
        localidad: texto(v.localidad), barrio: texto(v.barrio), direccion: texto(v.direccion),
        fotos: fotosDeTexto(v.fotos).fotos
      };
    }
    var salida = limpio(Object.assign({}, b, extra));
    salida.consentimiento = b.consentimiento;                       // se envía siempre, aunque sea false
    if (tipo === "vender") { salida.acepta_comision = extra.acepta_comision; }
    return salida;
  }

  var RUTAS = { invierte: "/publico/contacto", busqueda: "/publico/busqueda", valorar: "/publico/valorar",
                vender: "/publico/vender", busqueda_pdf: "/publico/busqueda/pdf" };
  function urlApi(apiUrl, ruta) {
    var base = texto(apiUrl).replace(/\/+$/, "");
    return base + ruta;
  }

  // ── formato ───────────────────────────────────────────────────────────────
  function formatoPesos(n) {
    if (n == null || !isFinite(n)) { return "—"; }
    return "$" + Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  }
  function formatoMillones(n) {
    if (n == null || !isFinite(n)) { return "—"; }
    var m = n / 1e6;
    return "$" + (m >= 100 ? Math.round(m) : Math.round(m * 10) / 10).toString().replace(".", ",") + " M";
  }
  var CONFIANZA = {
    alta: "Confianza alta: hay varios inmuebles muy parecidos en tu zona.",
    media: "Confianza media: hay inmuebles comparables, pero no idénticos.",
    baja: "Confianza baja: tómalo solo como una primera idea."
  };
  function textoConfianza(c) { return CONFIANZA[c] || ""; }

  // ── errores ───────────────────────────────────────────────────────────────
  function mensajeDeError(status, detalle) {
    if (status === 422 && typeof detalle === "string" && detalle) { return detalle; }
    if (status === 429) { return "Hiciste muchas solicitudes seguidas. Espera un rato e inténtalo de nuevo."; }
    if (status === 403) { return "No pudimos verificar que eres una persona. Inténtalo de nuevo."; }
    if (status === 413 || status === 411) { return "Los datos enviados son demasiado grandes."; }
    if (status === 404 || status === 503) { return "El servicio no está disponible por ahora. Inténtalo más tarde."; }
    if (status === 0) { return "No pudimos conectarnos. Revisa tu conexión e inténtalo de nuevo."; }
    return "No pudimos procesar tu solicitud. Inténtalo de nuevo.";
  }

  // Envía el cuerpo con límite de tiempo. `fetchFn` se inyecta (en el navegador es window.fetch).
  // Devuelve { ok, status, datos, error, blob }; nunca lanza.
  function enviar(fetchFn, url, cuerpoJson, opciones) {
    opciones = opciones || {};
    var controlador = typeof AbortController !== "undefined" ? new AbortController() : null;
    var reloj = setTimeout(function () { if (controlador) { controlador.abort(); } }, opciones.timeoutMs || TIMEOUT_MS);
    return fetchFn(url, {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(cuerpoJson),
      signal: controlador ? controlador.signal : undefined, credentials: "omit", referrerPolicy: "no-referrer"
    }).then(function (res) {
      clearTimeout(reloj);
      if (!res.ok) {
        return res.json().catch(function () { return {}; }).then(function (j) {
          return { ok: false, status: res.status, error: mensajeDeError(res.status, j && j.detail) };
        });
      }
      if (opciones.blob) { return res.blob().then(function (b) { return { ok: true, status: res.status, blob: b }; }); }
      return res.json().then(function (j) { return { ok: true, status: res.status, datos: j }; });
    }).catch(function () {
      clearTimeout(reloj);
      return { ok: false, status: 0, error: mensajeDeError(0) };
    });
  }

  var api = {
    PLAZOS: PLAZOS, RUTAS: RUTAS, millonesAPesos: millonesAPesos, plazoDe: plazoDe, fotosDeTexto: fotosDeTexto,
    validar: validar, cuerpo: cuerpo, urlApi: urlApi, formatoPesos: formatoPesos, formatoMillones: formatoMillones,
    textoConfianza: textoConfianza, mensajeDeError: mensajeDeError, enviar: enviar
  };
  if (typeof module !== "undefined" && module.exports) { module.exports = api; }
  if (typeof window !== "undefined") { window.PropioLib = api; }
})();
