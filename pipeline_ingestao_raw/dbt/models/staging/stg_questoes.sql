select raw_payload ->> 'id_pergunta' as pergunta_id, raw_payload ->> 'pesquisa_id' as pesquisa_id,
       raw_payload ->> 'enunciado' as enunciado, raw_payload ->> 'tipo' as tipo,
       raw_payload ->> 'alternativas' as alternativas, run_id, ingested_at, source_file
from {{ source('raw_staging', 'questoes_raw') }}
