// Configuración PÚBLICA del sitio (spec 0010). Aquí solo van valores que cualquiera puede ver: nunca llaves secretas.
//   apiUrl           → dirección de la API pública de Propio; el sitio solo llama a sus rutas /publico/*.
//   turnstileSiteKey → llave PÚBLICA del widget anti-bots de Cloudflare ("" = sin widget).
// Se ajusta al publicar (dominio real) y no se versiona con datos de pruebas locales.
window.PROPIO_CONFIG = {
  apiUrl: "https://api.por-definir.example",
  turnstileSiteKey: ""
};
