#!/usr/bin/env python3
"""Build de produccion de la landing NEFUSAC.

Toma el index.html compilado desde el diseno y produce la version que se sirve:
CSS aparte, fuentes locales, <picture> con WebP y srcset, menu movil, SEO,
UTM por seccion y accesibilidad. No toca copy, colores ni diseno.

Uso: python3 tools/construir-produccion.py   (desde landing/)
Es idempotente: parte siempre de index.src.html, no de su propia salida.
"""
import json
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(RAIZ, "index.src.html")
OUT = os.path.join(RAIZ, "index.html")
CSS = os.path.join(RAIZ, "styles.css")
DIMS = json.load(open(os.path.join(RAIZ, "assets", "DIMENSIONES.json")))

DOMINIO = "https://ventanasnefusacpvc.com"
TEL = "+51981124794"
WA = "51981124794"

# ---------------------------------------------------------------- PASO 5
# Un mensaje distinto por seccion + UTM, en el orden real en que aparecen
# los 7 enlaces en el documento (verificado sobre el markup).
CTAS = [
    ("nav", "Hola NEFUSAC, quiero cotizar mis ventanas de PVC."),
    ("hero", "Hola NEFUSAC, vi la portada y quiero cotizar mis ventanas de PVC."),
    ("led", "Hola NEFUSAC, quiero ventanas de PVC con luz LED perimetral."),
    ("cierre", "Hola NEFUSAC, quiero hablar de mi ventana y mi proyecto."),
    ("contacto", "Hola NEFUSAC, los contacto desde la web para una cotizacion."),
    ("footer", "Hola NEFUSAC, quiero cotizar mis ventanas de PVC."),
    ("flotante", "Hola NEFUSAC, quiero cotizar mis ventanas de PVC."),
]


def wa_url(contenido, texto):
    from urllib.parse import quote
    return (f"https://wa.me/{WA}?text={quote(texto)}"
            f"&utm_source=web&utm_medium=cta&utm_content={contenido}")


# ---------------------------------------------------------------- PASO 4
JSONLD = {
    "@context": "https://schema.org",
    "@graph": [
        {
            "@type": "LocalBusiness",
            "@id": DOMINIO + "/#empresa",
            "name": "NEFUSAC — Negociación Futura S.A.C.",
            "description": ("Fabricación e instalación de ventanas de PVC a medida en Lima, "
                            "con aislamiento acústico y térmico y vidrio laminado de 6 mm."),
            "url": DOMINIO + "/",
            "telephone": TEL,
            "email": "cotiza@nefusac.com.pe",
            "foundingDate": "1988",
            "image": [DOMINIO + "/assets/og-nefusac.jpg",
                      DOMINIO + "/assets/operario-nefusac-planta-fabricacion-pvc.jpg",
                      DOMINIO + "/assets/familia-sala-ventana-pvc-nefusac.jpg"],
            "logo": DOMINIO + "/assets/logo.jpg",
            "priceRange": "$$",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "Jr. Mariscal Agustín Gamarra 132, Urb. El Pino",
                "addressLocality": "San Luis",
                "addressRegion": "Lima",
                "addressCountry": "PE",
            },
            "areaServed": {"@type": "City", "name": "Lima"},
            "sameAs": ["https://wa.me/" + WA],
        },
        {
            "@type": "Product",
            "@id": DOMINIO + "/#producto",
            "name": "Ventanas de PVC NEFUSAC Serie 50NF / 52NF",
            "description": ("Sistema corredizo de PVC con hoja fija, vidrio laminado de "
                            "seguridad de 6 mm, perfil autoextinguible sin puente térmico, "
                            "sellado perimetral continuo y drenaje controlado. "
                            "Disponible en blanco y negro, fabricado a medida."),
            "brand": {"@type": "Brand", "name": "NEFUSAC"},
            "material": "PVC-U",
            "image": [DOMINIO + "/assets/ventana-pvc-corrediza-blanca-sala-jardin.jpg",
                      DOMINIO + "/assets/ventana-pvc-perfil-negro-dormitorio-mar.jpg",
                      DOMINIO + "/assets/ventana-pvc-led-perimetral-sala.jpg",
                      DOMINIO + "/assets/ventanas-pvc-edificio-institucional-lima.jpg"],
            "manufacturer": {"@id": DOMINIO + "/#empresa"},
            "audience": {"@type": "Audience",
                         "audienceType": "Residencial y corporativo"},
        },
    ],
}

