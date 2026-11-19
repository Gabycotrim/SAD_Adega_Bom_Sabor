
from pathlib import Path
import pandas as pd


# ==========================================================
# 1. CONFIGURAÇÕES
# ==========================================================

BASE_DIR = Path(__file__).resolve().parents[1]

ARQUIVO_EXCEL = (
    BASE_DIR / "data" / "raw" /
    "Base_Adega_Bom_Sabor_2026.xlsx"
)

PASTA_SAIDA = BASE_DIR / "data" / "processed"

ARQUIVO_SAIDA = (
    PASTA_SAIDA / "recomendacoes_produtos.csv"
)


# ==========================================================
# 2. CARREGAMENTO DOS DADOS
# ==========================================================

print("\nCARREGANDO DADOS...")

produtos = pd.read_excel(
    ARQUIVO_EXCEL,
    sheet_name="Produtos"
)

estoque = pd.read_excel(
    ARQUIVO_EXCEL,
    sheet_name="Estoque"
)

compras = pd.read_excel(
    ARQUIVO_EXCEL,
    sheet_name="Compras"
)

compras["data_compra"] = pd.to_datetime(
    compras["data_compra"]
)

data_referencia = compras["data_compra"].max()

print(f"Data de referência das vendas: {data_referencia.date()}")


# ==========================================================
# 3. CÁLCULO DAS VENDAS POR PRODUTO
# ==========================================================

inicio_30 = data_referencia - pd.Timedelta(value=29, unit="D")
inicio_60 = data_referencia - pd.Timedelta(value=59, unit="D")
inicio_90 = data_referencia - pd.Timedelta(value=89, unit="D")

vendas_30 = (
    compras[compras["data_compra"] >= inicio_30]
    .groupby("produto_id")["quantidade"]
    .sum()
)

vendas_60 = (
    compras[compras["data_compra"] >= inicio_60]
    .groupby("produto_id")["quantidade"]
    .sum()
)

vendas_90 = (
    compras[compras["data_compra"] >= inicio_90]
    .groupby("produto_id")["quantidade"]
    .sum()
)

vendas_anteriores = (
    compras[
        (compras["data_compra"] >= inicio_60) &
        (compras["data_compra"] < inicio_30)
    ]
    .groupby("produto_id")["quantidade"]
    .sum()
)


# ==========================================================
# 4. INTEGRAÇÃO DOS DADOS
# ==========================================================

dados = (
    produtos
    .merge(estoque, on="produto_id", how="left")
)

dados["vendas_30d"] = (
    dados["produto_id"].map(vendas_30).fillna(0)
)

dados["vendas_60d"] = (
    dados["produto_id"].map(vendas_60).fillna(0)
)

dados["vendas_90d"] = (
    dados["produto_id"].map(vendas_90).fillna(0)
)

dados["vendas_30d_anteriores"] = (
    dados["produto_id"].map(vendas_anteriores).fillna(0)
)


# ==========================================================
# 5. INDICADORES DE DEMANDA E ESTOQUE
# ==========================================================

dados["media_diaria_90d"] = (
    dados["vendas_90d"] / 90
)

dados["cobertura_dias"] = (
    dados["estoque_atual"] /
    dados["media_diaria_90d"].replace(0, pd.NA)
)

dados["dias_ate_reposicao"] = dados["lead_time_dias"]

dados["gap_ate_estoque_maximo"] = (
    dados["estoque_maximo"] - dados["estoque_atual"]
).clip(lower=0)


# ==========================================================
# 6. CLASSIFICAÇÃO DO ESTOQUE
# ==========================================================

def classificar_estoque(linha):

    if linha["estoque_atual"] < linha["estoque_minimo"]:
        return "Abaixo do mínimo"

    if linha["estoque_atual"] > linha["estoque_maximo"]:
        return "Acima do máximo"

    return "Dentro da faixa"


dados["situacao_estoque"] = dados.apply(
    classificar_estoque,
    axis=1
)


# ==========================================================
# 7. CLASSIFICAÇÃO DA TENDÊNCIA
# ==========================================================

