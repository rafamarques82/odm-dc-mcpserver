"""
Chatbot Tools - IBM watsonx.ai Integration
------------------------------------------
Ferramentas MCP para interagir com chatbot usando IBM watsonx.ai
"""

import os
import json
import logging
import sys
import builtins
from pathlib import Path

log = logging.getLogger(__name__)

# Importa o cliente watsonx.ai
try:
    # Adiciona o diretório watsonaix ao path
    watsonaix_path = Path(__file__).parent.parent / "watsonaix"
    sys.path.insert(0, str(watsonaix_path))
    
    from llm import IBMWatsonxClient
    
    # Carrega configuração
    config_path = watsonaix_path / "config.json"
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Permite sobrescrever com variáveis de ambiente
        api_key = os.getenv("IBM_WATSONX_API_KEY", config["ibm_watsonx"]["api_key"])
        project_id = os.getenv("IBM_WATSONX_PROJECT_ID", config["ibm_watsonx"]["project_id"])
        region = os.getenv("IBM_WATSONX_REGION", config["ibm_watsonx"]["region"])
        model_id = os.getenv("IBM_WATSONX_MODEL_ID", config["ibm_watsonx"]["model_id"])
        
        # Verifica se as credenciais foram configuradas
        if api_key == "YOUR_API_KEY" or project_id == "YOUR_PROJECT_ID":
            log.warning("IBM watsonx.ai não configurado. Configure as credenciais em watsonaix/config.json ou via variáveis de ambiente.")
            watsonx_client = None
        else:
            watsonx_client = IBMWatsonxClient(api_key, project_id, region, model_id)
            log.info("Cliente IBM watsonx.ai inicializado com sucesso")
    else:
        log.warning(f"Arquivo de configuração não encontrado: {config_path}")
        watsonx_client = None
        
except Exception as e:
    log.error(f"Erro ao inicializar cliente watsonx.ai: {e}")
    watsonx_client = None


# Histórico de conversação (em memória - para produção, use um banco de dados)
conversation_history = {}


