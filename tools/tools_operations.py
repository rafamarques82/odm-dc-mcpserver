# -*- coding: utf-8 -*-
"""
Tools relacionados a Decision Operations para o Decision Center, via backend Java (ODMHttpServer).

Disponíveis:
- criar_operation     → POST /operations?action=create
- atualizar_operation → PUT  /operations?action=update
- visualizar_operation→ GET  /operations?action=view

Todas as operações são delegadas ao servidor Java (ODMHttpServer) e usam o JavaBackendClient
configurado por OTHER_BASE_URL (padrão: http://localhost:8080).

No backend:
- /operations?action=create (POST) cria Decision Operation no projeto.
- /operations?action=update (PUT)  atualiza Decision Operation existente.
- /operations?action=view   (GET)  retorna detalhes de uma Decision Operation.
"""

from mcp.server.fastmcp import FastMCP
from helpers.http_java_client import JavaBackendClient
import os
import json

# Cliente Java (base_url pode ser sobrescrita via env OTHER_BASE_URL)
java = JavaBackendClient(
    base_url=os.getenv("OTHER_BASE_URL", "http://localhost:8080")
)

import builtins
mcp: FastMCP = builtins.__dict__.get("mcp")


@mcp.tool()
def criar_operation(
    projectName: str,
    operationName: str,
    ruleflowName: str,
    variableSetName: str,
    parameters: list,
    baselineName: str = "Main",
    rulesetName: str = None,
    description: str = None,
    rulesetParameters: dict = None
):
    """
    Cria uma Decision Operation no backend Java (POST /operations?action=create).
    
    ⚠️ REQUISITOS OBRIGATÓRIOS:
    Uma Decision Operation SEMPRE requer:
    1. Ruleflow associado (ruleflowName)
    2. Variable Set (variableSetName) - usado para descriptors, params e rulesetParams
    3. Parâmetros (parameters) - pelo menos um parâmetro IN, OUT ou INOUT
    
    IMPORTANTE: Operations NÃO têm pacote específico - são criadas no nível do projeto.
    
    Parâmetros OBRIGATÓRIOS:
      - projectName: nome do projeto/Decision Service
      - operationName: nome da operation
      - ruleflowName: nome do ruleflow a associar (OBRIGATÓRIO)
      - variableSetName: nome do Variable Set (OBRIGATÓRIO - usado para registry)
      - parameters: lista de parâmetros do contrato (OBRIGATÓRIO), cada um com:
          * name: nome do parâmetro
          * direction: "IN", "OUT" ou "INOUT" (maiúsculas)
          * bomType: tipo BOM (nome da classe do vocabulário)
    
    Parâmetros OPCIONAIS:
      - baselineName: branch/baseline (padrão: "Main")
      - rulesetName: nome do ruleset para runtime (recomendado)
      - description: descrição da operation
      - rulesetParameters: dict com pares chave-valor extras para o ruleset
    
    Exemplo correto (baseado em test_operation_ruleflow.json):
    ```python
    criar_operation(
        projectName="DS-FinanciamentoImobiliario",
        operationName="CalcularFinanciamento",
        ruleflowName="Fluxo de Calculo de Financiamento",
        variableSetName="variaveis",
        parameters=[
            {"name": "credito", "direction": "IN", "bomType": "credito"},
            {"name": "elegivel", "direction": "OUT", "bomType": "booleano"},
            {"name": "financiamento", "direction": "INOUT", "bomType": "financiamento"}
        ],
        rulesetName="FinanciamentoRuleset",
        description="Operação para calcular financiamento imobiliário"
    )
    ```
    
    Retorna:
      Dict com informações da operation criada, incluindo:
      - operationName
      - dsmRuleflowLinked (ruleflow associado)
      - parameters (lista de parâmetros)
      - registry (Variable Sets registrados)
      - status
    """
    payload = {
        "projectName": projectName,
        "baselineName": baselineName,
        "operationName": operationName,
        "variableSetName": variableSetName
    }
    
    # Ruleflow (obrigatório)
    payload["ruleflow"] = {"ruleflowName": ruleflowName}
    
    # Parameters (obrigatório)
    payload["parameters"] = parameters
    
    # Registry (usa o mesmo variableSetName para todos)
    payload["registry"] = {
        "descriptorSets": [variableSetName],
        "paramsSets": [variableSetName],
        "rulesetParamSets": [variableSetName]
    }
    
    # Opcionais
    if description:
        payload["description"] = description
    if rulesetName:
        payload["rulesetName"] = rulesetName
    if rulesetParameters:
        payload["rulesetParameters"] = rulesetParameters
    
    return java.post(
        "operations",
        params={"action": "create"},
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"}
    )


