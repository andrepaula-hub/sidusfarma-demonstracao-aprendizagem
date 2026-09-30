{{ config(materialized='table') }}

select 'questao' as record_type, q.pergunta_id as record_id, q.pesquisa_id,
       'pesquisa_id inexistente em pesquisas.csv' as rejection_reason, q.run_id, q.ingested_at
from {{ ref('stg_questoes') }} q
left join {{ ref('stg_pesquisas') }} p using (pesquisa_id)
where p.pesquisa_id is null

union all

select 'respondente', r.cliente_id, r.pesquisa_id,
       'id_pesq inexistente em pesquisas.csv', r.run_id, r.ingested_at
from {{ ref('stg_respondentes') }} r
left join {{ ref('stg_pesquisas') }} p using (pesquisa_id)
where p.pesquisa_id is null

union all

select 'resposta', r.resposta_id, r.pesquisa_id,
       'pesquisa_id inexistente em pesquisas.csv', r.run_id, r.ingested_at
from {{ ref('stg_respostas') }} r
left join {{ ref('stg_pesquisas') }} p using (pesquisa_id)
where p.pesquisa_id is null
