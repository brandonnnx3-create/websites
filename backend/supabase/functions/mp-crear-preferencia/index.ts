// Supabase Edge Function: crea una preferencia de pago de Mercado Pago
// (Checkout Pro) y devuelve el link al que hay que mandar al cliente.
//
// Por qué existe: crear una preferencia requiere el Access Token PRIVADO de
// la cuenta de Mercado Pago del dueño. Ese token nunca puede vivir en el
// navegador (cualquiera lo vería con F12) — por eso esto corre acá, server-side.
//
// ⚠ No pude probar esto contra la API real de Mercado Pago en el entorno
// donde lo escribí (sin salida a internet) — antes de usarlo en producción,
// probalo primero con credenciales de TEST y confirmá el formato exacto
// contra la documentación oficial vigente: https://www.mercadopago.com.ar/developers

import { corsHeaders } from "../_shared/cors.ts";

const ACCESS_TOKEN = Deno.env.get("MP_ACCESS_TOKEN"); // se configura como secret en Supabase, nunca acá
const SITIO_URL = Deno.env.get("SITIO_URL") || "https://tnbaires.ar";
const FUNCIONES_URL = Deno.env.get("SUPABASE_URL") + "/functions/v1";

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response(null, { headers: corsHeaders });

  if (!ACCESS_TOKEN) {
    return new Response(
      JSON.stringify({ error: "Falta configurar el secret MP_ACCESS_TOKEN en Supabase." }),
      { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  }

  try {
    const { items, externalReference } = await req.json();
    // items: [{ nombre, cw, talle, precio, cantidad }], armado desde bolsaItems del sitio

    if (!Array.isArray(items) || items.length === 0) {
      return new Response(JSON.stringify({ error: "Faltan items." }), {
        status: 400,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const preferencia = {
      items: items.map((it: any) => ({
        title: `${it.nombre} ${it.cw} — Talle ${it.talle}`,
        quantity: it.cantidad || 1,
        unit_price: Number(it.precio),
        currency_id: "ARS",
      })),
      external_reference: externalReference || `tn-baires-${Date.now()}`,
      back_urls: {
        success: `${SITIO_URL}/index.html#pago-exitoso`,
        pending: `${SITIO_URL}/index.html#pago-pendiente`,
        failure: `${SITIO_URL}/index.html#pago-fallido`,
      },
      auto_return: "approved",
      notification_url: `${FUNCIONES_URL}/mp-webhook`,
    };

    const resp = await fetch("https://api.mercadopago.com/checkout/preferences", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${ACCESS_TOKEN}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(preferencia),
    });

    if (!resp.ok) {
      const detalle = await resp.text();
      return new Response(JSON.stringify({ error: "Mercado Pago rechazó la preferencia.", detalle }), {
        status: 502,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const data = await resp.json();
    return new Response(
      JSON.stringify({
        init_point: data.init_point,
        sandbox_init_point: data.sandbox_init_point,
        preference_id: data.id,
      }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  } catch (err) {
    return new Response(JSON.stringify({ error: String(err) }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
