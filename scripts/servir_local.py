#!/usr/bin/env python3
"""Servidor local del sitio (solo librería estándar), para verlo y probarlo en este equipo.

    python3 scripts/servir_local.py [puerto]              # sirve el sitio en http://127.0.0.1:<puerto>/
    PROPIO_API_URL=http://localhost:8123 python3 scripts/servir_local.py 3012

Si `PROPIO_API_URL` está definida, responde `/assets/js/config.js` con esa dirección (y `PROPIO_TURNSTILE_SITEKEY`
si existe) SIN tocar el archivo del repo: así `assets/js/config.js` nunca lleva `localhost` ni datos de pruebas, y
`scripts/verificar.py` sigue pasando. Solo escucha en 127.0.0.1."""
import functools
import http.server
import json
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


class Manejador(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        api = os.environ.get("PROPIO_API_URL", "").strip()
        if api and self.path.split("?")[0] == "/assets/js/config.js":
            cuerpo = ("window.PROPIO_CONFIG = {apiUrl: %s, turnstileSiteKey: %s};\n" % (
                json.dumps(api), json.dumps(os.environ.get("PROPIO_TURNSTILE_SITEKEY", "")))).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/javascript; charset=utf-8")
            self.send_header("Content-Length", str(len(cuerpo)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(cuerpo)
            return
        super().do_GET()

    def log_message(self, formato, *args):       # sin datos de las peticiones en el registro
        pass


if __name__ == "__main__":
    puerto = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    servidor = http.server.ThreadingHTTPServer(("127.0.0.1", puerto), functools.partial(Manejador, directory=str(RAIZ)))
    print(f"Sitio en http://localhost:{puerto}/   (Ctrl+C para detener)")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
