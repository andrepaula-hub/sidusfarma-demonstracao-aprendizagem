# Status Report — Artefato 3

**Projeto:** Governança e Integração de Dados — Sindusfarma  
**Atualização:** 14 de agosto de 2026  
**Baseline revisada:** `develop` em `c030e75`  
**Estado geral:** correção matemática concluída; pacote privado concluído; publicação online condicionada ao Cloudflare Access

## 1. Resumo executivo

O Artefato 3 foi reprocessado e revisado de ponta a ponta. A arquitetura original foi preservada quando adequada, mas os contratos de ingestão, a semântica das respostas, os universos dos KPIs, o runner, os outputs, os gráficos e a documentação foram corrigidos.

O resultado atual atende aos seis itens do enunciado e possui evidência automatizada. A revisão adversarial final não encontrou bloqueador matemático P0. Permanecem decisões externas do parceiro e uma condição administrativa para publicar o site com autenticação.

Foram estruturados somente dois MRs:

| MR | Branch | Escopo | Dependência |
|---|---|---|---|
| [!18](https://git.inteli.edu.br/graduacao/2026-2a/t13/g02/-/merge_requests/18) | `fix/a3-confiabilidade-integral` | matemática, qualidade, KPIs, runner, testes, outputs, gráficos, relatório, SPEC, ADR e CI | nenhuma |
| [!19](https://git.inteli.edu.br/graduacao/2026-2a/t13/g02/-/merge_requests/19) | `security/a3-private-pages` | pacote por allowlist, privacy gate e deploy manual protegido | !18 |

Essa separação evita misturar a aprovação acadêmica com uma configuração administrativa de infraestrutura. O segundo MR pode ser integrado sem publicar: o job de deploy só existe quando a variável protegida `CLOUDFLARE_ACCESS_CONFIRMED=true` for configurada.

## 2. Participação dos agentes

O trabalho foi dividido em frentes independentes e depois consolidado pelo agente principal:

| Frente | Responsabilidade | Resultado |
|---|---|---|
| Orquestração matemática | reconstruir contratos, universos, fórmulas e valores esperados | aprovou os seis KPIs após as correções |
| Ingestão e qualidade | revisar NA, schema, respostas polimórficas e testes | 20.607/20.607 respostas válidas |
| KPIs e granularidade | materializar zeros, alinhar denominadores e criar scorecards | KPIs 03, 04, 05 e 06 corrigidos |
| Segurança e CI | avaliar Cloudflare Pages, autenticação e risco de exposição | arquitetura com Cloudflare Access e allowlist |
| Redação técnica | reconciliar relatório, inventário, SPEC e ADR | seis seções e sete gráficos preservados |
| QA adversarial | procurar erros matemáticos, vazamentos e divergências | nenhum P0; quatro P1 encontrados e tratados/documentados |

## 3. Atendimento ao enunciado

| Item exigido | Evidência | Status |
|---|---|---|
| 1. Contextualização quantitativa | processo, decisões e unidade principal descritos | concluído |
| 2. Unidades e variáveis | mais de três unidades e mais de dez variáveis classificadas | concluído |
| 3. Qualidade dos dados | volumes, ausências, completude, duplicatas, relações e inconsistências | concluído |
| 4. Estatística descritiva | frequências, percentuais, moda, estatísticas numéricas e série temporal | concluído |
| 5. Indicadores iniciais | seis KPIs com objetivo, fórmula, variáveis, universo e interpretação | concluído |
| 6. Granularidade e síntese | KPI-03 e KPI-05 comparados em diferentes grãos | concluído |
| Formato | Markdown, tabelas, cálculos, sete gráficos e interpretações | concluído |

Documento principal: `docs/modelagem_quantitativa_de_dados_do_parceiro.md`.

## 4. Fonte, proveniência e limite de autoridade

A remessa recebida em 13/08/2026 contém seis CSVs usados como fonte operacional provisória. Os arquivos brutos permanecem em `REFERENCE_MATERIAL/`, ignorados pelo Git.

Cada output v2 registra:

- fingerprint SHA-256 conjunto;
- SHA-256, tamanho, linhas e colunas por arquivo;
- encoding UTF-8 com BOM;
- delimitador `;`;
- política de ausência;
- data do snapshot;
- status `csv-provisional` e `pending_partner_confirmation`.

A autoridade definitiva não pode ser declarada sem o parceiro porque:

- `clientes.csv` possui uma chave a mais que `clientes.xlsx`;
- existem 72 valores brutos divergentes em `respostas.valor` entre CSV e XLSX;
- `respondentes.csv` não possui equivalente XLSX.

O teste privado de integração registra essas divergências e impede reconciliação silenciosa.

## 5. Correções P0 implementadas

### 5.1 Contrato da fonte

- as 11 colunas vazias `Unnamed` deixaram de ser obrigatórias;
- a remessa passou a ter manifesto versionado;
- a origem CSV foi declarada provisória;
- o drift conhecido CSV/XLSX passou a ter teste de regressão.

### 5.2 Ausência e respostas polimórficas

Somente vazio físico ou whitespace é convertido em ausência. Textos não vazios como `NA`, `N/A`, `null`, `None`, `-` e `s/i` são preservados.

As regras de representação são avaliadas por tipo:

| Tipo | Representação aceita | Linhas | Válidas |
|---|---|---:|---:|
| aberta | `valor` | 154 | 154 |
| numérica | `valor` | 540 | 540 |
| múltipla escolha | `alternativa` ou `valor` | 5.853 | 5.853 |
| caixas de seleção | `alternativa` | 10.052 | 10.052 |
| matriz | linha + coluna ou alternativa + valor | 4.008 | 4.008 |
| **Total** | regra do tipo | **20.607** | **20.607** |

Resultado: nenhuma linha avaliável está sem representação válida. A ausência física de `respostas.valor` é 8.307, mas isso não significa ausência de resposta quando outro campo permitido contém a representação.

### 5.3 Integridade cruzada

O relatório v2 distingue `error`, `warning` e `ambiguity`. Foram adicionadas verificações de:

- título da questão versus pesquisa;
- empresa da participação versus empresa do contato;
- participantes declarados versus observados;
- pesquisa declarada com zero observado;
- resposta sem par pesquisa/empresa observado;
- market share histórico versus cadastro atual;
- questão duplicada sem derrubar o runner.

Nenhuma relação individual é inferida sem chave compartilhada.

### 5.4 Publicação transacional

- staging criado no mesmo volume dos destinos;
- JSON estrito, sem `NaN` ou `Infinity`;
- contratos validados antes da publicação;
- substituição atômica dos dois JSONs e sete PNGs;
- rollback testado com falha injetada durante a publicação;
- execução duplicada de questão gera diagnóstico controlado.

### 5.5 KPIs corrigidos

| KPI | Resultado principal | Situação semântica |
|---|---|---|
| KPI-01 | 362 pesquisas em 51 meses; cobertura 98,9071% | descritivo |
| KPI-02 | 366 pesquisas; 332 finalizadas (90,7104%) | descritivo |
| KPI-03 | média 6,5486%; mediana 6,6752%; 366 pesquisas e 40 zeros | cobertura cadastral, não adesão oficial |
| KPI-04 | 6.987/331 = 21,1088 dias úteis | proxy, não SLA oficial |
| KPI-05 | 18.680 participações; média 51,0383; 366 pesquisas e 40 zeros | contagem, não taxa |
| KPI-06 | 39/39.713 = 0,0982% | diagnóstico com scorecards |

Detalhes materiais:

- KPI-03 usa somente pesquisa e empresa existentes nos respectivos cadastros;
- KPI-03 diferencia 18.680 linhas válidas de 18.671 pares pesquisa/empresa distintos;
- a cobertura técnica dos KPIs 03 e 05 é 99,7064%;
- KPI-04 tem sensibilidade para 329 pesquisas finalizadas, média 21,1489 dias úteis;
- KPI-06 mostra que 35/366 pesquisas são afetadas por ausência em campos críticos, evitando que a micro média oculte a concentração.

## 6. Outputs e contratos

Foram regenerados atomicamente:

- `docs/data/quality_report.json`;
- `docs/data/kpis_summary.json`;
- sete gráficos em `docs/images/`.

Os dois contratos usam `schema_version: 2.0` e possuem JSON Schemas em `docs/data/schemas/`.

Os JSONs são **internos e pseudonimizados**. Eles não contêm e-mails nem respostas individuais, mas mantêm mapas por identificador técnico e amostras de órfãos para auditoria. Por isso, não entram no pacote do site.

Volumetria reconciliada:

| Medida | Valor |
|---|---:|
| registros | 46.148 |
| colunas somadas | 75 |
| células | 347.115 |
| ausências físicas | 95.019 |
| completude global ponderada | 72,6261% |
| registros duplicados completos | 0 |

## 7. Testes e evidências

Validação do núcleo do MR 1 antes da camada de publicação:

- 56 testes aprovados;
- Python 3.12.10;
- cobertura total 93,46%;
- mínimo obrigatório 85%;
- snapshot real incluído;
- `mkdocs build --strict` aprovado;
- sete PNGs validados por existência, dimensões e variância visual;
- `git diff --check` aprovado.

Validação final integrada após o MR 2:

- 61 testes aprovados, incluindo o snapshot real;
- cinco testes específicos de publicação privada aprovados;
- cobertura total 91,11%;
- configuração YAML parseada;
- origem privada gerada com 11 arquivos aprovados;
- build privado estrito aprovado;
- privacy gate aprovado.

Comandos principais:

```powershell
$env:PARTNER_DATA_DIR = "<diretório privado da remessa>"
$env:PARTNER_SNAPSHOT_DATE = "2026-08-13"
python -m scripts.runners.run_full_analysis
python -m pytest --cov=scripts --cov-report=term-missing --cov-fail-under=85
python -m mkdocs build --strict
```

```powershell
python -m scripts.publication.prepare_private_site
python -m mkdocs build --strict --config-file mkdocs.private.yml --site-dir public
python -m scripts.publication.privacy_gate --site-dir public
```

## 8. Publicação privada

### 8.1 Arquitetura implementada

```text
docs/ e contratos internos
          |
          v
allowlist fechada
          |
          +-- relatório sem links para JSON interno
          +-- sete gráficos agregados
          +-- CSS e JavaScript necessários
          |
          v
.build/private-docs
          |
          v
MkDocs + privacy gate
          |
          v
public/
          |
          v
Cloudflare Pages + Cloudflare Access
```

Não existe senha no HTML ou JavaScript. A autenticação proposta usa identidades individuais autorizadas no Cloudflare Access, por One-time PIN ou provedor de identidade.

### 8.2 Conteúdo excluído

- dados CSV, XLSX, ZIP e `REFERENCE_MATERIAL`;
- documento de contexto;
- inventário técnico;
- SPEC, ADR e tasks internas;
- `STATUS_REPORT_ARTEFATO_3.md`;
- JSONs internos;
- mapas por pesquisa/empresa;
- amostras de IDs órfãos.

### 8.3 Gate de deploy

O deploy é manual, serializado e só aparece em `develop` quando a variável protegida `CLOUDFLARE_ACCESS_CONFIRMED=true` existir. Essa variável é uma confirmação operacional, não uma prova técnica.

Antes do primeiro deploy, é obrigatório:

1. criar o projeto Cloudflare Pages de Direct Upload sem publicar conteúdo;
2. proteger o domínio `*.pages.dev` e os previews com Cloudflare Access;
3. configurar uma política `Allow` somente para identidades autorizadas;
4. cadastrar no GitLab o token de escopo mínimo e o Account ID;
5. testar deslogado a página inicial e uma URL direta de imagem;
6. testar usuário sem associação e membro autorizado;
7. somente então criar a variável protegida e executar o job manual.

Enquanto isso não ocorrer, a publicação online permanece **NO-GO**. O pacote local está aprovado.

Referências: [Cloudflare Pages Direct Upload](https://developers.cloudflare.com/pages/get-started/direct-upload/), [Direct Upload com CI](https://developers.cloudflare.com/pages/how-to/use-direct-upload-with-continuous-integration/) e [proteção do `pages.dev` com Access](https://developers.cloudflare.com/pages/platform/known-issues/#enable-access-on-your-pagesdev-domain).

## 9. Pendências externas e limitações assumidas

| ID | Pendência | Fallback implementado | Bloqueia o quê |
|---|---|---|---|
| D1 | parceiro definir CSV ou XLSX canônico | CSV provisório + manifesto + teste de drift | automação de nova remessa |
| D2 | empresas convidadas/elegíveis por pesquisa | cobertura sobre cadastro | adesão oficial |
| D3 | campos, status e calendário do prazo | KPI-04 como proxy | SLA oficial |
| D4 | empresa correta nos 140 conflitos | preservar ambiguidade e usar empresa da participação no descritivo | indicador oficial refinado |
| D5 | Cloudflare Access configurado e validado | pacote local e deploy desativado | site online |
| D6 | regra institucional para pequenas células | site restrito e sem mapas por ID | eventual publicação mais ampla |

Também permanecem 17 âncoras quebradas preexistentes no documento de contexto. Esse arquivo não foi modificado, conforme decisão explícita do time; a correção deve ser tratada pelo responsável do artefato correspondente.

## 10. Commits e ordem de integração

### MR [!18](https://git.inteli.edu.br/graduacao/2026-2a/t13/g02/-/merge_requests/18) — `fix/a3-confiabilidade-integral`

1. `e8537a9` — semântica de ausência e respostas;
2. `a9d43f6` — universos e scorecards dos KPIs;
3. `0bf8453` — contratos v2 e publicação transacional;
4. `5ca9e96` — outputs, gráficos e documentação;
5. `c178afc` — CI sintética e snapshot privado;
6. `c098dac` — caráter interno/pseudonimizado dos contratos.

### MR [!19](https://git.inteli.edu.br/graduacao/2026-2a/t13/g02/-/merge_requests/19) — `security/a3-private-pages`

- commit funcional `0a5df4f` — allowlist, privacy gate, pacote privado e deploy protegido;
- commits documentais subsequentes — criação deste status report e registro dos links dos MRs.

Ordem obrigatória:

1. revisar e integrar o MR 1 em `develop`;
2. atualizar/rebasear o MR 2 contra a nova `develop`;
3. revisar e integrar o MR 2;
4. não executar o deploy até concluir o checklist administrativo.

## 11. Veredito final

O Artefato 3 está **matematicamente confiável, reproduzível e pronto para revisão de merge**. O código, os JSONs, os gráficos e o Markdown descrevem o mesmo snapshot e os mesmos universos.

O site está **tecnicamente empacotado e protegido contra publicação acidental de dados internos**, mas não deve ser colocado online antes de o Cloudflare Access ser habilitado e verificado em sessão anônima.

**Status acadêmico:** GO para revisão e merge do MR 1.  
**Status do pacote privado:** GO para revisão e merge do MR 2.  
**Status do deploy online:** NO-GO até a confirmação administrativa e os testes de autenticação.
