// Supabase Edge Function: recibe la notificación de pago de Mercado Pago.
//
// Importante (seguridad): NUNCA confiamos en el status que viene en el body
// de la notificación — cualquiera podría mandarnos un POST fabricado diciendo
// "aprobado". Lo que hacemos es tomar solo el ID de pago que llega y volver a
// consultarlo contra la API oficial de Mercado Pago con el Access Token
// privado; el estado real es el que devuelve esa consulta, no el webhook.
//
// ⚠ No pude probar esto contra Mercado Pago real (sin salida a internet en
// el entorno donde lo escribí) — probalo primero con un pago de TEST antes
// de usarlo en producción, y confirmá el formato exacto del payload contra
// la documentación oficial vigente (puede variar entre integraciones IPN
// clásicas y "webhooks" nuevos): https://www.mercadopago.com.ar/developers

import { createClient } from "jsr:@supabase/supabase-js@2";
import { corsHeaders } from "../_shared/cors.ts";

const ACCESS_TOKEN = Deno.env.get("MP_ACCESS_TOKEN");
const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!; // secret, nunca la anon key

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response(null, { headers: corsHeaders });

  try {
    const body = await req.json().catch(() => ({}));
    const url = new URL(req.url);

    // el id de pago puede venir por query string (?data.id=...&type=payment)
    // o en el body (integraciones nuevas: {type:"payment", data:{id:"..."}})
    const paymentId =
      body?.data?.id || url.searchParams.get("data.id") || url.searchParams.get("id");
    const tipo = body?.type || url.searchParams.get("type") || url.searchParams.get("topic");

    if (tipo !== "payment" || !paymentId) {
      // otros tipos de notificación (merchant_order, etc.) los ignoramos
      return new Response("ok", { status: 200, headers: corsHeaders });
    }

    // consultamos el pago real contra la API de Mercado Pago
    const pagoResp = await fetch(`https://api.mercadopago.com/v1/payments/${paymentId}`, {
      headers: { Authorization: `Bearer ${ACCESS_TOKEN}` },
    });
    if (!pagoResp.ok) {
      return new Response("no se pudo verificar el pago", { status: 502, headers: corsHeaders });
    }
    const pago = await pagoResp.json();

    const supabase = createClient(SUPABASE_URL, SERVICE_ROLE_KEY);
    const { error } = await supabase.from("pedidos_pagados").upsert(
      {
        external_reference: pago.external_reference,
        mp_payment_id: String(pago.id),
        status: pago.status, // approved | rejected | pending | in_process | ...
        monto: pago.transaction_amount,
        detalle: pago,
      },
      { onConflict: "mp_payment_id" }
    );
    if (error) {
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // Notificación al dueño: lo más simple y confiable sin más infraestructura
    // es que el dueño mire la tabla pedidos_pagados en Supabase Studio, o
    // (opcional) agregar acá un fetch a un webhook de WhatsApp/Telegram si en
    // el futuro quieren aviso instantáneo — no lo agrego ahora para no sumar
    // otra cuenta/credencial que todavía no tienen.

    return new Response("ok", { status: 200, headers: corsHeaders });
  } catch (err) {
    return new Response(String(err), { status: 500, headers: corsHeaders });
  }
});
