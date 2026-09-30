select raw_payload ->> 'id_cliente' as cliente_id, raw_payload ->> 'id_empresa' as empresa_id,
       raw_payload ->> 'cargo' as cargo, raw_payload ->> 'departamento' as departamento,
       raw_payload ->> 'e-mail' as email, run_id, ingested_at, source_file
from {{ source('raw_staging', 'clientes_raw') }}
