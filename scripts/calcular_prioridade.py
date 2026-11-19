
from pathlib import Path
import pandas as pd


# ==========================================================
# 1. CONFIGURAÇÕES
# ==========================================================

BASE_DIR = Path(__file__).resolve().parents[1]

ARQUIVO_ENTRADA = (
    BASE_DIR / "data" / "processed" /
    "recomendacoes_produtos.csv"
)

ARQUIVO_SAIDA = (
    BASE_DIR / "data" / "processed" /
    "prioridade_reposicao.csv"
)


# Pesos definidos para o SAD
PESO_ESTOQUE = 25
PESO_COBERTURA = 30
PESO_VENDAS = 20
PESO_TENDENCIA = 15
PESO_MARGEM = 10

PONTUACAO_MAXIMA = 100


# ==========================================================
# 2. CARREGAMENTO DOS DADOS
# ==========================================================

print("\nCARREGANDO RECOMENDAÇÕES...")

dados = pd.read_csv(
    ARQUIVO_ENTRADA,
    sep=";",
    encoding="utf-8-sig"
)

colunas_numericas = [
    "estoque_atual",
    "estoque_minimo",
    "estoque_maximo",
    "lead_time_dias",
    "vendas_30d",
    "vendas_90d",
    "cobertura_dias",
    "margem_pct"
]

for coluna in colunas_numericas:
    dados[coluna] = pd.to_numeric(
        dados[coluna],
        errors="coerce"
    )

print(f"Produtos carregados: {len(dados)}")


# ==========================================================
# 3. PONTUAÇÃO DA SITUAÇÃO DO ESTOQUE (0 A 25)
# ==========================================================

def pontuar_estoque(linha):

    estoque = linha["estoque_atual"]
    minimo = linha["estoque_minimo"]

    if estoque <= 0:
        return 25

    if minimo <= 0:
        return 0

    proporcao = estoque / minimo

    if proporcao <= 0.50:
        return 20

    if proporcao < 1:
        return 15

    if proporcao < 1.25:
        return 5

    return 0


dados["pontos_estoque"] = dados.apply(
    pontuar_estoque,
    axis=1
)


# ==========================================================
# 4. PONTUAÇÃO DA COBERTURA (0 A 30)
# ==========================================================

def pontuar_cobertura(linha):

    cobertura = linha["cobertura_dias"]
    prazo = linha["lead_time_dias"]

    if linha["vendas_90d"] <= 0:
        return 0

    if pd.isna(cobertura) or pd.isna(prazo):
        return 0

    if cobertura <= prazo:
        return 30

    if cobertura <= prazo * 1.25:
        return 22

    if cobertura <= prazo * 1.50:
        return 15

    if cobertura <= prazo * 2:
        return 8

    return 0


dados["pontos_cobertura"] = dados.apply(
    pontuar_cobertura,
    axis=1
)


# ==========================================================
# 5. PONTUAÇÃO DO VOLUME DE VENDAS (0 A 20)
# ==========================================================

# O percentil compara o volume de cada produto
# com os demais produtos ativos da própria base.

ativos = (
    dados["ativo"]
    .astype(str)
    .str.strip()
    .str.lower()
    .isin(["sim", "true", "1"])
)

dados["pontos_vendas"] = 0.0

vendas_positivas = (
    ativos &
    (dados["vendas_90d"] > 0)
)

dados.loc[vendas_positivas, "pontos_vendas"] = (
    dados.loc[vendas_positivas, "vendas_90d"]
    .rank(pct=True, method="average")
    * PESO_VENDAS
)


# ==========================================================
# 6. PONTUAÇÃO DA TENDÊNCIA (0 A 15)
# ==========================================================

pontuacao_tendencia = {
    "Crescente": 15,
    "Demanda iniciada ou retomada": 12,
    "Estável": 10,
    "Volume insuficiente para tendência": 5,
    "Decrescente": 3,
    "Sem vendas recentes": 0,
    "Sem vendas nos dois períodos": 0
}

dados["pontos_tendencia"] = (
    dados["tendencia_demanda"]
    .map(pontuacao_tendencia)
    .fillna(0)
)


# ==========================================================
# 7. PONTUAÇÃO DA MARGEM (0 A 10)
# ==========================================================

# A margem é comparada com a dos demais produtos ativos.
# O percentil evita favorecer apenas valores monetários
# absolutos e mantém a pontuação dentro de 0 a 10.

dados["pontos_margem"] = 0.0

margens_validas = (
    ativos &
    dados["margem_pct"].notna()
)

dados.loc[margens_validas, "pontos_margem"] = (
    dados.loc[margens_validas, "margem_pct"]
    .rank(pct=True, method="average")
    * PESO_MARGEM
)


# ==========================================================
# 8. CÁLCULO DA PONTUAÇÃO TOTAL
# ==========================================================

componentes = [
    "pontos_estoque",
    "pontos_cobertura",
    "pontos_vendas",
    "pontos_tendencia",
    "pontos_margem"
]

dados["pontuacao_bruta"] = dados[componentes].sum(axis=1)

dados["pontuacao_prioridade"] = (
    dados["pontuacao_bruta"].clip(
        lower=0,
        upper=PONTUACAO_MAXIMA
    )
)


# ==========================================================
# 9. REGRAS DE PROTEÇÃO
# ==========================================================

# Produtos inativos não recebem prioridade de compra.
dados.loc[~ativos, "pontuacao_prioridade"] = 0

