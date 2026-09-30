select raw_payload ->> 'id' as pesquisa_id, raw_payload ->> 'titulo' as titulo,
       raw_payload ->> 'status' as status, raw_payload ->> 'tipo' as tipo, raw_payload ->> 'area' as area,
       nullif(raw_payload ->> 'participantes', '')::integer as participantes,
       raw_payload ->> 'data_solicitacao' as data_solicitacao, raw_payload ->> 'data_entrega' as data_entrega,
       run_id, ingested_at, source_file
from {{ source('raw_staging', 'pesquisas_raw') }}
