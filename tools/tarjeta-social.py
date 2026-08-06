#!/usr/bin/env python3
"""Genera assets/og-nefusac.jpg: la tarjeta que se ve al compartir el enlace.

Antes era un recorte de la foto de la familia. Una foto sola no comunica de quien
es el enlace: en WhatsApp la tarjeta compite con decenas de mensajes y lo que la
identifica es la marca. Aqui la foto queda de fondo, oscurecida, con el logo, el
titular y el telefono encima.

Formato 1200x630 (1.91:1), el que piden WhatsApp, Facebook, LinkedIn y X.
Se mantiene por debajo de 300 KB, umbral tipico para que WhatsApp la muestre.

Uso: python3 tools/tarjeta-social.py   (desde landing/)
"""
import os
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(RAIZ, "assets")
FNT = "/tmp/fnt"

W, H = 1200, 630
VERDE = (140, 198, 62)
NEGRO = (7, 8, 8)
HUESO = (244, 246, 242)


def fuente(arch, px):
    return ImageFont.truetype(os.path.join(FNT, arch), px)


def main():
    # Fondo: la sala con corrediza negra, elegida por ser luminosa y de dia.
    # Se recorta 1.91:1 ANCLADO ARRIBA: esta foto es una de las capturas del
    # render y trae el rotulo impreso en el pie, asi que tomar la franja
    # superior lo deja fuera sin tener que taparlo.
    # Nota de calidad: la fuente mide 547 px de ancho, asi que hay que ampliar
    # 2.19x para llegar a 1200. Con el original a resolucion nativa la tarjeta
    # saldria nitida; con esta sale algo blanda, aceptable a tamano de chat.
    fondo = Image.open(os.path.join(A, "ventana-pvc-corrediza-negra-sala.jpg")).convert("RGB")
    alto = round(fondo.width / (W / H))
    lienzo = fondo.crop((0, 0, fondo.width, alto)).resize((W, H), Image.LANCZOS)
    # menos oscurecido que antes: la foto se eligio por luminosa y bajarla
    # demasiado anulaba el motivo de elegirla. La legibilidad se resuelve con el
    # degradado inferior, no apagando toda la imagen.
    lienzo = ImageEnhance.Brightness(lienzo).enhance(0.72)

    # degradado inferior, mas marcado para compensar el fondo mas claro
    grad = Image.new("L", (1, H))
    for i in range(H):
        t = i / H
        grad.putpixel((0, i), int(240 * min(1, max(0, (t - 0.18) / 0.82) ** 1.15)))
    velo = Image.new("RGB", (W, H), NEGRO)
    lienzo = Image.composite(velo, lienzo, grad.resize((W, H)))

    d = ImageDraw.Draw(lienzo)
    M = 68  # margen

    # logo, en su placa verde como en la barra del sitio
    logo = Image.open(os.path.join(A, "logo.jpg")).convert("RGB")
    lh = 76
    logo = logo.resize((round(logo.width * lh / logo.height), lh), Image.LANCZOS)
    placa = Image.new("RGB", (logo.width + 24, lh + 18), VERDE)
    mask = Image.new("L", placa.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, placa.size[0] - 1, placa.size[1] - 1],
                                           radius=14, fill=255)
    placa.paste(logo, (12, 9))
    lienzo.paste(placa, (M, M), mask)

    # titular, en dos lineas como en el hero
    f1 = fuente("archivo-black-latin-400-normal.ttf", 82)
    d.text((M, 300), "EL RUIDO SE QUEDA", font=f1, fill=HUESO)
    d.text((M, 392), "AFUERA.", font=f1, fill=VERDE)

    # telefono arriba a la derecha, a la altura del logo: al pie chocaba con la
    # bajada y le tapaba "Fabricantes desde 1988"
    f3 = fuente("archivo-latin-700-normal.ttf", 29)
    tel = "WhatsApp 981 124 794"
    tw = d.textlength(tel, font=f3)
    px, py = 24, 14
    bx1 = W - M - tw - px * 2
    by1 = M + (lh + 18 - (29 + py * 2)) // 2      # centrado con la placa del logo
    d.rounded_rectangle([bx1, by1, bx1 + tw + px * 2, by1 + 29 + py * 2],
                        radius=999, fill=VERDE)
    d.text((bx1 + px, by1 + py - 3), tel, font=f3, fill=NEGRO)

    # bajada, ahora con todo el ancho disponible
    f2 = fuente("archivo-latin-500-normal.ttf", 31)
    d.text((M, 502), "Ventanas de PVC a medida en Lima  ·  Fabricantes desde 1988",
           font=f2, fill=(226, 232, 220))

    # se guarda ajustando calidad hasta quedar bajo el umbral de WhatsApp
    p = os.path.join(A, "og-nefusac.jpg")
    for q in (90, 86, 82, 78, 74, 70):
        lienzo.save(p, "JPEG", quality=q, optimize=True, progressive=True)
        if os.path.getsize(p) <= 300 * 1024:
            break
    print(f"og-nefusac.jpg  {W}x{H}  calidad {q}  {os.path.getsize(p)/1024:.0f} KB")


if __name__ == "__main__":
    main()
