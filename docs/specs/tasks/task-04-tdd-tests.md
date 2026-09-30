# Especificação de Tarefa: TASK-04 — Testes Automatizados da Pipeline (TDD Red)

## 1. Visão Geral
- **ID**: TASK-04
- **Componente**: Testes Automatizados
- **Responsável**: André Lobo
- **Tipo**: Test

## 2. Abordagem Técnica
- Implementação de suíte Pytest modular em `tests/`, separada por ingestão,
  qualidade, estatística descritiva, indicadores e fluxo completo.
- Fixtures sintéticas representativas das seis fontes, sem versionar dados do
  parceiro.
- Regressão opcional do snapshot real por `PARTNER_DATA_DIR`, limitada a
  métricas agregadas documentadas.
- Asserções para schemas, parsing, integridade referencial, fórmulas,
  granularidade, privacidade, determinismo e publicação atômica.

## 3. Definition of Done (DoD)
- [x] Suíte modular implementada com asserções rigorosas e dados sintéticos.
- [x] Dependências e configuração do Pytest declaradas.
- [x] Coleta dos testes validada sem erros de sintaxe ou importação.
- [x] Fase TDD Red validada com falhas acionáveis para os módulos ainda
  pendentes da TASK-05.
- [x] Suíte integral em estado Green após a implementação da TASK-05.
