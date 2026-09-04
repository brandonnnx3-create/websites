from PIL import Image
import os, shutil, subprocess

# ---------------------------------------------------------------------------
# Calidad de imagen
#
# Las fuentes en src2/ y src3/ ya son JPEG comprimidos para web (1100-1300 px).
# Eso es el techo real de calidad: no hay forma de recuperar detalle que el
# archivo no tiene. Lo mejor posible con estas fuentes es NO volver a
# comprimirlas.
#
# Por eso hay dos modos:
#   ancho = 0  -> copia sin recomprimir. Los pixeles quedan identicos al
#                 original (verificado con ImageChops: diferencia nula).
#                 Si esta jpegtran se usa "-optimize -progressive", que es
#                 recompresion SIN PERDIDA: mismos pixeles, ~3% menos peso y
#                 carga progresiva. Si no esta, se copia el archivo tal cual.
#   ancho > 0  -> se achica (solo para las miniaturas del slider, que se ven
#                 a 190 px en pantalla). Ahi la recompresion es inevitable,
#                 pero se hace con calidad alta y sin submuestreo de croma
#                 (subsampling=0 / 4:4:4) para que los colores saturados
#                 —el violeta de la TN, el amarillo neon de la 95— no se
#                 empasten en los bordes.
# ---------------------------------------------------------------------------

COPIA = 0  # marca de "no recomprimir"

def _hay_jpegtran():
    try:
        subprocess.run(["jpegtran", "-version"], capture_output=True, check=False)
        return True
    except (OSError, FileNotFoundError):
        return False

HAY_JPEGTRAN = _hay_jpegtran()

def procesar(path, w, q, outpath):
    """Devuelve (ancho, alto) de la imagen escrita en outpath."""
    if w == COPIA:
        hecho = False
        if HAY_JPEGTRAN:
            r = subprocess.run(
                ["jpegtran", "-copy", "none", "-optimize", "-progressive", path],
                capture_output=True)
            if r.returncode == 0 and r.stdout:
                with open(outpath, "wb") as f:
                    f.write(r.stdout)
                hecho = True
        if not hecho:
            shutil.copyfile(path, outpath)
        with Image.open(outpath) as im:
            return im.size
    im = Image.open(path).convert("RGB")
    if im.width > w:
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    im.save(outpath, "JPEG", quality=q, optimize=True,
            progressive=True, subsampling=0)
    return im.size

CFG = {
 "__IMG_LOGO__":           ("src2/logo_square.jpg",         160, 88, "logo.jpg"),
 "__IMG_SLIDE1__":         ("src2/slide1_wide.jpg", COPIA, 0, "hero-1.jpg"),
 "__IMG_SLIDE2__":         ("src2/slide2_wide.jpg", COPIA, 0, "hero-2.jpg"),
 "__IMG_SLIDE3__":         ("src2/slide3_wide.jpg", COPIA, 0, "hero-3.jpg"),
 "__IMG_TN_BLACK__":       ("src3/tn_black.jpg", COPIA, 0, "tn-triple-black.jpg"),
 "__IMG_TN_BLACKWHITE__":  ("src3/tn_black_white.jpg", COPIA, 0, "tn-black-white.jpg"),
 "__IMG_TN_VIOLET__":      ("src3/tn_violet.jpg", COPIA, 0, "tn-violet-fade.jpg"),
 "__IMG_TN_WHITE__":       ("src3/tn_white.jpg", COPIA, 0, "tn-triple-white.jpg"),
 "__IMG_TN_WHITEGREEN__":  ("src3/tn_white_green.jpg", COPIA, 0, "tn-white-green.jpg"),
 "__IMG_AM95_OG__":        ("src3/am95_og.jpg", COPIA, 0, "am95-og-blue-red.jpg"),
 "__IMG_AM95_NEON__":      ("src3/am95_neon.jpg", COPIA, 0, "am95-neon-yellow.jpg"),
 "__IMG_AM95_WHITE__":     ("src3/am95_white.jpg", COPIA, 0, "am95-triple-white.jpg"),
 "__IMG_AM95_BLACKGREY__": ("src3/am95_black_grey.jpg", COPIA, 0, "am95-black-grey.jpg"),
 "__IMG_AM95_NAVYJEWEL__": ("src3/am95_navy_jewel.jpg", COPIA, 0, "am95-navy-jewel.jpg"),
 "__IMG_SHOX_OLIVE__":     ("src3/shox_olive.jpg", COPIA, 0, "shox-olive-green.jpg"),
 "__IMG_SHOX_CREAM__":     ("src3/shox_cream.jpg", COPIA, 0, "shox-cream-red.jpg"),
 "__IMG_SHOX_BLACK__":     ("src3/shox_black.jpg", COPIA, 0, "shox-full-black.jpg"),
 "__IMG_JORDAN__":         ("src3/jordan_cement.jpg", COPIA, 0, "jordan3-white-cement.jpg"),
 "__IMG_JORDAN_BLACKCAT__":("src3/jordan_black_cat.jpg", COPIA, 0, "jordan3-black-cat.jpg"),
 "__IMG_MIZUNO__":         ("src3/mizuno_white.jpg", COPIA, 0, "mizuno-triple-white.jpg"),
 "__IMG_MIZUNO_TEAL__":    ("src3/mizuno_black_teal.jpg", COPIA, 0, "mizuno-black-teal.jpg"),
 "__IMG_NOCTA__":          ("src3/nocta_black.jpg", COPIA, 0, "nocta-triple-black.jpg"),
 "__IMG_NOCTA_WHITE__":    ("src3/nocta_white.jpg", COPIA, 0, "nocta-triple-white.jpg"),
 "__IMG_UPTEMPO__":        ("src3/uptempo_black.jpg", COPIA, 0, "uptempo-black-white.jpg"),
 "__IMG_TN_FUEGO__":       ("src3/tn_fuego.jpg", COPIA, 0, "tn-fuego.jpg"),
 # Slider "todos los modelos": salen de las fotos de producto completas (src3),
 # no de los recortes cuadrados de src4 — esos venian cortados desde el archivo
 # y no habia CSS que pudiera mostrar la zapatilla entera.
 "__IMG_SL_1__":  ("src3/tn_black.jpg", 420, 82, "sl-tn-1.jpg"),
 "__IMG_SL_2__":  ("src3/tn_violet.jpg", 420, 82, "sl-tn-2.jpg"),
 "__IMG_SL_3__":  ("src3/tn_fuego.jpg", 420, 82, "sl-tn-3.jpg"),
 "__IMG_SL_4__":  ("src3/tn_white_green.jpg", 420, 82, "sl-tn-4.jpg"),
 "__IMG_SL_5__":  ("src3/am95_og.jpg", 420, 82, "sl-am95-1.jpg"),
 "__IMG_SL_6__":  ("src3/am95_neon.jpg", 420, 82, "sl-am95-2.jpg"),
 "__IMG_SL_7__":  ("src3/am95_navy_jewel.jpg", 420, 82, "sl-am95-3.jpg"),
 "__IMG_SL_8__":  ("src3/shox_olive.jpg", 420, 82, "sl-shox-1.jpg"),
 "__IMG_SL_9__":  ("src3/shox_cream.jpg", 420, 82, "sl-shox-2.jpg"),
 "__IMG_SL_10__": ("src3/jordan_cement.jpg", 420, 82, "sl-jordan-1.jpg"),
 "__IMG_SL_11__": ("src3/jordan_black_cat.jpg", 420, 82, "sl-jordan-2.jpg"),
 "__IMG_SL_12__": ("src3/mizuno_black_teal.jpg", 420, 82, "sl-mizuno-1.jpg"),
 "__IMG_SL_13__": ("src3/nocta_black.jpg", 420, 82, "sl-nocta-1.jpg"),
 "__IMG_SL_14__": ("src3/uptempo_black.jpg", 420, 82, "sl-uptempo-1.jpg"),
}

