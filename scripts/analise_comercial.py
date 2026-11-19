
import pandas as pd

ARQUIVO = "data/raw/Base_Adega_Bom_Sabor_2026.xlsx"

produtos = pd.read_excel(ARQUIVO, sheet_name="Produtos")
estoque = pd.read_excel(ARQUIVO, sheet_name="Estoque")
compras = pd.read_excel(ARQUIVO, sheet_name="Compras")

# Integrar os dados comerciais e de estoque
analise = produtos.merge(
    estoque,
    on="produto_id",
    how="left"
)

# Resumir vendas por produto
vendas = compras.groupby("produto_id").agg(
    quantidade_vendida=("quantidade", "sum"),
    faturamento=("valor_total", "sum"),
    ultima_venda=("data_compra", "max"),
    quantidade_transacoes=("compra_id", "nunique")
).reset_index()

analise = analise.merge(
    vendas,
    on="produto_id",
    how="left"
)

# Produtos sem vendas registradas
analise["quantidade_vendida"] = (
    analise["quantidade_vendida"].fillna(0)
)

analise["faturamento"] = analise["faturamento"].fillna(0)

analise["quantidade_transacoes"] = (
    analise["quantidade_transacoes"].fillna(0)
)

# Data de referência: último dia do histórico
DATA_REFERENCIA = compras["data_compra"].max()

analise["dias_sem_venda"] = (
    DATA_REFERENCIA - analise["ultima_venda"]
).dt.days

print("\n========== RESUMO COMERCIAL ==========")

print("Total de produtos:", len(analise))

print(
    "Produtos sem vendas:",
    analise["ultima_venda"].isna().sum()
)

print(
    "Produtos inativos com vendas:",
    (
        (analise["ativo"] == "Não")
        & (analise["quantidade_vendida"] > 0)
    ).sum()
)

print("\n========== TOP 10 MAIS VENDIDOS ==========")

print(
    analise.nlargest(10, "quantidade_vendida")[
        ["produto_id", "nome_produto",
         "quantidade_vendida", "estoque_atual"]
    ].to_string(index=False)
)

print("\n========== 10 PRODUTOS COM MENOR VENDA ==========")

print(
    analise.nsmallest(10, "quantidade_vendida")[
        ["produto_id", "nome_produto",
         "quantidade_vendida", "estoque_atual"]
    ].to_string(index=False)
)

print("\n========== PRODUTOS ABAIXO DO MÍNIMO ==========")

print(
    analise[analise["estoque_atual"] < analise["estoque_minimo"]][
        ["produto_id", "nome_produto", "ativo",
         "quantidade_vendida", "estoque_atual",
         "estoque_minimo", "lead_time_dias"]
    ].to_string(index=False)
)

print("\n========== PRODUTOS ACIMA DO MÁXIMO ==========")

print(
    analise[analise["estoque_atual"] > analise["estoque_maximo"]][
        ["produto_id", "nome_produto",
         "quantidade_vendida", "estoque_atual",
         "estoque_maximo"]
    ].to_string(index=False)
)

print("\n========== FIM DA ANÁLISE ==========")
