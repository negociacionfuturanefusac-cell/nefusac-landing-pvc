#!/usr/bin/env python3
"""Compila NEFUSAC Landing v7.dc.html (DSL de Claude Design) a HTML estatico.

Uso: coloca el .dc.html exportado del proyecto de diseno junto a este script y
ejecuta `python3 compilar-dc.py`. Genera index.html y assets-needed.json.
Si el diseno cambia de version, actualiza DATA con lo que devuelva renderVals()
y HOOKS con los ref/handler nuevos: resolve() y bind_hooks() fallan a proposito
ante cualquier identificador sin mapear, en vez de emitir "None" en silencio.

El .dc.html usa: <x-dc>, <helmet>, <sc-for>, <sc-if>, {{ interpolacion }},
style-hover y props estilo React. Aqui se resuelve todo en build-time y la
interactividad se delega a assets/app.js en JS puro (sin React ni support.js).
"""
import html
import json
import re

SRC = "NEFUSAC Landing v7.dc.html"
OUT = "index.html"

# ---------------------------------------------------------------- datos
# Espejo de renderVals() del componente. Las rutas remotas del proyecto de
# diseno se reescriben a assets/ locales (ver manifest de assets).
WORDS = ['CONFORT TÉRMICO', 'VIDRIO LAMINADO 6MM', 'AUTOEXTINGUIBLE',
         'MANTENIMIENTO MÍNIMO', 'FABRICACIÓN A MEDIDA']

DATA = {
    'showGaleria': True,
    'showCertificaciones': True,
    'formEnviado': False,
    'marquee': WORDS + WORDS,
    'ruidos': ['Tráfico y avenidas', 'Obras y construcción', 'Bocinas y motores'],
    'counters': [
        {'value': 4, 'unit': 'capas', 'label': 'Atenúan el ruido: vidrio laminado de 6 mm, junta, excelente sellado y drenaje controlado'},
        {'value': 6, 'unit': 'mm', 'label': 'Vidrio laminado de seguridad'},
        {'value': 100, 'unit': '%', 'label': 'Fabricación a medida, previa evaluación técnica del vano'},
        {'value': 38, 'unit': 'años', 'label': 'de experiencia en acabados de construcción desde 1988.'},
    ],
    'features': [
        {'num': '01', 'title': 'Confort térmico', 'body': 'El perfil de PVC no genera puente térmico: a diferencia del aluminio, el marco no transmite calor ni frío y evita la condensación en el perfil.'},
        {'num': '02', 'title': 'Material autoextinguible', 'body': 'El PVC-U es autoextinguible: no alimenta la llama y deja de arder al retirarse la fuente de fuego.'},
        {'num': '03', 'title': 'Cero corrosión', 'body': 'El perfil de PVC no se oxida, no se pica y no se deforma con la humedad. Ideal para cualquier clima.'},
        {'num': '04', 'title': 'Excelente cierre y drenaje controlado', 'body': 'Junta en el encuentro hoja–marco, más excelente sellado perimetral continuo contra el vano. El agua que llega al riel se evacúa al exterior por el drenaje controlado.'},
    ],
    # gal1..gal7 + cierre-bano: mismo mapeo que usa la variante "export" del proyecto
    'galeria': [
        {'src': 'assets/gal1.jpg', 'alt': 'Sala con jardín — corrediza blanca'},
        {'src': 'assets/gal2.jpg', 'alt': 'Dormitorio frente al mar'},
        {'src': 'assets/gal3.jpg', 'alt': 'Cocina — corrediza sobre encimera'},
        {'src': 'assets/gal4.jpg', 'alt': 'Detalle corrediza blanca'},
        {'src': 'assets/gal5.jpg', 'alt': 'Dormitorio — perfil negro, vista al mar'},
        {'src': 'assets/gal6.jpg', 'alt': 'Sala — corrediza negra'},
        {'src': 'assets/gal7.jpg', 'alt': 'Home office — vista a la ciudad'},
        {'src': 'assets/cierre-bano.jpg', 'alt': 'Baño — corrediza en perfil negro'},
    ],
}

# Las imagenes grandes del proyecto se sirven desde las versiones optimizadas
# (assets/export/*.jpg en el proyecto de diseno) -> assets/*.jpg en el repo.
REMAP = {
    'https://nefusacventanaspvc.vercel.app/assets/logo.jpg': 'assets/logo.jpg',
    'https://nefusacventanaspvc.vercel.app/assets/certificaciones.png': 'assets/certificaciones.png',
}
PNG_TO_JPG = ['led-sala', 'led-bano-2', 'led-estudio', 'led-estar', 'led-noche',
              'led-cocina-isla', 'led-sala-2', 'led-escalera',
              'proy-9', 'proy-10', 'proy-11', 'equipo-nefusac', 'cierre-familia']

# ---------------------------------------------------------------- utilidades


