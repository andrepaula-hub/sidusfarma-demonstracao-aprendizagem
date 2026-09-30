# G02 — Central de Pesquisas do Sindusfarma

Projeto acadêmico desenvolvido para compreender e apoiar o processo analítico
da Central de Pesquisas do Sindusfarma. A documentação navegável é construída
com MkDocs, e o Artefato 3 possui um pipeline Python reproduzível para
qualidade, estatística descritiva, indicadores e gráficos agregados.

## Estrutura principal

- `docs/`: documentação, resultados agregados e imagens publicáveis;
- `scripts/data_quality/`: schema, ingestão, normalização e auditoria;
- `scripts/metrics/`: estatística descritiva e KPIs;
- `scripts/visualization/`: gráficos agregados;
- `scripts/runners/`: orquestração e publicação transacional;
- `tests/`: contratos sintéticos e regressão opcional da remessa real.

Para a entrega atual de ETL, a decisão de arquitetura e o mapa de cobertura
dos requisitos estão em [Referência de artefatos atuais — Sprint 3](docs/referencia_artefatos_atuais_sprint_3.md).

Os CSVs recebidos do parceiro não são versionados. O diretório local deve
conter `clientes.csv`, `empresas.csv`, `pesquisas.csv`, `questoes.csv`,
`respondentes.csv` e `respostas.csv`.

## Preparação

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-test.txt
.\.venv\Scripts\python.exe -m pip install -r requirements-docs.txt
```

## Executar a análise

```powershell
.\.venv\Scripts\python.exe -m scripts.runners.run_full_analysis `
  --source-dir "C:\caminho\protegido\para\Dados"
```

O comando atualiza `docs/data/quality_report.json`,
`docs/data/kpis_summary.json` e os sete gráficos de `docs/images/`. A entrada
não é alterada, e uma falha não substitui resultados publicados anteriormente.

Também é possível definir `PARTNER_DATA_DIR` e omitir `--source-dir`.

## Validar

```powershell
.\.venv\Scripts\python.exe -m pytest
$env:PARTNER_DATA_DIR = "C:\caminho\protegido\para\Dados"
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m mkdocs build --strict
```

Para visualizar a documentação durante a edição:

```powershell
.\.venv\Scripts\python.exe -m mkdocs serve
```
