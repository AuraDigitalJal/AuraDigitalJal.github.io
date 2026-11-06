#!/usr/bin/env python3
"""Sincroniza accesos sociales Aura Digital en la portada publicada (idempotente)."""
from pathlib import Path
from html import escape

IG = "https://www.instagram.com/invitacionesauradigital?rpxt=MWpkMHZjOXF5Mnl4dw%3D%3D&utm_source=qr"
FB = "https://www.facebook.com/share/19rHvPb4LE/?mibextid=wwXIfr"

css = """
/* Aura Digital: enlaces sociales discretos en portada */
.aura-hero-social{display:flex;align-items:center;justify-content:flex-start;flex-wrap:wrap;gap:20px;width:100%;max-width:100%;margin:18px 0 0}
.aura-hero-social a{display:inline-flex;align-items:center;gap:8px;min-height:38px;font:500 12px/1.3 var(--body-font);letter-spacing:.015em;color:var(--text);text-decoration:none;opacity:.85;transition:color .2s,opacity .2s}
.aura-hero-social a:hover{color:var(--accent);opacity:1}
.aura-hero-social a:focus-visible{outline:2px solid var(--accent);outline-offset:4px;border-radius:3px}
.aura-hero-social a+a{padding-left:20px;border-left:1px solid var(--border)}
.aura-hero-social svg{width:20px;height:20px;flex:none}
@media(max-width:720px){.hero .hero-grid{grid-template-areas:"kicker" "title" "text" "visual" "actions" "social" "benefits"!important}.hero .aura-hero-social{grid-area:social!important;justify-content:center!important;margin:14px auto 0!important;gap:20px!important}.hero .aura-hero-social a{font-size:11px;min-height:36px}}
"""

def social_nav(ig, fb):
    return (
        '<nav class="aura-hero-social" aria-label="Redes sociales de Aura Digital">'
        f'<a href="{escape(ig, quote=True)}" target="_blank" rel="noopener noreferrer" aria-label="Instagram de Aura Digital">'
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/>'
        '<circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/></svg><span>Instagram</span></a>'
        f'<a href="{escape(fb, quote=True)}" target="_blank" rel="noopener noreferrer" aria-label="Facebook de Aura Digital">'
        '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
        '<path d="M15.2 21v-8h2.8l.45-3.5H15.2V7.3c0-1.05.3-1.75 1.75-1.75h1.7V2.4a23.5 23.5 0 0 0-2.5-.14c-2.5 0-4.2 1.53-4.2 4.35V9.5H9.2V13h2.75v8z"/></svg><span>Facebook</span></a></nav>'
    )

def patch_html(path):
    text = path.read_text(encoding="utf-8")
    if 'class="aura-hero-social"' not in text:
        start = text.index('<div class="hero-actions">')
        end = text.index('</div>', start) + len('</div>')
        assert end - start < 1600, "Cierre hero-actions inesperado"
        assert 'class="benefits"' in text[end:end+140], "Cambió la estructura de portada"
        text = text[:end] + ' ' + social_nav(IG, FB) + text[end:]
    if '/* Aura Digital: enlaces sociales discretos en portada */' not in text:
        body = text.index('<body')
        style_end = text.rfind('</style>', 0, body)
        assert style_end >= 0, "No existe hoja de estilo en head"
        text = text[:style_end] + css + text[style_end:]
    original = '"instagram":"#","facebook":"#","tiktok":"#"'
    if original in text:
        assert text.count(original) == 1, "Datos sociales duplicados"
        text = text.replace(original, '"instagram":"'+IG+'","facebook":"'+FB+'","tiktok":"#"', 1)
    assert text.count('class="aura-hero-social"') == 1
    assert IG in text and FB in text and 'grid-template-areas:"kicker" "title" "text" "visual" "actions" "social" "benefits"' in text
    path.write_text(text, encoding="utf-8")
    print(f"Portada actualizada: {path}, {len(text)} caracteres")

patch_html(Path("index.html"))
