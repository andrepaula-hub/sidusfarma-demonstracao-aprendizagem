{{ config(unique_key='empresa_id') }}

select empresa_id, nome_fantasia, percentual_mercado, nacionalidade, associado,
       tipo_associado, cidade, estado, pais, run_id, ingested_at
from {{ ref('stg_empresas') }}
where empresa_id is not null
