# Testes da modelagem quantitativa

Esta suíte formaliza os contratos definidos em
`docs/specs/spec-analise-quantitativa-dados.md`. Ela usa apenas dados sintéticos
versionáveis e não depende dos arquivos confidenciais do parceiro para a
execução padrão.

## Execução

No Windows/PowerShell, a partir da raiz do repositório:

```powershell
python -m pip install -r requirements-test.txt
python -m pytest -m "not integration"
```

Para verificar opcionalmente o snapshot local dos seis CSVs do parceiro:

```powershell
$env:PARTNER_DATA_DIR = "C:\caminho\para\Dados"
$env:PARTNER_SNAPSHOT_DATE = "2026-08-13"
python -m pytest -m integration
```

O teste de integração é ignorado quando `PARTNER_DATA_DIR` não está definido.
Ele confere somente métricas agregadas já registradas na especificação, além
do drift conhecido entre CSV e XLSX (uma chave adicional em `clientes.csv` e
72 valores divergentes em `respostas.valor`). Nenhum registro individual é
publicado pelo teste.

## Estado TDD

A suíte está na fase **Green**: os contratos sintéticos e os schemas JSON v2
são executados em todo commit. O job privado de integração acrescenta a
reconciliação dos volumes, relações, representações de respostas, KPIs e drift
da remessa real, sem publicar seus registros.
