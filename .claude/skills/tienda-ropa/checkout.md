# Checkout — flujo completo

Todo esto ya está implementado en `template.html`. Este documento explica
cómo funciona para no tener que reconstruirlo ni volver a explicarlo.

El carrito se llama **"bolsa"** en el código. Es un panel lateral (drawer),
no una página aparte. Tiene **tres pasos** que maneja `mostrarPasoBolsa(paso)`:

```
resumen  →  entrega  →  pago
```

Con botones para volver (`bolsaVolverResumen`, `bolsaVolverEntrega`). El
estado del carrito se persiste en `localStorage` bajo `BOLSA_KEY`, así que no
se pierde si el cliente cierra la pestaña.

---

## Paso 1 — Resumen

`renderBolsa()` dibuja los ítems. Cada ítem del carrito es:

```js
{ nombre, cw /* colorway/variante */, talle, precio, img, cantidad }
```

Se agrega con `agregarABolsa(item)`. Detalle de UX deliberado: **agregar un
producto NO abre el panel automáticamente**. Si alguien está sumando varios
pares seguidos, forzarlo a cerrar el drawer cada vez es molesto. Alcanza con
el flash del botón ("En la bolsa", 1400 ms) y el contador que se actualiza.

El talle se toma del selector activo de la tarjeta (`.talla[aria-pressed]` en
la pieza destacada, `.talle-mini.activo` en la grilla).

## Paso 2 — Entrega

Tres opciones (`envioSeleccionado = {tipo, costo, km}`):

| tipo | costo | notas |
|---|---|---|
| `retiro` | `0` | retira en el local |
| `correo` | `ENVIOS.costoCorreo` (default `4500`) | pide nombre, DNI, dirección, CP, provincia — `datosCorreo()` / `correoCompleto()` valida que no falte nada |
| `moto` | calculado por km | ver abajo |

### Cálculo del envío en moto

1. El cliente escribe la dirección. `buscarDirecciones(texto)` la geocodifica
   con **Nominatim (OpenStreetMap)** — gratis, sin API key. Uso respetuoso:
   una consulta por vez, con debounce, según la política de Nominatim.
2. `distanciaRutaKm()` pide la distancia de ruta real.
3. Si esa consulta falla, cae al respaldo: `distanciaKm()` (Haversine, línea
   recta) multiplicado por `ENVIOS.factorRuta` (default `1.35`).
4. `costoMoto(km)` aplica `ENVIOS.tarifaKm` (default `$500/km`).

El punto de origen (`ENVIOS.lat` / `ENVIOS.lng`) lo carga el dueño desde el
panel. **Arranca en `null`**: hasta que lo cargue, el envío en moto no
calcula.

El paso no deja avanzar si eligió correo y `correoCompleto()` es falso.

## Paso 3 — Pago

Cinco métodos (`metodoPagoSeleccionado`, arranca en `efectivo`):

`efectivo` · `transferencia` · `mercadopago` · `rapipago` · `pagofacil`

**Recargo:** `recargoAplicable()` devuelve true sólo para `transferencia` y
`mercadopago`. `totalConRecargo(subtotal, envio)` aplica
`PAGOS.recargoPorcentaje` (default `10%`) sobre subtotal + envío.

### Confirmación por WhatsApp (el camino por defecto)

Todos los métodos menos Mercado Pago terminan armando un mensaje de WhatsApp
con el detalle del pedido y abriendo:

```js
window.open('https://wa.me/' + WHATSAPP_NUM + '?text=' + encodeURIComponent(msg), '_blank');
```

El dueño confirma el pago a mano. **Esto funciona perfecto y no requiere
backend ni cuenta de nada.** Es el default correcto para un local chico.

### Mercado Pago automático (opcional)

Se activa cargando `PAGOS.mpFuncionUrl` desde el panel. El sitio hace:

```js
fetch(pg.mpFuncionUrl, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({ items, externalReference: 'tn-' + Date.now() })
})
// → espera { init_point } y hace window.location.href = init_point
```

Los `items` incluyen los productos **más** una línea por el envío y otra por
el recargo, para que el total de MP coincida exactamente con el del sitio.

Manejo de error: el botón se deshabilita mientras carga, y si falla vuelve a
habilitarse mostrando el mensaje y sugiriendo otro método. No deja al cliente
colgado.

El backend está escrito (`backend/supabase/functions/mp-crear-preferencia` y
`mp-webhook`) pero **nunca se probó contra la API real de Mercado Pago**.
Antes de usarlo con plata real hay que probarlo con el Access Token de *test*.
Ver `backend/README.md`.

---

## Por qué el token de MP no puede vivir en el sitio

Confirmar un pago automáticamente requiere consultar la API de Mercado Pago
con el **Access Token privado** del local. Ese token en el navegador lo ve
cualquiera con F12. Por eso hace falta la Edge Function. Si alguien pide
"conectá Mercado Pago sin backend", la respuesta es que no se puede hacer de
forma segura: lo máximo sin servidor es un link de pago estático, que no
confirma nada automáticamente.
