select raw_payload ->> 'ID' as empresa_id, raw_payload ->> 'Nome Fantasia' as nome_fantasia,
       raw_payload ->> '% de mercado' as percentual_mercado, raw_payload ->> 'Nacionalidade' as nacionalidade,
       raw_payload ->> 'Associado' as associado, raw_payload ->> 'Tipo de Associado' as tipo_associado,
       raw_payload ->> 'Cidade' as cidade, raw_payload ->> 'Estado' as estado, raw_payload ->> 'País' as pais,
       run_id, ingested_at, source_file
from {{ source('raw_staging', 'empresas_raw') }}
