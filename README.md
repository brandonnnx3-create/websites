# websites

Sitios web estáticos, uno por cliente/marca.

## Sitios

### `@tn_baires` — streetwear / sneakers, Buenos Aires

Tienda online estática: catálogo con filtros por modelo, ficha de producto con
galería, carrito, checkout con cálculo de envío y Mercado Pago, y panel de
administración.

- **Publicado en:** https://brandonnnx3-create.github.io/websites/
- **Panel de admin:** https://brandonnnx3-create.github.io/websites/admin.html
- **Salida compilada:** `dist/tn-baires-sitio/`

## Cómo compilar

```bash
pip install -r requirements.txt
python3 build.py
```

`build.py` procesa las fotos de `src2/ src3/ src4/`, reemplaza los tokens
`__IMG_*__` de `template.html` y `__PRODUCTOS_JSON__` de
`admin_template.html`, y escribe todo en `dist/tn-baires-sitio/`.

Opcional: si `jpegtran` está instalado, las fotos de producto se optimizan sin
pérdida (mismos píxeles, ~3% menos peso, carga progresiva). Si no está, se
copian tal cual.

## Cómo se publica

`.github/workflows/pages.yml` sube `dist/tn-baires-sitio/` a GitHub Pages en
cada push a `main`. **`dist/` está versionado**: si cambiás `template.html` hay
que correr `build.py` y commitear el resultado, porque el workflow no compila.

## Estructura

```
template.html          sitio completo (HTML + CSS + JS en un archivo)
admin_template.html    panel de administración
build.py               pipeline de imágenes + reemplazo de tokens
src2/ src3/ src4/      fotos fuente (logo y hero / producto / slider)
dist/tn-baires-sitio/  salida publicada
backend/supabase/      Edge Functions de Mercado Pago (opcional, sin desplegar)
.claude/skills/        playbook para armar tiendas nuevas
```

## Para armar una tienda nueva

Está todo documentado en `.claude/skills/tienda-ropa/`: la arquitectura y sus
motivos (`SKILL.md`), el flujo de checkout completo (`checkout.md`) y el
modelo de datos con el panel de admin (`datos.md`). Claude Code carga ese
playbook solo cuando se le pide una tienda de ropa en este repo.

## Estado

- El sitio y el panel funcionan y están publicados.
- El backend de Mercado Pago está escrito pero **no desplegado ni probado
  contra la API real**. Mientras tanto el checkout confirma por WhatsApp, que
  sí funciona. Ver `backend/README.md`.
- El panel de admin guarda en `localStorage`, o sea **por navegador**: los
  cambios no se publican solos, hay que recompilar.
