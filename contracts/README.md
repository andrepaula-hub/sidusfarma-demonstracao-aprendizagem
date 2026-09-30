# Contratos de Dados

Esta pasta reúne os contratos de dados adotados pelo grupo para validar, versionar e auditar o ciclo de vida dos dados. Os contratos são arquivos YAML versionados no repositório e usados como referência para validações de pipeline, CI e documentação de governança.

O objetivo dos contratos é transformar regras documentais em critérios verificáveis. Sempre que uma carga, transformação, publicação, arquivamento ou descarte ocorrer, a execução deve registrar evidências compatíveis com o contrato aplicável.

| Arquivo | Escopo | Uso no ciclo de vida |
|---|---|---|
| `contrato_fontes_raw.yml` | Arquivos recebidos do parceiro e ingestão para raw | Valida fonte, arquivo, checksum, codificação, delimitador, campos mínimos e evidências de entrada |
| `contrato_staging.yml` | Dados carregados para staging | Valida schema, campos obrigatórios, tipos esperados, status de validação e critérios de quarentena |
| `contrato_pesquisas_trusted.yml` | Dados promovidos para trusted | Valida qualidade mínima, unicidade, integridade referencial, versão do dataset e critérios de promoção |
| `contrato_dw_analytics.yml` | Modelos analíticos, fatos, dimensões e métricas | Valida campos finais, grão, transformações, regras de mascaramento e rastreabilidade até o DW |
| `contrato_dashboard_publicacao.yml` | Publicações e dashboards | Valida dataset publicado, versão consumida, data de publicação e evidências de rastreabilidade |
| `contrato_retencao_arquivamento.yml` | Retenção, arquivamento, descarte e anonimização | Define prazos, gatilhos, aprovações e evidências obrigatórias para arquivar, descartar ou anonimizar |
| `contrato_execucao_linhagem.yml` | Execuções, logs e linhagem | Valida `run_id`, versões de pipeline/contrato/dataset, entradas, saídas, status e cadeia de linhagem |

Campos marcados como `A confirmar` nos contratos indicam decisão de negócio ou confirmação operacional pendente com o parceiro. Eles não bloqueiam a proposta técnica; indicam que a regra deve ser validada antes de virar política definitiva ou automação de descarte.