DIST = "dist/tn-baires-sitio"
ASSETS = f"{DIST}/assets"
os.makedirs(ASSETS, exist_ok=True)

html = open("template.html", encoding="utf-8").read()
total = 0
for token,(path,w,q,outname) in CFG.items():
    outpath = f"{ASSETS}/{outname}"
    dims = procesar(path, w, q, outpath)
    size = os.path.getsize(outpath)
    total += size
    modo = "sin recomprimir" if w == COPIA else f"escalada q{q}"
    print(f"{outname:28} {dims} -> {size/1024:7.1f} KB  [{modo}]")
    html = html.replace(token, f"assets/{outname}")

with open(f"{DIST}/index.html", "w", encoding="utf-8") as f:
    f.write(html)

# robots.txt + sitemap.xml (dominio de ejemplo, actualizar cuando tengan el real)
open(f"{DIST}/robots.txt","w").write("User-agent: *\nAllow: /\nSitemap: https://tnbaires.ar/sitemap.xml\n")
open(f"{DIST}/sitemap.xml","w").write(
"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://tnbaires.ar/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>
</urlset>
""")

html_size = os.path.getsize(f"{DIST}/index.html")
print(f"\nimagenes: {total/1024:.0f} KB (en {len(CFG)} archivos separados)")
print(f"index.html: {html_size/1024:.0f} KB (sin imagenes embebidas)")

# ---------- panel admin.html ----------
import re
m = re.search(r'var PRODUCTOS_DEFAULT = (\[.*?\]);', html, re.S)
productos_json = m.group(1) if m else "[]"
admin_html = open("admin_template.html", encoding="utf-8").read()
admin_html = admin_html.replace("__PRODUCTOS_JSON__", productos_json)
admin_html = admin_html.replace("__IMG_LOGO__", "assets/logo.jpg")
with open(f"{DIST}/admin.html", "w", encoding="utf-8") as f:
    f.write(admin_html)
print(f"admin.html: {os.path.getsize(f'{DIST}/admin.html')/1024:.0f} KB")

# zip para entrega (solo si existe la carpeta de salida del sandbox de Claude.ai)
if os.path.isdir("/mnt/user-data/outputs"):
    shutil.make_archive("/mnt/user-data/outputs/tn-baires-sitio", "zip", "dist", "tn-baires-sitio")
    print("\nzip listo: /mnt/user-data/outputs/tn-baires-sitio.zip")
