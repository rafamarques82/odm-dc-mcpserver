
# -*- coding: utf-8 -*-
"""
Decision Center MCP Server (Modularizado)
-----------------------------------------

Servidor MCP principal responsável por:
1) Instanciar o MCP (FastMCP).
2) Publicar o MCP em builtins para que os módulos /tools registrem suas tools via @mcp.tool().
3) Importar (com import fixo) todos os módulos de tools.
4) Inicializar o transporte (STDIO por padrão, HTTP opcional).

Estrutura esperada:

mcp_server/
│
├── decision_center_mcp_server.py        # (este arquivo)
│
├── helpers/
│   ├── dc_rest_client.py                # cliente REST para Decision Center
│   └── http_java_client.py              # cliente HTTP p/ servidor Java (ODMHttpServer)
│
└── tools/
    ├── tools_decisioncenter.py          # DC REST (about, DS, branches, tests, deploy)
    ├── tools_rules.py                   # regras (create/edit/view)
    ├── tools_ruleflows.py               # ruleflows (create/update/view)
    ├── tools_decisiontables.py          # Decision Tables (visualizar/criar/atualizar)
    ├── tools_vocab.py                   # vocabulário
    └── tools_variables.py               # variables (listar/visualizar/criar/atualizar/deletar)
"""

import os
import sys
import logging
from mcp.server.fastmcp import FastMCP

# -------------------------------------------------------------------
# LOGGING
# -------------------------------------------------------------------
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
log = logging.getLogger("decision-center-mcp")

# Alguns clientes STDIO são sensíveis a framing; CRLF + flush
try:
    sys.stdout.reconfigure(newline="\r\n", write_through=True)
except Exception:
    pass

# -------------------------------------------------------------------
# CONFIG GERAL DO MCP (via variáveis de ambiente)
# -------------------------------------------------------------------
MCP_TRANSPORT = os.getenv("MCP_TRANSPORT", "stdio").strip().lower()   # "stdio" (default) ou "http"
HTTP_HOST     = os.getenv("HTTP_HOST", "127.0.0.1").strip()
HTTP_PORT     = int(os.getenv("HTTP_PORT", "8000"))
JSON_RESPONSE = os.getenv("JSON_RESPONSE", "false").lower() == "true"

# -------------------------------------------------------------------
# INSTÂNCIA MCP PRINCIPAL
# -------------------------------------------------------------------
mcp = FastMCP("Decision Center MCP", json_response=JSON_RESPONSE)

# -------------------------------------------------------------------
# PUBLICA MCP EM builtins ANTES DE IMPORTAR OS MÓDULOS DE TOOLS
# (necessário pois os decorators @mcp.tool() são avaliados no import)
# -------------------------------------------------------------------
import builtins
builtins.mcp = mcp

# -------------------------------------------------------------------
# IMPORT FIXO DOS MÓDULOS DE TOOLS
# (cada módulo usa builtins.mcp para registrar suas tools via @mcp.tool)
# -------------------------------------------------------------------
from tools.tools_decisioncenter import *   # noqa: F401,F403
from tools.tools_rules import *            # noqa: F401,F403
from tools.tools_ruleflows import *        # noqa: F401,F403
from tools.tools_decisiontables import *   # noqa: F401,F403
from tools.tools_vocab import *            # noqa: F401,F403
from tools.tools_variables import *        # noqa: F401,F403
from tools.tools_operations import *       # noqa: F401,F403
from tools.tools_chatbot import *          # noqa: F401,F403
from tools.tools_project_generator import * # noqa: F401,F403
# -------------------------------------------------------------------
# INICIALIZAÇÃO DO SERVIDOR MCP
# -------------------------------------------------------------------
if __name__ == "__main__":
    try:
        if MCP_TRANSPORT == "http":
            log.info(f"Iniciando servidor MCP (HTTP) em http://{HTTP_HOST}:{HTTP_PORT}/mcp")
            try:
                app = mcp.streamable_http_app()
            except AttributeError:
                # Compatibilidade com versões antigas do SDK
                app = mcp.http_app()

            import uvicorn
            uvicorn.run(app, host=HTTP_HOST, port=HTTP_PORT)
        else:
            log.info("Iniciando servidor MCP (STDIO)")
            mcp.run(transport="stdio")

    except Exception as e:
        log.exception(f"Erro fatal no servidor MCP: {e}")
