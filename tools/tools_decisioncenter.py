
# -*- coding: utf-8 -*-
"""
Ferramentas de comunicação com o Decision Center via REST.

Contém: 
- about
- list_decision_services
- list_branches
- list_test_suites
- run_test_suite
- get_test_report
- list_servers
- deploy_ruleapp
- find_decision_service_id_by_name
- get_deployments
- get_rules
- get_ruleflows
- get_packages
- get_branches_and_test_suites
"""

from mcp.server.fastmcp import FastMCP
from helpers.dc_rest_client import DecisionCenterClient

import os

# Instância única do cliente DC
dc = DecisionCenterClient(
    base_url=os.getenv("DC_BASE_URL", "http://my-odm.ibm.com:9060/decisioncenter-api/v1"),
    username=os.getenv("DC_USERNAME", "odmAdmin"),
    password=os.getenv("DC_PASSWORD", "odmAdmin")
)

# MCP é importado dinamicamente pelo servidor principal
import builtins
mcp: FastMCP = builtins.__dict__.get("mcp")


@mcp.tool()
def about():
    """
    Retorna informações do endpoint /about do Decision Center.
    """
    return dc.get("about")


@mcp.tool()
def list_decision_services():
    """
    Lista todos os Decision Services presentes no repositório DC.
    """
    return dc.get("decisionservices")


@mcp.tool()
def list_branches(decision_service_id: str):
    """
    Lista branches de um Decision Service específico.

    Parâmetros:
    - decision_service_id: ID do Decision Service.
    """
    return dc.get(f"decisionservices/{decision_service_id}/branches")


@mcp.tool()
def list_test_suites(decision_service_id: str):
    """
    Lista test suites de um Decision Service.

    Parâmetros:
    - decision_service_id: ID do Decision Service.
    """
    return dc.get(f"decisionservices/{decision_service_id}/testsuites")


@mcp.tool()
def run_test_suite(test_suite_id: str):
    """
    Executa um test suite e retorna testReportId e status.
    """
    return dc.post(f"testsuites/{test_suite_id}/run")

@mcp.tool()
def get_exemplo(decision_service_id: str):
    """
    Projeto de exemplo contendo:
    - Regras formatadas corretamente;
    - Decision Tables formatadas corretamente;
    - Fluxos de regras (ruleflows)  formatados corretamente;
    Deve ser executado quando der erro na criação de regras, ruleflows ou decision table.

    Um exemplo de criação de regras, ruleflows e decision table .
    """
    return dc.get("projects/d968001f-96b2-4c73-9bfa-72d2984c3e4f/rules?withContent=true&useDependencies=true")

@mcp.tool()
def get_test_report(test_report_id: str):
    """
    Recupera relatório de teste por ID.
    """
    return dc.get(f"testreports/{test_report_id}")


@mcp.tool()
def list_servers():
    """
    Lista servidores configurados para deploy (RES targets).
    """
    return dc.get("servers")


@mcp.tool()
def deploy_ruleapp(deployment_id: str):
    """
    Realiza deploy de RuleApp para um RES.

    Parâmetros:
    - deployment_id: ID da deployment configuration.
    """
    return dc.post(f"deployments/{deployment_id}/deploy")


@mcp.tool()
def find_decision_service_id_by_name(name: str):
    """
    Busca o ID de um Decision Service pelo nome.
    """
    data = dc.get("decisionservices")
    elements = data.get("elements", [])
    for el in elements:
        if el.get("name") == name:
            return el.get("id")
    return None


@mcp.tool()
def get_deployments(decision_service_id: str):
    """
    Lista configurações de deploy de um Decision Service.
    """
    return dc.get(f"decisionservices/{decision_service_id}/deployments")


@mcp.tool()
def get_rules(decision_service_id: str):
    """
    Retorna todas as regras do projeto com conteúdo incluído.
    """
    return dc.get(f"projects/{decision_service_id}/rules?withContent=true&useDependencies=true")


@mcp.tool()
def get_ruleflows(decision_service_id: str):
    """
    Retorna todos os ruleflows do projeto.
    """
    return dc.get(f"projects/{decision_service_id}/ruleflows?withImage=false&useDependencies=true")


@mcp.tool()
def get_packages(decision_service_id: str):
    """
    Lista packages (pastas) de um projeto.
    """
    return dc.get(f"projects/{decision_service_id}/folders?useDependencies=true")


