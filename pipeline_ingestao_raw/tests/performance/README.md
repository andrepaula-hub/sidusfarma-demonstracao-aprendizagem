# Performance e confiabilidade

O teste de carga não substitui a validação de dados. A qualidade desta entrega
é verificada em camadas: contrato, unidade, integração, execução real da DAG,
testes dbt, idempotência, falha controlada e telemetria.

Para verificar disponibilidade e tempo de resposta das interfaces, execute:

```bash
cd pipeline_ingestao_raw
docker compose --profile performance run --rm k6
```

O gate falha se mais de 1% das requisições falhar ou se o percentil 95 exceder
1,5 s. Para carga de dados em produção, o padrão é definir volume-alvo, SLO de
latência/throughput, orçamento de erro e dados sintéticos representativos; não
é aceitável usar dados pessoais reais como massa de estresse.