def classificar_tendencia(linha):

    recente = linha["vendas_30d"]
    anterior = linha["vendas_30d_anteriores"]

    total = recente + anterior

    if total == 0:
        return "Sem vendas nos dois períodos"

    if total < 5:
        return "Volume insuficiente para tendência"

    if anterior == 0 and recente > 0:
        return "Demanda iniciada ou retomada"

    if recente == 0:
        return "Sem vendas recentes"

    variacao = (recente - anterior) / anterior

    if variacao >= 0.20:
        return "Crescente"

    if variacao <= -0.20:
        return "Decrescente"

    return "Estável"


dados["tendencia_demanda"] = dados.apply(
    classificar_tendencia,
    axis=1
)


# ==========================================================
# 8. IDENTIFICAÇÃO DO RISCO DE RUPTURA
# ==========================================================

def avaliar_risco(linha):

    if linha["vendas_90d"] == 0:
        return "Sem demanda observada"

    if linha["cobertura_dias"] <= linha["lead_time_dias"]:
        return "Alto"

    return "Baixo"


dados["risco_ruptura"] = dados.apply(
    avaliar_risco,
    axis=1
)


# ==========================================================
# 9. MECANISMO DE DECISÃO
# ==========================================================



def gerar_recomendacao(linha):

    ativo = str(linha["ativo"]).strip().lower()

    estoque_atual = linha["estoque_atual"]
    estoque_minimo = linha["estoque_minimo"]
    estoque_maximo = linha["estoque_maximo"]

    vendas_30 = linha["vendas_30d"]
    vendas_anteriores = linha["vendas_30d_anteriores"]
    vendas_90 = linha["vendas_90d"]

    risco = linha["risco_ruptura"]
    cobertura = linha["cobertura_dias"]
    prazo = linha["lead_time_dias"]
    tendencia = linha["tendencia_demanda"]
    margem = linha["margem_pct"]

    # Regra 1: produto inativo
    if ativo in ["não", "nao", "false", "0"]:

        return (
            "Não repor",
            "Produto inativo. Avaliar sua situação comercial antes "
            "de qualquer decisão de reposição."
        )

    # Regra 2: ausência de demanda nos últimos 90 dias
    if vendas_90 == 0:

        if estoque_atual == 0:

            return (
                "Investigar antes de repor",
                "Produto sem vendas observadas nos últimos 90 dias "
                "e sem estoque. Investigar a demanda antes de comprar."
            )

        if estoque_atual > estoque_maximo:

            return (
                "Reduzir ou suspender reposição",
                "Produto sem vendas nos últimos 90 dias e com estoque "
                "acima do máximo. Evitar novas compras."
            )

        return (
            "Monitorar demanda",
            "Não foram observadas vendas nos últimos 90 dias. "
            "Monitorar a procura antes de realizar novas compras."
        )

    # Regra 3: estoque acima do máximo
    if estoque_atual > estoque_maximo:

        return (
            "Reduzir ou suspender reposição",
            "Estoque acima do limite máximo. Recomenda-se evitar "
            "novas compras e acompanhar o giro do produto."
        )

    # Regra 4: ausência de vendas nos últimos 30 dias
    if vendas_30 == 0:

        return (
            "Investigar demanda antes de repor",
            "Existem vendas anteriores, mas não houve vendas nos "
            "últimos 30 dias. Investigar a interrupção da demanda."
        )

    # Regra 5: estoque zerado com demanda recente
    if estoque_atual == 0:

        justificativa = (
            f"Produto ativo com estoque zerado, abaixo do "
            f"mínimo de {estoque_minimo} unidades. "
            f"Apresentou {vendas_30:.0f} venda(s) nos últimos "
            f"30 dias e {vendas_90:.0f} venda(s) nos últimos "
            f"90 dias. A cobertura estimada é de "
            f"{cobertura:.1f} dias, enquanto o prazo de "
            f"reposição é de {prazo} dias. "
        )

        if vendas_90 <= 2:
            justificativa += (
                "O volume de vendas observado é baixo. "
                "Recomenda-se avaliar cuidadosamente a "
                "necessidade e a quantidade antes da compra."
            )
        else:
            justificativa += (
                "Recomenda-se avaliar a reposição para "
                "reduzir o risco de ruptura."
            )

        return (
            "Priorizar avaliação de reposição",
            justificativa
        )


    # Regra 6: cobertura menor ou igual ao prazo de reposição
    if risco == "Alto":

        justificativa = (
            f"Cobertura estimada de {cobertura:.1f} dias, "
            f"inferior ou igual ao prazo de reposição de {prazo} dias."
        )

        if estoque_atual < estoque_minimo:

            justificativa += (
                f" Estoque atual ({estoque_atual}) abaixo do mínimo "
                f"({estoque_minimo})."
            )

        if tendencia == "Decrescente":

            justificativa += (
                " A demanda apresenta tendência decrescente. "
                "Avaliar cuidadosamente a quantidade antes da compra."
            )

            return (
                "Priorizar avaliação de reposição",
                justificativa
            )

        if tendencia == "Volume insuficiente para tendência":

            justificativa += (
                " O volume de vendas ainda é insuficiente para "
                "determinar uma tendência confiável."
            )

        if margem < 0:

            justificativa += (
                " A margem calculada é negativa; verificar os dados "
                "comerciais antes de decidir."
            )

        return (
            "Priorizar avaliação de reposição",
            justificativa
        )

    # Regra 7: estoque abaixo do mínimo, sem risco de ruptura
    if estoque_atual < estoque_minimo:

        justificativa = (
            f"Estoque atual ({estoque_atual}) abaixo do mínimo "
            f"({estoque_minimo}), mas a cobertura estimada de "
            f"{cobertura:.1f} dias supera o prazo de reposição "
            f"de {prazo} dias."
        )

        if tendencia == "Decrescente":

            justificativa += (
                " A demanda está diminuindo. Avaliar a quantidade "
                "necessária antes de programar a reposição."
            )

        elif tendencia == "Crescente":

            justificativa += (
                " A demanda apresenta tendência crescente."
            )

        return (
            "Avaliar reposição programada",
            justificativa
        )

    # Regra 8: estoque dentro da faixa
    return (
        "Monitorar estoque",
        "Estoque dentro da faixa estabelecida e sem risco elevado "
        "de ruptura identificado. Manter acompanhamento da demanda."
    )



