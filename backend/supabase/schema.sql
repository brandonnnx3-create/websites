-- Tabla donde el webhook de Mercado Pago registra los pagos confirmados.
-- El panel admin (o el propio dueño desde el editor de tablas de Supabase)
-- la consulta para ver qué pedidos ya están pagados de verdad.

create table if not exists pedidos_pagados (
  id bigint generated always as identity primary key,
  external_reference text not null,      -- el mismo id de pedido que mandamos al crear la preferencia
  mp_payment_id text not null unique,     -- id del pago en Mercado Pago (evita duplicados)
  status text not null,                   -- approved, rejected, pending, etc.
  monto numeric not null,
  detalle jsonb,                          -- respuesta completa de la API de pagos, por si hace falta despues
  creado_en timestamptz not null default now()
);

-- RLS activado y SIN políticas: nadie puede leer ni escribir esta tabla
-- usando la clave pública (anon key) del sitio. Solo el backend (que usa
-- la service role key, nunca expuesta al navegador) puede escribir, y el
-- dueño puede ver los pagos entrando a Supabase Studio con su propia
-- cuenta (Table Editor > pedidos_pagados) — eso no pasa por RLS.
alter table pedidos_pagados enable row level security;
