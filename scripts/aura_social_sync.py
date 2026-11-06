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

HERO_CTA_CSS = "\n/* Aura Digital: prioridades CTA portada v2 */\n.hero .hero-actions{display:flex!important;flex-direction:column!important;align-items:flex-start!important;gap:10px!important;margin-top:18px!important}\n.hero .hero-actions .aura-hero-social{order:0;justify-content:flex-start!important;width:auto!important;max-width:100%;margin:0 0 4px!important}\n.hero .hero-actions>a{flex:0 0 auto!important;width:auto!important;max-width:100%;min-width:0!important}\n.hero .hero-actions>a[data-wa]{order:1;min-height:39px!important;padding:8px 15px!important;font-size:.81rem!important;font-weight:650!important;border-radius:10px!important}\n.hero .hero-actions>a[data-hero-secondary-link]{order:2;min-height:38px!important;padding:7px 14px!important;font-size:.82rem!important}\n@media(max-width:720px){.hero .hero-actions{align-items:center!important;margin-top:12px!important;gap:9px!important}.hero .hero-actions .aura-hero-social{justify-content:center!important;margin:0 auto 3px!important;gap:18px!important}.hero .hero-actions .btn{flex:0 0 auto!important;min-width:0!important}}\n"

def arrange_hero_cta(path):
    """Mantener Instagram/Facebook arriba, luego WhatsApp y por último Ver proyectos."""
    import re
    text = path.read_text(encoding="utf-8")
    action_tag = '<div class="hero-actions">'
    nav_matches = list(re.finditer(r'<nav class="aura-hero-social"[^>]*>.*?</nav>', text, re.S))
    assert len(nav_matches) == 1, f"Esperaba exactamente una barra social, hallé {len(nav_matches)}"
    nav_match = nav_matches[0]
    nav_html = nav_match.group(0)
    action_start = text.index(action_tag)
    action_end = text.index('</div>', action_start) + len('</div>')
    if not (action_start < nav_match.start() < action_end):
        text = text[:nav_match.start()] + text[nav_match.end():]
        action_start = text.index(action_tag)
        insert_at = action_start + len(action_tag)
        text = text[:insert_at] + nav_html + text[insert_at:]
    else:
        insert_at = action_start + len(action_tag)
        nav_match = re.search(r'<nav class="aura-hero-social"[^>]*>.*?</nav>', text, re.S)
        if nav_match.start() != insert_at:
            text = text[:nav_match.start()] + text[nav_match.end():]
            action_start = text.index(action_tag)
            insert_at = action_start + len(action_tag)
            text = text[:insert_at] + nav_html + text[insert_at:]
    new_start = text.index(action_tag)
    new_end = text.index('</div>', new_start) + len('</div>')
    fragment = text[new_start:new_end]
    assert fragment.find('class="aura-hero-social"') >= 0, "Falta barra social"
    assert fragment.find('class="aura-hero-social"') < fragment.find('data-wa') < fragment.find('data-hero-secondary-link'), (
        "El orden esperado es redes sociales > WhatsApp > Ver proyectos"
    )
    css_label = '/* Aura Digital: prioridades CTA portada v2 */'
    if css_label not in text:
        body = text.index('<body')
        css_end = text.rfind('</style>', 0, body)
        assert css_end >= 0, "No se encontró style en head"
        text = text[:css_end] + HERO_CTA_CSS + text[css_end:]
    assert text.count(css_label) == 1
    path.write_text(text, encoding="utf-8")
    print("Orden verificado: Instagram/Facebook → WhatsApp compacto → Ver proyectos")

patch_html(Path("index.html"))
arrange_hero_cta(Path("index.html"))
