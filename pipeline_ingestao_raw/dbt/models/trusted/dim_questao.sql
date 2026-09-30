{{ config(unique_key='pergunta_id') }}

select q.pergunta_id, q.pesquisa_id, q.enunciado, q.tipo, q.alternativas, q.run_id, q.ingested_at
from {{ ref('stg_questoes') }} q
inner join {{ ref('dim_pesquisa') }} p using (pesquisa_id)
where q.pergunta_id is not null