HEAD = f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ventanas de PVC a medida en Lima | NEFUSAC — Fabricantes desde 1988</title>
<meta name="description" content="Ventanas de PVC a medida en Lima con aislamiento acústico y térmico real: vidrio laminado de 6 mm, perfil autoextinguible y sellado perimetral continuo. Fabricamos e instalamos desde 1988. Cotiza gratis por WhatsApp.">
<meta name="keywords" content="ventanas de PVC Lima, ventanas acústicas Perú, ventanas antiruido, vidrio laminado 6mm, ventanas corredizas PVC, NEFUSAC">
<meta name="author" content="Negociación Futura S.A.C.">
<meta name="robots" content="index, follow">
<meta name="theme-color" content="#8CC63E">
<link rel="canonical" href="{DOMINIO}/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="NEFUSAC">
<meta property="og:locale" content="es_PE">
<meta property="og:url" content="{DOMINIO}/">
<meta property="og:title" content="Ventanas de PVC a medida en Lima | NEFUSAC">
<meta property="og:description" content="El ruido se queda afuera. Ventanas de PVC con aislamiento acústico y térmico real. Cotiza gratis por WhatsApp: 981 124 794.">
<meta property="og:image" content="{DOMINIO}/assets/og-nefusac.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Familia en su sala con una ventana de PVC NEFUSAC y vista a la ciudad">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Ventanas de PVC a medida en Lima | NEFUSAC">
<meta name="twitter:description" content="El ruido se queda afuera. Aislamiento acústico y térmico real. Cotiza por WhatsApp: 981 124 794.">
<meta name="twitter:image" content="{DOMINIO}/assets/og-nefusac.jpg">
<link rel="icon" href="assets/logo.jpg">
<link rel="preload" as="font" type="font/woff2" href="assets/fonts/archivo-black-latin-400-normal.woff2" crossorigin>
<link rel="preload" as="image" href="assets/poster-1.webp" fetchpriority="high">
<link rel="stylesheet" href="styles.css">
<script type="application/ld+json">
{json.dumps(JSONLD, ensure_ascii=False, indent=1)}
</script>
'''

FUENTES = "".join(
    f"@font-face{{font-family:'{fam}';font-style:normal;font-weight:{w};"
    f"font-display:swap;src:url('assets/fonts/{arch}') format('woff2');}}\n"
    for fam, w, arch in [
        ("Archivo", 400, "archivo-latin-400-normal.woff2"),
        ("Archivo", 500, "archivo-latin-500-normal.woff2"),
        ("Archivo", 600, "archivo-latin-600-normal.woff2"),
        ("Archivo", 700, "archivo-latin-700-normal.woff2"),
        ("Archivo Black", 400, "archivo-black-latin-400-normal.woff2"),
    ])

# ---------------------------------------------------------------- PASO 3 y 6
CSS_EXTRA = '''
/* ═══════════════════════════════════════════════════════════════════════
   Añadido en el build de produccion. El bloque de arriba es el CSS del
   diseño, intacto. Nada de aqui cambia colores, tipografias ni espaciados
   del diseño: solo agrega comportamiento responsive y accesibilidad.
   ═══════════════════════════════════════════════════════════════════════ */

/* La cinta de valores del hero sangra a proposito (left:-2%; width:104%). Se
   recorta EN SU PROPIO contenedor, no con un overflow-x:hidden global: ese
   truco tapaba desbordes reales de otras secciones y dejaba el texto recortado
   e inalcanzable en lugar de hacerlos visibles al medirlos. */
[data-marquee] { max-width: 100vw; }
header[id="inicio"] { overflow: hidden; }

/* <picture> debe ocupar la caja que antes ocupaba el <img> */
picture { display: block; }
figure > picture, section > picture { width: 100%; height: 100%; }
picture > img { display: block; }

/* Los width/height del markup estan SOLO para reservar la proporcion y evitar
   CLS. Como atributos son hints de presentacion y equivalen a width:445px, lo
   que deformaba el logo (445x40) y desbordaba la barra en movil. Cualquier
   regla de autor gana al hint, y el style inline del diseño gana a esta: asi
   la proporcion queda reservada y el tamaño lo sigue decidiendo el diseño. */
