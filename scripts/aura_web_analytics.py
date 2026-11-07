#!/usr/bin/env python3
"""Activa Cloudflare Web Analytics solo en el index comercial de Aura Digital."""
from pathlib import Path

PAGE = Path("index.html")
BEACON_URL = "https://static.cloudflareinsights.com/beacon.min.js"
TOKEN = "a1cbe51ed62c497caceb31cc91309081"
MARKER = "<!-- Cloudflare Web Analytics: portada comercial Aura Digital -->"
SNIPPET = (
    "\n" + MARKER + "\n"
    + '<script type="module" src="' + BEACON_URL + '" '
    + "data-cf-beacon='" + '{"token":"' + TOKEN + '"}' + "'></script>\n"
)

html = PAGE.read_text(encoding="utf-8")
if BEACON_URL in html:
    print("Cloudflare Web Analytics ya instalado; no hay cambios.")
else:
    if html.count("</body>") != 1:
        raise SystemExit("HTML no esperado: no se modifica la página.")
    PAGE.write_text(html.replace("</body>", SNIPPET + "</body>"), encoding="utf-8")
    print("Instalado únicamente en index.html del sitio principal.")
