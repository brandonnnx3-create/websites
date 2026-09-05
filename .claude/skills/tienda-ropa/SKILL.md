---
name: tienda-ropa
description: Playbook para construir sitios de tienda de ropa/calzado en este repo (catálogo, ficha de producto, carrito, checkout con envío y Mercado Pago, panel de administración). Usalo cuando el pedido sea armar, clonar o modificar una tienda online de indumentaria, sneakers o accesorios — incluido "hacé una tienda como la de tn-baires", "agregá checkout", "agregá panel de admin" o cambios sobre sites/tn-baires. La implementación de referencia completa y funcionando es tn-baires.
---

# Tienda de ropa / calzado — playbook

Este repo ya tiene **una tienda entera funcionando**: `@tn_baires`. No la
reinventes. Para una tienda nueva, se copia esa y se cambian los datos.

**No leas los 133 KB de `template.html` de una.** Ubicá la parte que
necesitás con `grep -n` sobre los nombres de función que están listados abajo
y leé sólo ese bloque.

## Implementación de referencia

| Archivo | Qué es |
|---|---|
| `template.html` | El sitio entero: HTML + CSS + JS en un archivo, sin dependencias ni framework. Contiene tokens `__IMG_*__` que `build.py` reemplaza. |
| `admin_template.html` | Panel de administración (`/admin.html`). Token `__PRODUCTOS_JSON__`. |
| `build.py` | Procesa las fotos, reemplaza los tokens y escribe `dist/tn-baires-sitio/`. |
| `src2/ src3/ src4/` | Fotos fuente (logo/hero, producto, slider). |
| `backend/supabase/` | Edge Functions de Mercado Pago (opcional, ver `backend/README.md`). |
| `.github/workflows/pages.yml` | Deploy automático a GitHub Pages. |

## Decisiones de arquitectura (y por qué)

Estas están tomadas y probadas. No las cambies sin un motivo concreto.

- **Un solo HTML, sin build de JS, sin framework.** El sitio es estático puro:
  se puede hostear gratis en GitHub Pages o Cloudflare Pages, carga rápido y
  no tiene nada que se rompa al actualizar dependencias.
- **El catálogo vive en `PRODUCTOS_DEFAULT`** (un array JSON embebido en el
  HTML) y el panel de admin lo pisa vía `localStorage`. Ver "Modelo de datos".
- **`localStorage`, no base de datos.** Consecuencia real y importante: los
  cambios que el dueño hace en el panel **viven sólo en el navegador donde los
  hizo**. No se propagan a los clientes. Para publicar cambios de verdad hay
  que exportar el JSON desde el panel y volver a compilar. Decíselo al cliente
  antes de que se lleve una sorpresa.
- **Las fotos NO se recomprimen.** `build.py` usa `COPIA` para las fotos de
  producto: `jpegtran -optimize -progressive` (sin pérdida) o copia directa.
  Sólo se recomprime lo que se achica (miniaturas del slider), con `quality=82`
  y `subsampling=0` (4:4:4) para que los colores saturados no se empasten.
- **`object-fit: contain` sobre fondo `--asfalto`, nunca `cover`.** Las fotos
  de calzado son verticales (~0.68 de relación). Con `cover` se corta la
  zapatilla. Este bug se arregló cuatro veces en distintos lugares del sitio
  (grilla, similares, carrito, slider, ficha): si agregás un contenedor de
  imagen nuevo, usá `contain` desde el principio.
- **Mobile primero, verificado con Playwright.** El breakpoint de la tabla del
  admin es 800 px; abajo de eso pasa a tarjetas. Inputs a 16 px para que iOS
  no haga zoom al enfocarlos. Área táctil mínima 40 px.

## Cómo arrancar una tienda nueva

1. `cp template.html admin_template.html build.py` a la carpeta de la tienda
   nueva y copiar las fotos a sus `src*/`.
2. Cambiar en `build.py`: `DIST`, y el mapa `CFG` (token → archivo fuente).
3. Cambiar en `template.html`:
   - `<title>`, meta description, nombre de marca en el header y el pie.
   - `WHATSAPP_NUM` (línea ~2278). Formato Argentina: `54` + `9` + área sin el
     `0` + número sin el `15`.
   - Las variables CSS de `:root` (paleta) y `html[data-tema="claro"]`.
   - `PRODUCTOS_DEFAULT`, `ENVIOS_DEFAULT`, `PAGOS_DEFAULT`.
   - Las claves de `localStorage`: `tn_baires_*` → `<marca>_*`. **Si no las
     cambiás, dos tiendas distintas se pisan los datos en el mismo navegador.**
   - Los rubros/categorías del mega menú (en tn-baires son modelos de
     zapatilla: `tn`, `am95`, `shox`, `jordan`, `mizuno`, `nocta`, `uptempo`).
     Para ropa serían `remeras`, `buzos`, `pantalones`, etc.
   - La guía de talles (en tn-baires es AR/US/CM de calzado; para ropa es
     S/M/L/XL con medidas de pecho y largo).
4. `pip install -r requirements.txt && python3 build.py`
5. Agregar el deploy en `.github/workflows/pages.yml`.

Cuando haya una segunda tienda conviene mover cada una a `sites/<marca>/` y
que el workflow arme un `dist/` con una carpeta por sitio. Hoy no está hecho
porque hay una sola.

## Qué preguntarle al cliente (antes de empezar)

Sin estos datos el sitio queda con placeholders:

1. Nombre, `@` de Instagram, logo, y número de WhatsApp real.
2. Fotos de producto verticales, lo más grandes posible (las de tn-baires son
   JPEG de 1100 px y ya es el techo — no se puede recuperar detalle que el
   archivo no tiene).
3. Catálogo: nombre, variante/color, precio, y stock **por talle**.
4. Envío: dirección del local (para el cálculo por km), `$/km`, costo de
   correo.
5. Pago: alias/CBU/titular de transferencia, alias de Mercado Pago, y el
   recargo % que le cobran a transferencia y MP.
6. Guía de talles real de lo que venden.

## Referencias

- `checkout.md` — el flujo de compra completo, paso por paso.
- `datos.md` — modelo de datos, claves de `localStorage` y panel de admin.
- `backend/README.md` — Mercado Pago real (Supabase Edge Functions).

## Advertencia legal (aplica a este rubro)

Estos sitios venden calzado/indumentaria de marcas de terceros (Nike, Jordan,
Mizuno). Vender producto original de reventa es legal; usar los logos de la
marca como si el sitio fuera oficial, no. Mantené el branding del sitio en la
marca del local, no en la del fabricante, y no pongas los isotipos de Nike ni
"Official" / "Oficial" en ningún lado.
