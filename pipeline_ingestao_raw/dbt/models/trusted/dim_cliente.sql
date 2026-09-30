{{ config(unique_key='cliente_id') }}

select cliente_id, empresa_id, cargo, departamento, email, run_id, ingested_at
from {{ ref('stg_clientes') }}
where cliente_id is not null
