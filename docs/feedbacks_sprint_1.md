# Feedbacks da Sprint 1

Registro consolidado dos feedbacks recebidos para os artefatos da Sprint 1.

## Resultado individual

O fator de performance da Sprint 1 foi **0,40** para os três artefatos.

| Componente | Nota | Peso | Observação |
|---|---:|---:|---|
| Demonstração de Aprendizagem | 0,00 | 60% | Nota pendente de ajuste após a correção da demonstração em papel. |
| Repositório | 10,00 | 20% | Não avaliado nesta sprint; relatório fornecido para ciência e providências futuras. |
| KANBAN | 10,00 | 20% | Não avaliado nesta sprint; relatório fornecido para ciência e providências futuras. |

**Cálculo:** 0,00 × 60% + 10,00 × 20% + 10,00 × 20% = **0,40**.

As questões 1, 2 e 3 da Demonstração de Aprendizagem ficaram, provisoriamente, com nota 0,00, sujeita à revisão após a correção em papel.

## 1. Contexto organizacional e requisitos da solução analítica

### Pontos positivos

- Entrega completa, organizada e sem lacunas estruturais; as seis seções e subseções foram apresentadas na ordem solicitada.
- Os indicadores da seção 5.2 estão bem especificados, com objetivo, significado para o negócio, granularidade, dimensões de segmentação e regra de cálculo em pseudocódigo.
- O denominador da taxa de adesão foi explicitado, reduzindo ambiguidades; a regra de pesquisa atrasada também foi definida de forma verificável.
- Os três dashboards possuem wireframes versionados e referenciados no repositório:
  - `docs/img/wireframe_painel_operacional.png`
  - `docs/img/wireframe_painel_estrategico.png`
  - `docs/img/wireframe_portal_acervo_publico.png`
- A escolha dos visuais foi justificada de forma consistente. O Dashboard 3 foi corretamente caracterizado como catálogo consultável, e não como painel analítico estrito.
- A matriz RF ↔ PN ↔ Dashboard cobre os seis requisitos funcionais e inclui verificações explícitas de cobertura nos dois sentidos.
- Os seis RF e seis RNF seguem o formato exigido, cobrindo sete das oito características da ISO 25010.
- A matriz de Papéis e Controles da seção 3.5 organiza adequadamente as responsabilidades.

### Limitações apontadas

- A análise está bem estruturada, mas pouco ancorada em evidências do inventário e da especificação quantitativa existentes no repositório. A seção 3.4 descreve problemas de qualidade em termos gerais, sem apresentar as contagens já apuradas.
- O escopo de seis RF, nove perguntas de negócio e três dashboards é mais estreito que o problema descrito, que também envolve representatividade de mercado, resultados e qualidade dos dados.

### Melhorias recomendadas

1. Incorporar à seção 3.4 os achados do inventário e da especificação quantitativa, informando contagens e percentuais por base e campo.
2. Amarrar os critérios de aceitação aos achados de qualidade, incluindo condições verificáveis sobre duplicidades e demais inconsistências.
3. Exibir permanentemente nos dashboards a cobertura do dado de respostas, evitando que os resultados sejam interpretados como retrato de todo o acervo.
4. Ampliar os requisitos funcionais para contemplar representatividade de mercado e tratamento por tipo de questão.

## 2. Data Model Canvas

### Pontos positivos

- O `docs/dmc.json` é válido, bem-formado e possui as três seções corporativas preenchidas.
- O recorte solicitado para as subseções de governança dos cubos foi respeitado.
- Os três cubos são coerentes com os dashboards do Artefato 1 e cobrem processos principais com tipos de fato adequados:

| Cubo | Tipo de fato | Avaliação |
|---|---|---|
| Ciclo de Vida da Pesquisa | Accumulating Snapshot | Adequado para marcos preenchidos ao longo do ciclo. |
| Adesão e Participação | Transaction Fact | Adequado para eventos discretos de participação. |
| Qualidade dos Dados das Pesquisas | Periodic Snapshot | Adequado para medições periódicas. |

- O cubo de Ciclo de Vida da Pesquisa é o mais desenvolvido, com nove fatos/eventos e dez métricas.

### Limitações apontadas

- O grão dos três cubos está subespecificado. Uma única sentença não fixa suficientemente o que uma linha representa nem quais medidas podem ser somadas, especialmente quando há várias datas e status.
- O domínio de resultados/respostas não está modelado, embora o Dashboard 3 seja o Portal do Acervo. Isso deixa uma lacuna de cobertura entre o dashboard e o modelo dimensional.

### Melhorias recomendadas

1. Reescrever o grão de cada cubo em duas ou três sentenças, explicitando o que uma linha representa e qual chave a identifica.
2. Completar as dimensões conformadas, declarando as dimensões compartilhadas entre os cubos, no mínimo `dim_tempo` e `dim_empresa`.
3. Modelar o domínio de resultados/respostas em uma estrutura com grão claro e consistente, dando lastro dimensional ao Dashboard 3.

## 3. Modelagem quantitativa dos dados do parceiro

### Pontos positivos

- Bom domínio da estrutura quantitativa das bases.
- Variáveis bem definidas e análise consistente de completude, duplicidade, integridade e estatística descritiva.
- Indicadores documentados quanto a fórmulas, universos, cobertura e limitações.
- Destaque para a análise de granularidade, a distinção entre cobertura cadastral e taxa de adesão, a análise de Pareto e as verificações automatizadas por scripts.

### Melhoria recomendada

- Preservar nos dashboards os denominadores, as coberturas e os filtros definidos no relatório, evitando que indicadores agregados ocultem problemas específicos em campos ou entidades.

## Próximas ações consolidadas

- [ ] Enriquecer a seção de qualidade de dados do contexto com evidências quantitativas do inventário.
- [ ] Revisar critérios de aceitação com base nos achados de qualidade.
- [ ] Tornar a cobertura dos dados visível nos dashboards.
- [ ] Ampliar RFs para representatividade de mercado e tipos de questão.
- [ ] Detalhar o grão e as chaves dos três cubos.
- [ ] Declarar dimensões conformadas compartilhadas.
- [ ] Modelar resultados/respostas para suportar o Portal do Acervo.
- [ ] Manter denominadores, coberturas e filtros do relatório nos dashboards.