@mcp.tool()
def atualizar_operation(
    projectName: str,
    operationName: str,
    baselineName: str = "Main",
    ruleflowName: str = None,
    ruleflowPackage: str = None,
    parameters: list = None,
    rulesetParameters: dict = None,
    descriptorSets: list = None,
    paramsSets: list = None,
    rulesetParamSets: list = None,
    packagePath: str = None,
    description: str = None,
    rulesetName: str = None,
    variableSetName: str = None
):
    """
    Atualiza uma Decision Operation existente (PUT /operations?action=update).
    
    Permite modificar:
    - Ruleflow associado
    - Parâmetros do contrato
    - Variable Sets registrados
    - Configurações de runtime
    - Descrição
    
    Parâmetros: (mesmos de criar_operation)
      - projectName: nome do projeto/Decision Service (obrigatório)
      - operationName: nome da operation a atualizar (obrigatório)
      - baselineName: branch/baseline (padrão: "Main")
      - [demais parâmetros opcionais conforme criar_operation]
    
    Nota: Apenas os parâmetros fornecidos serão atualizados.
          Parâmetros omitidos mantêm seus valores atuais.
    
    Retorna:
      Dict com informações da operation atualizada.
    """
    payload = {
        "projectName": projectName,
        "baselineName": baselineName,
        "operationName": operationName
    }
    
    # Ruleflow
    if ruleflowName:
        ruleflow_data = {"ruleflowName": ruleflowName}
        if ruleflowPackage:
            ruleflow_data["packageName"] = ruleflowPackage
        payload["ruleflow"] = ruleflow_data
    
    # Parameters (contrato)
    if parameters:
        payload["parameters"] = parameters
    
    # Ruleset parameters
    if rulesetParameters:
        payload["rulesetParameters"] = rulesetParameters
    
    # Registry (Variable Sets)
    registry = {}
    if descriptorSets:
        registry["descriptorSets"] = descriptorSets
    if paramsSets:
        registry["paramsSets"] = paramsSets
    if rulesetParamSets:
        registry["rulesetParamSets"] = rulesetParamSets
    if registry:
        payload["registry"] = registry
    
    # Opcionais
    if packagePath:
        payload["packagePath"] = packagePath
    if description:
        payload["description"] = description
    if rulesetName:
        payload["rulesetName"] = rulesetName
    if variableSetName:
        payload["variableSetName"] = variableSetName
    
    return java.put(
        "operations",
        params={"action": "update"},
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"}
    )


@mcp.tool()
def visualizar_operation(
    projectName: str,
    operationName: str,
    baselineName: str = "Main",
    descriptorSets: list = None,
    paramsSets: list = None,
    rulesetParamSets: list = None
):
    """
    Visualiza detalhes de uma Decision Operation (GET /operations?action=view).
    
    Retorna informações completas sobre a operation, incluindo:
    - Nome e descrição
    - Ruleflow associado
    - Parâmetros do contrato (entrada/saída)
    - Variable Sets registrados
    - Configurações de runtime
    
    Parâmetros:
      - projectName: nome do projeto/Decision Service (obrigatório)
      - operationName: nome da operation (obrigatório)
      - baselineName: branch/baseline (padrão: "Main")
      - descriptorSets: lista de Variable Sets para incluir na visualização (opcional)
      - paramsSets: lista de Variable Sets para incluir na visualização (opcional)
      - rulesetParamSets: lista de Variable Sets para incluir na visualização (opcional)
    
    Exemplo de uso:
    ```python
    visualizar_operation(
        projectName="MeuProjeto",
        operationName="AprovarCredito",
        descriptorSets=["GlobalVariables"]
    )
    ```
    
    Retorna:
      Dict com:
      - operationName: nome da operation
      - dsmRuleflowLinked: ruleflow associado (se houver)
      - parameters: lista de parâmetros com name, direction, bomType
      - registry: Variable Sets registrados
      - description: descrição
      - packagePath: caminho do pacote
      - runtimeRulesetName: nome do ruleset (se configurado)
    """
    params = {
        "projectName": projectName,
        "baselineName": baselineName,
        "operationName": operationName
    }
    
    # Adicionar Variable Sets se fornecidos
    payload = {}
    registry = {}
    if descriptorSets:
        registry["descriptorSets"] = descriptorSets
    if paramsSets:
        registry["paramsSets"] = paramsSets
    if rulesetParamSets:
        registry["rulesetParamSets"] = rulesetParamSets
    if registry:
        payload["registry"] = registry
    
    if payload:
        return java.get(
            "operations",
            params={**params, "action": "view"},
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"}
        )
    else:
        return java.get(
            "operations",
            params={**params, "action": "view"}
        )

# Made with Bob
