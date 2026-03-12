
# -*- coding: utf-8 -*-
"""
JavaBackendClient
-----------------

Cliente HTTP responsável por comunicar-se com seu servidor Java
(ODMHttpServer), que contém:

- Regras (create/edit/view)
- Ruleflows (create/update/view)
- Decision Tables (visualizar/criar/atualizar)
- Vocabulário
- Variables (NOVO)
- Projetos

Este módulo é utilizado por TODOS os tools em /tools que dependem do
backend Java (tudo exceto algumas chamadas REST do DC).

Objetivo:
---------

Reunir em uma única classe toda lógica de:

- GET /rules, /projects, /vocabularies, /ruleflows, /decisiontables, /variables
- POST
- PUT
- DELETE (para variables, por exemplo)

Comportamento:
--------------

- Sessão reutilizada
- URLs normalizadas
- Tratamento de erros padronizado
- Retorno JSON quando possível
"""

import requests
from typing import Dict, Any, Optional


class JavaBackendClient:
    """
    Cliente HTTP para o servidor Java (ODMHttpServer).

    Parâmetros:
    - base_url (str): Ex: http://localhost:8080

    Recursos:
    - Sessão persistente
    - GET, POST, PUT, DELETE padronizados
    - Tratamento consistente de erros
    """

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    # ----------------------------------------------------------
    # Normaliza path
    # ----------------------------------------------------------
    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    # ----------------------------------------------------------
    # GET
    # ----------------------------------------------------------
    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executa GET no servidor Java.

        Retorno sempre é JSON quando possível.
        """
        try:
            r = self.session.get(self._url(path), params=params, timeout=60)
            r.raise_for_status()
            try:
                return r.json()
            except ValueError:
                # JSON inválido, mas status OK
                return {
                    "success": True,
                    "status": r.status_code,
                    "message": "Operação concluída com sucesso",
                    "response_text": r.text[:200]
                }
        except requests.exceptions.HTTPError as e:
            return {"error": f"HTTP {e.response.status_code}: {str(e)}"}
        except Exception as e:
            return {"error": str(e)}

    # ----------------------------------------------------------
    # POST
    # ----------------------------------------------------------
    def post(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Executa POST no backend Java.

        - params = query string
        - data = body (string)
        - headers = Content-Type, etc.
        """
        try:
            r = self.session.post(
                self._url(path),
                params=params,
                data=data,
                headers=headers or {},
                timeout=120
            )
            r.raise_for_status()
            ct = r.headers.get("Content-Type", "")

            # Tenta parsear JSON, mas se falhar retorna sucesso com texto
            if "application/json" in ct:
                try:
                    return r.json()
                except ValueError:
                    # JSON inválido, mas status OK - considera sucesso
                    return {
                        "success": True,
                        "status": r.status_code,
                        "message": "Operação concluída com sucesso",
                        "response_text": r.text[:200]  # Primeiros 200 chars
                    }
            else:
                # Não é JSON, retorna sucesso com informações básicas
                return {
                    "success": True,
                    "status": r.status_code,
                    "contentType": ct,
                    "response_text": r.text[:200] if r.text else ""
                }

        except requests.exceptions.HTTPError as e:
            # Erro HTTP (4xx, 5xx)
            return {"error": f"HTTP {e.response.status_code}: {str(e)}"}
        except Exception as e:
            return {"error": str(e)}

    # ----------------------------------------------------------
    # PUT
    # ----------------------------------------------------------
    def put(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Executa PUT no backend Java.
        """
        try:
            r = self.session.put(
                self._url(path),
                params=params,
                data=data,
                headers=headers or {},
                timeout=120
            )
            r.raise_for_status()
            ct = r.headers.get("Content-Type", "")

            # Tenta parsear JSON, mas se falhar retorna sucesso com texto
            if "application/json" in ct:
                try:
                    return r.json()
                except ValueError:
                    # JSON inválido, mas status OK - considera sucesso
                    return {
                        "success": True,
                        "status": r.status_code,
                        "message": "Operação concluída com sucesso",
                        "response_text": r.text[:200]  # Primeiros 200 chars
                    }
            else:
                # Não é JSON, retorna sucesso com informações básicas
                return {
                    "success": True,
                    "status": r.status_code,
                    "contentType": ct,
                    "response_text": r.text[:200] if r.text else ""
                }

        except requests.exceptions.HTTPError as e:
            # Erro HTTP (4xx, 5xx)
            return {"error": f"HTTP {e.response.status_code}: {str(e)}"}
        except Exception as e:
            return {"error": str(e)}

    # ----------------------------------------------------------
    # DELETE
    # ----------------------------------------------------------
    def delete(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa DELETE no backend Java.

        Usado principalmente em:
        - /variables
        """
        try:
            r = self.session.delete(self._url(path), params=params, timeout=60)
            r.raise_for_status()
            ct = r.headers.get("Content-Type", "")

            # Tenta parsear JSON, mas se falhar retorna sucesso com texto
            if "application/json" in ct:
                try:
                    return r.json()
                except ValueError:
                    # JSON inválido, mas status OK - considera sucesso
                    return {
                        "success": True,
                        "status": r.status_code,
                        "message": "Operação concluída com sucesso",
                        "response_text": r.text[:200]
                    }
            else:
                # Não é JSON, retorna sucesso com informações básicas
                return {
                    "success": True,
                    "status": r.status_code,
                    "contentType": ct,
                    "response_text": r.text[:200] if r.text else ""
                }

        except requests.exceptions.HTTPError as e:
            return {"error": f"HTTP {e.response.status_code}: {str(e)}"}
        except Exception as e:
            return {"error": str(e)}
