
import pandas as pd

ARQUIVO = "data/raw/Base_Adega_Bom_Sabor_2026.xlsx"

produtos = pd.read_excel(ARQUIVO, sheet_name="Produtos")
compras = pd.read_excel(ARQUIVO, sheet_name="Compras")

data_ref = compras["data_compra"].max()

inicio_recente = data_ref - pd.Timedelta(value=29, unit="D")
inicio_anterior = data_ref - pd.Timedelta(value=59, unit="D")

periodo_recente = compras[
    compras["data_compra"] >= inicio_recente
]

periodo_anterior = compras[
    (compras["data_compra"] >= inicio_anterior)
    & (compras["data_compra"] < inicio_recente)
]

recente = periodo_recente.groupby(
    "produto_id"
)["quantidade"].sum()

anterior = periodo_anterior.groupby(
    "produto_id"
)["quantidade"].sum()

analise = produtos[["produto_id", "nome_produto", "ativo"]].copy()

analise["vendas_30d"] = (
    analise["produto_id"].map(recente).fillna(0)
)

analise["vendas_30d_anterior"] = (
    analise["produto_id"].map(anterior).fillna(0)
)

def classificar_tendencia(linha):
    atual = linha["vendas_30d"]
    anterior = linha["vendas_30d_anterior"]

    if atual == 0 and anterior == 0:
        return "Sem vendas nos dois períodos"

    if atual == 0:
        return "Sem vendas recentes"

    if anterior == 0:
        return "Demanda iniciada ou retomada"

    variacao = (atual - anterior) / anterior * 100

    if variacao >= 20:
        return "Crescente"
    elif variacao <= -20:
        return "Decrescente"
    else:
        return "Estável"

analise["tendencia"] = analise.apply(
    classificar_tendencia,
    axis=1
)

print("\n========== TENDÊNCIA DE VENDAS ==========")

print(
    analise["tendencia"]
    .value_counts()
    .to_string()
)

print("\n========== PRODUTOS COM TENDÊNCIA ==========")

print(
    analise[
        analise["produto_id"].isin([61, 90, 134, 144])
    ].to_string(index=False)
)

print("\n========== PRODUTOS COM QUEDA ==========")

print(
    analise[
        analise["tendencia"] == "Decrescente"
    ][
        ["produto_id", "nome_produto",
         "vendas_30d_anterior", "vendas_30d"]
    ].to_string(index=False)
)
