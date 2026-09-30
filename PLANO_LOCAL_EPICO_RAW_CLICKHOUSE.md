# Plano local — épico Raw no ClickHouse

**Estado:** rascunho local; não versionar, não commitar e não usar como descrição de MR.

## Objetivo do épico

Preservar cada arquivo de origem sem alteração no object storage e carregar no ClickHouse uma representação auditável, por linha, do mesmo conteúdo. Esta primeira etapa não executa cast, limpeza, renomeação, normalização de datas ou deduplicação de negócio; tais tratamentos pertencem ao staging.

## Tarefas do épico

### 1. Definir já no raw

- [ ] **Metadados técnicos:** `dataset_name`, `source_file`, `source_checksum`, `file_size_bytes`, `source_row_number`, `raw_payload`, `run_id`, `ingested_at`, `pipeline_version` e `contract_version`.
- [ ] **Falhas:** separar falha fatal de remessa (arquivo ausente, checksum ausente, encoding/delimitador/cabeçalho inválido ou CSV impossível de ler) de evento por linha. A falha fatal sempre grava auditoria com motivo e contagens disponíveis. Uma carga parcial pode permanecer fisicamente auditável, mas a remessa só fica **pronta/consumível** quando todos os arquivos e reconciliações terminarem com sucesso; não apagar raw para simular atomicidade.
- [ ] **Rastreabilidade:** toda linha deve apontar para arquivo, checksum, número da linha e execução; toda execução deve registrar início, fim, status, versões e contagens por dataset.
- [ ] **Reprocessamento/idempotência:** a chave lógica é `(dataset_name, source_checksum, source_row_number)`. Reexecutar o mesmo checksum não pode criar novo dado lógico; arquivo alterado, com checksum novo, é uma nova versão preservada.
- [ ] **Raw físico:** o arquivo original permanece no object storage. O ClickHouse recebe `raw_payload` e os metadados, não substitui a evidência binária original.

### 2. Registrar em contratos YAML

- [ ] Estender `contracts/contrato_fontes_raw.yml` com schema da tabela raw ClickHouse, campos técnicos obrigatórios, chave lógica, formato de payload e contagens esperadas por execução.
- [ ] Estender `contracts/contrato_execucao_linhagem.yml` com status por task/lote, motivo de falha, origem e destino ClickHouse.
- [ ] Declarar no contrato a política de reprocessamento e a retenção aplicável; manter `status: proposed` enquanto não houver aprovação do responsável de negócio.
- [ ] Manter regras objetivas: condição, ação, evidência produzida e critério de aceite.

### 3. Implementar a primeira carga raw no ClickHouse com base no MR 49

- [ ] Reaproveitar a estrutura Airflow, MinIO, checksum, leitura CSV, logs estruturados, auditoria e retries do MR 49.
- [ ] Adicionar ClickHouse ao `docker-compose` e substituir a persistência PostgreSQL desta etapa por tabelas raw e de auditoria no ClickHouse.
- [ ] Criar DDL da tabela raw com particionamento por data de ingestão, ordenação pela chave lógica e estratégia explícita de idempotência compatível com ClickHouse.
- [ ] Carregar somente payload bruto e metadados; não executar dbt staging/trusted nesta entrega.
- [ ] Documentar o runbook operacional e a análise das métricas por task no README do módulo.

### 4. Testar e medir

- [ ] Teste de arquivo obrigatório ausente, encoding/delimitador/cabeçalho inválido e checksum inexistente.
- [ ] Teste de carga de uma remessa, reconciliação entre linhas lidas e linhas raw gravadas e verificação dos metadados por linha.
- [ ] Teste de reexecução do mesmo checksum sem novo dado lógico.
- [ ] Teste de arquivo corrigido/alterado, que cria nova versão sem apagar a anterior.
- [ ] Teste de auditoria de falha e sucesso, com duração por task e contagens por dataset.
- [ ] Registrar limiares operacionais iniciais para alerta (falha de execução, ausência de remessa e divergência de contagem); limiares de qualidade por campo ficam para staging.

## Pesquisa cruzada: decisões existentes

## Verificação de sobreposição com `develop` e branches remotas (9 set. 2026)

O último `develop` mesclado contém principalmente artefatos documentais de fluxo, controles de dados classificados, maturidade e auditoria/rastreabilidade. Não há nele uma implementação de runtime Airflow + ClickHouse para este épico.

Porém, há trabalho **não mesclado** que se sobrepõe e deve ser resolvido com o grupo antes de qualquer código novo:

| Branch remota | Sobreposição observada | Decisão necessária |
|---|---|---|
| `chore/etl-02-ambiente-local-servicos` | Docker local com ClickHouse, Airflow, Prometheus e Grafana. | Reusar/mesclar como ambiente-base em vez de criar outro compose. |
| `feat/etl-04-schemas-adapter-clickhouse` | No estado remoto atual, aponta para o mesmo incremento de ambiente local; o nome sugere schema/adapter, mas esses arquivos ainda não aparecem no diff. | Confirmar o dono e o escopo antes de depender da branch. |
| `feat/ingestao-eventos-clickhouse` | Pipeline completo, contratos, DDL, testes e integração ClickHouse. | Avaliar se é o caminho técnico do grupo antes de iniciar implementação paralela. |
| `codex/ingestao-raw-replicada-clickhouse` | Implementação específica de raw replicado, controle de quorum, DDL, contrato e testes ClickHouse. | Não duplicar: revisar e decidir se será adotada, adaptada ou descartada. |
| `feature/ingestao-raw-object-storage-giacomo` | Pipeline raw de object storage, mas com destinos SQLite/Snowflake. | Pode fornecer ideias de contrato/fluxo, mas não resolve o destino ClickHouse. |

