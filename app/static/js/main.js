
// ==========================================================
// 1. GRÁFICO DE DISTRIBUIÇÃO DOS PERFIS
// ==========================================================

document.addEventListener("DOMContentLoaded", function () {

    const elementoDados = document.getElementById("dadosPerfis");
    const elementoGrafico = document.getElementById("graficoPerfis");

    if (elementoDados && elementoGrafico && typeof Chart !== "undefined") {

        const perfis = JSON.parse(elementoDados.textContent);

        const labelsOriginais = Object.keys(perfis);
        const valores = Object.values(perfis);

        const total = valores.reduce(
        (soma, valor) => soma + valor,
        0
        );

        const labels = labelsOriginais.map(function (nome, indice) {
        const percentual = total > 0
        ? (valores[indice] / total * 100).toFixed(1)
        : "0.0";

        return `${nome}: ${valores[indice]} (${percentual}%)`;
        });

        new Chart(elementoGrafico, {
            type: "doughnut",

            data: {
                labels: labels,

                datasets: [{
                    data: valores,

                    backgroundColor: [
                        "#5a1832",
                        "#c9a45c",
                        "#28734c",
                        "#a83245",
                        "#7b2948",
                        "#b66b20",
                        "#8a8290"
                    ],

                    borderWidth: 2,
                    borderColor: "#ffffff"
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                plugins: {
                    legend: {
                        position: "bottom",

                        labels: {
                            padding: 18,
                            usePointStyle: true
                        }
                    },

                    tooltip: {
                        callbacks: {
                            label: function (context) {

                                const total = valores.reduce(
                                    (soma, valor) => soma + valor,
                                    0
                                );

                                const percentual = total > 0
                                    ? (context.raw / total * 100).toFixed(1)
                                    : "0.0";

                                return `${labelsOriginais[context.dataIndex]}: ${context.raw} produtos (${percentual}%)`;
                            }
                        }
                    }
                }
            }
        });

    } else if (elementoGrafico) {

        console.error(
            "Não foi possível inicializar o gráfico. Verifique o carregamento do Chart.js."
        );
    }


      // ======================================================
    // 2. PESQUISA E FILTROS DE PRODUTOS
    // ======================================================

    const busca = document.getElementById("buscaProduto");
    const filtroPerfil = document.getElementById("filtroPerfil");
    const filtroPrioridade = document.getElementById("filtroPrioridade");

    const tabela = document.getElementById("tabelaProdutos");
    const contador = document.getElementById("contadorProdutos");
    const mensagemVazia = document.getElementById("mensagemVazia");

    if (!busca || !filtroPerfil || !filtroPrioridade || !tabela) {
        return;
    }

    const linhas = Array.from(
        tabela.querySelectorAll("tbody tr")
    );

    // Normaliza códigos, removendo zeros à esquerda
    function normalizarCodigo(codigo) {
    return codigo.replace(/^0+(?=\d)/, "");
}

    function filtrarProdutos() {

        const termo = busca.value
            .trim()
            .toLocaleLowerCase("pt-BR");

        const perfilSelecionado = filtroPerfil.value
            .trim()
            .toLocaleLowerCase("pt-BR");

        const prioridadeSelecionada = filtroPrioridade.value
            .trim()
            .toLocaleLowerCase("pt-BR");

        let quantidadeVisivel = 0;

        linhas.forEach(function (linha) {

            const textoLinha = linha.textContent
                .toLocaleLowerCase("pt-BR");

            const perfilLinha = linha.cells[5].textContent
                .trim()
                .toLocaleLowerCase("pt-BR");

            const prioridadeLinha = linha.dataset.prioridade
                .trim()
                .toLocaleLowerCase("pt-BR");

            // Código do produto está na primeira coluna
            const codigoLinha = linha.cells[0].textContent.trim();

            // Pesquisa numérica: código exato
            // Pesquisa textual: correspondência parcial no conteúdo da linha
            const correspondeBusca = /^\d+$/.test(termo)
            ? normalizarCodigo(codigoLinha) === normalizarCodigo(termo)
            : textoLinha.includes(termo);

            const correspondePerfil =
                perfilSelecionado === "" ||
                perfilLinha === perfilSelecionado;

            const correspondePrioridade =
                prioridadeSelecionada === "" ||
                prioridadeLinha === prioridadeSelecionada;

            const mostrar =
                correspondeBusca &&
                correspondePerfil &&
                correspondePrioridade;

            linha.style.display = mostrar ? "" : "none";

            if (mostrar) {
                quantidadeVisivel++;
            }

        });

        contador.textContent =
            `Exibindo ${quantidadeVisivel} de ${linhas.length} produtos.`;

        mensagemVazia.hidden = quantidadeVisivel !== 0;
    }

    busca.addEventListener("input", filtrarProdutos);
    filtroPerfil.addEventListener("change", filtrarProdutos);
    filtroPrioridade.addEventListener("change", filtrarProdutos);


    // ======================================================
    // 3. CARTÕES INTERATIVOS DO DASHBOARD
    // ======================================================

    const cartoesIndicadores = document.querySelectorAll(
        ".indicador-clicavel"
    );

    cartoesIndicadores.forEach(function (cartao) {

        function aplicarFiltro() {

            // Limpa a pesquisa anterior
            busca.value = "";

            // Verifica se o cartão representa uma prioridade
            if (cartao.dataset.filtrarPrioridade) {

                filtroPrioridade.value =
                    cartao.dataset.filtrarPrioridade;

                filtroPerfil.value = "";

            }

            // Verifica se o cartão representa um perfil
            else if (cartao.dataset.filtrarPerfil) {

                filtroPerfil.value =
                    cartao.dataset.filtrarPerfil;

                filtroPrioridade.value = "";

            }

            // Atualiza a tabela
            filtrarProdutos();

            // Leva o usuário até os resultados
            tabela.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        }

        // Clique do mouse
        cartao.addEventListener("click", aplicarFiltro);

        // Acesso pelo teclado
        cartao.addEventListener("keydown", function (evento) {

            if (evento.key === "Enter" || evento.key === " ") {
                evento.preventDefault();
                aplicarFiltro();
            }

        });

    });


console.log("SAD Adega Bom Sabor: dashboard carregado.");

});
