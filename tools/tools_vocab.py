# -*- coding: utf-8 -*-
"""
Tools de vocabulário do Decision Service.

- consultar_vocabulario (consultar vocabulário)
"""

from mcp.server.fastmcp import FastMCP
from helpers.http_java_client import JavaBackendClient
import os

java = JavaBackendClient(
    base_url=os.getenv("OTHER_BASE_URL", "http://localhost:8080")
)

import builtins
mcp: FastMCP = builtins.__dict__.get("mcp")


@mcp.tool()
def consultar_vocabulario(decisionServiceName: str, baselineName: str):
    """
    Consulta o vocabulário BOM na baseline especificada.

    Retorna:
    - classes
    - propriedades
    - verbalizações
    """
    return java.get(
        "vocabularies",
        params={
            "decisionServiceName": decisionServiceName,
            "baselineName": baselineName
        }
    )

# Made with Bob
