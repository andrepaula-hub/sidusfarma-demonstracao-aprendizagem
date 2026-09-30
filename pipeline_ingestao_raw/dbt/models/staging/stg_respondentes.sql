select raw_payload ->> 'id_pesq' as pesquisa_id, raw_payload ->> 'id_empresa' as empresa_id,
       raw_payload ->> 'id_cliente' as cliente_id, raw_payload ->> 'hora_inicio' as hora_inicio,
       raw_payload ->> 'hora_termino' as hora_termino, run_id, ingested_at, source_file
from {{ source('raw_staging', 'respondentes_raw') }}
