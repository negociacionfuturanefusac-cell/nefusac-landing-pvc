#!/usr/bin/env python3
"""Genera el favicon cuadrado a partir del emblema del logo.

Por que existe este script: en los resultados de Google el sitio salia con el
globo terraqueo genérico en lugar del logo. El favicon SI estaba declarado, pero
apuntaba a assets/logo.jpg, que mide 445x132 (relacion 3.37:1). Google exige que
el favicon sea CUADRADO y multiplo de 48 px; un rectangulo asi lo descarta.

Dos decisiones de diseño:

1. Se usa solo el ROMBO, no la palabra "NEFUSAC". A 16 px —el tamaño al que se
   ve de verdad un favicon— el texto es una mancha ilegible. Usar la marca
   grafica y no el logotipo completo es la practica estandar.

2. El rombo ocupa el 76% del lienzo, no el 100%. Google encierra el favicon en
   un chip CIRCULAR: si el rombo llegara a los bordes, sus cuatro puntas
   caerian justo sobre la circunferencia y se recortarian. Con ese margen las
   puntas quedan holgadamente dentro del circulo, y lo unico que se recorta son
   las esquinas verdes del fondo, que no llevan informacion.

Sobre la nitidez: el emblema en el archivo original mide 78x78 px. Para los
tamaños grandes se amplia la MASCARA con Lanczos y despues se umbraliza al 50%,
lo que devuelve bordes perfectamente duros. La figura son solo aristas rectas,
asi que rectas entran y rectas salen — no queda el halo borroso de una
ampliacion normal. No se redibujo como vector a proposito: la geometria son dos
rombos entrelazados y trazarla a mano se arriesga a alterar el logo.

Uso: python3 tools/favicon.py   (desde la raiz del repo)
"""
import os

from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(RAIZ, "assets")

# Recuadro del emblema dentro de assets/logo.jpg, medido barriendo los pixeles
# oscuros y cortando en el primer hueco limpio antes de la "N".
CAJA = (26, 26, 104, 103)          # izq, arr, der, abj  -> 78x78

VERDE = (140, 198, 62)             # #8CC63E, el mismo de <meta name="theme-color">
NEGRO = (7, 8, 8)
OCUPACION = 0.76                   # cuanto del lienzo ocupa el rombo

# Multiplos de 48, como pide Google. El 180 es el que reclama iOS para el icono
# de la pantalla de inicio y no sigue esa regla.
TAMANOS = [48, 96, 192, 512]
APPLE = 180


def mascara_emblema():
    """Devuelve el emblema como mascara cuadrada en blanco y negro, sin fondo."""
    logo = Image.open(os.path.join(A, "logo.jpg")).convert("RGB")
    em = logo.crop(CAJA)
    # el JPEG dejo el negro sucio y el verde moteado: se separa por luminancia
    gris = em.convert("L")
    m = gris.point(lambda v: 255 if v < 110 else 0, mode="L")

    # El emblema mide 78x77, no es exactamente cuadrado. Se RELLENA a cuadrado
    # en vez de estirarlo: un 1.3% de deformacion no se ve, pero deformar el
    # logo de un cliente no es algo que se haga "porque no se nota".
    lado = max(m.size)
    cuadrada = Image.new("L", (lado, lado), 0)
    cuadrada.paste(m, ((lado - m.width) // 2, (lado - m.height) // 2))
    return cuadrada


def icono(mask, lado):
    """Compone el emblema centrado sobre el cuadrado verde, con bordes duros."""
    dibujo = round(lado * OCUPACION)
    # ampliar suave y volver a endurecer: asi las aristas quedan limpias
    m = mask.resize((dibujo, dibujo), Image.LANCZOS).point(
        lambda v: 255 if v >= 128 else 0, mode="L")

    lienzo = Image.new("RGB", (lado, lado), VERDE)
    tinta = Image.new("RGB", (dibujo, dibujo), NEGRO)
    off = ((lado - dibujo) // 2, (lado - dibujo) // 2)
    lienzo.paste(tinta, off, m)
    return lienzo


def main():
    mask = mascara_emblema()
    print(f"emblema recortado: {mask.size[0]}x{mask.size[1]}")

    for lado in TAMANOS:
        p = os.path.join(A, f"icono-{lado}.png")
        icono(mask, lado).save(p, "PNG", optimize=True)
        print(f"  assets/icono-{lado}.png{'':<4} {os.path.getsize(p):>6} B")

    p = os.path.join(A, "apple-touch-icon.png")
    icono(mask, APPLE).save(p, "PNG", optimize=True)
    print(f"  assets/apple-touch-icon.png {os.path.getsize(p):>6} B")

    # favicon.ico en la RAIZ: navegadores y rastreadores lo piden por
    # convencion en /favicon.ico aunque no este declarado. Es la red de
    # seguridad si alguna vez se pierde el <link>.
    p = os.path.join(RAIZ, "favicon.ico")
    icono(mask, 256).save(p, "ICO", sizes=[(16, 16), (32, 32), (48, 48)])
    print(f"  favicon.ico{'':<15} {os.path.getsize(p):>6} B  (16/32/48)")


if __name__ == "__main__":
    main()