def find_block(s, tag, start=0):
    """Devuelve (open_ini, open_fin, close_ini, close_fin) del primer <tag>
    en s a partir de start, respetando anidamiento."""
    om = re.compile(r'<%s(\s[^>]*)?>' % tag, re.S).search(s, start)
    if not om:
        return None
    depth = 1
    pos = om.end()
    pat = re.compile(r'<(/?)%s(?:\s[^>]*)?>' % tag, re.S)
    while depth:
        m = pat.search(s, pos)
        if not m:
            raise ValueError('<%s> sin cerrar' % tag)
        depth += -1 if m.group(1) else 1
        pos = m.end()
    return om.start(), om.end(), m.start(), m.end()


def attrs_of(tag_text):
    return dict(re.findall(r'([A-Za-z0-9_:-]+)\s*=\s*"([^"]*)"', tag_text))


def expr(raw):
    """Extrae el interior de {{ ... }}."""
    m = re.fullmatch(r'\s*\{\{\s*(.*?)\s*\}\}\s*', raw, re.S)
    return m.group(1) if m else raw


def resolve(path, scope):
    """Resuelve 'c.value' / 'word' / 'true' contra scope + DATA."""
    path = path.strip()
    if path in ('true', 'false'):
        return path == 'true'
    parts = path.split('.')
    if parts[0] in scope:
        cur = scope[parts[0]]
    elif parts[0] in DATA:
        cur = DATA[parts[0]]
    else:
        # Nunca emitir "None" silenciosamente: si aparece un identificador no
        # previsto es que el DSL cambio y hay que mapearlo explicitamente.
        raise KeyError('identificador del DSL sin mapear: %r' % path)
    for p in parts[1:]:
        cur = cur[p]
    return cur


# refs y handlers de React -> hooks data-* que consume assets/app.js.
# Se sustituyen ANTES de interpolar, porque no son datos sino puntos de anclaje.
HOOKS = {
    ' ref="{{ heroVideoRef }}"': ' data-hero-video',
    ' ref="{{ marqueeRef }}"': ' data-marquee',
    ' onClick="{{ descargarCatalogo }}"': ' data-descargar-catalogo',
    ' onSubmit="{{ enviarFormulario }}"': ' data-form-cotiza',
}


def bind_hooks(s):
    for react, plain in HOOKS.items():
        if react not in s:
            raise ValueError('hook esperado y no encontrado: %s' % react.strip())
        s = s.replace(react, plain)
    return s


# ---------------------------------------------------------------- expansion

def expand(s, scope):
    """Expande sc-for / sc-if recursivamente."""
    # sc-if
    while True:
        b = find_block(s, 'sc-if')
        if not b:
            break
        o0, o1, c0, c1 = b
        cond = resolve(expr(attrs_of(s[o0:o1]).get('value', '')), scope)
        inner = expand(s[o1:c0], scope) if cond else ''
        s = s[:o0] + inner + s[c1:]
    # sc-for
    while True:
        b = find_block(s, 'sc-for')
        if not b:
            break
        o0, o1, c0, c1 = b
        a = attrs_of(s[o0:o1])
        items = resolve(expr(a.get('list', '')), scope)
        var = a.get('as', 'item')
        body = s[o1:c0]
        out = []
        for it in items:
            sc = dict(scope)
            sc[var] = it
            out.append(interpolate(expand(body, sc), sc))
        s = s[:o0] + ''.join(out) + s[c1:]
    return s


def interpolate(s, scope):
    def sub(m):
        val = resolve(m.group(1), scope)
        if isinstance(val, bool):
            return 'true' if val else 'false'
        return html.escape(str(val), quote=True)
    return re.sub(r'\{\{\s*(.*?)\s*\}\}', sub, s, flags=re.S)


# ---------------------------------------------------------------- atributos

HOVER_RULES = []


