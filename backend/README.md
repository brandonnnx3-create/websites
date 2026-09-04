# Backend de Mercado Pago (opcional)

Esto conecta el cobro real con Mercado Pago y confirma automáticamente
cuando un cliente pagó. El sitio funciona perfectamente sin esto (con
confirmación manual por WhatsApp) — esto es un upgrade, no un requisito.

## Por qué hace falta esto y no alcanza con el sitio solo

Confirmar un pago de forma automática requiere consultar la API de Mercado
Pago con el **Access Token privado** de la cuenta del local. Ese token no
puede vivir en el navegador (lo vería cualquiera con F12), así que tiene que
correr en un servidor. Estas dos funciones (`mp-crear-preferencia` y
`mp-webhook`) son ese servidor — ya están escritas, lo que falta es
desplegarlas con credenciales reales.

## Lo que necesito que hagan ustedes (una sola vez, ~15 minutos, gratis)

1. **Cuenta de Mercado Pago Developers**
   - Entrar a https://www.mercadopago.com.ar/developers con la cuenta de MP
     real del local (o crear una).
   - Crear una "Aplicación" en el panel de desarrolladores.
   - Copiar el **Access Token** (empezá con el de **prueba/test**, no el de
     producción, hasta confirmar que todo funciona).

2. **Cuenta de Supabase** (gratis, sin tarjeta)
   - Crear cuenta en https://supabase.com con GitHub.
   - Crear un proyecto nuevo (elegí cualquier nombre/región).
   - En el proyecto: **SQL Editor** → pegar y correr el contenido de
     `backend/supabase/schema.sql`.
   - En **Project Settings → API**: copiar `Project URL`, `anon public key`
     y `service_role key` (esta última es secreta, no la compartan en
     ningún lado público).

3. **Pasarme (a mí o a quien siga el proyecto) estos 4 datos**, idealmente
   pegados directo en la configuración de Supabase (Edge Functions →
   Secrets), no en un chat: `MP_ACCESS_TOKEN`, `SUPABASE_URL`,
   `SUPABASE_SERVICE_ROLE_KEY`, y la URL real del sitio (`SITIO_URL`).

## Lo que hago yo con eso

- Desplegar las dos funciones (`supabase functions deploy`).
- Conectar el botón "Pagar con Mercado Pago" del sitio para que llame a
  `mp-crear-preferencia` y redirija al cliente al checkout real de MP.
- Configurar el webhook en el panel de Mercado Pago apuntando a
  `mp-webhook`.
- Probar un pago de prueba de punta a punta antes de pasar a producción.

## Estructura

```
backend/
  supabase/
    schema.sql                          -- tabla pedidos_pagados
    functions/
      mp-crear-preferencia/index.ts     -- arma el checkout y devuelve el link
      mp-webhook/index.ts               -- confirma el pago real contra la API de MP
      _shared/cors.ts
```

## Aviso importante

Este código lo escribí sin acceso a internet real (no pude probarlo contra
la API de Mercado Pago en vivo). Antes de usarlo con plata real:
1. Probarlo con el Access Token de **test** de Mercado Pago.
2. Hacer un pago de prueba completo (con las tarjetas de prueba que da MP).
3. Confirmar que `pedidos_pagados` en Supabase se llena correctamente.
4. Recién ahí pasar a producción con el Access Token real.
