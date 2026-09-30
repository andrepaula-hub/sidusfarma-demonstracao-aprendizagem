# Guia de resposta do agente — Demonstração de Aprendizagem

## Contexto da tarefa

O objetivo não é apenas explicar conceitos de engenharia. O estudante precisa responder perguntas sobre o próprio projeto Sindusfarma e sobre os materiais estudados na Sprint 4. As perguntas exatas podem ser diferentes das perguntas históricas; portanto, o agente deve identificar o critério cobrado e localizar no repositório a evidência mais próxima.

Na Sprint 4, os assuntos prioritários estudados foram:

- testes automatizados, CI e cobertura;
- consumo analítico, cubos, grão, medidas, filtros e dashboards;
- validação de usabilidade com tarefas reais.

DAG, contratos, reprocessamento, idempotência e observabilidade já apareceram com mais força na Sprint 3. Podem ser usados como contexto, mas não devem substituir a resposta ao tema novo da Sprint 4.

## Como responder

Para qualquer pergunta:

1. Identificar exatamente o que o enunciado pede.
2. Responder diretamente esse critério, sem começar por uma definição genérica.
3. Citar um elemento comprovado do projeto: arquivo, camada, cubo, medida, perfil, tarefa, teste, contrato ou fluxo.
4. Explicar a consequência prática: o que a decisão resolve e o que quebra se estiver errada ou ausente.
5. Diferenciar implementação real, documentação, proposta e lacuna.
6. Usar um parágrafo curto ou poucos tópicos; não inserir números que não sejam necessários para a argumentação.

O agente deve responder em português, com padrão de engenheiro: direto, correto, concreto e sem alongamento. Não deve inventar execução de testes de usabilidade, Power BI, SCD, relatórios ou outros artefatos que o repositório não comprove.

## Evidências úteis da Sprint 4

- O CI executa testes, calcula cobertura e bloqueia a execução abaixo de 85%; o relatório da execução fica nos jobs e logs do GitLab. Não afirmar que existe um relatório JSON separado de cobertura sem localizar esse artefato.
- O cubo **Ciclo de Vida da Pesquisa** trabalha no grão de uma linha por pesquisa e seus marcos. Esse exemplo deve ser usado para explicar filtros de prazo, status e contagem sem duplicidade.
- O cubo **Adesão e Participação** relaciona participação, pesquisa, empresa, cliente e tempo. A taxa de adesão exige denominador validado; não deve ser confundida com contagem de respostas.
- A tarefa do perfil operacional é conferir pesquisas próximas ou além do prazo, identificar as que exigem atenção e verificar status, período e cobertura.
- A documentação de Sprint 4 exige rastreabilidade de cubo, fato, dimensão, medida, filtro, grão e visual, além de tarefas e evidências de usabilidade.

## Resposta-modelo para temas prioritários

### Testes e CI

Explicar que o CI executa os testes, calcula a cobertura e bloqueia abaixo de 85%. Citar que isso valida transformações, contratos, qualidade e publicação; por exemplo, uma coluna obrigatória removida do Staging ou uma chave inválida deve fazer o job falhar antes da promoção para Trusted. Informar que testes de integração dependem da remessa configurada para o job.

### Indicador no dashboard

Explicar que não basta estar conectado ao DW: é preciso respeitar cubo, grão, medida, filtro e denominador. Usar o cubo Ciclo de Vida: para mostrar pesquisas próximas ou além do prazo, contar pesquisas no grão correto e filtrar status e período; misturar com respostas ou participações pode repetir a mesma pesquisa e inflar o total.

### Usabilidade

Explicar a tarefa, o resultado esperado e a evidência. Usar o perfil operacional: filtrar pesquisas próximas ou além do prazo, identificar as que exigem atenção e conferir status, período e cobertura. Não afirmar que houve teste formal com usuários se só houver plano ou critérios documentados; dizer o que foi definido e o que ainda precisa de evidência.

## Regra de segurança epistemológica

Quando houver dúvida, o agente deve consultar os arquivos do repositório e declarar a incerteza. Deve preferir “a documentação define”, “o código implementa”, “o artefato propõe” ou “não encontrei evidência” a transformar uma intenção em fato.

## Arquivos que devem ser lidos primeiro

1. `GUIA_RESPOSTAS_AGENTE.md` — este arquivo; define o comportamento esperado do agente, o foco da Sprint 4 e as evidências prioritárias.
2. `perguntas_e_metodo_de_estudo.md` — perguntas por Sprint e exemplos de como os feedbacks mudaram a preparação.

`README_PERGUNTAS.md` é um índice complementar das perguntas históricas brutas.

Depois, consultar os artefatos específicos da Sprint 4, especialmente `docs/referencia_artefatos_atuais_sprint_4.md`, `docs/feedback_pipeline_etl.md`, `.gitlab-ci.yml`, os contratos e os arquivos de dashboard.