img[width][height] { width: auto; height: auto; max-width: 100%; }

/* ── PASO 6 · foco visible en todo lo interactivo ───────────────────── */
a:focus-visible, button:focus-visible, summary:focus-visible,
input:focus-visible, textarea:focus-visible {
  outline: 3px solid #8CC63E;
  outline-offset: 3px;
  border-radius: 4px;
}
/* sobre fondo verde el propio verde no contrasta: se invierte */
#contacto a:focus-visible, #contacto button:focus-visible,
#contacto input:focus-visible, #contacto textarea:focus-visible {
  outline-color: #070808;
}

/* ── PASO 6 · respetar la preferencia de menos movimiento ───────────── */
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  *, *::before, *::after {
    animation-duration: 0.001ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.001ms !important;
  }
  [data-marquee] { animation: none !important; transform: none !important; }
  [data-reveal] { opacity: 1 !important; transform: none !important; }
}

/* ── PASO 2 · entrada progresiva sin JavaScript ─────────────────────── */
@supports (animation-timeline: view()) {
  @media (prefers-reduced-motion: no-preference) {
    [data-reveal] {
      animation: aparecer linear both;
      animation-timeline: view();
      animation-range: entry 0% entry 42%;
    }
    @keyframes aparecer {
      from { opacity: 0; transform: translateY(46px); }
      to   { opacity: 1; transform: translateY(0); }
    }
  }
}

