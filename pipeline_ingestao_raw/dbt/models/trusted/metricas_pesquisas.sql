{{ config(unique_key='pesquisa_id') }}

select p.pesquisa_id,
       count(distinct r.resposta_id) as quantidade_respostas,
       count(distinct rp.cliente_id) as quantidade_respondentes,
       count(distinct rp.cliente_id)::numeric / nullif(p.participantes, 0) as taxa_participacao,
       p.participantes as quantidade_pesquisas_planejada,
       p.data_entrega,
       p.run_id,
       p.ingested_at
from {{ ref('dim_pesquisa') }} p
left join {{ ref('fato_resposta') }} r using (pesquisa_id)
left join {{ ref('stg_respondentes') }} rp using (pesquisa_id)
group by p.pesquisa_id, p.participantes, p.data_entrega, p.run_id, p.ingested_at
