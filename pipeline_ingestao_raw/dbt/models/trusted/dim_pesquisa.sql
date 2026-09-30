{{ config(unique_key='pesquisa_id') }}

select pesquisa_id, titulo, status, tipo, area, participantes, data_solicitacao,
       data_entrega, run_id, ingested_at
from {{ ref('stg_pesquisas') }}
where pesquisa_id is not null
