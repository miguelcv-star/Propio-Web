#!/usr/bin/env bash
# Ver Propio Web en el navegador — DOBLE-CLIC desde Finder.
# Regenera las páginas desde src/, las revisa y abre el sitio en un servidor local.
# Para detenerlo: Ctrl+C o cerrar esta ventana.
cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1

if ! command -v python3 >/dev/null 2>&1; then
  echo "No encuentro python3. Instálalo (https://www.python.org/downloads/) y vuelve a abrir este archivo."
  read -r -p "Pulsa Enter para cerrar…" _; exit 1
fi

echo "→ Regenerando las páginas…"
python3 scripts/construir.py || { echo "El generador falló (ver arriba)."; read -r -p "Pulsa Enter para cerrar…" _; exit 1; }

echo "→ Revisando el sitio…"
python3 scripts/verificar.py || echo "(Hay observaciones arriba; el sitio se abre igual para que lo veas.)"

# Primer puerto libre desde el 8080
PUERTO=8080
while lsof -iTCP:"$PUERTO" -sTCP:LISTEN >/dev/null 2>&1; do PUERTO=$((PUERTO + 1)); done
URL="http://localhost:$PUERTO/"

echo
echo "→ Sitio en $URL   (Ctrl+C para detener)"
( sleep 1; open "$URL" ) &
# Solo escucha en este equipo (127.0.0.1): nadie más en la red puede verlo.
exec python3 scripts/servir_local.py "$PUERTO"
