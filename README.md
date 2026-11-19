# SAD Adega Bom Sabor

## Sistema de Apoio à Decisão para Gestão e Priorização de Reposição de Estoque

## 1. Apresentação do Projeto

O **SAD Adega Bom Sabor** é uma Prova de Conceito (POC) de um Sistema de Apoio à Decisão desenvolvido para auxiliar a gestão de estoque e a priorização de reposição de produtos da Adega Bom Sabor.

O sistema utiliza dados de produtos, estoque e compras para realizar análises comerciais, identificar situações de risco, avaliar tendências de demanda e calcular índices de prioridade de reposição.

A proposta é transformar dados operacionais em informações organizadas e recomendações justificadas, oferecendo suporte ao processo decisório do gestor.

O sistema foi desenvolvido utilizando Python, Flask, pandas, openpyxl, HTML, CSS e JavaScript.

## 2. Problema Decisório

A gestão de estoque exige decisões relacionadas à reposição, manutenção ou redução de compras de produtos.

A ausência de critérios estruturados pode dificultar a identificação de produtos com risco de ruptura, excesso de estoque, redução de demanda ou necessidade de acompanhamento.

O problema decisório abordado pelo projeto consiste em:

**Como priorizar a reposição de produtos considerando estoque disponível, histórico de vendas, cobertura de estoque, prazo de reposição, tendência de demanda e margem?**

O SAD busca apoiar essa decisão por meio da análise integrada desses indicadores e da apresentação de recomendações para o gestor.

## 3. Objetivo Geral

Desenvolver uma Prova de Conceito de um Sistema de Apoio à Decisão capaz de analisar informações comerciais e de estoque, calcular prioridades e apresentar recomendações que auxiliem o gestor na tomada de decisões sobre reposição de produtos.

### 3.1 Objetivos Específicos

- Validar e analisar a estrutura da base de dados disponibilizada para o projeto.
- Identificar situações de estoque abaixo do mínimo ou acima do máximo.
- Analisar o comportamento das vendas em diferentes períodos.
- Avaliar a cobertura de estoque em relação ao prazo de reposição.
- Identificar tendências de demanda.
- Calcular uma pontuação de prioridade por produto.
- Classificar produtos conforme seu nível de prioridade.
- Apresentar recomendações e justificativas para apoiar as decisões gerenciais.
- Disponibilizar informações por meio de uma aplicação web.

## 4. Tecnologias Utilizadas

| Tecnologia | Aplicação no projeto |
|---|---|
| Python | Linguagem principal e processamento dos dados |
| Flask | Desenvolvimento da aplicação web |
| pandas | Manipulação e análise de dados |
| openpyxl | Leitura de planilhas Excel |
| HTML | Estrutura das páginas |
| CSS | Estilização da interface |
| JavaScript | Funcionalidades e interações da interface |
| Git | Controle de versão |

## 5. Base de Dados

O projeto utiliza a planilha `Base_Adega_Bom_Sabor_2026.xlsx`, disponibilizada como material fictício da atividade acadêmica.

A planilha está armazenada em:

`data/raw/Base_Adega_Bom_Sabor_2026.xlsx`

### 5.1 Abas da Planilha

| Aba | Conteúdo |
|---|---|
| Dicionario | Descrição dos campos da base |
| Clientes | Informações dos clientes |
| Produtos | Cadastro e características dos produtos |
| Estoque | Informações sobre disponibilidade e limites de estoque |
| Compras | Histórico de compras e movimentações comerciais |

### 5.2 Processamento dos Dados

Os dados originais são lidos pelos scripts de análise e processamento. Os resultados são armazenados em arquivos CSV na pasta `data/processed/`.

A planilha original não é modificada durante o processamento.

Os arquivos processados são gerados localmente e não são versionados pelo Git, conforme configuração do `.gitignore`.

## 6. Modelo de Análise e Apoio à Decisão

O sistema utiliza diferentes indicadores para avaliar a situação dos produtos e apoiar a priorização de reposição.

### 6.1 Indicadores Analisados

- Estoque atual: quantidade disponível do produto.
- Estoque mínimo: limite mínimo definido para controle.
- Estoque máximo: limite máximo de referência.
- Vendas recentes: movimentação comercial em diferentes períodos.
- Cobertura de estoque: estimativa de quantos dias o estoque disponível pode atender à demanda observada.
- Lead time: prazo de reposição do produto.
- Tendência de demanda: comportamento das vendas ao longo dos períodos analisados.
- Margem: indicador utilizado na composição da pontuação de prioridade.

### 6.2 Pontuação Multicritério

