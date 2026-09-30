select raw_payload ->> 'id_resposta' as resposta_id, raw_payload ->> 'pesquisa_id' as pesquisa_id,
       raw_payload ->> 'id_pergunta' as pergunta_id, raw_payload ->> 'id_empresa' as empresa_id,
       raw_payload ->> 'valor' as valor, raw_payload ->> 'alternativa' as alternativa,
       run_id, ingested_at, source_file
from {{ source('raw_staging', 'respostas_raw') }}
