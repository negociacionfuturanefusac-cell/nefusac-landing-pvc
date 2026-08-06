#!/usr/bin/env python3
"""Migracion de SEO de imagenes: nombres de archivo y textos alternativos.

Google usa el nombre del archivo como senal en la busqueda de imagenes, y
`gal1.jpg` o `proy-7.jpg` no dicen nada. Este script renombra las 30 fotos y sus
variantes de srcset a nombres con palabras clave, y reescribe los alt para que
nombren el producto ("ventana de PVC") y no solo el ambiente.

Se ejecuta UNA sola vez sobre index.src.html y assets/. Es idempotente: si los
nombres ya estan migrados no hace nada.

Uso: python3 tools/seo-imagenes.py   (desde landing/)
"""
import json
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(RAIZ, "assets")
SRC = os.path.join(RAIZ, "index.src.html")

# stem viejo -> (stem nuevo con palabras clave, alt nuevo)
# Los alt describen la foto e incluyen el producto de forma natural: se leen
# como una frase, no como una lista de palabras clave.
TABLA = {
    # galeria de ambientes
    "gal1": ("ventana-pvc-corrediza-blanca-sala-jardin",
             "Ventana corrediza de PVC blanca en una sala con vista al jardín"),
    "gal2": ("ventana-pvc-dormitorio-vista-al-mar",
             "Ventana de PVC en un dormitorio frente al mar al atardecer"),
    "gal3": ("ventana-pvc-corrediza-cocina-encimera",
             "Ventana corrediza de PVC sobre la encimera de una cocina"),
    "gal4": ("ventana-pvc-corrediza-blanca-detalle",
             "Detalle del perfil de una ventana corrediza de PVC blanca"),
    "gal5": ("ventana-pvc-perfil-negro-dormitorio-mar",
             "Ventana de PVC con perfil negro en un dormitorio con vista al mar"),
    "gal6": ("ventana-pvc-corrediza-negra-sala",
             "Ventana corrediza de PVC negra en una sala de estar"),
    "gal7": ("ventana-pvc-home-office-vista-ciudad",
             "Ventana de PVC en un home office con vista a la ciudad"),
    "cierre-bano": ("ventana-pvc-corrediza-bano-perfil-negro",
                    "Ventana corrediza de PVC con perfil negro en un baño"),
    # accesorio de LED perimetral
    "led-sala": ("ventana-pvc-led-perimetral-sala",
                 "Ventana de PVC con luz LED perimetral encendida en una sala"),
    "led-bano-2": ("ventana-pvc-led-perimetral-bano-travertino",
                   "Ventana de PVC con LED perimetral en un baño en travertino"),
    "led-estudio": ("ventana-pvc-negra-led-perimetral-estudio",
                    "Ventana de PVC negra con LED perimetral en un estudio"),
    "led-estar": ("ventana-pvc-led-perimetral-estar",
                  "Ventana de PVC con LED perimetral sobre el sofá de un estar"),
    "led-noche": ("ventana-pvc-led-perimetral-de-noche",
                  "Ventana de PVC con halo de LED perimetral en un ambiente nocturno"),
    "led-cocina-isla": ("ventana-pvc-corrediza-led-perimetral-cocina",
                        "Ventana corrediza de PVC con LED perimetral encendido en una cocina"),
    "led-sala-2": ("ventana-pvc-blanca-led-perimetral-atardecer",
                   "Ventana de PVC blanca con halo LED al atardecer en una sala"),
    "led-escalera": ("ventana-pvc-led-perimetral-escalera",
                     "Ventana de PVC con LED perimetral iluminando una escalera"),
    # proyectos instalados
    "proy-1": ("ventanas-pvc-edificio-institucional-lima",
               "Fachada de un edificio institucional en Lima con ventanas de PVC instaladas por NEFUSAC"),
    "proy-2": ("ventana-pvc-interior-residencial-jardin",
               "Ventana de PVC en un interior residencial con vista al jardín"),
    "proy-3": ("ventanas-pvc-residencia-privada-interior",
               "Sala de una residencia privada con ventanas verticales de PVC"),
    "proy-4": ("ventanas-pvc-conjunto-modular-terraza",
               "Conjunto de viviendas modulares con terraza y ventanas de PVC"),
    "proy-5": ("ventana-pvc-corrediza-salida-jardin",
               "Ventana corrediza de PVC con salida al jardín"),
    "proy-6": ("ventanas-pvc-cocina-tres-cuerpos",
               "Cocina con tres ventanas de PVC de cuerpos independientes"),
    "proy-7": ("ventanas-pvc-vivienda-modular",
               "Vivienda modular equipada con ventanas de PVC de NEFUSAC"),
    "proy-8": ("ventanas-pvc-modulo-blanco-panoramicas",
               "Módulo blanco con ventanas panorámicas de PVC"),
    "proy-9": ("ventana-pvc-corrediza-bano-enchape",
               "Ventana corrediza de PVC sobre enchape en un baño"),
    "proy-10": ("sellado-perimetral-ventana-pvc-en-obra",
                "Sellado perimetral de una ventana de PVC durante la instalación en obra"),
    "proy-11": ("ventana-pvc-corrediza-departamento-enchape",
                "Ventana corrediza de PVC sobre enchape en un departamento"),
    "proy-12": ("ventana-pvc-panoramica-mezanine",
                "Ventana panorámica de PVC con persianas en un mezanine"),
    # empresa y cierre
    "equipo-nefusac": ("operario-nefusac-planta-fabricacion-pvc",
                       "Operario de NEFUSAC en la planta de fabricación de ventanas de PVC"),
    "cierre-familia": ("familia-sala-ventana-pvc-nefusac",
                       "Familia en su sala disfrutando una ventana de PVC de NEFUSAC"),
}


