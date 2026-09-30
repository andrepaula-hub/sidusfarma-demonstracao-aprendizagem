# Feedback — PIPELINE ETL

**Recebido em:** 22 de setembro de 2026  
**Escopo avaliado no feedback:** pacote `etl/`, infraestrutura correlata, CI,
testes, documentação arquitetural e homologação.  
**Evidência externa citada:** pipeline GitLab `70008`.

## Síntese do retorno recebido

O retorno reconhece que o PIPELINE ETL entrega extração, transformação por
fonte, carga, rejeições, retentativas, dependências e retomada. Também registra
uma homologação versionada com 46.148 registros extraídos, 41.389 válidos e
4.759 rejeitados, com reconciliação e reexecução por hash de conteúdo.

As ressalvas recebidas são:

1. a suíte bloqueia sob `--strict-markers`, pois usa o marcador `clickhouse`
   sem registrá-lo no `pytest.ini`;
2. os jobs de CI não demonstram uma execução completa e reprodutível dos
   testes, cobertura e integração;
3. numa falha de carga após lotes confirmados, `linhas_carregadas` pode ser
   persistido como zero;
4. uma falha em `iniciar_execucao` fica fora do encerramento de métricas por
   fonte;
5. a Visão de Engenharia descreve comportamentos já alterados no código;
6. a referência abreviada a “ADR-002” é ambígua, pois há mais de um documento
   com esse identificador; e
7. o orquestrador depende do adaptador concreto `ClickHouseSink` para o ciclo
   de execução, em vez de depender exclusivamente de uma porta.

## Triagem técnica local

Esta triagem compara a árvore versionada de `origin/main` disponível no
repositório em 22/09/2026. Ela não substitui a inspeção da execução remota
`70008`, cujos logs e imagens não estão presentes neste checkout.

| Item | Veredito | Evidência e encaminhamento |
| --- | --- | --- |
| Marcador `clickhouse` não registrado | **Confirmado — pedir correção** | [`pytest.ini`](../pytest.ini) habilita `--strict-markers` e declara apenas `integration`; a CI seleciona `-m clickhouse` e há quatro módulos ETL marcados. Registrar o marcador e manter um teste de coleta na CI. |
| Dependências/serviços da CI | **Plausível, precisa ser reproduzido no pipeline alvo** | A configuração local instala `requirements-test.txt` e `requirements-etl.txt`; o primeiro não declara DuckDB. Não foi localizado uso atual de DuckDB nos testes desta linha, portanto a falha atribuída a ele precisa vir acompanhada do log/job e SHA do pipeline. A falha de pull do MinIO também é de infraestrutura remota e deve ser confirmada/reexecutada. |
| `linhas_carregadas=0` após falha parcial | **Confirmado — pedir correção** | O sink só leva `lotes_confirmados` em `SinkIndisponivel`; o orquestrador só atribui `linhas_carregadas` após `carregar` retornar com sucesso. Propagar também as linhas confirmadas e criar teste de falha entre lotes, seguido de retentativa e reconciliação. |
| Falha em `iniciar_execucao` sem métricas de encerramento | **Confirmado — pedir correção** | `iniciar_execucao` é chamado antes do `try` em `etl/orquestracao/pipeline.py`; se ele levantar, `_encerrar` não é alcançado. Incluir essa chamada no caminho protegido, preservando a exceção original. |
| Visão de Engenharia desatualizada | **Confirmado — pedir correção documental** | A visão ainda afirma que a conexão ocorre antes da política de retentativa e que a falha de `finalizar_execucao` interrompe métricas. O código abre o cliente tardiamente e protege a gravação final; atualizar/remover a seção de divergências para retratar o estado vigente. |
| Acoplamento a `ClickHouseSink` | **Confirmado — melhoria arquitetural, não bloqueante** | `OrquestradorIngestao` recebe `ClickHouseSink`, embora extração e transformação usem portas. É uma dívida técnica razoável: uma porta de auditoria/execução permitiria manter persistência e rastreabilidade sem acoplar a orquestração ao adaptador. |
| Ambiguidade de “ADR-002” | **Confirmado — pedir correção documental** | Há múltiplos documentos `ADR-002` em `docs/specs/`. Usar título/slug e link relativo completo nas referências. |
| Números de homologação e testes diagnósticos | **Não refutado, mas não revalidado localmente** | As contagens 46.148 / 41.389 / 4.759 também constam da evidência versionada. Os totais de 467 e 46 testes, a versão 25.8 e o pipeline 70008 exigem log, SHA e ambiente exatos para serem auditáveis. |

## Solicitação de revisão recomendada

Pedir revisão é justificável. Prioridade sugerida:

1. corrigir `pytest.ini` e a matriz de dependências/serviços dos jobs, depois
   anexar ao MR a execução verde completa;
2. propagar `linhas_carregadas` em `SinkIndisponivel`, testar falha parcial e
   comprovar a reconciliação após retentativa;
3. envolver `iniciar_execucao` no ciclo de instrumentação e acrescentar teste
   para sua falha; e
4. atualizar a Visão de Engenharia e desambiguar as ADRs.

O acoplamento ao `ClickHouseSink` é válido como melhoria de arquitetura, mas
não precisa bloquear a entrega se os quatro itens anteriores forem corrigidos
e comprovados.

## Texto sugerido para devolver ao grupo

> Concordamos com as ressalvas de CI, contagem parcial, instrumentação de
> `iniciar_execucao` e atualização documental. Antes de concluir a revisão,
> pedimos os links/logs e o SHA do pipeline 70008 para reproduzir os problemas
> de DuckDB e de pull do MinIO no mesmo contexto. O marcador `clickhouse` não
> registrado e as duas lacunas no tratamento de falha são reproduzíveis pela
> árvore atual e serão tratados como correções prioritárias.
