
import pandas as pd

ARQUIVO = "data/raw/Base_Adega_Bom_Sabor_2026.xlsx"

# Carregar dados
produtos = pd.read_excel(ARQUIVO, sheet_name="Produtos")
estoque = pd.read_excel(ARQUIVO, sheet_name="Estoque")
compras = pd.read_excel(ARQUIVO, sheet_name="Compras")

# Data de referência: último dia disponível na base
data_referencia = compras["data_compra"].max()

print("Data de referência:", data_referencia.date())

# Criar períodos de análise
for dias in [30, 60, 90]:
    inicio = data_referencia - pd.Timedelta(
    value=int(dias - 1),
    unit="D"
    )

    periodo = compras[
        (compras["data_compra"] >= inicio)
        & (compras["data_compra"] <= data_referencia)
    ]

    vendas_periodo = (
        periodo.groupby("produto_id")["quantidade"]
        .sum()
        .rename(f"vendas_{dias}d")
    )

    produtos = produtos.merge(
        vendas_periodo,
        on="produto_id",
        how="left"
    )

    produtos[f"vendas_{dias}d"] = (
        produtos[f"vendas_{dias}d"].fillna(0).astype(int)
    )

# Integrar estoque
analise = produtos.merge(
    estoque,
    on="produto_id",
    how="left"
)

# Média diária considerando os últimos 90 dias
analise["media_diaria_90d"] = (
    analise["vendas_90d"] / 90
)

# Cobertura estimada
analise["cobertura_dias"] = (
    analise["estoque_atual"]
    / analise["media_diaria_90d"].replace(0, float("nan"))
)

# Identificar última venda de cada produto
ultima_venda = (
    compras.groupby("produto_id")["data_compra"]
    .max()
)

analise = analise.merge(
    ultima_venda.rename("ultima_venda"),
    on="produto_id",
    how="left"
)

analise["dias_sem_venda"] = (
    data_referencia - analise["ultima_venda"]
).dt.days

# Mostrar resultados
print("\n========== RESUMO DAS VENDAS ==========")

print("Vendas nos últimos 30 dias:",
      analise["vendas_30d"].sum())

print("Vendas nos últimos 60 dias:",
      analise["vendas_60d"].sum())

print("Vendas nos últimos 90 dias:",
      analise["vendas_90d"].sum())

print("\n========== MAIOR DEMANDA RECENTE ==========")

print(
    analise.nlargest(10, "vendas_90d")[
        ["produto_id", "nome_produto",
         "vendas_30d", "vendas_60d", "vendas_90d",
         "estoque_atual", "lead_time_dias",
         "cobertura_dias"]
    ].round(2).to_string(index=False)
)

print("\n========== PRODUTOS SEM VENDA NOS ÚLTIMOS 90 DIAS ==========")

print(
    analise[analise["vendas_90d"] == 0][
        ["produto_id", "nome_produto", "ativo",
         "estoque_atual", "estoque_maximo",
         "dias_sem_venda"]
    ].to_string(index=False)
)

print("\n========== PRODUTOS COM RISCO DE RUPTURA ==========")

risco = analise[
    (analise["vendas_90d"] > 0)
    & (
        analise["cobertura_dias"]
        <= analise["lead_time_dias"]
    )
]

print(
    risco[
        ["produto_id", "nome_produto",
         "vendas_90d", "estoque_atual",
         "lead_time_dias", "cobertura_dias"]
    ].round(2).to_string(index=False)
)

# Salvar resultado para futuras etapas
analise.to_csv(
    "data/processed/analise_temporal.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nArquivo salvo: data/processed/analise_temporal.csv")