Conclusão: o épico continua necessário na `develop`, mas a implementação deve esperar a definição de qual branch aberta será a base canônica. O plano atual serve para fechar os quatro controles e comparar essas alternativas, não para competir com código já em andamento.

### 1. Já existe, foi bem avaliado e deve ser aplicado

| Evidência existente | Feedback que valida a ideia | Aplicação no épico raw |
|---|---|---|
| `contrato_fontes_raw.yml`: arquivo, encoding, delimitador, chave, checksum, tamanho, linhas, colunas e `run_id`. | O feedback do MR 49 deu 2,0/2,0 ao domínio das fontes, formatos e grão raw; o data mapping foi apontado como o ponto mais forte. | Reaproveitar como base do contrato raw; complementar apenas o destino ClickHouse e a chave/idempotência. |
| `contrato_execucao_linhagem.yml`: `run_id`, versões, início/fim, status, datasets de entrada/saída e transformação. | O feedback de governança elogiou regras objetivas, evidência confirmada versus proposta e metadados/catálogo como padrão excepcional. | Usar esses campos para a tabela/auditoria de execução, sem inventar outro modelo paralelo. |
| Inventário das bases: seis CSVs, UTF-8-BOM, `;`, volume, grão, chaves e divergências conhecidas. | O MR 49 foi elogiado por documentar volumetria, encoding, delimitador e grãos. | Fazer o pre-check de remessa baseado no inventário e no contrato, antes da carga. |
| Padrão do MR 49: MinIO, Airflow, SHA-256, `run_id`, logs, retries e reexecução idempotente. | Feedback: 1,8/2,0 em eficiência; reconheceu `ON CONFLICT`, particionamento, retries e auditoria. | Manter o desenho de orquestração; substituir somente a persistência PostgreSQL por ClickHouse. |
| `contrato_retencao_arquivamento.yml`: raw versionado, checksum e retenção proposta de 12 meses. | A avaliação de governança reconheceu ciclo de vida e controles como rigorosos. | Preservar como política proposta; não automatizar descarte sem aprovação do Owner. |
| Metadados MC-01 a MC-23 na governança: fonte, linhagem, localização, qualidade, versão, limitações e responsáveis. | O feedback destacou a ficha de metadados de 36 campos. | Selecionar o subconjunto operacional necessário para raw, mantendo o catálogo como fonte de semântica. |

### 2. Já foi proposto, mas precisa ser revisto antes de aplicar

| Proposta/estado atual | Problema apontado | Revisão necessária |
|---|---|---|
| MR 49 persiste raw e auditoria em PostgreSQL. | A especificação atual exige ClickHouse; o MR é referência, não implementação final. | Reescrever DDL, conexão e estratégia de idempotência especificamente para ClickHouse. |
| Métricas do MR 49 registram volumes e status, sem limites numéricos. | Feedback: sem limiar, métrica é registro, não controle. | Declarar limites operacionais mínimos e, no staging, limites de qualidade por campo/dataset. |
| Um único commit, descrição de MR vazia e briefing `PONDERADA_...` na raiz. | Feedback: prejudicou documentação e revisão incremental. | Trabalhar em tarefas pequenas; README fala com o operador; briefing fica fora do artefato operacional. |
| `contrato_staging.yml` afirma `type_validation: true`, mas não define tipos por campo. | Não permite validação verificável de casts ou schema. | Não usar isso para raw; criar depois uma matriz explícita de tipos no contrato de staging/ClickHouse. |
| Política de retenção está marcada como `proposed`. | Não é uma decisão aprovada pelo parceiro. | Usar como hipótese documentada, sem descarte automático e sem apresentá-la como fato. |
| Dados de origem CSV têm autoridade provisória frente ao XLSX. | Inventário documenta divergências ainda não resolvidas. | Sempre registrar checksum, origem e versão; não escolher uma fonte canônica silenciosamente. |

### 3. Ainda não foi proposto e deve ser definido agora

| Lacuna | Proposta para decidir no épico raw |
|---|---|
| Schema físico ClickHouse | Nome de banco/tabela, tipos, `raw_payload`, particionamento, `ORDER BY` e política de TTL. |
| Idempotência específica de ClickHouse | Como impedir/reconciliar duplicata lógica, já que o banco não oferece unicidade transacional como PostgreSQL. A estratégia deve ser testada, não apenas declarada. |
| Auditoria de execução no destino novo | Tabela de execução, status por task, motivo de falha, duração e contagens por dataset. |
| Política de carga parcial | Definir se qualquer falha fatal aborta toda a remessa (recomendado para raw) e como registrar o que não chegou a ser lido. |
| Manifesto da remessa | Relacionar arquivo original no object storage, checksum, versão, data/hora de recebimento, contrato e linhas gravadas no ClickHouse. |
| Limiares operacionais | Ausência de arquivo, falha da DAG, divergência entre linhas lidas/gravadas e atraso de execução. |
| Testes integrados ClickHouse | Fixture Docker e casos de sucesso, falha e reprocessamento contra a tecnologia real. |

## Critério de pronto

Para cada linha raw no ClickHouse, é possível identificar arquivo original, checksum, linha de origem, execução e versões. Para cada remessa, é possível conferir contagens, status e motivo de falha. Reexecutar o mesmo arquivo não cria outro dado lógico; uma nova versão do arquivo não apaga a anterior.
