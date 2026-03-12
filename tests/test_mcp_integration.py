#!/usr/bin/env python3
"""
Script de Teste de Integração MCP + Chatbot
============================================

Este script testa se as ferramentas do chatbot estão corretamente
integradas ao MCP Server.
"""

import sys
import json
import time
import asyncio
from pathlib import Path

# Adiciona o diretório do projeto ao path
project_path = Path(__file__).parent
sys.path.insert(0, str(project_path))

def test_mcp_server_import():
    """Testa se o MCP Server pode ser importado"""
    print("=" * 70)
    print("🧪 TESTE DE INTEGRAÇÃO MCP + CHATBOT")
    print("=" * 70)
    print()
    
    print("1️⃣ Testando importação do MCP Server...")
    try:
        # Importa o módulo principal
        import builtins
        from mcp.server.fastmcp import FastMCP
        
        # Cria instância MCP
        mcp = FastMCP("Test MCP", json_response=False)
        builtins.mcp = mcp
        
        print("   ✅ FastMCP importado com sucesso")
        return True, mcp
    except ImportError as e:
        print(f"   ❌ Erro ao importar FastMCP: {e}")
        print("   Execute: pip install mcp")
        return False, None


def test_chatbot_tools_import(mcp):
    """Testa se as ferramentas do chatbot podem ser importadas"""
    print("\n2️⃣ Testando importação das ferramentas do chatbot...")
    try:
        # Importa o módulo de ferramentas
        from tools import tools_chatbot
        
        print("   ✅ Módulo tools_chatbot importado com sucesso")
        return True
    except Exception as e:
        print(f"   ❌ Erro ao importar tools_chatbot: {e}")
        return False


async def test_list_tools(mcp):
    """Lista todas as ferramentas registradas no MCP"""
    print("\n3️⃣ Listando ferramentas registradas no MCP...")
    try:
        tools = await mcp.list_tools()
        
        chatbot_tools = [t for t in tools if 'chatbot' in t.name.lower()]
        
        if not chatbot_tools:
            print("   ⚠️  Nenhuma ferramenta de chatbot encontrada")
            print("   Ferramentas disponíveis:")
            for tool in tools:
                print(f"      - {tool.name}")
            return False
        
        print(f"   ✅ {len(chatbot_tools)} ferramentas de chatbot encontradas:")
        for tool in chatbot_tools:
            print(f"      ✓ {tool.name}")
            if hasattr(tool, 'description') and tool.description:
                desc = tool.description.split('\n')[0][:60]
                print(f"        {desc}...")
        
        return True
    except Exception as e:
        print(f"   ❌ Erro ao listar ferramentas: {e}")
        return False