/* ── PASO 3 · menu movil, accesible y sin JavaScript ────────────────── */
.nav-movil { display: none; position: relative; }
.nav-movil > summary {
  list-style: none; cursor: pointer; display: flex; align-items: center;
  gap: 9px; padding: 10px 16px; border-radius: 999px;
  border: 1px solid rgba(140,198,62,0.55); background: rgba(7,8,8,0.6);
  color: #F4F6F2; font-weight: 700; font-size: 12.5px; letter-spacing: 0.14em;
}
.nav-movil > summary::-webkit-details-marker { display: none; }
.nav-movil > summary:hover { border-color: #8CC63E; }
.nav-movil .barras { display: grid; gap: 4px; }
.nav-movil .barras i { display: block; width: 18px; height: 2px; background: #8CC63E; }
.nav-movil[open] > summary { border-color: #8CC63E; }
.nav-movil-panel {
  position: absolute; right: 0; top: calc(100% + 12px); z-index: 95;
  min-width: 250px; display: grid; gap: 2px; padding: 10px;
  background: rgba(7,8,8,0.97); border: 1px solid rgba(140,198,62,0.3);
  border-radius: 16px; box-shadow: 0 22px 50px rgba(0,0,0,0.55);
}
.nav-movil-panel a {
  display: block; padding: 13px 16px; border-radius: 10px;
  color: rgba(244,246,242,0.9); font-size: 14px; font-weight: 700;
  letter-spacing: 0.12em;
}
.nav-movil-panel a:hover { background: rgba(140,198,62,0.14); color: #FFFFFF; }
.nav-movil-panel .destacado {
  margin-top: 6px; background: #8CC63E; color: #070808; text-align: center;
}
.nav-movil-panel .destacado:hover { background: #A5DB5C; color: #070808; }
.nav-movil-panel .tel {
  border-top: 1px solid rgba(244,246,242,0.14); margin-top: 6px;
  padding-top: 14px; color: #8CC63E; letter-spacing: 0.06em;
}

/* el menu aparece justo donde el diseño ocultaba los enlaces del nav */
@media (max-width: 1080px) {
  .nav-movil { display: block; }
}

/* ── PASO 3 · tablet ────────────────────────────────────────────────── */
@media (max-width: 768px) {
  /* el mosaico de 4 columnas pasa a 2 y los spans se neutralizan */
  [data-mosaico] { grid-template-columns: repeat(2, 1fr) !important; }
  [data-mosaico] > figure { grid-column: auto !important; grid-row: auto !important; }
  [data-mosaico] > figure[data-ancho] { aspect-ratio: 1 / 1 !important; }
  /* los max-width fijos del diseño dejan de encajonar el texto */
  [style*="max-width: 620px"], [style*="max-width: 660px"],
  [style*="max-width: 680px"], [style*="max-width: 720px"],
  [style*="max-width: 880px"], [style*="max-width: 900px"],
  [style*="max-width: 560px"], [style*="max-width: 620px"] { max-width: 100% !important; }
  header[id="inicio"] { height: auto !important; min-height: 88vh !important; }
  section { padding-left: 5vw !important; padding-right: 5vw !important; }
}

/* ── PASO 3 · aire en las tarjetas con padding grande ───────────────── */
@media (max-width: 620px) {
  /* el editor deja hasta 48px de padding lateral: en un telefono se come el
     ancho util y el texto queda apretado contra los bordes. */
  [style*="padding: 54px 48px"] { padding: 34px 22px !important; }
  [style*="padding: 34px 38px"] { padding: 26px 20px !important; }
  [style*="padding: 34px 28px"] { padding: 26px 20px !important; }
  [style*="padding: 30px 28px"] { padding: 24px 18px !important; }
  [style*="padding: 26px 28px"] { padding: 22px 18px !important; }
  /* CORREO y TELEFONO van lado a lado con minmax(150px): a 412px no caben y
     el campo se sale de la pantalla. Apilados quedan comodos de tipear. */
  [data-form-cotiza] div[style*="minmax(min(100%, 150px)"] {
    grid-template-columns: 1fr !important;
  }
  /* la justificacion abre huecos horribles a poco ancho */
  [style*="text-align: justify"] { text-align: left !important; }
}

/* ── PASO 3 · movil ─────────────────────────────────────────────────── */
@media (max-width: 480px) {
  [data-mosaico] { grid-template-columns: 1fr !important; }
  /* el H1 a 360px: clamp() ya lo baja, pero se afina el interlineado */
  h1 { font-size: clamp(30px, 9.2vw, 44px) !important; line-height: 1.02 !important; }
  h2 { font-size: clamp(23px, 6.6vw, 34px) !important; }
  /* el parrafo del hero traia width/height fijos del editor */
  header[id="inicio"] p[style*="width: 495px"] {
    width: auto !important; height: auto !important;
  }
  /* la tira de valores no debe empujar el ancho de la pagina */
  [data-marquee] > span { padding: 0 16px !important; font-size: 16px !important; }
  figure { border-radius: 14px !important; }
}
'''

JS = '''/* NEFUSAC — lo minimo indispensable en el cliente (~2 KB).
 *
 * El resto salio del JavaScript: la entrada progresiva es CSS
 * (animation-timeline: view()), la descarga del catalogo es un <a download>,
 * el marquee y el parallax son CSS. Queda solo lo que no tiene equivalente
 * declarativo:
 *   1. arrancar los videos 2 y 3 al entrar en pantalla (preload="none")
 *   2. la cuenta ascendente de los indicadores
 *   3. armar el mensaje de WhatsApp del formulario
 * Nada de esto oculta contenido: sin JS la pagina se lee completa y las
 * cifras ya vienen escritas en el HTML.
 */
(function () {
  'use strict';

  /* 1 · videos diferidos ------------------------------------------------ */
  var diferidos = document.querySelectorAll('video[data-diferido]');
  if (diferidos.length && 'IntersectionObserver' in window) {
    var ov = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        var v = e.target;
        if (e.isIntersecting) {
          v.muted = true;
          if (!v.dataset.listo) { v.dataset.listo = '1'; v.load(); }
          v.play().catch(function () {});
        } else if (!v.paused) {
          v.pause();
        }
      });
    }, { threshold: 0.2 });
    diferidos.forEach(function (v) { ov.observe(v); });
  }

  /* el video del hero: algunos navegadores descartan el atributo muted */
  var hero = document.querySelector('video[data-hero]');
  if (hero) {
    hero.muted = true;
    hero.play().catch(function () {});
  }

  /* 2 · indicadores ------------------------------------------------------ */
  var cifras = document.querySelectorAll('[data-count]');
  if (cifras.length && 'IntersectionObserver' in window &&
      !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var oc = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        oc.unobserve(e.target);
        var fin = parseInt(e.target.getAttribute('data-count'), 10);
        var t0 = performance.now();
        (function paso(t) {
          var p = Math.min((t - t0) / 1600, 1);
          e.target.textContent = Math.round(fin * (1 - Math.pow(1 - p, 3)));
          if (p < 1) requestAnimationFrame(paso);
        })(t0);
      });
    }, { threshold: 0.5 });
    cifras.forEach(function (c) { oc.observe(c); });
  }

  /* 3 · formulario -> WhatsApp ------------------------------------------ */
  var form = document.querySelector('[data-form-cotiza]');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var f = new FormData(form);
      var l = function (k, v) { return v ? k + ': ' + v + '\\n' : ''; };
      var msg = 'Hola NEFUSAC, quiero una cotización.\\n' +
        l('Nombre', f.get('nombre')) + l('Correo', f.get('correo')) +
        l('Teléfono', f.get('telefono')) + l('Proyecto', f.get('proyecto')) +
        l('Mensaje', f.get('mensaje'));
      window.open('https://wa.me/URL_WA?text=' + encodeURIComponent(msg.trim()) +
        '&utm_source=web&utm_medium=form&utm_content=formulario', '_blank', 'noopener');
      var ok = form.querySelector('[data-form-ok]');
      if (ok) { ok.hidden = false; }
    });
  }
})();
'''


# ================================================================ helpers
def dims_de(ruta):
    return DIMS.get(os.path.basename(ruta))


def picture(m):
    """Convierte <img src="assets/x.jpg" ...> en <picture> con WebP + fallback."""
    tag = m.group(0)
    src = re.search(r'src="(assets/[^"]+)"', tag)
    if not src:
        return tag
    ruta = src.group(1)
    d = dims_de(ruta)
    if not d:
        return tag
    stem, ext = os.path.splitext(ruta)
    # Solo la PRIMERA imagen del documento (el logo de la barra) va con prioridad
    # alta: es lo unico sobre el pliegue. El logo del pie es la misma ruta pero
    # esta al final, y darle prioridad le robaria ancho de banda al hero.
    picture.n = getattr(picture, "n", 0) + 1
    sobre_el_pliegue = picture.n == 1

    # width/height reales -> sin CLS
    if "width=" not in tag:
        tag = tag.replace("<img", f'<img width="{d["w"]}" height="{d["h"]}"', 1)
    # carga
    if sobre_el_pliegue:
        tag = tag.replace("<img", '<img loading="eager" fetchpriority="high" decoding="async"', 1)
    else:
        tag = tag.replace("<img", '<img loading="lazy" decoding="async"', 1)

    # srcset por ancho cuando hay variantes
    if d["srcset"]:
        anchos = d["srcset"] + [d["w"]]
        webp = ", ".join(
            (f"{stem}-w{w}.webp {w}w" if w != d["w"] else f"{stem}.webp {w}w")
            for w in anchos)
        jpg = ", ".join(
            (f"{stem}-w{w}{ext} {w}w" if w != d["w"] else f"{ruta} {w}w")
            for w in anchos)
        sizes = '(max-width: 480px) 92vw, (max-width: 768px) 46vw, 33vw'
        fuentes = (f'<source type="image/webp" srcset="{webp}" sizes="{sizes}">'
                   f'<source type="image/jpeg" srcset="{jpg}" sizes="{sizes}">')
    else:
        fuentes = f'<source type="image/webp" srcset="{stem}.webp">'
    return f"<picture>{fuentes}{tag}</picture>"


def construir():
    s = open(SRC, encoding="utf-8").read()

    # ---- CSS fuera del HTML ------------------------------------------------
    estilos = re.findall(r"<style[^>]*>(.*?)</style>", s, re.S)
    s = re.sub(r"<style[^>]*>.*?</style>", "", s, flags=re.S)
    css = FUENTES + "\n" + "\n".join(estilos) + CSS_EXTRA

    # ---- head nuevo -------------------------------------------------------
    s = re.sub(r"<head>.*?</head>", "<head>\n" + HEAD + "</head>", s, flags=re.S)
    s = s.replace('<html lang="es">', '<html lang="es-PE">')

    # ---- tipografia: unidades que no se separan ---------------------------
    # En el editor alguien quiso que "6" y "mm" no cayeran en lineas distintas y
    # metio una tanda de &nbsp; ANTES del numero. Eso no une nada: solo abre un
    # hueco de 6 espacios, muy visible en movil. La forma correcta es un espacio
    # duro ENTRE el numero y la unidad, que es justo lo que se buscaba.
    # Solo en el texto visible: dentro de <script> (el JSON-LD) las entidades no
    # se decodifican, y Google leeria literalmente "6&nbsp;mm" en la descripcion.
    def unir_unidades(tramo):
        tramo = re.sub(r'(?:&nbsp;\s*){2,}', ' ', tramo)   # se elimina el hueco
        return re.sub(r'(\d)\s+mm\b', r'\1&nbsp;mm', tramo)

    partes = re.split(r'(<script\b.*?</script>)', s, flags=re.S)
    s = "".join(p if i % 2 else unir_unidades(p) for i, p in enumerate(partes))
    print("unidades unidas con espacio duro: %d (solo texto visible)"
          % len(re.findall(r'&nbsp;mm', s)))

    # ---- PASO 3 · pisos rigidos de ancho ----------------------------------
    # El editor deja `minmax(340px, 1fr)` y `min-width: 280px`. Ese valor es un
    # piso DURO: la pista no baja de ahi aunque el contenedor sea mas angosto, y
    # el bloque se sale de la pantalla. Con min(100%, N) el piso cede cuando no
    # cabe y se comporta igual cuando si cabe, en todo ancho y sin media query.
    n_grid = len(re.findall(r'minmax\(\d+px, 1fr\)', s))
    s = re.sub(r'minmax\((\d+)px, 1fr\)', r'minmax(min(100%, \1px), 1fr)', s)
    n_flex = len(re.findall(r'min-width: \d+px', s))
    s = re.sub(r'min-width: (\d+)px', r'min-width: min(100%, \1px)', s)
    print("pisos flexibilizados: %d grids + %d flex" % (n_grid, n_flex))

    # ---- PASO 2 · imagenes ------------------------------------------------
    s = re.sub(r'<img\b[^>]*?>', picture, s)

    # ---- PASO 2 · videos --------------------------------------------------
    def video(m):
        t = m.group(0)
        t = t.replace('preload="auto"', 'preload="none"')
        t = re.sub(r'poster="assets/([^"]+)\.jpg"', r'poster="assets/\1.webp"', t)
        if "video-1.mp4" in t:                      # hero: arranca solo
            t = t.replace("<video", "<video data-hero", 1)
        else:                                       # 2 y 3: al entrar en pantalla
            t = t.replace(" autoplay", "").replace("<video", "<video data-diferido", 1)
        return t
    s = re.sub(r"<video\b[^>]*>", video, s)

    # ---- PASO 5 · un CTA por seccion, con UTM -----------------------------
    orden = iter(CTAS)

    def cta(m):
        try:
            contenido, texto = next(orden)
        except StopIteration:
            return m.group(0)
        return 'href="%s"' % wa_url(contenido, texto)
    s = re.sub(r'href="https://wa\.me/[^"]*"', cta, s)

    # ---- PASO 5 · telefono clicable y rel en externos ---------------------
    s = s.replace(
        '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#8CC63E"',
        '<a href="tel:%s" style="color: inherit; display: inline-flex; align-items: center; gap: 8px;" '
        'aria-label="Llamar al 981 124 794"><svg width="15" height="15" viewBox="0 0 24 24" '
        'fill="none" stroke="#8CC63E"' % TEL, 1)
    s = s.replace("      981 124 794\n    </span>", "      981 124 794</a>\n    </span>", 1)
    s = re.sub(r'target="_blank"(?![^>]*rel=)', 'target="_blank" rel="noopener"', s)

    # ---- PASO 2 · el catalogo ya no necesita JS ---------------------------
    s = s.replace(" data-descargar-catalogo", "")

    # ---- PASO 3 · marcar el mosaico y el menu movil -----------------------
    s = s.replace('<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px;">',
                  '<div data-mosaico style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px;">', 1)
    s = re.sub(r'(<figure style="grid-column: span 2;(?! grid-row) )', r'\1', s)
    s = s.replace('<figure style="grid-column: span 2; margin: 0;',
                  '<figure data-ancho style="grid-column: span 2; margin: 0;')

    destinos = [("#inicio", "INICIO"), ("#silencio", "SILENCIO"), ("#producto", "PRODUCTO"),
                ("#galeria", "AMBIENTES"), ("#led", "LUCES LED"), ("#ficha", "FICHA TÉCNICA"),
                ("#empresa", "EMPRESA")]
    enlaces = "".join(f'<a href="{h}">{t}</a>' for h, t in destinos)
    menu = (
        '<details class="nav-movil">'
        '<summary aria-label="Abrir menú de navegación"><span class="barras" aria-hidden="true">'
        '<i></i><i></i><i></i></span>MENÚ</summary>'
        '<nav class="nav-movil-panel" aria-label="Navegación principal">'
        + enlaces +
        f'<a class="tel" href="tel:{TEL}">981 124 794</a>'
        f'<a class="destacado" href="{wa_url("menu-movil", "Hola NEFUSAC, quiero cotizar mis ventanas de PVC.")}" '
        'target="_blank" rel="noopener">COTIZA POR WHATSAPP</a>'
        '</nav></details>')
    s = s.replace("</nav>", menu + "</nav>", 1)

    # ---- PASO 2 · cifras escritas en el HTML (sin JS ya son correctas) ----
    def cifra(m):
        return m.group(0).replace(">0<", ">" + m.group(1) + "<")
    s = re.sub(r'<span data-count="(\d+)"[^>]*>0</span>', cifra, s)

    # ---- confirmacion del formulario, presente y oculta -------------------
    s = s.replace(
        '<p style="margin: 0; color: rgba(15,20,16,0.5); font-size: 13px;">Tu solicitud',
        '<p data-form-ok hidden style="margin: 0; color: #3D7212; font-size: 14px; font-weight: 700;">'
        'Se abrió WhatsApp con tu solicitud. Envíala y te respondemos en el día.</p>'
        '<p style="margin: 0; color: rgba(15,20,16,0.5); font-size: 13px;">Tu solicitud', 1)

    # ---- salida ------------------------------------------------------------
    s = s.replace('<script src="assets/app.js"></script>',
                  '<script src="assets/app.js" defer></script>')
    s = re.sub(r"\n{3,}", "\n\n", s)
    open(OUT, "w", encoding="utf-8").write(s)
    open(CSS, "w", encoding="utf-8").write(css)
    open(os.path.join(RAIZ, "assets", "app.js"), "w", encoding="utf-8").write(
        JS.replace("URL_WA", WA))

    open(os.path.join(RAIZ, "robots.txt"), "w", encoding="utf-8").write(
        f"User-agent: *\nAllow: /\n\nSitemap: {DOMINIO}/sitemap.xml\n")
    # Una sola <url>: los anclajes (#silencio, #led...) no son paginas distintas
    # para Google, que los normaliza a "/". Listarlos solo ensuciaba el sitemap.
    # Debajo van las fotos con <image:image>, que es como Google las descubre
    # para la busqueda de imagenes; el title es el alt de cada una.
    imgs = []
    for ruta, alt in sorted(re.findall(r'<img[^>]*src="(assets/[^"]+)"[^>]*alt="([^"]*)"', s)):
        if any(x in ruta for x in ("logo", "-w")):
            continue
        imgs.append(f"    <image:image><image:loc>{DOMINIO}/{ruta}</image:loc>"
                    f"<image:title>{alt.replace('&', '&amp;')}</image:title></image:image>")
    open(os.path.join(RAIZ, "sitemap.xml"), "w", encoding="utf-8").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
        f"  <url>\n    <loc>{DOMINIO}/</loc>\n"
        "    <changefreq>monthly</changefreq>\n    <priority>1.0</priority>\n"
        + "\n".join(imgs) + "\n  </url>\n</urlset>\n")

    print("index.html  %6.1f KB" % (os.path.getsize(OUT) / 1024))
    print("styles.css  %6.1f KB" % (os.path.getsize(CSS) / 1024))
    print("app.js      %6.1f KB" % (os.path.getsize(os.path.join(RAIZ, 'assets', 'app.js')) / 1024))
    print("robots.txt + sitemap.xml escritos")


if __name__ == "__main__":
    construir()