def fix_tag(m):
    """Normaliza un tag: props React -> HTML, style-hover -> clase, limpieza."""
    tag = m.group(0)
    if tag.startswith('</') or tag.startswith('<!'):
        return tag
    name = re.match(r'<([A-Za-z0-9-]+)', tag).group(1)

    # style-hover -> clase + regla :hover con !important (igual que el runtime)
    hov = re.search(r'\sstyle-hover="([^"]*)"', tag)
    if hov:
        decls = [d.strip() for d in hov.group(1).split(';') if d.strip()]
        css = ';'.join(d if re.search(r'!\s*important$', d, re.I) else d + ' !important'
                       for d in decls)
        cls = 'hv%d' % (len(HOVER_RULES) + 1)
        HOVER_RULES.append('.%s:hover{%s}' % (cls, css))
        tag = tag.replace(hov.group(0), '')
        if re.search(r'\sclass="([^"]*)"', tag):
            tag = re.sub(r'\sclass="([^"]*)"', lambda k: ' class="%s %s"' % (k.group(1), cls), tag)
        else:
            tag = tag[:len(name) + 1] + ' class="%s"' % cls + tag[len(name) + 1:]

    # booleanos React -> atributos HTML
    for react, plain in [('autoPlay', 'autoplay'), ('playsInline', 'playsinline'),
                         ('muted', 'muted'), ('loop', 'loop'), ('required', 'required')]:
        tag = re.sub(r'\s%s="(?:\{\{\s*)?true(?:\s*\}\})?"' % react,
                     ' ' + plain, tag)

    # marca estable para la tira de certificaciones (ver fix en index.html):
    # su regla CSS no puede depender del nombre de archivo, porque al empaquetar
    # la landing en un HTML autocontenido el src pasa a ser un data: URI.
    if 'certificaciones' in tag:
        tag = tag[:len(name) + 1] + ' data-certificaciones' + tag[len(name) + 1:]

    # atributos solo-editor
    tag = re.sub(r'\s(?:data-screen-label|hint-placeholder-count|hint-placeholder-val|sc-name)="[^"]*"', '', tag)

    # rutas de assets
    for remote, local in REMAP.items():
        tag = tag.replace(remote, local)
    for stem in PNG_TO_JPG:
        tag = tag.replace('assets/%s.png' % stem, 'assets/%s.jpg' % stem)

    # videos: atributos que el navegador necesita para autoplay silencioso
    if name == 'video':
        for need in ('autoplay', 'muted', 'loop', 'playsinline'):
            if not re.search(r'\s%s(\s|>|=)' % need, tag):
                tag = tag[:len(name) + 1] + ' ' + need + tag[len(name) + 1:]
    return tag


# ---------------------------------------------------------------- main

def main():
    src = open(SRC, encoding='utf-8').read()

    hb = find_block(src, 'helmet')
    helmet = src[hb[1]:hb[2]]
    xb = find_block(src, 'x-dc')
    body = src[xb[1]:xb[2]]
    body = body[:hb[0] - xb[1]] + body[hb[3] - xb[1]:]
    body = re.sub(r'<script type="text/x-dc".*?</script>', '', body, flags=re.S)

    body = expand(body, {})
    body = bind_hooks(body)
    body = interpolate(body, {})
    body = re.sub(r'<[^>]+>', fix_tag, body)

    # el <style> del helmet se conserva tal cual; se le anexan las reglas :hover
    hov = '\n'.join(HOVER_RULES)
    helmet = helmet.replace('</style>', '\n/* estados :hover (compilados desde style-hover) */\n'
                            + hov + '\n</style>', 1)

    doc = HEAD.replace('{{HELMET}}', helmet.strip()) + '\n' + body.strip() + '\n' + TAIL
    doc = re.sub(r'\n{3,}', '\n\n', doc)
    import os
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'w', encoding='utf-8').write(doc)
    print('escrito %s (%d bytes, %d reglas :hover)' % (OUT, len(doc), len(HOVER_RULES)))
    # inventario de assets referenciados
    refs = sorted(set(re.findall(r'(?:src|href|poster)="(assets/[^"]+)"', doc)))
    json.dump(refs, open('assets-needed.json', 'w'), indent=1)
    print('assets referenciados: %d' % len(refs))
    leftovers = re.findall(r'\{\{|sc-for|sc-if|style-hover|x-dc|helmet|ref="', doc)
    print('restos de DSL sin resolver:', len(leftovers), sorted(set(leftovers)) or '(ninguno)')


HEAD = '''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ventanas de PVC en Lima | NEFUSAC — Aislamiento Acústico y Térmico</title>
<meta name="description" content="Ventanas de PVC a medida en Lima: aislamiento acústico y térmico, vidrio laminado de 6 mm, perfiles autoextinguibles. Fabricación e instalación para hogares y proyectos corporativos. Cotiza gratis por WhatsApp.">
<meta name="keywords" content="ventanas de PVC Lima, ventanas acústicas Perú, ventanas antiruido, vidrio laminado, ventanas corredizas PVC, NEFUSAC">
<meta name="author" content="Negociación Futura S.A.C.">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://nefusacventanaspvc.vercel.app/">
<meta property="og:title" content="Ventanas de PVC en Lima | NEFUSAC">
<meta property="og:description" content="El ruido se queda afuera. Ventanas de PVC con aislamiento acústico y térmico real. Cotiza gratis por WhatsApp: 981 124 794.">
<meta property="og:type" content="website">
<meta property="og:locale" content="es_PE">
<meta property="og:image" content="assets/cierre-familia.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#070808">
<link rel="icon" href="assets/logo.jpg">
{{HELMET}}
</head>
<body>
'''

TAIL = '''<script src="assets/app.js"></script>
</body>
</html>
'''

if __name__ == '__main__':
    main()
