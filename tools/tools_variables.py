# -*- coding: utf-8 -*-
"""
Tools de Variables:

- listar_variables (listar variáveis)
- visualizar_variable (visualizar variável)
- criar_variable (criar variável)
- atualizar_variable (atualizar variável)
- deletar_variable (deletar variável)
"""

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
def listar_variables(projectName: str, baselineName: str = "Main"):
    """
    Lista todas as variáveis do projeto.

    Ideal para:
    - verificar existência
    - evitar duplicações
    - validar baseline
    """
    return java.get(
        "variables",
        params={"projectName": projectName, "baselineName": baselineName}
    )


@mcp.tool()
def visualizar_variable(projectName: str, variableName: str, baselineName: str = "Main"):
    """
    Detalha uma variável específica.

    Inclui:
    - nome
    - tipo
    - valor
    - descrição
    - metadados
    """
    return java.get(
        "variables",
        params={
            "projectName": projectName,
            "baselineName": baselineName,
            "variableName": variableName
        }
    )


@mcp.tool()
def atualizar_variable(
    projectName: str,
    variableName: str,
    value=None,
    varType: str = None,
    description: str = None,
    baselineName: str = "Main"
):
    """
    Atualiza parcialmente uma variável existente.

    Apenas os valores fornecidos serão alterados.
    """
    payload = {
        "projectName": projectName,
        "baselineName": baselineName,
        "variableName": variableName
    }
    if value is not None:
        payload["value"] = value
    if varType is not None:
        payload["type"] = varType
    if description is not None:
        payload["description"] = description

    return java.put(
        "variables",
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"}
    )


@mcp.tool()
def deletar_variable(projectName: str, variableName: str, baselineName: str = "Main"):
    """
    Remove uma variável do projeto.

    Aviso:
    - Se regras dependem desta variável, podem ocorrer falhas no DC.
    """
    return java.delete(
        "variables",
        params={
            "projectName": projectName,
            "baselineName": baselineName,
            "variableName": variableName
        }
    )


@mcp.tool()
def criar_variaveis_no_variable_set(
    projectName: str,
    variableSetName: str,
    variables: list,
    packageName: str = "",
    baselineName: str = "Main",
    resetIfExists: bool = False
):
    """
    Cria ou atualiza variáveis dentro de um Variable Set no IBM ODM 9.5.
    
    Esta ferramenta usa o endpoint POST /variables do servidor Java para criar
    variáveis de negócio dentro de um Variable Set no Decision Center.
    Suporta criação em lote e tipos BOM complexos.
    
    IMPORTANTE: Para Variable Sets novos (nunca commitados), a primeira execução
    pode falhar com erro de commit. Neste caso, execute a ferramenta NOVAMENTE com os
    mesmos parâmetros - a segunda execução funcionará corretamente pois o
    VariableSet terá sido inicializado na primeira tentativa.
    
    Args:
        projectName: Nome do projeto no Decision Center
        variableSetName: Nome do Variable Set (ex: "variables")
        variables: Lista de dicionários com as variáveis a criar. Cada variável deve ter:
            - name: Nome da variável (obrigatório), não use espaços ou caracteres especiais
            - bomType: Tipo BOM completo (ex: "com.example.Cliente" ou "number")
            - verbalization: Frase de verbalização (opcional)
            - initialValue: Valor inicial em formato IRL (opcional, ex: "10", '"texto"')
        packageName: Nome do pacote (padrão: "" = raiz do projeto)
        baselineName: Nome da baseline (padrão: "Main")
        resetIfExists: Se true, limpa variáveis existentes antes de criar (padrão: false)
    
    Returns:
        Dict com resultado da criação contendo:
        - status: "success" ou "error"
        - variableSetName: Nome do Variable Set
        - variables: Lista de variáveis criadas/atualizadas
        - projectName: Nome do projeto
        - baselineName: Nome da baseline
    
    Example:
        >>> # Criar variáveis de tipos primitivos
        >>> criar_variaveis_no_variable_set(
        ...     projectName="MeuProjeto",
        ...     variableSetName="variables",
        ...     variables=[
        ...         {
        ...             "name": "idade",
        ...             "bomType": "int",
        ...             "verbalization": "a idade",
        ...             "initialValue": "0"
        ...         },
        ...         {
        ...             "name": "nome",
        ...             "bomType": "java.lang.String",
        ...             "verbalization": "o nome",
        ...             "initialValue": '""'
        ...         }
        ...     ]
        ... )
        
        >>> # Criar variáveis de tipos BOM customizados
        >>> criar_variaveis_no_variable_set(
        ...     projectName="MeuProjeto",
        ...     variableSetName="variables",
        ...     packageName="regras.credito",
        ...     variables=[
        ...         {
        ...             "name": "cliente",
        ...             "bomType": "com.example.model.Cliente",
        ...             "verbalization": "o cliente"
        ...         },
        ...         {
        ...             "name": "emprestimo",
        ...             "bomType": "com.example.model.Emprestimo",
        ...             "verbalization": "o empréstimo"
        ...         }
        ...     ]
        ... )
    
    Notas:
        - Servidor Java deve estar rodando (padrão: http://localhost:8080)
        - Configure OTHER_BASE_URL se o servidor estiver em outra porta
        - Tipos BOM devem existir no XOM do projeto
        - initialValue deve estar em formato IRL válido
        - Se resetIfExists=true, TODAS as variáveis do set serão removidas primeiro
    """
    # Valida parâmetros obrigatórios
    if not projectName or not variableSetName:
        return {
            "status": "error",
            "error": "projectName e variableSetName são obrigatórios"
        }
    
    if not variables or not isinstance(variables, list):
        return {
            "status": "error",
            "error": "variables deve ser uma lista não vazia"
        }
    
    # Valida estrutura das variáveis
    for i, var in enumerate(variables):
        if not isinstance(var, dict):
            return {
                "status": "error",
                "error": f"Variável na posição {i} deve ser um dicionário"
            }
        if "name" not in var or not var["name"]:
            return {
                "status": "error",
                "error": f"Variável na posição {i} deve ter 'name' não vazio"
            }
    
    # Monta payload para o backend Java
    payload = {
        "projectName": projectName,
        "packageName": packageName,
        "variableSetName": variableSetName,
        "baselineName": baselineName,
        "resetIfExists": resetIfExists,
        "variables": variables
    }
    
    try:
        # Chama endpoint POST /variables do servidor Java
        result = java.post(
            "variables",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"}
        )
        
        # Verifica se houve erro
        if isinstance(result, dict) and "error" in result:
            return {
                "status": "error",
                "error": result["error"],
                "payload": payload
            }
        
        # Sucesso
        return {
            "status": "success",
            "message": f"Variáveis criadas/atualizadas no Variable Set '{variableSetName}'",
            "result": result,
            "projectName": projectName,
            "baselineName": baselineName,
            "variableSetName": variableSetName,
            "totalVariables": len(variables)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "payload": payload
        }

# Made with Bob