@mcp.tool()
def get_branches_and_test_suites(name: str):
    """
    Retorna branches e test suites dado o nome do Decision Service.
    """
    dsid = find_decision_service_id_by_name(name)
    if not dsid:
        return {"error": f"Decision Service '{name}' não encontrado"}

    branches = dc.get(f"decisionservices/{dsid}/branches")
    suites = dc.get(f"decisionservices/{dsid}/testsuites")
    return {
        "decisionServiceId": dsid,
        "branches": branches,
        "testsuites": suites
    }


@mcp.tool()
def importar_projeto(zip_path: str):
    """
    Importa um projeto ODM (arquivo .zip) para o Decision Center.
    
    Esta tool usa o endpoint REST /decisionservices/import para importar
    um arquivo .zip de projeto ODM gerado pelo Rule Designer ou pela tool
    'criar_projeto_odm'.
    
    ⚠️ IMPORTANTE: WORKFLOW OBRIGATÓRIO APÓS IMPORTAÇÃO ⚠️
    
    Após importar o projeto, você DEVE SEMPRE:
    1. Chamar list_decision_services() para validar que o projeto foi criado
    2. Se um documento (PDF/DOCX/XLSX) foi fornecido pelo usuário:
       a. Analisar o documento para identificar TODAS as regras de negócio
       b. Criar CADA regra usando criar_regra()
       c. Criar decision tables se houver usando criar_decision_table()
       d. Criar ruleflow para organizar execução usando criar_ruleflow()
       e. Validar que TODAS as regras foram criadas com sucesso
    
    NÃO deixe o projeto vazio se houver regras no documento!
    
    WORKFLOW OBRIGATÓRIO:
    1. importar_projeto(zip_path) -> Importa o projeto
    2. list_decision_services() -> VALIDA que o projeto foi criado
    3. [SE DOCUMENTO] Analisar documento e criar TODAS as regras/DTs/flows
    4. Validar criação completa
    
    Args:
        zip_path: Caminho completo do arquivo .zip a ser importado
                  (ex: "/tmp/odm_projects/MeuProjeto.zip")
    
    Returns:
        Dict com resultado da importação:
        {
            "status": "success" ou "error",
            "message": "Mensagem de sucesso/erro",
            "decision_service_id": "ID do DS criado" (se sucesso)
        }
    
    Workflow Recomendado Completo:
        1. criar_projeto_odm() -> gera .zip
        2. importar_projeto() -> importa no DC
        3. list_decision_services() -> VALIDA importação (OBRIGATÓRIO)
        4. [SE DOCUMENTO] Criar TODAS as regras/DTs/flows do documento
        5. Validar que tudo foi criado corretamente
    
    Example:
        >>> # Criar projeto
        >>> resultado = criar_projeto_odm("MeuProjeto")
        >>>
        >>> # Importar
        >>> importar_projeto(resultado["zip_path"])
        {
            "status": "success",
            "message": "Projeto importado com sucesso",
            "decision_service_id": "abc-123-def"
        }
        >>>
        >>> # VALIDAR (OBRIGATÓRIO)
        >>> list_decision_services()
        # Confirma que o projeto "MeuProjeto" está na lista
    
    Notas:
        - O arquivo .zip deve existir no caminho especificado
        - O Decision Center deve estar acessível
        - Credenciais devem estar configuradas (DC_USERNAME, DC_PASSWORD)
        - Se o projeto já existir, pode ocorrer erro de duplicação
        - SEMPRE valide com list_decision_services() após importar
    """
    import os
    
    # Valida se o arquivo existe
    if not os.path.exists(zip_path):
        return {
            "status": "error",
            "error": f"Arquivo não encontrado: {zip_path}"
        }
    
    # Valida extensão
    if not zip_path.endswith('.zip'):
        return {
            "status": "error",
            "error": "O arquivo deve ter extensão .zip"
        }
    
    # Faz upload do arquivo
    result = dc.post_file("decisionservices/import", zip_path, field_name="file")
    
    # Processa resultado
    if "error" in result:
        return {
            "status": "error",
            "error": result["error"],
            "zip_path": zip_path
        }
    
    # Sucesso - tenta extrair ID do decision service criado
    decision_service_id = result.get("id") or result.get("decisionServiceId")
    
    return {
        "status": "success",
        "message": "Projeto importado com sucesso no Decision Center",
        "decision_service_id": decision_service_id,
        "zip_path": zip_path,
        "response": result
    }


# Tool criar_variaveis_no_variable_set foi movida para tools/tools_variables.py
