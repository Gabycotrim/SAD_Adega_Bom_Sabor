# SAD Adega Bom Sabor

Prova de Conceito de um Sistema de Apoio à Decisão para apoiar a priorização de reposição e a gestão de estoque da Adega Bom Sabor.

## Tecnologias
- Python
- Flask
- pandas
- openpyxl
- HTML, CSS e JavaScript

## Requisitos
Python 3.11 ou superior recomendado; Git.

## Preparar o ambiente no Windows (PowerShell)
```powershell
py --version
git --version
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Se `py` não for reconhecido, instale o Python pelo site oficial e marque a opção para adicionar Python ao PATH.

## Validar a planilha
Com o ambiente virtual ativado:
```powershell
python scripts\validar_base.py
```

## Executar a aplicação
```powershell
python app.py
```
Abra http://127.0.0.1:5000 no navegador.

## Problema decisório preliminar
Apoiar o gestor de compras/estoque a priorizar produtos para reposição, manutenção ou redução da reposição, considerando vendas recentes, estoque disponível, limites de estoque, prazo de reposição e margem. Os critérios finais serão definidos após a validação da base.

## Importante
A POC deverá ir além de gráficos: precisa processar critérios e apresentar recomendações justificadas para o decisor. As recomendações apoiam, mas não substituem, a decisão gerencial.