# Sem vendas nos últimos 30 dias:
# a pontuação fica limitada a 39 pontos.
sem_venda_recente = dados["vendas_30d"] == 0

dados.loc[
    ativos & sem_venda_recente,
    "pontuacao_prioridade"
] = dados.loc[
    ativos & sem_venda_recente,
    "pontuacao_prioridade"
].clip(upper=39)


# ==========================================================
# 10. CLASSIFICAÇÃO DA PRIORIDADE
# ==========================================================

def classificar_prioridade(linha):

    ativo = linha["ativo"].strip().lower()

    if ativo not in ["sim", "true", "1"]:
        return "Sem prioridade - produto inativo"

    if linha["vendas_90d"] == 0:
        return "Sem prioridade - sem demanda observada"

    if linha["vendas_30d"] == 0:
        return "Investigar demanda"

    pontos = linha["pontuacao_prioridade"]

    if pontos >= 80:
        return "Prioridade muito alta"

    if pontos >= 60:
        return "Prioridade alta"

    if pontos >= 40:
        return "Prioridade moderada"

    if pontos >= 20:
        return "Prioridade baixa"

    return "Sem prioridade de reposição"


dados["classificacao_prioridade"] = dados.apply(
    classificar_prioridade,
    axis=1
)


# ==========================================================
# 11. JUSTIFICATIVA DA PONTUAÇÃO
# ==========================================================

def gerar_justificativa(linha):

    motivos = []

    if linha["pontos_estoque"] > 0:
        motivos.append("estoque reduzido em relação ao mínimo")

    if linha["pontos_cobertura"] >= 22:
        motivos.append("cobertura próxima ou inferior ao prazo de reposição")

    if linha["tendencia_demanda"] == "Crescente":
        motivos.append("tendência crescente de vendas")

    if linha["tendencia_demanda"] == "Decrescente":
        motivos.append("tendência decrescente de vendas")

    if linha["pontos_vendas"] >= 15:
        motivos.append("volume de vendas elevado em relação aos demais produtos")

    if linha["vendas_30d"] == 0:
        motivos.append("ausência de vendas nos últimos 30 dias")

    if linha["pontos_margem"] >= 8:
        motivos.append("margem relativamente elevada")

    if not motivos:
        return "Sem fatores relevantes de prioridade identificados."

    return "; ".join(motivos) + "."


dados["justificativa_prioridade"] = dados.apply(
    gerar_justificativa,
    axis=1
)


# ==========================================================
# 11.1. PERFIL DE DECISÃO GERENCIAL
# ==========================================================

def classificar_perfil(linha):

    ativo = str(linha["ativo"]).strip().lower()

    if ativo not in ["sim", "true", "1"]:
        return "Suspender reposição"

    if linha["estoque_atual"] > linha["estoque_maximo"]:
        return "Suspender reposição"

    if linha["vendas_90d"] == 0:
        return "Investigar demanda"

    if linha["vendas_30d"] == 0:
        return "Investigar demanda"

    if linha["risco_ruptura"] == "Alto":

        if linha["tendencia_demanda"] == "Decrescente":
            return "Reposição cautelosa"

        return "Reposição urgente"

    if linha["estoque_atual"] < linha["estoque_minimo"]:

        if linha["tendencia_demanda"] in [
            "Crescente",
            "Demanda iniciada ou retomada"
        ]:
            return "Reposição estratégica"

        return "Reposição programada"

    return "Monitorar"


dados["perfil_decisao"] = dados.apply(
    classificar_perfil,
    axis=1
)


# ==========================================================
# 12. EXPORTAÇÃO
# ==========================================================


colunas_resultado = [
    "produto_id",
    "nome_produto",
    "tipo",
    "ativo",
    "estoque_atual",
    "estoque_minimo",
    "estoque_maximo",
    "vendas_30d",
    "vendas_30d_anteriores",
    "vendas_90d",
    "cobertura_dias",
    "lead_time_dias",
    "risco_ruptura",
    "tendencia_demanda",
    "margem_pct",
    "pontos_estoque",
    "pontos_cobertura",
    "pontos_vendas",
    "pontos_tendencia",
    "pontos_margem",
    "pontuacao_bruta",
    "pontuacao_prioridade",
    "classificacao_prioridade",
    "perfil_decisao",
    "recomendacao",
    "justificativa_prioridade"
]


resultado = dados[colunas_resultado].copy()

resultado = resultado.sort_values(
    by="pontuacao_prioridade",
    ascending=False
)

resultado.to_csv(
    ARQUIVO_SAIDA,
    index=False,
    sep=";",
    encoding="utf-8-sig"
)


# ==========================================================
# 13. RELATÓRIO FINAL
# ==========================================================

print("\n" + "=" * 60)
print("ÍNDICE DE PRIORIDADE DE REPOSIÇÃO")
print("=" * 60)

print(f"\nProdutos analisados: {len(resultado)}")

print("\nDISTRIBUIÇÃO DAS PRIORIDADES:")

print(
    resultado["classificacao_prioridade"]
    .value_counts()
    .to_string()
)

print("\nDEZ PRODUTOS COM MAIOR PONTUAÇÃO:")

print(
    resultado[
        [
            "produto_id",
            "nome_produto",
            "pontuacao_prioridade",
            "classificacao_prioridade",
            "justificativa_prioridade"
        ]
    ].head(10).to_string(index=False)
)

print("\nArquivo gerado:")
print(ARQUIVO_SAIDA)

print("\nCÁLCULO DO ÍNDICE CONCLUÍDO!")