O cálculo de prioridade considera cinco critérios, com pesos que totalizam 100 pontos:

| Critério | Peso |
|---|---:|
| Estoque | 25 pontos |
| Cobertura de estoque | 30 pontos |
| Vendas | 20 pontos |
| Tendência | 15 pontos |
| Margem | 10 pontos |
| **Total** | **100 pontos** |

A pontuação é calculada por produto, considerando as regras implementadas no script `calcular_prioridade.py`.

Os critérios possuem regras específicas de pontuação, e os resultados são combinados para formar o índice de prioridade.

Produtos inativos e produtos sem demanda observada recebem tratamentos específicos, evitando que sejam classificados automaticamente como candidatos à reposição.

### 6.3 Classificação da Prioridade

A pontuação é utilizada para classificar os produtos:

| Pontuação | Classificação |
|---|---|
| 80 a 100 | Prioridade muito alta |
| 60 a 79,99 | Prioridade alta |
| 40 a 59,99 | Prioridade moderada |
| 20 a 39,99 | Prioridade baixa |
| Abaixo de 20 | Sem prioridade de reposição |

Existem também classificações especiais para produtos inativos e produtos sem demanda observada.

### 6.4 Recomendações Gerenciais

Além da pontuação, o sistema apresenta recomendações de acordo com as condições identificadas na análise.

Entre as recomendações implementadas estão:

- Monitorar estoque.
- Investigar demanda antes de repor.
- Avaliar reposição programada.
- Reduzir ou suspender reposição.
- Não repor.
- Priorizar avaliação de reposição.
- Monitorar demanda.

As recomendações são acompanhadas de justificativas, permitindo que o gestor compreenda os fatores que influenciaram a classificação.

**Importante:** a pontuação e as recomendações são instrumentos de apoio à decisão. A decisão final permanece sob responsabilidade do gestor.

## 7. Estrutura do Projeto

A organização atual do projeto está distribuída da seguinte forma:

```text
SAD_Adega_Bom_Sabor/
│
├── app/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   │
│   └── templates/
│       ├── index.html
│       ├── produto.html
│       └── comparativo.html
│
├── data/
│   ├── raw/
│   │   └── Base_Adega_Bom_Sabor_2026.xlsx
│   │
│   └── processed/
│       └── .gitkeep
│
├── docs/
│   └── .gitkeep
│
├── scripts/
│   ├── analise_comercial.py
│   ├── analise_risco.py
│   ├── analise_temporal.py
│   ├── analise_tendencia.py
│   ├── calcular_prioridade.py
│   ├── diagnostico_dados.py
│   ├── gerar_recomendacoes.py
│   ├── validar_base.py
│   └── verificar_consistencia.py
│
├── tests/
│   └── .gitkeep
│
├── .gitignore
├── app.py
├── README.md
└── requirements.txt
```

### 7.1 Descrição dos Diretórios

- `app/`: contém os arquivos da aplicação web.
- `app/static/css/`: contém os estilos visuais.
- `app/static/js/`: contém os scripts JavaScript da interface.
- `app/templates/`: contém os templates HTML.
- `data/raw/`: armazena a base original.
- `data/processed/`: armazena os arquivos processados.
- `docs/`: destinado à documentação complementar.
- `scripts/`: reúne os scripts de análise, validação e processamento.
- `tests/`: reservado para testes automatizados.

## 8. Funcionalidades do Sistema

### 8.1 Painel Principal

Apresenta uma visão geral dos produtos e das classificações de prioridade, permitindo acompanhar a situação geral do estoque.

### 8.2 Análise Individual de Produtos

Permite consultar informações específicas de cada produto, incluindo indicadores, pontuação, classificação e recomendação gerencial.

### 8.3 Comparativo de Produtos

Apresenta um comparativo dos cinco produtos com maior pontuação de prioridade, facilitando a identificação dos itens que merecem maior atenção.

### 8.4 Análises Complementares

O projeto também possui scripts destinados à análise comercial, análise de risco, análise temporal, análise de tendência, diagnóstico dos dados e verificação de consistência.

## 9. Requisitos para Execução

Para executar o projeto, são necessários:

- Python 3.14.3 (versão utilizada nos testes)
- Git.
- Navegador web atualizado.
- Acesso à planilha original disponibilizada com o projeto.

As dependências Python estão declaradas no arquivo `requirements.txt`.

## 10. Instalação e Configuração

### 10.1 Clonar o Repositório

```powershell
git clone https://github.com/Gabycotrim/SAD_Adega_Bom_Sabor.git
cd SAD_Adega_Bom_Sabor
```

