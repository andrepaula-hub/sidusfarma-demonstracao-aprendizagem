"""Contratos centralizados das seis fontes quantitativas do parceiro."""

from __future__ import annotations


DATASET_FILES = {
    "clientes": "clientes.csv",
    "empresas": "empresas.csv",
    "pesquisas": "pesquisas.csv",
    "questoes": "questoes.csv",
    "respondentes": "respondentes.csv",
    "respostas": "respostas.csv",
}

REQUIRED_COLUMNS = {
    "clientes": ("id_cliente", "id_empresa", "cargo", "departamento", "e-mail"),
    "empresas": (
        "ID",
        "Nome Fantasia",
        "% de mercado",
        "Nacionalidade",
        "Associado",
        "Tipo de Associado",
        "Cidade",
        "Estado",
        "País",
    ),
    "pesquisas": (
        "id",
        "titulo",
        "status",
        "tipo",
        "area",
        "participantes",
        "part_mercado",
        "data_solicitacao",
        "data_aprov",
        "data_divulgacao",
        "data_limite",
        "prorrogada_ate",
        "data_entrega",
        "dias_uteis_para_entrega",
        "complexidade",
        "tipo de resposta",
        "tempo_preenchimento",
        "objetivos",
        "dia da semana de lançamento",
        "dias úteis aberta",
        "dias entre a solicitação e a divulgação",
        "dias para tabulação",
    ),
    "questoes": (
        "id_pergunta",
        "pesquisa_id",
        "pesquisa_titulo",
        "enunciado",
        "tipo",
        "qtd_alternativas",
        "alternativas",
        "linhas_matriz",
        "colunas_matriz",
        "confianca",
        "formato_arquivo",
        "col_origem",
        "observacoes",
    ),
    "respondentes": (
        "id_pesq",
        "hora_inicio",
        "hora_termino",
        "id_empresa",
        "market_share",
        "id_cliente",
    ),
    "respostas": (
        "id_resposta",
        "pesquisa_id",
        "id_pergunta",
        "respondent_id",
        "id_empresa",
        "alternativa",
        "linha_matriz",
        "coluna_matriz",
        "valor",
    ),
}

PRIMARY_KEYS = {
    "clientes": ["id_cliente"],
    "empresas": ["ID"],
    "pesquisas": ["id"],
    "questoes": ["id_pergunta"],
    "respondentes": ["id_pesq", "id_empresa", "id_cliente"],
    "respostas": ["id_resposta"],
}

RELATIONSHIPS = [
    {"child": "clientes.id_empresa", "parent": "empresas.ID"},
    {"child": "questoes.pesquisa_id", "parent": "pesquisas.id"},
    {"child": "respondentes.id_pesq", "parent": "pesquisas.id"},
    {"child": "respondentes.id_empresa", "parent": "empresas.ID"},
    {"child": "respondentes.id_cliente", "parent": "clientes.id_cliente"},
    {"child": "respostas.pesquisa_id", "parent": "pesquisas.id"},
    {"child": "respostas.id_pergunta", "parent": "questoes.id_pergunta"},
    {"child": "respostas.id_empresa", "parent": "empresas.ID"},
]

IDENTIFIER_COLUMNS = {
    "clientes": ("id_cliente", "id_empresa"),
    "empresas": ("ID",),
    "pesquisas": ("id",),
    "questoes": ("id_pergunta", "pesquisa_id"),
    "respondentes": ("id_pesq", "id_empresa", "id_cliente"),
    "respostas": (
        "id_resposta",
        "pesquisa_id",
        "id_pergunta",
        "respondent_id",
        "id_empresa",
    ),
}

DATE_COLUMNS = {
    "pesquisas": (
        "data_solicitacao",
        "data_aprov",
        "data_divulgacao",
        "data_limite",
        "prorrogada_ate",
        "data_entrega",
    ),
    "respondentes": ("hora_inicio", "hora_termino"),
}

PERCENTAGE_COLUMNS = {
    "empresas": ("% de mercado",),
    "pesquisas": ("part_mercado",),
    "respondentes": ("market_share",),
}

NUMERIC_COLUMNS = {
    "pesquisas": (
        "participantes",
        "dias_uteis_para_entrega",
        "tempo_preenchimento",
        "dia da semana de lançamento",
        "dias úteis aberta",
        "dias entre a solicitação e a divulgação",
        "dias para tabulação",
    ),
    "questoes": ("qtd_alternativas",),
}

CRITICAL_FIELDS = (
    "pesquisas.id",
    "pesquisas.status",
    "pesquisas.data_solicitacao",
    "pesquisas.dias_uteis_para_entrega",
    "empresas.ID",
    "respondentes.id_pesq",
    "respondentes.id_empresa",
)

# Cada tupla interna representa campos que precisam estar preenchidos em conjunto;
# uma resposta é válida quando satisfaz pelo menos uma das tuplas do seu tipo.
RESPONSE_REPRESENTATION_RULES = {
    "aberta": (("valor",),),
    "numerica": (("valor",),),
    "multipla_escolha": (("alternativa",), ("valor",)),
    "caixas_de_selecao": (("alternativa",),),
    "matriz_avaliacao": (
        ("linha_matriz", "coluna_matriz"),
        ("alternativa", "valor"),
    ),
}
