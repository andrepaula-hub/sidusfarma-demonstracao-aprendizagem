from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_dbt_documentation_and_orphan_policy_are_declared():
    readme = (ROOT / "README.md").read_text()
    schema = (ROOT / "dbt/models/schema.yml").read_text()
    assert "dbt Docs" in readme
    assert "quarantine_registros_orfaos" in schema


def test_all_contract_datasets_have_a_staging_model():
    datasets = ("clientes", "empresas", "pesquisas", "questoes", "respondentes", "respostas")
    for dataset in datasets:
        assert (ROOT / "dbt/models/staging" / f"stg_{dataset}.sql").exists()
