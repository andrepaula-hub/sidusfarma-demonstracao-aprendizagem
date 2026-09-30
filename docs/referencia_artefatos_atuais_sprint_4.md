# Referência de artefatos atuais — Sprint 4

**Atualizado em:** 14 de setembro de 2026  
**Baseline técnica analisada:** `origin/main` (`440edb6`)  
**Fonte do escopo:** bloco "Implementação de Reports com Base nos Cubos de Dados" do documento técnico recebido.

## Leitura do enunciado

A Sprint 4 não pede uma nova ETL. Ela pede a camada de consumo analítico: reports em **Power BI** conectados aos cubos derivados do repositório analítico, mais um teste de usabilidade executado e documentado. O entregável obrigatório é `docs/solucao_dashboard.md`.

O enunciado não exige publicar o `.pbix` nem determina um número de páginas, mas a documentação precisa permitir verificar o modelo consumido, as medidas, os filtros, as interações e o resultado dos testes. Nenhum teste de usabilidade pode ser declarado como executado sem evidência de participantes e resultados reais.

## Ponto de partida disponível

| Ativo local | Evidência | Uso na Sprint 4 | Situação |
| --- | --- | --- | --- |
| Contrato analítico | `contracts/contrato_dw_analytics.yml` define `dim_empresa`, `dim_pesquisa`, `fato_resposta` e `metricas_pesquisas`. | Fonte para documentar cubos, grão e linhagem. | Parcial: está `proposed` e não é um modelo físico comprovado. |
| Ingestão ClickHouse | `etl/`, `infra/`, migrations, DAGs Airflow e testes de integração ClickHouse/MinIO. | Base de ingestão rastreável para alimentar a camada analítica. | Entregue para ingestão; não é, por si só, o DW dimensional pronto para consumo BI. |
| Definições de KPIs e qualidade | `docs/modelagem_quantitativa_de_dados_do_parceiro.md`, JSONs v2 e gráficos agregados. | Fonte para fórmulas, universo, cobertura e ressalvas. | Reutilizável; não substitui medidas DAX nem report. |
| Proposta visual | Três wireframes em `docs/img/` e requisitos em `docs/contexto_organizacional_+_requisitos_da_solução_analítica.md`. | Norte para páginas e públicos dos reports. | Documentado; implementação em Power BI não encontrada. |
| Governança de publicação | `contracts/contrato_dashboard_publicacao.yml`. | Versionamento do dataset/modelo e registro de publicação. | Proposto; falta registro de uma publicação real. |
| Dashboard antigo | `legacy/streamlit/`. | Referência histórica de conteúdo, se necessário. | Não deve ser apresentado como entrega da Sprint 4. |

Não foram encontrados nesta cópia local `docs/solucao_dashboard.md`, arquivo `.pbix`/`.pbit`, export de report Power BI, medidas DAX versionadas ou evidências de testes de usabilidade. Portanto, não há base para afirmar que os reports foram implementados ou validados.

## Épicos e backlog recomendado

### E4.1 — Dataset analítico consumível e rastreável

**Objetivo:** tornar explícito qual modelo aprovado alimenta o Power BI e como ele é atualizado.

1. Confirmar a fonte de consumo: tabelas trusted/analytics, conexão, credenciais e versão do dataset.
2. Fechar grão, chaves e relacionamentos de `dim_pesquisa`, `dim_empresa`, `fato_resposta` e `metricas_pesquisas`.
3. Completar as dimensões conformadas, no mínimo Tempo e Empresa; documentar papéis de data.
4. Modelar o domínio de resultados/respostas para sustentar o Portal do Acervo sem expor dados identificáveis.
5. Registrar `dataset_version`, `model_version`, atualização e linhagem exigidos pelos contratos.

**Critério de pronto:** cada tabela e medida usada no report tem grão, chave, origem, transformação, versão e classificação de acesso documentados; o report não consulta raw, staging ou quarentena.

### E4.2 — Reports e modelo semântico no Power BI

**Objetivo:** implementar visuais interativos sobre os cubos, sem alterar a semântica já aprovada dos indicadores.

Escopo mínimo sugerido:

| Report/página | Cubos e medidas candidatas | Interações obrigatórias |
| --- | --- | --- |
| Painel Operacional | ciclo de vida / `metricas_pesquisas`: pesquisas ativas, concluídas, prazo, qualidade. | período, responsável, empresa solicitante, status; detalhe/drill-through por pesquisa. |
| Painel Estratégico | ciclo de vida e adesão: volume por período, participação/cobertura, composição por tipo/área. | período, segmento/empresa e tipo; drill-down temporal; comparação entre recortes. |
| Portal do Acervo | resultados/respostas somente em nível autorizado e agregado. | tema, período, empresa; busca/consulta. |

Para cada visual, documentar: cubo/tabela de origem, dimensão, medida DAX (ou indicação explícita de que é agregação simples), filtros, segmentações, hierarquia, nível de detalhe e regra de segurança. KPI de cobertura ou participação deve manter numerador, denominador, população e limitações visíveis; não converter cobertura cadastral em “taxa de adesão” sem validação de negócio.

**Critério de pronto:** `.pbix` ou evidência exportável do report existe, conecta ao dataset aprovado, possui relações sem ambiguidade e cada visual possui rastreabilidade documental.

### E4.3 — Qualidade funcional, desempenho e usabilidade

**Objetivo:** comprovar que pessoas conseguem usar os reports para tarefas reais e que os números permanecem corretos ao filtrar.

Plano mínimo de tarefas:

1. Filtrar o Painel Operacional por período e status e identificar pesquisas em atraso.
2. Fazer drill-down temporal no Painel Estratégico e comparar participação/cobertura entre empresas ou segmentos.
3. Aplicar duas segmentações simultâneas e conferir a atualização cruzada de cards e gráficos.
4. Usar drill-through até o detalhe autorizado de uma pesquisa e retornar ao resumo.
5. Localizar uma pesquisa publicada no Portal do Acervo usando tema, período e empresa.

Para cada execução registrar participante anônimo/role, pré-condição, tarefa, resultado esperado, resultado observado, tempo, erros, severidade, evidência e ação corretiva. Separar teste de precisão dos dados, teste de interação e teste de desempenho. O teste deve ser feito por ao menos uma pessoa que não construiu aquele report; caso isso não seja viável, registrar a limitação em vez de simular independência.

**Critério de pronto:** todas as tarefas têm resultado documentado; falhas possuem decisão (corrigida, aceita com justificativa ou pendente) e o report foi retestado após correções relevantes.

### E4.4 — Documentação e aceite

**Objetivo:** produzir o artefato avaliável `docs/solucao_dashboard.md`.

Estrutura recomendada:

1. objetivo, público, versão e escopo;
2. cubos consumidos, grãos, dimensões, fatos e relações;
3. páginas/visuais e filtros;
4. catálogo de medidas DAX e regras de cálculo;
5. segurança, privacidade e publicação;
6. plano, execução e resultados de usabilidade;
7. limitações, decisões e próximos passos;
8. links para arquivo do report/evidências, dataset e versão.

## Dependências e riscos que precisam de decisão

| Tema | Estado atual | Decisão/evidência necessária |
| --- | --- | --- |
| Dataset analítico | A ingestão ClickHouse está implementada, mas o contrato de DW/Analytics ainda está marcado como `proposed`. | Materializar e aprovar o dataset/cubos que o Power BI consumirá; não ligar o report diretamente às tabelas de ingestão. |
| Autoridade dos dados | A remessa CSV está marcada como provisória e possui divergências conhecidas com XLSX. | Confirmação do parceiro/Data Owner antes de comunicar indicadores como oficiais. |
| Grão e respostas | Feedback anterior aponta grão insuficiente e ausência de modelagem de resultados/respostas. | Fechar o modelo antes de construir o Portal do Acervo e seus drill-throughs. |
| LGPD/acesso | Há dados de contato e o contrato de publicação está `proposed`. | Definir público, RLS/perfis e quais campos/agregações podem aparecer em cada report. |
| Usabilidade | Não há testes ou participantes registrados. | Recrutar participantes, executar o roteiro e anexar evidências reais. |

## Relação com a Sprint 3

A Sprint 4 pode começar por modelagem, protótipo de report e plano de testes. A Sprint 3 já entrega a base de ingestão ClickHouse; o aceite de integração ponta a ponta da Sprint 4 depende de materializar e aprovar o dataset/cubos analíticos, além de registrar sua versão e confirmar a autoridade da fonte.