def renombrar():
    """Renombra cada foto y todas sus variantes (-wN) en jpg/png/webp."""
    movidos = 0
    for viejo, (nuevo, _) in TABLA.items():
        for f in sorted(os.listdir(A)):
            base, ext = os.path.splitext(f)
            if ext not in (".jpg", ".png", ".webp"):
                continue
            # coincide exacto o con sufijo de variante -w400 / -w640 ...
            m = re.fullmatch(re.escape(viejo) + r"(-w\d+)?", base)
            if not m:
                continue
            destino = nuevo + (m.group(1) or "") + ext
            if f == destino:
                continue
            os.rename(os.path.join(A, f), os.path.join(A, destino))
            movidos += 1
    return movidos


def actualizar_html():
    s = open(SRC, encoding="utf-8").read()
    n_src = n_alt = 0
    for viejo, (nuevo, alt) in TABLA.items():
        # rutas: assets/viejo.ext y assets/viejo-wN.ext
        patron = r'assets/' + re.escape(viejo) + r'(-w\d+)?\.(jpg|png|webp)'
        s, k = re.subn(patron, lambda m: f"assets/{nuevo}{m.group(1) or ''}.{m.group(2)}", s)
        n_src += k
        # el alt viejo cuelga del <img> cuyo src ya quedo renombrado
        patron_alt = (r'(<img[^>]*src="assets/' + re.escape(nuevo) +
                      r'\.(?:jpg|png|webp)"[^>]*alt=")([^"]*)(")')
        s, k = re.subn(patron_alt, lambda m: m.group(1) + alt + m.group(3), s)
        n_alt += k
    open(SRC, "w", encoding="utf-8").write(s)
    return n_src, n_alt


def actualizar_manifiestos():
    for nombre in ("DIMENSIONES.json", "MANIFEST.json"):
        p = os.path.join(A, nombre)
        if not os.path.exists(p):
            continue
        txt = open(p, encoding="utf-8").read()
        for viejo, (nuevo, _) in TABLA.items():
            txt = re.sub(r'\b' + re.escape(viejo) + r'(-w\d+)?\.(jpg|png|webp)',
                         lambda m: f"{nuevo}{m.group(1) or ''}.{m.group(2)}", txt)
        open(p, "w", encoding="utf-8").write(txt)


if __name__ == "__main__":
    n = renombrar()
    src, alt = actualizar_html()
    actualizar_manifiestos()
    print(f"archivos renombrados : {n}")
    print(f"rutas actualizadas   : {src}")
    print(f"alt reescritos       : {alt}")
    quedan = [f for f in os.listdir(A)
              if re.match(r'^(gal\d|proy-\d)', os.path.splitext(f)[0])]
    print(f"nombres genericos que quedan: {len(quedan)}")
