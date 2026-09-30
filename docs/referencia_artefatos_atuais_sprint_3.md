# Referência de artefatos atuais — Sprint 3

**Atualizado em:** 14 de setembro de 2026  
**Baseline verificada:** `origin/main` em `440edb6`  
**Observação de checkout:** a pasta aberta está na branch histórica `feature/ingestao-raw-airflow-dbt` (`8193ddf`), que já foi integrada na linha atual. Ela não é a referência para aferir o estado final da Sprint 3.

## Fonte de verdade e conclusão

A Sprint 3 está implementada na linha de integração atual (`main`). O destino de ingestão é **ClickHouse**, não PostgreSQL. O PostgreSQL presente na branch histórica é apenas parte daquela implementação anterior; a linha atual contém o módulo `etl/`, o ambiente `infra/` e testes próprios para ClickHouse.

O escopo técnico solicitado — ETL Python, orquestração, CI, observabilidade, testes e documentação arquitetural — possui implementação e evidências versionadas. O resultado deve ser descrito como **tecnicamente homologado, com ressalvas sobre a qualidade/autorização de negócio da remessa**, e não como pendente de ClickHouse. Isso não equivale a garantir nota máxima: a avaliação deve considerar também coerência da linha integrada, demonstração atual e controles operacionais fora do ambiente local.

## O que foi entregue

| Requisito | Evidência na `main` | Status |
| --- | --- | --- |
| ETL em Python e camadas | `etl/` separa domínio, configuração, adaptadores, transformadores, orquestração e observabilidade. | Entregue |
| Extração e raw imutável | `etl/adaptadores/extratores/`, armazenamento S3/MinIO e testes `tests/etl/test_raw_s3.py`. | Entregue |
| Transformação e carga | Transformadores por domínio, rejeições tipadas e `etl/adaptadores/sinks/clickhouse.py`. | Entregue |
| ClickHouse | Migrations `001`–`005`, tabelas de ingestão, auditoria, rejeições e views seguras; Compose com ClickHouse. | Entregue |
| Orquestração | Fluxos de remessa/fonte, retries/retomada e DAGs Airflow em `infra/airflow/dags/`. | Entregue |
| Observabilidade | Logs estruturados, métricas, Prometheus, Grafana e alertas operacionais. | Entregue |
| CI e qualidade de código | `.gitlab-ci.yml` executa Ruff, mypy, cobertura, docs e job dedicado ClickHouse + MinIO. | Entregue |
| Testes | Unitários, contratos, integração ClickHouse, raw/S3, orquestração, observabilidade e Docker. | Entregue |
| Arquitetura ISO/IEC 10746 e UML | `docs/arquitetura/visoes-logicas.md`, visões de engenharia/tecnologia, sequência e diagramas de casos de uso/componentes. | Entregue |

## Evidência de execução, sem extrapolação

O relatório de homologação (`docs/homologacao/relatorio-integrado.md`) registra duas passagens completas da remessa de 13/08/2026 em ClickHouse 25.3.14.14 e MinIO isolados:

| Resultado por passagem | Valor |
| --- | ---:|
| Linhas extraídas | 46.148 |
| Válidas e carregadas | 41.389 |
| Rejeitadas | 4.759 |
| Reconciliação | extraídas = válidas + rejeitadas |

O mesmo documento registra tipos compatíveis, anti-joins sem órfãos entre registros aceitos, hashes estáveis na reexecução e preservação dos seis arquivos raw no S3. Há também registro de 567 testes aprovados, 94,06% de cobertura ETL, Ruff e mypy aprovados naquela homologação. Isso é evidência versionada de execução; não substitui uma nova execução do ambiente atual caso seja necessária uma revalidação.

## Status correto

| Frente | Situação |
| --- | --- |
| Aderência técnica da Sprint 3 | Concluída na `main`, com ClickHouse, Airflow, CI, observabilidade, testes e documentação. |
| Qualidade da remessa | Requer análise do Data Steward: 4.759 rejeições foram preservadas e explicadas, não ignoradas. |
| Fonte canônica | Pendente de decisão do parceiro: CSV é provisório diante das divergências CSV × XLSX. |
| DW dimensional, Power BI e publicação | Não pertencem à conclusão da ingestão; são evolução de analytics/consumo da Sprint 4. |

## Riscos de avaliação antes de chamar a entrega de “10”

| Risco verificado | Impacto provável | Ação recomendada |
| --- | --- | --- |
| A `main` reúne mais de uma implementação histórica de ingestão (incluindo a antiga `pipeline_ingestao_raw/`, o módulo `etl/` e outros incrementos de ingestão). | Pode transmitir duplicidade de arquitetura e dificultar a identificação do caminho canônico. | Declarar no README qual é o runtime oficial da Sprint 3 e mover/remover do escopo de execução os legados, sem apagar evidência necessária. |
| O README da linha integrada ainda descreve as DAGs como vazias, enquanto a árvore possui DAGs. | Inconsistência documental, mesmo com código entregue. | Atualizar o runbook/README e executar o fluxo descrito a partir de um clone limpo. |
| A evidência de homologação é histórica. O teste de carga de DAGs no Docker está numa branch de teste e não está incorporado na `main`. | Não há prova automatizada final de que a composição atual carrega as DAGs no Docker. | Mesclar ou reproduzir esse teste na `main` e anexar a saída da CI. |
| Alguns requisitos são explicitamente locais/propostos: TLS, RBAC/grants ClickHouse, alertas de DLQ, replay automático, p95 de desempenho e políticas de retenção. | Não invalida o MVP acadêmico, mas impede apresentar o ambiente como operação produtiva plenamente controlada. | Classificar como fora do ambiente local ou implementar apenas o que o critério da disciplina exigir. |
| Fonte canônica e promoção de qualidade dependem do parceiro/Data Owner. | Impede afirmar que os dados são “oficiais/aprovados para consumo”. | Manter a ressalva e registrar a decisão externa quando houver. |

## Próximas ações úteis, sem reabrir a Sprint 3

1. Revisar os motivos de rejeição com o Data Steward e decidir correção/promover/aceitar exceções.
2. Obter a confirmação do parceiro sobre a fonte canônica e manter a proveniência até a decisão.
3. Usar as tabelas de ingestão aprovadas como entrada para materializar os cubos/dataset analítico da Sprint 4; não conectar Power BI diretamente a raw, rejeições ou staging.
4. Se houver mudança de infraestrutura ou contratos, reexecutar a homologação isolada; não tratar a evidência de setembro como prova automática para código alterado.

## Transição para a Sprint 4

O bloco de especificação sobre Power BI, cubos e testes de usabilidade é a próxima camada. O backlog e as dependências dessa entrega estão em [Referência de artefatos atuais — Sprint 4](referencia_artefatos_atuais_sprint_4.md).
