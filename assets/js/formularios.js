// Formularios del sitio (spec 0010): valida, envía a la API PÚBLICA de Propio (solo rutas /publico/*) y muestra el
// resultado. Todo el texto de la respuesta entra con textContent (nunca innerHTML). Sin datos personales en la URL,
// en localStorage ni en la consola. La lógica pura vive en lib.js.
(function () {
  "use strict";
  if (typeof document === "undefined") { return; }
  var L = window.PropioLib;
  var CFG = window.PROPIO_CONFIG || {};
  if (!L) { return; }

  function el(tag, props, hijos) {
    var n = document.createElement(tag);
    Object.keys(props || {}).forEach(function (k) {
      if (k === "texto") { n.textContent = props[k]; } else if (k === "clase") { n.className = props[k]; } else { n.setAttribute(k, props[k]); }
    });
    (hijos || []).forEach(function (h) { if (h) { n.appendChild(typeof h === "string" ? document.createTextNode(h) : h); } });
    return n;
  }
  function limpiar(n) { while (n.firstChild) { n.removeChild(n.firstChild); } }

  // ── Cloudflare Turnstile (solo si hay llave pública configurada) ──────────
  var turnstileListo = null;
  function cargarTurnstile() {
    if (turnstileListo) { return turnstileListo; }
    turnstileListo = new Promise(function (resolver, rechazar) {
      var s = document.createElement("script");
      s.src = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";
      s.async = true; s.defer = true;
      s.onload = function () { resolver(window.turnstile); };
      s.onerror = function () { rechazar(new Error("turnstile")); };
      document.head.appendChild(s);
    });
    return turnstileListo;
  }

  function iniciar(form) {
    var tipo = form.getAttribute("data-propio-form");
    var estado = form.querySelector("[data-estado]");
    var boton = form.querySelector("[type=submit]");
    var contenedorResultados = document.querySelector("[data-resultados]");
    var contenedorTs = form.querySelector("[data-turnstile]");
    var inicio = Date.now(), enviando = false, token = null, widgetId = null;

    if (CFG.turnstileSiteKey && contenedorTs) {
      cargarTurnstile().then(function (ts) {
        widgetId = ts.render(contenedorTs, {
          sitekey: CFG.turnstileSiteKey, callback: function (t) { token = t; }, "expired-callback": function () { token = null; }
        });
      }).catch(function () { aviso("No pudimos cargar la verificación anti-spam. Recarga la página.", "error"); });
    }

    function aviso(mensaje, clase) {
      estado.textContent = mensaje; estado.className = "web-estado" + (clase ? " " + clase : "");
    }
    function valores() {
      var v = {};
      Array.prototype.forEach.call(form.elements, function (c) {
        if (!c.name) { return; }
        v[c.name] = c.type === "checkbox" ? c.checked : c.value;
      });
      return v;
    }
    function mostrarErrores(errores) {
      var primero = null;
      Array.prototype.forEach.call(form.querySelectorAll("[data-error-for]"), function (p) { p.textContent = ""; });
      Array.prototype.forEach.call(form.elements, function (c) { if (c.name) { c.removeAttribute("aria-invalid"); } });
      Object.keys(errores).forEach(function (campo) {
        var p = form.querySelector('[data-error-for="' + campo + '"]');
        var c = form.elements[campo];
        if (p) { p.textContent = errores[campo]; }
        if (c) { c.setAttribute("aria-invalid", "true"); if (!primero) { primero = c; } }
      });
      if (primero) { primero.focus(); } else if (errores._form) { aviso(errores._form, "error"); }
    }
    function reiniciarVerificacion() {
      token = null;
      if (widgetId !== null && window.turnstile) { window.turnstile.reset(widgetId); }
    }

    // ── resultados por tipo ────────────────────────────────────────────────
    function tarjetaInmueble(i) {
      var arriendo = i.operacion === "arriendo";
      var datos = [i.tipo_inmueble, i.area_construida ? i.area_construida + " m²" : null,
        i.habitaciones != null ? i.habitaciones + " hab." : null, i.banos != null ? i.banos + " baños" : null,
        i.estrato != null ? "estrato " + i.estrato : null].filter(Boolean).join(" · ");
      var ubic = [i.barrio, i.localidad, i.ciudad].filter(Boolean).join(", ");
      var enlaces = el("p", { clase: "web-enlaces" });
      if (i.enlace) {
        enlaces.appendChild(el("a", { href: i.enlace, target: "_blank", rel: "noopener noreferrer", texto: "Ver aviso original" }));
      }
      return el("article", { clase: "web-inmueble" }, [
        el("h3", { texto: i.titulo || "Inmueble" }),
        el("p", { clase: "web-precio", texto: L.formatoPesos(i.precio) + (arriendo ? " /mes" : "") }),
        el("p", { clase: "web-datos", texto: datos }), el("p", { clase: "web-datos", texto: ubic }), enlaces
      ]);
    }
    function pintarBusqueda(r, v) {
      limpiar(contenedorResultados);
      var lista = r.inmuebles || [];
      contenedorResultados.appendChild(el("h2", { texto: lista.length ? "Inmuebles que cumplen lo que buscas" : "Por ahora no encontramos inmuebles" }));
      contenedorResultados.appendChild(el("p", { clase: "meta", texto: lista.length
        ? "Mostramos hasta 20, de avisos publicados en portales. Los precios y la disponibilidad pueden haber cambiado: verifícalos en el aviso original."
        : "No hay inmuebles activos con esas características. Ya recibimos tu solicitud y te escribiremos si aparece algo." }));
      if (lista.length) {
        var rejilla = el("div", { clase: "web-inmuebles" });
        lista.forEach(function (i) { rejilla.appendChild(tarjetaInmueble(i)); });
        contenedorResultados.appendChild(rejilla);
        var bPdf = el("button", { type: "button", clase: "btn-secundario", texto: "Descargar reporte en PDF" });
        bPdf.addEventListener("click", function () { descargarPdf(v, bPdf); });
        contenedorResultados.appendChild(el("p", { clase: "web-form-acciones" }, [bPdf]));
      }
      contenedorResultados.hidden = false;
      contenedorResultados.scrollIntoView({ behavior: "smooth", block: "start" });
    }
    function descargarPdf(v, b) {
      if (CFG.turnstileSiteKey && !token) { aviso("Completa la verificación anti-spam y vuelve a pulsar «Descargar».", "error"); return; }
      b.disabled = true; b.textContent = "Preparando PDF…";
      var cuerpoPdf = L.cuerpo("busqueda", v, { tiempo_ms: Date.now() - inicio, turnstile: token });
      reiniciarVerificacion();
      L.enviar(window.fetch.bind(window), L.urlApi(CFG.apiUrl, L.RUTAS.busqueda_pdf), cuerpoPdf, { blob: true, timeoutMs: 40000 })
        .then(function (r) {
          b.disabled = false; b.textContent = "Descargar reporte en PDF";
          if (!r.ok) { aviso(r.error, "error"); return; }
          var u = URL.createObjectURL(r.blob);
          var a = el("a", { href: u, download: "inmuebles-para-ti.pdf" });
          document.body.appendChild(a); a.click(); document.body.removeChild(a);
          setTimeout(function () { URL.revokeObjectURL(u); }, 10000);
        });
    }
    function pintarEstimacion(r, v) {
      limpiar(contenedorResultados);
      var e = r.estimacion;
      contenedorResultados.appendChild(el("h2", { texto: "Tu estimación" }));
      if (!e) {
        contenedorResultados.appendChild(el("p", { texto: r.mensaje || "Sin estimación para esta zona por ahora." }));
      } else {
        var mes = e.operacion === "arriendo" ? " /mes" : "";
        contenedorResultados.appendChild(el("div", { clase: "web-estimacion" }, [
          el("p", { clase: "meta", texto: "Valor estimado" }),
          el("p", { clase: "web-precio", texto: L.formatoPesos(e.central) + mes }),
          el("p", { texto: "Rango: " + L.formatoPesos(e.minimo) + " a " + L.formatoPesos(e.maximo) + mes }),
          el("p", { clase: "meta", texto: "Alrededor de " + L.formatoPesos(e.precio_m2) + " por m²" }),
          el("p", {}, [el("span", { clase: "web-etiqueta " + e.confianza, texto: "Confianza " + e.confianza })]),
          el("p", { clase: "meta", texto: L.textoConfianza(e.confianza) }),
          el("p", { clase: "meta", texto: e.aviso })
        ]));
      }
      contenedorResultados.hidden = false;
      contenedorResultados.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    var MENSAJES_OK = {
      invierte: "¡Gracias! Recibimos tus datos y te contactaremos pronto.",
      vender: "¡Gracias! Recibimos tu inmueble. Si cumple los requisitos lo revisaremos y te contactaremos pronto."
    };

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      if (enviando) { return; }
      var v = valores();
      var errores = L.validar(tipo, v);
      mostrarErrores(errores);
      if (Object.keys(errores).length) { aviso("Revisa los campos marcados.", "error"); return; }
      if (v.sitio_web) { aviso(MENSAJES_OK[tipo] || "¡Gracias! Recibimos tu solicitud.", "ok"); return; }   // bot: se descarta en silencio
      if (CFG.turnstileSiteKey && !token) { aviso("Completa la verificación anti-spam para continuar.", "error"); return; }
      enviando = true; boton.disabled = true; var textoBoton = boton.textContent; boton.textContent = "Enviando…";
      aviso("Enviando…", "");
      var cuerpo = L.cuerpo(tipo, v, { tiempo_ms: Date.now() - inicio, turnstile: token, prefijoMensaje: form.getAttribute("data-prefijo-mensaje") });
      reiniciarVerificacion();
      L.enviar(window.fetch.bind(window), L.urlApi(CFG.apiUrl, L.RUTAS[tipo]), cuerpo).then(function (r) {
        enviando = false; boton.disabled = false; boton.textContent = textoBoton;
        if (!r.ok) { aviso(r.error + " Tus datos siguen aquí: puedes reintentar.", "error"); return; }
        if (tipo === "busqueda") { aviso("Listo: te mostramos lo que encontramos.", "ok"); pintarBusqueda(r.datos, v); }
        else if (tipo === "valorar") { aviso("Listo: aquí está tu estimación.", "ok"); pintarEstimacion(r.datos, v); }
        else { aviso((r.datos && r.datos.mensaje) || MENSAJES_OK[tipo] || "¡Gracias! Recibimos tu solicitud.", "ok"); form.reset(); inicio = Date.now(); }
      });
    });
  }

  Array.prototype.forEach.call(document.querySelectorAll("form[data-propio-form]"), iniciar);
})();
