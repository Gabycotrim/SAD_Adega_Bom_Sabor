
from pathlib import Path

import pandas as pd

from flask import Flask, render_template


# ==========================================================
# 1. CONFIGURAÇÃO DA APLICAÇÃO
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent


ARQUIVO_DADOS = (
    BASE_DIR
    / "data"
    / "processed"
    / "prioridade_reposicao.csv"
)

ARQUIVO_RECOMENDACOES = (
    BASE_DIR
    / "data"
    / "processed"
    / "recomendacoes_produtos.csv"
)


app = Flask(
    __name__,
    template_folder="app/templates",
    static_folder="app/static",
)


# ==========================================================
# 2. CARREGAMENTO DOS DADOS
# ==========================================================

def carregar_dados():

    if not ARQUIVO_DADOS.exists():
        raise FileNotFoundError(
            f"Arquivo de dados não encontrado: {ARQUIVO_DADOS}"
        )

    dados = pd.read_csv(
        ARQUIVO_DADOS,
        sep=";",
        encoding="utf-8-sig"
    )

    return dados


# ==========================================================
# 3. ROTA PRINCIPAL - DASHBOARD
# ==========================================================

@app.route("/")
def index():

    dados = carregar_dados()

    total_produtos = len(dados)

    prioridades = dados["classificacao_prioridade"].value_counts()

    perfis = dados["perfil_decisao"].value_counts()

    indicadores = {
        "total_produtos": total_produtos,

        "prioridade_alta": int(
            prioridades.get("Prioridade alta", 0)
        ),

        "prioridade_moderada": int(
            prioridades.get("Prioridade moderada", 0)
        ),

        "prioridade_baixa": int(
            prioridades.get("Prioridade baixa", 0)
        ),

        "reposicao_urgente": int(
            perfis.get("Reposição urgente", 0)
        ),

        "investigar_demanda": int(
            perfis.get("Investigar demanda", 0)
        ),

        "suspender_reposicao": int(
            perfis.get("Suspender reposição", 0)
        ),

        "monitorar": int(
            perfis.get("Monitorar", 0)
        )
    }

    produtos = (
        dados
        .fillna("")
        .to_dict(orient="records")
    )

    perfis_grafico = (
        dados["perfil_decisao"]
        .value_counts()
        .to_dict()
    )

    return render_template(
        "index.html",
        indicadores=indicadores,
        produtos=produtos,
        perfis_grafico=perfis_grafico
    )



# ==========================================================
# 4. DETALHAMENTO INDIVIDUAL DO PRODUTO
# ==========================================================


@app.route("/produto/<int:produto_id>")
def detalhe_produto(produto_id):

    # Carrega os dados de prioridade
    dados = carregar_dados()

    produto_encontrado = dados[
        dados["produto_id"] == produto_id
    ]

    if produto_encontrado.empty:
        return "Produto não encontrado.", 404

    produto = (
        produto_encontrado
        .iloc[0]
        .fillna("")
        .to_dict()
    )

    # Carrega as recomendações detalhadas
    if not ARQUIVO_RECOMENDACOES.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {ARQUIVO_RECOMENDACOES}"
        )

    recomendacoes = pd.read_csv(
        ARQUIVO_RECOMENDACOES,
        sep=";",
        encoding="utf-8-sig"
    )

    recomendacao_encontrada = recomendacoes[
        recomendacoes["produto_id"] == produto_id
    ]

    if not recomendacao_encontrada.empty:

        recomendacao = recomendacao_encontrada.iloc[0]

        produto["recomendacao_detalhada"] = (
            recomendacao["recomendacao"]
        )

        produto["justificativa_recomendacao"] = (
            recomendacao["justificativa"]
        )

    return render_template(
        "produto.html",
        produto=produto
    )

# ==========================================================
# 5. COMPARATIVO DOS CINCO PRODUTOS PRIORITÁRIOS
# ==========================================================

@app.route("/comparativo")
def comparativo():

    dados = carregar_dados()

    dados_grafico = (
        dados
        .sort_values(
            by="pontuacao_prioridade",
            ascending=False
        )
        .head(5)
        .fillna(0)
        .to_dict(orient="records")
    )

    produtos = dados_grafico

    return render_template(
        "comparativo.html",
        produtos=produtos,
        dados_grafico=dados_grafico
    )

# ==========================================================
# 6. EXECUÇÃO DA APLICAÇÃO
# ==========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
