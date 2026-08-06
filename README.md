# NEFUSAC — Landing Ventanas de PVC (v7)

Landing page de **Negociación Futura S.A.C.** para la línea de ventanas de PVC,
compilada desde el proyecto de Claude Design
[`NEFUSAC Ventanas PVC Alto Impacto`](https://claude.ai/design/p/7b6994dd-ac3b-4ed9-bb33-d4e9c4430873),
archivo fuente `NEFUSAC Landing v7.dc.html`.

## Qué es esto

El archivo original del diseño es un **bundle autoextraíble de 18.52 MB**: lleva
`<script type="__bundler/manifest">` con 47 assets en base64 y
`<script type="__bundler/template">` con el markup como string, que se desempaqueta
en el navegador con React + ReactDOM + el runtime de Claude Design.

Acá eso es **HTML estático de producción, sin JavaScript de framework**. El
andamiaje se resolvió en build-time (`<x-dc>`, `<helmet>`, `<sc-for>`, `<sc-if>`,
`{{ }}`, `style-hover`, `sc-camel-*`) y en el cliente quedan 3 KB propios.

| Archivo | Contenido |
|---|---|
| `index.html` | Markup de producción (74 KB) |
| `styles.css` | CSS del diseño + responsive y accesibilidad (13 KB) |
| `assets/app.js` | 3 KB: videos diferidos, contadores y formulario |
| `assets/` | Imágenes WebP + fallback, videos, fuentes, PDF |
| `robots.txt` · `sitemap.xml` | Indexación |
| `index.src.html` | Entrada del build, no se sirve |
| `tools/compilar-dc.py` | Diseño `.dc.html` → `index.src.html` |
| `tools/construir-produccion.py` | `index.src.html` → producción |

Para reconstruir: `python3 tools/construir-produccion.py`. Es idempotente.

## Lo que falta: las fotos buenas

**Las 28 fotos de galería, LED y proyectos son capturas del render** y traen el
rótulo impreso en el pixel; por eso `<style id="stopgap-rotulos">` oculta los
`figcaption`. Se nota en el peso: el manifest del bundle declara **5.12 MB de
JPEG** y acá las imágenes suman 1.95 MB, o sea menor resolución.

**Se arregla subiendo el bundle de 18.52 MB**: parseando su manifest salen los 34
JPEG a resolución real, las 5 woff2 y el PDF. Después basta borrar ese `<style>`.

## Contraste: 5 casos que no alcanzan AA

Medido sobre el render, no en teoría. El par que el brief pedía verificar pasa
bien: **#8CC63E sobre #070808 da 9.80:1**. Pero hay 14 nodos en 5 casos que no
llegan a 4.5:1, todos con colores del diseño sobre fondos claros o verdes.
No se cambiaron porque el diseño estaba fuera de alcance:

| Caso | Actual | Mínimo que pasa |
|---|---|---|
| Kickers `#5E9A22` sobre `#F7F8F4` | 3.22:1 | `#4D7E1C` → 4.56:1 |
| Números 01–04 `#5E9A22` sobre blanco | 3.43:1 | `#50831D` → 4.56:1 |
| Kicker `#6FA023` sobre blanco | 3.12:1 | `#5A821C` → 4.52:1 |
| Texto blanco 85% sobre `#6FA023` | 3.12:1 | fondo a `#5A821C`, o texto a `#070808` → 6.42:1 |
| Nota de certificaciones, blanco 78% | 3.12:1 | ídem |

Todos pasan **AA para texto grande** (3:1); fallan para texto normal.

## Interactividad (`assets/app.js`)

Port 1:1 de la lógica del componente original:

- **Videos de fondo** — reafirma `muted`/`loop`/`playsinline` y reintenta
  `play()` tras la primera interacción, porque varios navegadores bloquean el
  autoplay si el video no está realmente silenciado.
- **Entrada progresiva** — `IntersectionObserver` sobre `[data-reveal]`, más un
  barrido en scroll que cubre los bloques ya visibles al cargar, donde el
  observer puede no disparar.
- **Contadores** — animan de 0 al valor de `data-count` con easing cúbico.
- **Parallax** del video del hero durante la primera pantalla.
- **Marquee** a 22 s (prop `marqueeSpeed` del diseño).
- **Catálogo** — se descarga como blob para renombrar el archivo; si falla, se
  abre en pestaña nueva.
- **Formulario** — no tiene backend: arma el mensaje y lo abre en WhatsApp
  (`wa.me/51981124794`), omitiendo los campos vacíos, y luego muestra la
  confirmación.

## Verificado

Con Chromium 1194 vía Playwright, sirviendo el directorio en local:

- Las 8 secciones (`inicio`, `silencio`, `producto`, `galeria`, `ficha`, `led`,
  `empresa`, `contacto`) presentes y sin residuo del DSL en el DOM.
- 33 `<img>` cargan sin roturas; 38 reglas `:hover` activas y comprobadas
  (el color del nav cambia al pasar el cursor).
- Los 57 bloques `[data-reveal]` se revelan al hacer scroll; ninguno queda oculto.
- Contadores llegan a 4 / 6 / 100 / 38.
- Mosaico de proyectos con sus spans correctos: 637×637 para `proy-1` y
  `proy-7`, 637×319 para `proy-3` y `proy-12`, 312×312 el resto.
- Galería y LED con 8 figuras en 4:3 cada una.
- Formulario: 6 campos, arma el mensaje correcto, omite vacíos y no duplica la
  confirmación si se envía dos veces.
- Sin scroll horizontal a 1440 px ni a 390 px.

Con los videos y el PDF ya instalados: sirven con HTTP 200 (el PDF en sus
7,294,931 bytes exactos) y los 3 MP4 decodifican sus 193 fotogramas completos
con PyAV, sin truncamiento.

Dos cosas del entorno de prueba que **no** son fallos de la página:
`fonts.googleapis.com` está bloqueado por el proxy, así que las tipografías
Archivo y Archivo Black caen a la del sistema (en producción cargan normal); y
el Chromium de Playwright no trae códecs propietarios, por lo que los `<video>`
reportan `MEDIA_ERR_SRC_NOT_SUPPORTED` y se quedan en su `poster`. La validez
de los MP4 se comprobó decodificándolos aparte, no en el navegador.

## Notas

- La landing es independiente del aplicativo de contratos en la raíz del repo
  (`/index.html`); no comparten código ni assets.
- Datos de contacto embebidos: WhatsApp 981 124 794, teléfono (01) 326 4240,
  `cotiza@nefusac.com.pe`, Jr. Mariscal Agustín Gamarra 132, San Luis, Lima.
- El formulario declara el uso de datos bajo la Ley N.º 29733; el texto del
  consentimiento viene del diseño y conviene revisarlo antes de publicar.
- Para regenerar desde el diseño: `tools/compilar-dc.py`. Coloca el `.dc.html`
  junto al script y ejecútalo; falla ruidosamente si el DSL trae algo sin mapear.
