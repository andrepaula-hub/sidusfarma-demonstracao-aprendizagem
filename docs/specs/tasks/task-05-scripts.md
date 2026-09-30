# Especificação de Tarefa: TASK-05 — Scripts & Gerador de Métricas (TDD Green)

## 1. Visão Geral
- **ID**: TASK-05
- **Componente**: Processamento e Visualização de Dados
- **Responsável**: André Lobo
- **Tipo**: Feature / Code

## 2. Abordagem Técnica
- Schema único para as seis fontes, com ingestão configurável e validação
  antecipada de arquivos e colunas.
- Normalização imutável de identificadores, datas, percentuais e variáveis
  numéricas, com erros de parsing contabilizados.
- Módulos puros para qualidade, integridade referencial, estatística descritiva,
  outliers, seis KPIs mínimos e comparação de granularidades.
- Runner transacional para JSON estrito e sete gráficos agregados, sem caminhos
  pessoais ou valores identificáveis nas saídas.
- Dependências declaradas em `requirements-analysis.txt` e execução por
  `python -m scripts.runners.run_full_analysis`.

## 3. Definition of Done (DoD)
- [x] Dois contratos JSON e sete gráficos estatísticos gerados com sucesso.
- [x] Todos os 36 testes sintéticos da TASK-04 aprovados.
- [x] Dois testes de regressão aprovados sobre a remessa real protegida.
- [x] Volumes e oito relações reconciliados com o inventário das bases.
- [x] Cobertura automatizada superior a 85% nos módulos de `scripts/`.
- [x] Build estrito da documentação concluído.
