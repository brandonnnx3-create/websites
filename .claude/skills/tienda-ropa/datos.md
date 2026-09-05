# Modelo de datos y panel de administración

## Producto

`PRODUCTOS_DEFAULT` es un array embebido en `template.html` (~línea 1445).
Cada producto:

```js
{
  "id": "tn-1",                    // único, estable: se usa en la URL (#producto/tn-1)
  "modelo": "tn",                  // rubro/categoría → filtros y mega menú
  "nombre": "Nike Air Max Plus",
  "colorway": "Triple Black",      // variante; en ropa sería el color
  "precio": 365000,                // entero, en pesos, sin decimales
  "img": "assets/tn-triple-black.jpg",   // foto principal
  "fotos": ["assets/..."],         // galería de la ficha
  "talles": [ {"talle": 40, "stock": 4}, {"talle": 41, "stock": 3} ],
  "activo": true,                  // false = no se muestra en el sitio
  "destacado": true,               // "pieza de la semana"
  "layout": "a",                   // a | b | c — tamaño del tile en la grilla
  "descripcion": "...",
  "enOferta": false,
  "precioOferta": 0
}
```

**Precios:** `precioMostrar(prod, promo)` decide qué mostrar. Regla: la oferta
propia del producto **gana** por sobre la promo general del sitio; los
descuentos **no se acumulan**. Eso es deliberado.

**Stock:** `totalStock()` y `estadoStock()` derivan del array `talles`. Un
talle con `stock: 0` aparece deshabilitado en el selector. Con todo en 0, el
producto muestra "Avisame" y manda un WhatsApp pidiendo el aviso de reposición.

## Claves de `localStorage`

```
tn_baires_productos   catálogo (pisa PRODUCTOS_DEFAULT)
tn_baires_promos      promociones con rango de fechas {desde, hasta, descuento}
tn_baires_envios      {lat, lng, tarifaKm, factorRuta, costoCorreo}
tn_baires_pagos       {recargoPorcentaje, transferenciaAlias/Cbu/Titular,
                       mpAlias, mpUsuario, mpFuncionUrl, rapipagoTexto, pagofacilTexto}
tn_baires_pedidos     pedidos (sólo el panel)
tn_baires_tema        'claro' | oscuro (sólo el sitio)
```

Todas se leen con el patrón `Object.assign({}, X_DEFAULT, JSON.parse(raw))`
dentro de un `try/catch`: si el JSON está corrupto o `localStorage` no está
disponible, cae al default en vez de romper la página.

**Al clonar la tienda hay que renombrar el prefijo `tn_baires_`.** Dos tiendas
con el mismo prefijo se pisan los datos en el mismo navegador.

`promoActiva()` compara contra `new Date().toISOString().slice(0,10)`, o sea
UTC. En Argentina (UTC-3) una promo puede activarse/desactivarse hasta 3 horas
antes de lo esperado. No es un bug crítico para promos de varios días, pero
tenelo en cuenta si alguien pide una promo de un solo día.

## Panel de administración (`admin.html`)

Pestañas: **Dashboard · Productos · Pedidos · Envíos · Pagos**.

- Productos: alta/baja/edición, precio, stock por talle, toggles de
  destacado/activo, galería de fotos.
- Pedidos: kanban por estado.
- Envíos: ubicación del local, `$/km`, costo de correo.
- Pagos: alias/CBU, recargo %, URL de la función de Mercado Pago.

`build.py` inyecta el catálogo en `admin_template.html` reemplazando el token
`__PRODUCTOS_JSON__` con el mismo JSON que quedó en el sitio.

### Mobile (< 800 px)

Esto costó una iteración entera, no lo rompas:

- La tabla de productos pasa a **tarjetas**. Cada `<td>` lleva `data-col` y el
  CSS lo usa como etiqueta.
- Cuidado con la especificidad: `.campo input[type=number]{width:100%}` le
  gana a `.talle-campo input{width:44px}` y hace que cada talle ocupe un
  renglón entero.
- El modal es una hoja anclada abajo con el pie fijo, para que Guardar y
  Cancelar queden siempre visibles.
- Inputs a **16 px** (abajo de eso iOS hace zoom al enfocar). Área táctil
  mínima 40 px.
- El `<input type=file>` nativo muestra un botón blanco en inglés
  ("Choose File"): va envuelto en un `<label>` con el estilo del panel.

## La limitación importante

`localStorage` es **por navegador**. Lo que el dueño cambia en el panel desde
su teléfono no lo ve ningún cliente, ni él mismo desde la computadora. El
panel sirve para preparar el catálogo y exportarlo; para publicar de verdad
hay que volver a compilar el sitio con el JSON nuevo.

Si el cliente necesita que los cambios se publiquen solos, eso ya requiere
backend (Supabase sirve: la infraestructura de Mercado Pago ya está armada
ahí) y es un proyecto aparte, no un ajuste.
