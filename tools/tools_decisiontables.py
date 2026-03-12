# tools_decisiontables.py

from mcp.server.fastmcp import FastMCP
from helpers.http_java_client import JavaBackendClient
import os
import json

java = JavaBackendClient(
    base_url=os.getenv("OTHER_BASE_URL", "http://localhost:8080")
)

import builtins
mcp: FastMCP = builtins.__dict__.get("mcp")


@mcp.tool()
def visualizar_decision_table(projectName: str, packageName: str, tableName: str, baselineName: str = "Main"):
    """
    Retorna a estrutura resumida da Decision Table (GET /decisiontables):
      - colunas de condição
      - colunas de ação
      - bodyPreview (string armazenável)
    """
    return java.get(
        "decisiontables",
        params={
            "projectName": projectName,
            "packageName": packageName,
            "tableName": tableName,
            "baselineName": baselineName
        }
    )


@mcp.tool()
def criar_decision_table(
    projectName: str,
    packageName: str,
    tableName: str,
    model: dict,
    baselineName: str = "Main",
    locale: str = "pt-BR",
    resetIfExists: bool = False
):
    r"""
    Criar Decision Table (POST /decisiontables)

    Objetivo
    --------
    Criar uma Decision Table no pacote informado via backend Java, enviando um `model`
    com `preconditions` (opcional), `conditions` (obrigatório) e `actions` (obrigatório).
    O servidor aplica *hard reset* quando `resetIfExists=true` e gera as linhas pelo
    produto cartesiano das partições. As colunas **não‑raiz** usam sempre o índice `0`,
    portanto os caminhos de `valuesByPath` variam apenas no **primeiro índice** (linhas),
    como `[0,0,0]`, `[1,0,0]`, `[2,0,0]`… 
    
    Requisitos do `model`
    ---------------------
    - `preconditions` (opcional): lista de objetos com `{ "statement": "<verbalização>" }`. 
    - `conditions` (obrigatório): cada condição deve conter:
        * `title`: rótulo da coluna na DT
        * `statement`: **verbalização do BOM**; pode usar marcadores como `<um número>`
        * `partitions`: faixas `{ "min":"...", "max":"..." }` ou valores `{ "value":"..." }`  
    - `actions` (obrigatório): cada ação deve conter:
        * `title`: rótulo da coluna de ação
        * `statement`: verbalização do BOM (pode conter `<um número>`)
        * `valuesByPath`: dicionário **caminho → valor**, com caminhos sequenciais
          `[linha,0,0,...]` (colunas não‑raiz no índice `0`) 

    Boas práticas e políticas de criação
    ------------------------------------
    - **Nunca** tente criar regras simples caso a **Decision Table** falhe; se é para planilhar, **crie DT**.  
    - **Nunca** use **outro nome** se a criação falhar (evita duplicação). Reenvie com o mesmo nome;
      quando necessário, use `resetIfExists=true` para limpar antes de recriar. 
    - **Consulte o vocabulário (BOM)** antes de criar (garante aderência das verbalizações dos statements). 
    - **Consulte o projeto de exemplo** e **regras existentes** para evitar conflitos de nomenclatura e semântica.  
    - **Verifique se existem pacotes existentes que condizem com a criação da nova Decision Table, se houver use eles, evite criar pacotes desnecessários.  

    - Se `baselineName` não for informado, a baseline **Main** é utilizada.  

    Exemplos de *statement* (verbalização do BOM)
    ---------------------------------------------
    - Condition:
      "a duração (em anos) de 'o empréstimo' está entre <um número> e <um número>" 
      "o nome de 'Participante Atual' é <uma cadeia>"
    - Action:
      "defina a taxa de juros anual de 'o empréstimo' para <um número>"  
      "atribuir à 'Aprovar Credito' o valor <um booleano>"
    
      
    Exemplo completo de `model`
    ---------------------------
    O payload abaixo corresponde à criação de 3 colunas de condição e ações com 30 linhas:

    {
      "preconditions": [
        { "statement": "se a idade de 'o tomador' é 21" }
      ],
      "conditions": [
        {
          "title": "Duração do empréstimo (anos)",
          "statement": "a duração (em anos) de 'o empréstimo' está entre <um número> e <um número>",
          "partitions": [
            { "min": "5",  "max": "10" },
            { "min": "11", "max": "15" },
            { "min": "16", "max": "20" },
            { "min": "21", "max": "25" },
            { "min": "26", "max": "30" }
          ]
        },
        {
          "title": "Loan to Value",
          "statement": "o Loan to Value de 'o empréstimo' é pelo menos <um número> e menor que <um número>",
          "partitions": [
            { "min": "0.0", "max": "0.7" },
            { "min": "0.7", "max": "0.9" }
          ]
        },
        {
          "title": "Score de crédito",
          "statement": "o score de crédito de 'o tomador' é pelo menos <um número>",
          "partitions": [
            { "value": "600" },
            { "value": "700" },
            { "value": "800" }
          ]
        }
      ],
      "actions": [
        {
          "title": "Taxa de juros anual",
          "statement": "defina a taxa de juros anual de 'o empréstimo' para <um número>",
          "valuesByPath": {
            "[0,0,0]":"0.040","[1,0,0]":"0.038","[2,0,0]":"0.036",
            "[3,0,0]":"0.042","[4,0,0]":"0.040","[5,0,0]":"0.038",
            "[6,0,0]":"0.044","[7,0,0]":"0.042","[8,0,0]":"0.040",
            "[9,0,0]":"0.046","[10,0,0]":"0.044","[11,0,0]":"0.042",
            "[12,0,0]":"0.048","[13,0,0]":"0.046","[14,0,0]":"0.044",
            "[15,0,0]":"0.042","[16,0,0]":"0.040","[17,0,0]":"0.038",
            "[18,0,0]":"0.044","[19,0,0]":"0.042","[20,0,0]":"0.040",
            "[21,0,0]":"0.046","[22,0,0]":"0.044","[23,0,0]":"0.042",
            "[24,0,0]":"0.048","[25,0,0]":"0.046","[26,0,0]":"0.044",
            "[27,0,0]":"0.050","[28,0,0]":"0.048","[29,0,0]":"0.046"
          }
        },
        {
          "title": "Fator de risco",
          "statement": "defina o fator de risco de 'o empréstimo' como <um número>",
          "valuesByPath": {
            "[0,0,0]":"1.00","[1,0,0]":"0.95","[2,0,0]":"0.90",
            "[3,0,0]":"1.10","[4,0,0]":"1.05","[5,0,0]":"1.00",
            "[6,0,0]":"1.20","[7,0,0]":"1.15","[8,0,0]":"1.10",
            "[9,0,0]":"1.30","[10,0,0]":"1.25","[11,0,0]":"1.20",
            "[12,0,0]":"1.40","[13,0,0]":"1.35","[14,0,0]":"1.30",
            "[15,0,0]":"1.05","[16,0,0]":"1.00","[17,0,0]":"0.95",
            "[18,0,0]":"1.15","[19,0,0]":"1.10","[20,0,0]":"1.05",
            "[21,0,0]":"1.25","[22,0,0]":"1.20","[23,0,0]":"1.15",
            "[24,0,0]":"1.45","[25,0,0]":"1.40","[26,0,0]":"1.35",
            "[27,0,0]":"1.50","[28,0,0]":"1.45","[29,0,0]":"1.40"
          }
        },
        {
          "title": "Desconto promocional",
          "statement": "defina o desconto promocional de 'o empréstimo' como <um número>",
          "valuesByPath": {
            "[0,0,0]":"0.005","[1,0,0]":"0.004","[2,0,0]":"0.003",
            "[3,0,0]":"0.004","[4,0,0]":"0.003","[5,0,0]":"0.002",
            "[6,0,0]":"0.003","[7,0,0]":"0.002","[8,0,0]":"0.001",
            "[9,0,0]":"0.002","[10,0,0]":"0.001","[11,0,0]":"0.000",
            "[12,0,0]":"0.001","[13,0,0]":"0.000","[14,0,0]":"0.000",
            "[15,0,0]":"0.004","[16,0,0]":"0.003","[17,0,0]":"0.002",
            "[18,0,0]":"0.003","[19,0,0]":"0.002","[20,0,0]":"0.001",
            "[21,0,0]":"0.002","[22,0,0]":"0.001","[23,0,0]":"0.000",
            "[24,0,0]":"0.001","[25,0,0]":"0.000","[26,0,0]":"0.000",
            "[27,0,0]":"0.000","[28,0,0]":"0.000","[29,0,0]":"0.000"
          }
        }
      ]
    }

    Return
    -------
    A resposta é a mesma retornada pelo backend Java (200 OK com resumo, ou erro):
    - Quando `resetIfExists=true`, o servidor faz *hard reset* antes de recriar.
      `actionColumns` e `bodyPreview`.
    """
    # Envia o payload "como veio" — sem alterar verbalizações (ex.: "<um número>")
    payload = {
        "projectName": projectName,
        "packageName": packageName,
        "tableName": tableName,
        "baselineName": baselineName,
        "locale": locale,
        "resetIfExists": resetIfExists,
        "model": model
    }
    headers = {"Content-Type": "application/json"}
    return java.post("decisiontables", data=json.dumps(payload), headers=headers)


@mcp.tool()
def atualizar_decision_table(
    projectName: str,
    packageName: str,
    tableName: str,
    model: dict,
    baselineName: str = "Main",
    locale: str = "pt-BR"
):
    """
    Atualiza uma Decision Table existente (PUT /decisiontables).
    """
    payload = {
        "projectName": projectName,
        "packageName": packageName,
        "tableName": tableName,
        "baselineName": baselineName,
        "locale": locale,
        "model": model
    }
    headers = {"Content-Type": "application/json"}
    return java.put("decisiontables", data=json.dumps(payload), headers=headers)

# Made with Bob
