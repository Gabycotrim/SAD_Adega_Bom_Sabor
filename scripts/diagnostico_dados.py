
import pandas as pd

ARQUIVO = "data/raw/Base_Adega_Bom_Sabor_2026.xlsx"

tabelas = ["Clientes", "Produtos", "Estoque", "Compras"]

for nome in tabelas:
    df = pd.read_excel(ARQUIVO, sheet_name=nome)

    print("\n" + "=" * 50)
    print(f"DIAGNÓSTICO: {nome}")
    print("=" * 50)

    print(f"\nQuantidade de registros: {len(df)}")
    print(f"Quantidade de colunas: {len(df.columns)}")

    print("\nDuplicados por linha:", df.duplicated().sum())

    print("\nValores ausentes por coluna:")
    print(df.isna().sum().to_string())

    print("\nTipos de dados:")
    print(df.dtypes.to_string())