async def test_chatbot_send_message(mcp):
    """Testa a ferramenta chatbot_send_message"""
    print("\n4️⃣ Testando chatbot_send_message...")
    try:
        # Busca a ferramenta
        tools = await mcp.list_tools()
        send_message_tool = None
        
        for tool in tools:
            if tool.name == 'chatbot_send_message':
                send_message_tool = tool
                break
        
        if not send_message_tool:
            print("   ❌ Ferramenta chatbot_send_message não encontrada")
            return False
        
        print("   📤 Enviando mensagem de teste...")
        
        # Testa a ferramenta
        result = await mcp.call_tool(
            'chatbot_send_message',
            {
                'message': 'Olá! Este é um teste de integração. Responda apenas com "Teste OK".',
                'conversation_id': 'test_integration',
                'max_tokens': 50,
                'temperature': 0.3
            }
        )
        
        # Verifica o resultado
        if isinstance(result, list) and len(result) > 0:
            content = result[0].text if hasattr(result[0], 'text') else str(result[0])
            result_dict = json.loads(content) if isinstance(content, str) else content
        else:
            result_dict = result
        
        if result_dict.get('status') == 'success':
            response = result_dict.get('response', '')
            print(f"   ✅ Resposta recebida: {response[:100]}...")
            return True
        elif result_dict.get('status') == 'error':
            error = result_dict.get('error', 'Erro desconhecido')
            print(f"   ❌ Erro na ferramenta: {error}")
            return False
        else:
            print(f"   ⚠️  Resposta inesperada: {result_dict}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro ao testar ferramenta: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_chatbot_list_conversations(mcp):
    """Testa a ferramenta chatbot_list_conversations"""
    print("\n5️⃣ Testando chatbot_list_conversations...")
    try:
        result = await mcp.call_tool('chatbot_list_conversations', {})
        
        if isinstance(result, list) and len(result) > 0:
            content = result[0].text if hasattr(result[0], 'text') else str(result[0])
            result_dict = json.loads(content) if isinstance(content, str) else content
        else:
            result_dict = result
        
        if result_dict.get('status') == 'success':
            conversations = result_dict.get('conversations', [])
            print(f"   ✅ {len(conversations)} conversa(s) ativa(s)")
            for conv in conversations:
                print(f"      - {conv.get('id')}: {conv.get('message_count')} mensagens")
            return True
        else:
            print(f"   ⚠️  Resposta: {result_dict}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro ao testar ferramenta: {e}")
        return False


async def test_chatbot_clear_conversation(mcp):
    """Testa a ferramenta chatbot_clear_conversation"""
    print("\n6️⃣ Testando chatbot_clear_conversation...")
    try:
        result = await mcp.call_tool(
            'chatbot_clear_conversation',
            {'conversation_id': 'test_integration'}
        )
        
        if isinstance(result, list) and len(result) > 0:
            content = result[0].text if hasattr(result[0], 'text') else str(result[0])
            result_dict = json.loads(content) if isinstance(content, str) else content
        else:
            result_dict = result
        
        if result_dict.get('status') in ['success', 'info']:
            print(f"   ✅ {result_dict.get('message', 'Conversa limpa')}")
            return True
        else:
            print(f"   ⚠️  Resposta: {result_dict}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro ao testar ferramenta: {e}")
        return False


async def main():
    """Executa todos os testes"""
    results = []
    
    # Teste 1: Importar MCP Server
    success, mcp = test_mcp_server_import()
    results.append(("Importação MCP Server", success))
    if not success:
        print_summary(results)
        return False
    
    # Teste 2: Importar ferramentas chatbot
    success = test_chatbot_tools_import(mcp)
    results.append(("Importação ferramentas chatbot", success))
    if not success:
        print_summary(results)
        return False
    
    # Teste 3: Listar ferramentas
    success = await test_list_tools(mcp)
    results.append(("Listagem de ferramentas", success))
    if not success:
        print_summary(results)
        return False
    
    # Teste 4: Enviar mensagem
    success = await test_chatbot_send_message(mcp)
    results.append(("chatbot_send_message", success))
    
    # Teste 5: Listar conversas
    success = await test_chatbot_list_conversations(mcp)
    results.append(("chatbot_list_conversations", success))
    
    # Teste 6: Limpar conversa
    success = await test_chatbot_clear_conversation(mcp)
    results.append(("chatbot_clear_conversation", success))
    
    # Resumo
    print_summary(results)
    
    return all(r[1] for r in results)


def print_summary(results):
    """Imprime resumo dos testes"""
    print("\n" + "=" * 70)
    print("📊 RESUMO DOS TESTES")
    print("=" * 70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{status:12} | {test_name}")
    
    print("-" * 70)
    print(f"Total: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("\nSeu MCP Server está pronto para usar o chatbot!")
        print("\nPara iniciar o servidor:")
        print("  python3.13 decision_center_mcp_server_Regras.py")
    else:
        print(f"\n⚠️  {total - passed} teste(s) falharam")
        print("\nVerifique os erros acima e:")
        print("1. Confirme que as dependências estão instaladas")
        print("2. Verifique se as credenciais estão configuradas")
        print("3. Consulte CHATBOT_SETUP_GUIDE.md")
    
    print()


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
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