### 10.2 Criar o Ambiente Virtual

```powershell
py -m venv .venv
```

### 10.3 Ativar o Ambiente Virtual

No Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Caso o PowerShell impeça a ativação por política de execução, consulte a documentação oficial do Python ou do Windows para ajustar a configuração do ambiente.

### 10.4 Instalar as Dependências

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 11. Validação e Execução

As etapas abaixo devem ser executadas na ordem apresentada.

### 11.1 Validar a Base de Dados

```powershell
python scripts\validar_base.py
```

O script verifica as abas esperadas, estrutura das colunas, valores ausentes, duplicidades, relacionamentos e datas de compra.

A validação apresenta um diagnóstico sem modificar a planilha original.

### 11.2 Gerar as Recomendações

```powershell
python scripts\gerar_recomendacoes.py
```

Esse procedimento processa os dados de produtos, estoque e compras e gera:

`data/processed/recomendacoes_produtos.csv`

### 11.3 Calcular a Prioridade de Reposição

```powershell
python scripts\calcular_prioridade.py
```

Esse procedimento utiliza o arquivo de recomendações para calcular a pontuação, a classificação e o perfil decisório de cada produto.

O resultado é armazenado em:

`data/processed/prioridade_reposicao.csv`

### 11.4 Executar a Aplicação Web

```powershell
python app.py
```

Após iniciar o servidor, abra o navegador e acesse:

http://127.0.0.1:5000

Para encerrar a aplicação, utilize `Ctrl + C` no terminal em que o servidor está sendo executado.

## 12. Análises Complementares

Além do fluxo principal, o projeto possui scripts independentes para aprofundar a análise dos dados:

| Script | Finalidade |
|---|---|
| `diagnostico_dados.py` | Diagnóstico da base de dados |
| `verificar_consistencia.py` | Verificação de consistência e relacionamentos |
| `analise_comercial.py` | Análise comercial |
| `analise_risco.py` | Análise de risco |
| `analise_tendencia.py` | Análise de tendência |
| `analise_temporal.py` | Análise temporal e geração de arquivo CSV |

Para executar uma análise complementar, utilize:

```powershell
python scripts\nome_do_script.py
```

Substitua `nome_do_script.py` pelo nome do arquivo desejado.

O script `analise_temporal.py` gera o arquivo `data/processed/analise_temporal.csv`.

## 13. Arquivos Gerados

Os principais arquivos produzidos durante o processamento são:

| Arquivo | Descrição |
|---|---|
| `recomendacoes_produtos.csv` | Recomendações e justificativas por produto |
| `prioridade_reposicao.csv` | Pontuações, classificações e perfis de prioridade |
| `analise_temporal.csv` | Resultado da análise temporal |

Os arquivos são armazenados em `data/processed/` e gerados novamente quando os scripts correspondentes são executados.

## 14. Limitações da Prova de Conceito

O SAD Adega Bom Sabor foi desenvolvido como uma Prova de Conceito acadêmica, utilizando uma base de dados fictícia.

Entre suas limitações atuais, destacam-se:

- As análises dependem da qualidade e da atualização da base fornecida.
- Os resultados representam o comportamento dos dados disponíveis, não garantindo previsões futuras.
- Os pesos e critérios do modelo representam escolhas metodológicas implementadas no projeto.
- O sistema não substitui a avaliação gerencial.
- A pasta `tests/` ainda não possui testes automatizados implementados.
- Os arquivos processados precisam ser gerados antes da execução da aplicação.

## 15. Possibilidades de Evolução

Como possibilidades de evolução do projeto, destacam-se:

- Implementação de testes automatizados.
- Aprimoramento das regras de classificação e recomendação.
- Inclusão de novos indicadores de desempenho.
- Automatização da atualização dos dados.
- Implementação de filtros e consultas avançadas.
- Exportação de relatórios gerenciais.
- Avaliação de técnicas estatísticas e preditivas para estimativa de demanda.
- Melhorias de segurança, autenticação e controle de acesso.

## 16. Considerações Finais

O SAD Adega Bom Sabor demonstra como a integração de dados comerciais e de estoque pode contribuir para a organização do processo decisório.

Por meio da validação dos dados, análise de indicadores, cálculo multicritério e apresentação de recomendações, a Prova de Conceito busca transformar informações operacionais em subsídios para decisões mais estruturadas.

O sistema evidencia a aplicação prática dos conceitos de Sistemas de Apoio à Decisão, análise de dados e desenvolvimento de aplicações web.

---

**Projeto acadêmico — Sistema de Apoio à Decisão (SAD)**

**Adega Bom Sabor**