#!/usr/bin/env python3
"""
Script de Teste do Chatbot IBM watsonx.ai
==========================================

Este script testa a integração do chatbot com IBM watsonx.ai.
Execute após configurar suas credenciais.
"""

import sys
import json
from pathlib import Path

# Adiciona o diretório watsonaix ao path
watsonaix_path = Path(__file__).parent / "watsonaix"
sys.path.insert(0, str(watsonaix_path))

def test_configuration():
    """Testa se a configuração está correta"""
    print("🔧 Testando configuração...")
    
    config_path = Path(__file__).parent / "watsonaix" / "config.json"
    
    if not config_path.exists():
        print("❌ Arquivo config.json não encontrado")
        return False
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    api_key = config["ibm_watsonx"]["api_key"]
    project_id = config["ibm_watsonx"]["project_id"]
    
    if api_key == "YOUR_API_KEY" or project_id == "YOUR_PROJECT_ID":
        print("❌ Credenciais não configuradas")
        print("   Por favor, edite watsonaix/config.json com suas credenciais")
        return False
    
    print("✅ Configuração OK")
    return True


def test_imports():
    """Testa se as dependências estão instaladas"""
    print("\n📦 Testando dependências...")
    
    try:
        from llm import IBMWatsonxClient
        print("✅ Módulo llm importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar módulo llm: {e}")
        return False
    
    try:
        from ibm_watsonx_ai.foundation_models import Model
        print("✅ ibm-watsonx-ai instalado")
    except ImportError:
        print("❌ ibm-watsonx-ai não instalado")
        print("   Execute: pip install -r watsonaix/requirements.txt")
        return False
    
    return True


def test_client_initialization():
    """Testa a inicialização do cliente"""
    print("\n🔌 Testando inicialização do cliente...")
    
    try:
        from llm import IBMWatsonxClient
        
        config_path = Path(__file__).parent / "watsonaix" / "config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        client = IBMWatsonxClient(
            api_key=config["ibm_watsonx"]["api_key"],
            project_id=config["ibm_watsonx"]["project_id"],
            region=config["ibm_watsonx"]["region"],
            model_id=config["ibm_watsonx"]["model_id"]
        )
        
        print("✅ Cliente inicializado com sucesso")
        return True, client
        
    except Exception as e:
        print(f"❌ Erro ao inicializar cliente: {e}")
        return False, None


def test_simple_generation(client):
    """Testa uma geração simples de texto"""
    print("\n💬 Testando geração de texto...")
    
    try:
        prompt = "Olá! Responda apenas com 'Olá, estou funcionando!'"
        print(f"   Prompt: {prompt}")
        
        response = client.generate_response(
            prompt=prompt,
            max_tokens=50,
            temperature=0.3
        )
        
        print(f"   Resposta: {response}")
        print("✅ Geração de texto funcionando")
        return True
        
    except Exception as e:
        print(f"❌ Erro na geração de texto: {e}")
        print(f"   Detalhes: {type(e).__name__}")
        return False


def test_chat_format(client):
    """Testa o formato de chat"""
    print("\n💭 Testando formato de chat...")
    
    try:
        messages = [
            {"role": "user", "content": "Qual é a capital do Brasil?"}
        ]
        
        response = client.generate_chat_response(
            messages=messages,
            max_tokens=100,
            temperature=0.3
        )
        
        print(f"   Resposta: {response}")
        print("✅ Formato de chat funcionando")
        return True
        
    except Exception as e:
        print(f"❌ Erro no formato de chat: {e}")
        return False


def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("🧪 TESTE DO CHATBOT IBM WATSONX.AI")
    print("=" * 60)
    
    # Teste 1: Configuração
    if not test_configuration():
        print("\n❌ Teste falhou: Configure suas credenciais primeiro")
        print("   Consulte CHATBOT_SETUP_GUIDE.md para instruções")
        return False
    
    # Teste 2: Imports
    if not test_imports():
        print("\n❌ Teste falhou: Instale as dependências")
        print("   Execute: pip install -r watsonaix/requirements.txt")
        return False
    
    # Teste 3: Inicialização
    success, client = test_client_initialization()
    if not success:
        print("\n❌ Teste falhou: Verifique suas credenciais")
        return False
    
    # Teste 4: Geração simples
    if not test_simple_generation(client):
        print("\n❌ Teste falhou: Erro na comunicação com IBM watsonx.ai")
        print("   Verifique:")
        print("   - API key está correta")
        print("   - Project ID está correto")
        print("   - Você tem créditos/quota disponível")
        return False
    
    # Teste 5: Formato de chat
    if not test_chat_format(client):
        print("\n⚠️  Aviso: Formato de chat com problemas")
    
    # Sucesso!
    print("\n" + "=" * 60)
    print("🎉 TODOS OS TESTES PASSARAM!")
    print("=" * 60)
    print("\n✅ Seu chatbot está configurado e funcionando corretamente!")
    print("\nPróximos passos:")
    print("1. Inicie o MCP Server: python3 decision_center_mcp_server_Regras.py")
    print("2. Use as ferramentas do chatbot via MCP")
    print("3. Consulte CHATBOT_SETUP_GUIDE.md para exemplos de uso")
    print()
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Made with Bob
