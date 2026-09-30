{{ config(unique_key='resposta_id') }}

select r.resposta_id, r.pesquisa_id, r.pergunta_id, r.empresa_id, r.valor, r.alternativa,
       r.run_id, r.ingested_at
from {{ ref('stg_respostas') }} r
inner join {{ ref('dim_pesquisa') }} p using (pesquisa_id)
inner join {{ ref('dim_questao') }} q using (pergunta_id)
inner join {{ ref('dim_empresa') }} e using (empresa_id)
where r.resposta_id is not null
