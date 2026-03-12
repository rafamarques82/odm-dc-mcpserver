
# -*- coding: utf-8 -*-
"""
DecisionCenterClient
--------------------

Cliente REST completo para comunicação com o IBM Decision Center.

Este módulo encapsula toda a interação via REST com:

- Decision Services,
- Branches,
- Test Suites,
- Reports,
- Deployments,
- Servers,
- Regras, Ruleflows, Decision Tables (via REST quando suportado),
- Qualquer outro endpoint oficial do Decision Center.

O objetivo é fornecer um acesso consistente, confiável e reutilizável
para todas as ferramentas (tools) do MCP, isolando a lógica de HTTP
em uma única classe bem definida.

O MCP chamará este cliente através dos módulos em /tools.

Este cliente também fornece tratamento de falhas, normalização de
URLs, sessões persistentes e cabeçalhos padrão.
"""

import requests
from requests.auth import HTTPBasicAuth
from typing import Dict, Any, Optional


class DecisionCenterClient:
    """
    Classe responsável por realizar chamadas REST ao Decision Center
    (DC), encapsulando autenticação, headers e tratamento de erros.

    Esta classe é utilizada por ferramentas do MCP no módulo
    tools_decisioncenter.py e outros que precisem do DC diretamente.

    Parâmetros:
    - base_url (str): URL base do Decision Center (ex: http://host:9060/decisioncenter-api/v1)
    - username (str): Usuário para autenticação básica
    - password (str): Senha do usuário

    Recursos Internos:
    - Sessão HTTP persistente para reduzir overhead
    - Métodos GET e POST padronizados
    - Normalização automática das URLs
    """

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password

        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(username, password)
        self.session.headers.update({"Accept": "application/json"})

    # -------------------------------------------------------------
    # MÉTODOS DE APOIO
    # -------------------------------------------------------------
    def _build_url(self, path: str) -> str:
        path = path.strip("/")
        return f"{self.base_url}/{path}"

    # -------------------------------------------------------------
    # MÉTODO GET PADRONIZADO
    # -------------------------------------------------------------
    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executa uma requisição GET ao Decision Center.

        Parâmetros:
        - path (str): Caminho relativo ao endpoint do DC.
        - params (dict|None): Parâmetros query opcionais.

        Retorno:
        - Dicionário decodificado do JSON, ou {"error": "..."} em caso de falha.
        """
        try:
            url = self._build_url(path)
            r = self.session.get(url, params=params, timeout=60)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            return {"error": f"GET {path} failed: {e}"}

    # -------------------------------------------------------------
    # MÉTODO POST PADRONIZADO
    # -------------------------------------------------------------
    def post(self, path: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executa uma requisição POST ao Decision Center.

        Parâmetros:
        - path (str): Caminho relativo do endpoint.
        - payload (dict|None): Corpo JSON enviado ao DC.

        Retorno:
        - JSON do DC ou {"error": "..."} caso haja erro.
        """
        try:
            url = self._build_url(path)
            r = self.session.post(url, json=payload, timeout=120)
            r.raise_for_status()

            # Algumas chamadas retornam 204 sem JSON
            try:
                return r.json()
            except ValueError:
                return {"status": r.status_code}

        except Exception as e:
            return {"error": f"POST {path} failed: {e}"}

    # -------------------------------------------------------------
    # MÉTODO POST COM UPLOAD DE ARQUIVO
    # -------------------------------------------------------------
    def post_file(self, path: str, file_path: str, field_name: str = "file") -> Dict[str, Any]:
        """
        Executa uma requisição POST com upload de arquivo ao Decision Center.

        Parâmetros:
        - path (str): Caminho relativo do endpoint.
        - file_path (str): Caminho completo do arquivo a ser enviado.
        - field_name (str): Nome do campo do formulário (padrão: "file").

        Retorno:
        - JSON do DC ou {"error": "..."} caso haja erro.
        """
        try:
            url = self._build_url(path)
            
            # Abre arquivo e faz upload
            with open(file_path, 'rb') as f:
                files = {field_name: (file_path.split('/')[-1], f, 'application/zip')}
                # Remove header Accept: application/json para upload
                headers = dict(self.session.headers)
                headers.pop('Accept', None)
                
                r = self.session.post(
                    url,
                    files=files,
                    headers=headers,
                    timeout=300
                )
                
                # Captura resposta antes de raise_for_status
                response_text = r.text
                response_status = r.status_code
                
                try:
                    r.raise_for_status()
                except Exception as e:
                    # Retorna erro detalhado
                    return {
                        "error": f"POST {path} with file failed: {e}",
                        "status_code": response_status,
                        "response": response_text[:500],  # Primeiros 500 chars
                        "file_path": file_path
                    }

            # Tenta retornar JSON, senão retorna status
            try:
                return r.json()
            except ValueError:
                return {
                    "status": "success",
                    "status_code": r.status_code,
                    "message": "Import successful",
                    "response": response_text[:200]
                }

        except FileNotFoundError:
            return {"error": f"File not found: {file_path}"}
        except Exception as e:
            return {"error": f"POST {path} with file failed: {e}"}