@builtins.mcp.tool()
def chatbot_send_message(message: str, conversation_id: str = "default", 
                        max_tokens: int = 500, temperature: float = 0.7) -> dict:
    """
    Envia uma mensagem para o chatbot e recebe uma resposta.
    
    Args:
        message: Mensagem do usuário
        conversation_id: ID da conversa para manter contexto (padrão: "default")
        max_tokens: Número máximo de tokens na resposta (padrão: 500)
        temperature: Controla criatividade da resposta 0.0-1.0 (padrão: 0.7)
    
    Returns:
        dict: Resposta do chatbot com status e conteúdo
    
    Example:
        >>> chatbot_send_message("Olá, como você pode me ajudar?")
        {"status": "success", "response": "Olá! Posso ajudá-lo com...", "conversation_id": "default"}
    """
    if watsonx_client is None:
        return {
            "status": "error",
            "error": "IBM watsonx.ai não está configurado. Configure as credenciais em watsonaix/config.json",
            "message": message
        }
    
    try:
        # Recupera ou cria histórico da conversa
        if conversation_id not in conversation_history:
            conversation_history[conversation_id] = []
        
        # Adiciona mensagem do usuário ao histórico
        conversation_history[conversation_id].append({
            "role": "user",
            "content": message
        })
        
        # Gera resposta usando o histórico completo
        response = watsonx_client.generate_chat_response(
            messages=conversation_history[conversation_id],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Adiciona resposta do assistente ao histórico
        conversation_history[conversation_id].append({
            "role": "assistant",
            "content": response
        })
        
        log.info(f"Chatbot respondeu para conversa {conversation_id}")
        
        return {
            "status": "success",
            "response": response,
            "conversation_id": conversation_id,
            "message_count": len(conversation_history[conversation_id])
        }
        
    except Exception as e:
        log.error(f"Erro ao processar mensagem do chatbot: {e}")
        return {
            "status": "error",
            "error": str(e),
            "message": message
        }


@builtins.mcp.tool()
def chatbot_clear_conversation(conversation_id: str = "default") -> dict:
    """
    Limpa o histórico de uma conversa específica.
    
    Args:
        conversation_id: ID da conversa a ser limpa (padrão: "default")
    
    Returns:
        dict: Status da operação
    
    Example:
        >>> chatbot_clear_conversation("default")
        {"status": "success", "message": "Conversa 'default' limpa com sucesso"}
    """
    try:
        if conversation_id in conversation_history:
            del conversation_history[conversation_id]
            log.info(f"Histórico da conversa {conversation_id} limpo")
            return {
                "status": "success",
                "message": f"Conversa '{conversation_id}' limpa com sucesso"
            }
        else:
            return {
                "status": "info",
                "message": f"Conversa '{conversation_id}' não existe ou já está vazia"
            }
    except Exception as e:
        log.error(f"Erro ao limpar conversa: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@builtins.mcp.tool()
def chatbot_get_conversation_history(conversation_id: str = "default") -> dict:
    """
    Recupera o histórico de uma conversa.
    
    Args:
        conversation_id: ID da conversa (padrão: "default")
    
    Returns:
        dict: Histórico da conversa
    
    Example:
        >>> chatbot_get_conversation_history("default")
        {"status": "success", "conversation_id": "default", "messages": [...]}
    """
    try:
        if conversation_id in conversation_history:
            return {
                "status": "success",
                "conversation_id": conversation_id,
                "messages": conversation_history[conversation_id],
                "message_count": len(conversation_history[conversation_id])
            }
        else:
            return {
                "status": "info",
                "conversation_id": conversation_id,
                "messages": [],
                "message_count": 0,
                "message": "Conversa não encontrada ou vazia"
            }
    except Exception as e:
        log.error(f"Erro ao recuperar histórico: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@builtins.mcp.tool()
def chatbot_list_conversations() -> dict:
    """
    Lista todas as conversas ativas.
    
    Returns:
        dict: Lista de IDs de conversas e contagem de mensagens
    
    Example:
        >>> chatbot_list_conversations()
        {"status": "success", "conversations": [{"id": "default", "message_count": 4}]}
    """
    try:
        conversations = [
            {
                "id": conv_id,
                "message_count": len(messages)
            }
            for conv_id, messages in conversation_history.items()
        ]
        
        return {
            "status": "success",
            "conversations": conversations,
            "total_conversations": len(conversations)
        }
    except Exception as e:
        log.error(f"Erro ao listar conversas: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@builtins.mcp.tool()
def chatbot_configure(api_key: str = None, project_id: str = None, 
                     region: str = None, model_id: str = None) -> dict:
    """
    Configura ou atualiza as credenciais do IBM watsonx.ai em tempo de execução.
    
    Args:
        api_key: API key do IBM Cloud (opcional)
        project_id: ID do projeto watsonx.ai (opcional)
        region: Região do serviço (opcional)
        model_id: ID do modelo a usar (opcional)
    
    Returns:
        dict: Status da configuração
    
    Example:
        >>> chatbot_configure(api_key="nova_key", project_id="novo_id")
        {"status": "success", "message": "Cliente watsonx.ai reconfigurado"}
    """
    global watsonx_client
    
    try:
        # Carrega configuração atual
        config_path = Path(__file__).parent.parent / "watsonaix" / "config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Atualiza apenas os parâmetros fornecidos
        if api_key:
            config["ibm_watsonx"]["api_key"] = api_key
        if project_id:
            config["ibm_watsonx"]["project_id"] = project_id
        if region:
            config["ibm_watsonx"]["region"] = region
        if model_id:
            config["ibm_watsonx"]["model_id"] = model_id
        
        # Salva configuração atualizada
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Reinicializa o cliente
        watsonx_client = IBMWatsonxClient(
            config["ibm_watsonx"]["api_key"],
            config["ibm_watsonx"]["project_id"],
            config["ibm_watsonx"]["region"],
            config["ibm_watsonx"]["model_id"]
        )
        
        log.info("Cliente watsonx.ai reconfigurado com sucesso")
        
        return {
            "status": "success",
            "message": "Cliente watsonx.ai reconfigurado com sucesso",
            "config": {
                "region": config["ibm_watsonx"]["region"],
                "model_id": config["ibm_watsonx"]["model_id"]
            }
        }
        
    except Exception as e:
        log.error(f"Erro ao configurar watsonx.ai: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


log.info("Módulo tools_chatbot carregado com sucesso")

# Made with Bob
