
import pandas as pd

ARQUIVO = "data/raw/Base_Adega_Bom_Sabor_2026.xlsx"

produtos = pd.read_excel(ARQUIVO, sheet_name="Produtos")
estoque = pd.read_excel(ARQUIVO, sheet_name="Estoque")
compras = pd.read_excel(ARQUIVO, sheet_name="Compras")

ids = [61, 90, 134, 144]

data_ref = compras["data_compra"].max()

resultado = []

for produto_id in ids:
    p = produtos[produtos["produto_id"] == produto_id].iloc[0]
    e = estoque[estoque["produto_id"] == produto_id].iloc[0]

    vendas = compras[compras["produto_id"] == produto_id]

    def total_vendido(dias):
        inicio = data_ref - pd.Timedelta(
            value=dias - 1, unit="D"
        )
        return vendas[
            (vendas["data_compra"] >= inicio)
            & (vendas["data_compra"] <= data_ref)
        ]["quantidade"].sum()

    resultado.append({
        "produto_id": produto_id,
        "nome": p["nome_produto"],
        "ativo": p["ativo"],
        "vendas_30d": total_vendido(30),
        "vendas_60d": total_vendido(60),
        "vendas_90d": total_vendido(90),
        "estoque": e["estoque_atual"],
        "minimo": e["estoque_minimo"],
        "maximo": e["estoque_maximo"],
        "prazo_reposicao": e["lead_time_dias"],
        "margem_pct": p["margem_pct"]
    })

df = pd.DataFrame(resultado)

print("\nANÁLISE DETALHADA DOS PRODUTOS EM RISCO")
print(df.to_string(index=False))
