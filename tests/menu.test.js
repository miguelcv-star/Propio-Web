// Criterio 3 de la spec 0001: el menú móvil. Sin dependencias: `node --test tests/`.
const test = require("node:test");
const assert = require("node:assert/strict");
const m = require("../assets/js/menu.js");

test("empieza cerrado y el botón dice «Abrir menú»", () => {
  const e = m.estadoInicial();
  assert.equal(e.abierto, false);
  assert.equal(m.etiqueta(e), "Abrir menú");
});

test("alternar abre y cierra, y cambia la etiqueta", () => {
  const abierto = m.alternar(m.estadoInicial());
  assert.equal(abierto.abierto, true);
  assert.equal(m.etiqueta(abierto), "Cerrar menú");
  assert.equal(m.alternar(abierto).abierto, false);
});

test("Escape cierra el menú abierto y otras teclas no hacen nada", () => {
  const abierto = { abierto: true };
  assert.equal(m.alEscape(abierto, "Escape").abierto, false);
  assert.equal(m.alEscape(abierto, "Tab").abierto, true);
});

function elemento() {
  const oyentes = {}; const attrs = {}; const clases = new Set();
  return {
    oyentes, attrs, clases, textContent: "", focuseado: false,
    addEventListener(t, f) { (oyentes[t] ||= []).push(f); },
    setAttribute(k, v) { attrs[k] = String(v); },
    getAttribute(k) { return attrs[k]; },
    classList: { add: (c) => clases.add(c), remove: (c) => clases.delete(c), contains: (c) => clases.has(c),
      toggle: (c, on) => (on ? clases.add(c) : clases.delete(c)) },
    focus() { this.focuseado = true; },
    disparar(t, ev = {}) { (oyentes[t] || []).forEach((f) => f(ev)); },
  };
}

test("iniciar: el botón controla aria-expanded, la clase del menú y Escape devuelve el foco", () => {
  const boton = elemento(), menu = elemento(), raiz = elemento(), enlace = elemento(), doc = elemento();
  menu.querySelectorAll = () => [enlace];
  m.iniciar({ boton, menu, raiz, documento: doc, ventana: elemento() });
  assert.ok(raiz.clases.has("con-js"), "marca que hay JS para que el CSS pueda ocultar el menú");
  assert.equal(boton.attrs["aria-expanded"], "false");
  boton.disparar("click");
  assert.equal(boton.attrs["aria-expanded"], "true");
  assert.ok(menu.clases.has("nav-open"));
  assert.equal(boton.textContent, "Cerrar menú");
  doc.disparar("keydown", { key: "Escape" });
  assert.equal(boton.attrs["aria-expanded"], "false");
  assert.ok(!menu.clases.has("nav-open"));
  assert.equal(boton.focuseado, true);
});

test("iniciar: elegir un enlace cierra el menú", () => {
  const boton = elemento(), menu = elemento(), raiz = elemento(), enlace = elemento();
  menu.querySelectorAll = () => [enlace];
  m.iniciar({ boton, menu, raiz, documento: elemento(), ventana: elemento() });
  boton.disparar("click");
  enlace.disparar("click");
  assert.equal(boton.attrs["aria-expanded"], "false");
});

test("iniciar: al ensanchar la ventana a escritorio el menú se cierra", () => {
  const boton = elemento(), menu = elemento(), raiz = elemento(), ventana = elemento();
  menu.querySelectorAll = () => [];
  ventana.innerWidth = 1280;
  m.iniciar({ boton, menu, raiz, documento: elemento(), ventana });
  boton.disparar("click");
  ventana.disparar("resize");
  assert.equal(boton.attrs["aria-expanded"], "false");
});
