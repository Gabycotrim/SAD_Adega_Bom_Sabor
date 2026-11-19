
import pandas as pd

ARQUIVO = "data/raw/Base_Adega_Bom_Sabor_2026.xlsx"

# Carregar as tabelas
clientes = pd.read_excel(ARQUIVO, sheet_name="Clientes")
produtos = pd.read_excel(ARQUIVO, sheet_name="Produtos")
estoque = pd.read_excel(ARQUIVO, sheet_name="Estoque")
compras = pd.read_excel(ARQUIVO, sheet_name="Compras")

print("\n========== 1. CLIENTES ==========")

print("\nStatus do clube:")
print(clientes["status_clube"].value_counts(dropna=False))

print("\nClientes sem data de adesão:")
print(clientes["data_adesao_clube"].isna().sum())

print("\nClientes com data de cancelamento:")
print(clientes["data_cancelamento_clube"].notna().sum())


print("\n========== 2. PRODUTOS ==========")

# Duas formas possíveis de calcular margem
produtos["margem_sobre_venda"] = (
    (produtos["preco_venda"] - produtos["custo_unitario"])
    / produtos["preco_venda"] * 100
)

produtos["markup_sobre_custo"] = (
    (produtos["preco_venda"] - produtos["custo_unitario"])
    / produtos["custo_unitario"] * 100
)

print("\nMargens cadastradas e recalculadas:")
print(
    produtos[
        [
            "produto_id",
            "margem_pct",
            "margem_sobre_venda",
            "markup_sobre_custo"
        ]
    ].head(10).round(2).to_string(index=False)
)

print("\nSituação dos produtos:")
print(produtos["ativo"].value_counts(dropna=False))


print("\n========== 3. ESTOQUE ==========")

estoque_analise = estoque.merge(
    produtos[["produto_id", "custo_unitario"]],
    on="produto_id",
    how="left"
)

estoque_analise["valor_calculado"] = (
    estoque_analise["estoque_atual"]
    * estoque_analise["custo_unitario"]
)

estoque_analise["diferenca_valor"] = (
    estoque_analise["valor_estoque_custo"]
    - estoque_analise["valor_calculado"]
)

print("\nProdutos com estoque atual abaixo do mínimo:",
      (estoque["estoque_atual"] < estoque["estoque_minimo"]).sum())

print("Produtos acima do estoque máximo:",
      (estoque["estoque_atual"] > estoque["estoque_maximo"]).sum())

print("Estoques negativos:",
      (estoque["estoque_atual"] < 0).sum())

print("\nDiferenças no valor financeiro do estoque:",
      (estoque_analise["diferenca_valor"].abs() > 0.01).sum())


print("\n========== 4. COMPRAS ==========")

# Conferência do preço unitário após desconto
compras["preco_calculado"] = (
    compras["preco_tabela"]
    * (1 - compras["desconto_pct"] / 100)
)

compras["total_calculado"] = (
    compras["quantidade"] * compras["preco_unitario"]
)

print("\nDiferenças no preço unitário:",
      (
          (compras["preco_unitario"] -
           compras["preco_calculado"]).abs() > 0.02
      ).sum())

print("Diferenças no valor total:",
      (
          (compras["valor_total"] -
           compras["total_calculado"]).abs() > 0.02
      ).sum())

print("\nCanais de venda:")
print(compras["canal"].value_counts(dropna=False))

print("\nFormas de pagamento:")
print(compras["forma_pagamento"].value_counts(dropna=False))

print("\nQuantidade de produtos vendidos:")
print(compras["quantidade"].describe())

print("\n========== FIM DA VERIFICAÇÃO ==========")