# ==========================================================
# 9.1. APLICAÇÃO DAS REGRAS DE DECISÃO
# ==========================================================

resultado = dados.apply(
    gerar_recomendacao,
    axis=1
)

dados["recomendacao"] = resultado.apply(lambda x: x[0])
dados["justificativa"] = resultado.apply(lambda x: x[1])


# ==========================================================
# 10. ORGANIZAÇÃO DO RESULTADO
# ==========================================================

colunas_saida = [
    "produto_id",
    "nome_produto",
    "tipo",
    "ativo",
    "preco_venda",
    "margem_pct",
    "estoque_atual",
    "estoque_minimo",
    "estoque_maximo",
    "situacao_estoque",
    "lead_time_dias",
    "vendas_30d",
    "vendas_30d_anteriores",
    "vendas_90d",
    "media_diaria_90d",
    "cobertura_dias",
    "tendencia_demanda",
    "risco_ruptura",
    "gap_ate_estoque_maximo",
    "recomendacao",
    "justificativa"
]

resultado_final = dados[colunas_saida].copy()

PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

resultado_final.to_csv(
    ARQUIVO_SAIDA,
    index=False,
    sep=";",
    encoding="utf-8-sig"
)


# ==========================================================
# 11. RELATÓRIO NO TERMINAL
# ==========================================================

print("\n" + "=" * 60)
print("RESULTADO DO MECANISMO DE DECISÃO")
print("=" * 60)

print(f"\nTotal de produtos analisados: {len(resultado_final)}")

print("\nRECOMENDAÇÕES:")

print(
    resultado_final["recomendacao"]
    .value_counts()
    .to_string()
)

print("\nPRODUTOS COM PRIORIDADE DE AVALIAÇÃO:")

prioritarios = resultado_final[
    resultado_final["recomendacao"] ==
    "Priorizar avaliação de reposição"
]

if prioritarios.empty:
    print("Nenhum produto classificado nesta categoria.")

else:
    print(
        prioritarios[
            [
                "produto_id",
                "nome_produto",
                "estoque_atual",
                "vendas_30d",
                "cobertura_dias",
                "lead_time_dias",
                "justificativa"
            ]
        ].to_string(index=False)
    )

print("\nArquivo gerado com sucesso:")
print(ARQUIVO_SAIDA)

print("\nANÁLISE CONCLUÍDA!")
