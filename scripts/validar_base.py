from pathlib import Path
import pandas as pd

ARQUIVO = Path(__file__).resolve().parents[1] / "data" / "raw" / "Base_Adega_Bom_Sabor_2026.xlsx"
ABAS_ESPERADAS = {"Dicionario", "Clientes", "Produtos", "Estoque", "Compras"}

def main():
    if not ARQUIVO.exists():
        raise FileNotFoundError(
            f"Planilha não encontrada: {ARQUIVO}\n"
            "Coloque Base_Adega_Bom_Sabor_2026.xlsx em data/raw."
        )

    xls = pd.ExcelFile(ARQUIVO)
    print("=" * 72)
    print("VALIDAÇÃO INICIAL — BASE ADEGA BOM SABOR")
    print(f"Arquivo: {ARQUIVO}")
    print("=" * 72)

    faltantes = ABAS_ESPERADAS - set(xls.sheet_names)
    extras = set(xls.sheet_names) - ABAS_ESPERADAS
    print(f"\nAbas encontradas: {xls.sheet_names}")
    print(f"Abas esperadas ausentes: {sorted(faltantes) if faltantes else 'Nenhuma'}")
    print(f"Abas adicionais: {sorted(extras) if extras else 'Nenhuma'}")

    dados = {}
    for aba in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=aba)
        dados[aba] = df
        print(f"\n--- {aba} ---")
        print(f"Linhas: {len(df)} | Colunas: {len(df.columns)}")
        print("Colunas:", ", ".join(map(str, df.columns)))
        print("Valores ausentes por coluna:")
        ausentes = df.isna().sum()
        ausentes = ausentes[ausentes > 0]
        print(ausentes.to_string() if not ausentes.empty else "Nenhum valor ausente.")
        duplicadas = int(df.duplicated().sum())
        print(f"Linhas totalmente duplicadas: {duplicadas}")

    # Verificações de chaves e relacionamentos
    print("\n--- RELACIONAMENTOS ---")
    checks = [
        ("Clientes.cliente_id", "Clientes", "cliente_id"),
        ("Produtos.produto_id", "Produtos", "produto_id"),
    ]
    for label, aba, coluna in checks:
        df = dados[aba]
        if coluna in df:
            print(f"{label}: duplicados={int(df[coluna].duplicated().sum())}; nulos={int(df[coluna].isna().sum())}")

    if {"Produtos", "Estoque"} <= dados.keys():
        produtos = set(dados["Produtos"]["produto_id"].dropna())
        estoque = set(dados["Estoque"]["produto_id"].dropna())
        print(f"Produtos sem registro de estoque: {len(produtos - estoque)}")
        print(f"Registros de estoque sem produto correspondente: {len(estoque - produtos)}")

    if "Compras" in dados:
        compras = dados["Compras"]
        if "produto_id" in compras and "Produtos" in dados:
            ids_produtos = set(dados["Produtos"]["produto_id"].dropna())
            ids_compras = set(compras["produto_id"].dropna())
            print(f"Compras com produto_id sem correspondência: {len(ids_compras - ids_produtos)}")
        if "cliente_id" in compras and "Clientes" in dados:
            ids_clientes = set(dados["Clientes"]["cliente_id"].dropna())
            ids_compras_clientes = set(compras["cliente_id"].dropna())
            print(f"Compras com cliente_id sem correspondência: {len(ids_compras_clientes - ids_clientes)}")
        if "data_compra" in compras:
            datas = pd.to_datetime(compras["data_compra"], errors="coerce")
            print(f"Datas de compra inválidas/ausentes: {int(datas.isna().sum())}")
            if datas.notna().any():
                print(f"Período das compras: {datas.min().date()} a {datas.max().date()}")

    print("\nVALIDAÇÃO CONCLUÍDA.")
    print("Atenção: valores ausentes/duplicados precisam ser interpretados por campo; nem todo nulo é erro.")
    print("Não foram alterados os dados originais.")

if __name__ == "__main__":
    main()
