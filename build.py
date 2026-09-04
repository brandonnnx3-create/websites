from PIL import Image
import os, shutil

CFG = {
 "__IMG_LOGO__":           ("src2/logo_square.jpg",         160, 88, "logo.jpg"),
 "__IMG_SLIDE1__":         ("src2/slide1_wide.jpg",       1300, 78, "hero-1.jpg"),
 "__IMG_SLIDE2__":         ("src2/slide2_wide.jpg",       1300, 78, "hero-2.jpg"),
 "__IMG_SLIDE3__":         ("src2/slide3_wide.jpg",       1300, 78, "hero-3.jpg"),
 "__IMG_TN_BLACK__":       ("src3/tn_black.jpg",          1100, 78, "tn-triple-black.jpg"),
 "__IMG_TN_BLACKWHITE__":  ("src3/tn_black_white.jpg",     950, 78, "tn-black-white.jpg"),
 "__IMG_TN_VIOLET__":      ("src3/tn_violet.jpg",          950, 78, "tn-violet-fade.jpg"),
 "__IMG_TN_WHITE__":       ("src3/tn_white.jpg",            950, 78, "tn-triple-white.jpg"),
 "__IMG_TN_WHITEGREEN__":  ("src3/tn_white_green.jpg",      950, 78, "tn-white-green.jpg"),
 "__IMG_AM95_OG__":        ("src3/am95_og.jpg",           1100, 78, "am95-og-blue-red.jpg"),
 "__IMG_AM95_NEON__":      ("src3/am95_neon.jpg",           950, 78, "am95-neon-yellow.jpg"),
 "__IMG_AM95_WHITE__":     ("src3/am95_white.jpg",          950, 78, "am95-triple-white.jpg"),
 "__IMG_AM95_BLACKGREY__": ("src3/am95_black_grey.jpg",     950, 78, "am95-black-grey.jpg"),
 "__IMG_AM95_NAVYJEWEL__": ("src3/am95_navy_jewel.jpg",     950, 78, "am95-navy-jewel.jpg"),
 "__IMG_SHOX_OLIVE__":     ("src3/shox_olive.jpg",          950, 78, "shox-olive-green.jpg"),
 "__IMG_SHOX_CREAM__":     ("src3/shox_cream.jpg",          950, 78, "shox-cream-red.jpg"),
 "__IMG_SHOX_BLACK__":     ("src3/shox_black.jpg",          950, 78, "shox-full-black.jpg"),
 "__IMG_JORDAN__":         ("src3/jordan_cement.jpg",       950, 78, "jordan3-white-cement.jpg"),
 "__IMG_JORDAN_BLACKCAT__":("src3/jordan_black_cat.jpg",    950, 78, "jordan3-black-cat.jpg"),
 "__IMG_MIZUNO__":         ("src3/mizuno_white.jpg",        950, 78, "mizuno-triple-white.jpg"),
 "__IMG_MIZUNO_TEAL__":    ("src3/mizuno_black_teal.jpg",   950, 78, "mizuno-black-teal.jpg"),
 "__IMG_NOCTA__":          ("src3/nocta_black.jpg",         950, 78, "nocta-triple-black.jpg"),
 "__IMG_NOCTA_WHITE__":    ("src3/nocta_white.jpg",         950, 78, "nocta-triple-white.jpg"),
 "__IMG_UPTEMPO__":        ("src3/uptempo_black.jpg",       950, 78, "uptempo-black-white.jpg"),
 "__IMG_TN_FUEGO__":       ("src3/tn_fuego.jpg",          1100, 78, "tn-fuego.jpg"),
 "__IMG_SL_1__":  ("src4/slider_tn1.jpg",       340, 66, "sl-tn-1.jpg"),
 "__IMG_SL_2__":  ("src4/slider_tn2.jpg",       340, 66, "sl-tn-2.jpg"),
 "__IMG_SL_3__":  ("src4/slider_tn3.jpg",       340, 66, "sl-tn-3.jpg"),
 "__IMG_SL_4__":  ("src4/slider_tn4.jpg",       340, 66, "sl-tn-4.jpg"),
 "__IMG_SL_5__":  ("src4/slider_95_1.jpg",      340, 66, "sl-am95-1.jpg"),
 "__IMG_SL_6__":  ("src4/slider_95_2.jpg",      340, 66, "sl-am95-2.jpg"),
 "__IMG_SL_7__":  ("src4/slider_95_3.jpg",      340, 66, "sl-am95-3.jpg"),
 "__IMG_SL_8__":  ("src4/slider_shox1.jpg",     340, 66, "sl-shox-1.jpg"),
 "__IMG_SL_9__":  ("src4/slider_shox2.jpg",     340, 66, "sl-shox-2.jpg"),
 "__IMG_SL_10__": ("src4/slider_jordan1.jpg",   340, 66, "sl-jordan-1.jpg"),
 "__IMG_SL_11__": ("src4/slider_jordan2.jpg",   340, 66, "sl-jordan-2.jpg"),
 "__IMG_SL_12__": ("src4/slider_mizuno1.jpg",   340, 66, "sl-mizuno-1.jpg"),
 "__IMG_SL_13__": ("src4/slider_nocta1.jpg",    340, 66, "sl-nocta-1.jpg"),
 "__IMG_SL_14__": ("src4/slider_uptempo1.jpg",  340, 66, "sl-uptempo-1.jpg"),
}

DIST = "dist/tn-baires-sitio"
ASSETS = f"{DIST}/assets"
os.makedirs(ASSETS, exist_ok=True)

html = open("template.html", encoding="utf-8").read()
total = 0
for token,(path,w,q,outname) in CFG.items():
    im = Image.open(path).convert("RGB")
    if im.width > w:
        im = im.resize((w, round(im.height*w/im.width)), Image.LANCZOS)
    outpath = f"{ASSETS}/{outname}"
    im.save(outpath, "JPEG", quality=q, optimize=True, progressive=True)
    size = os.path.getsize(outpath)
    total += size
    print(f"{outname:28} {im.size} -> {size/1024:7.1f} KB")
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
