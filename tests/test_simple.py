#!/usr/bin/env python3
"""
Teste Simples - Debug de Detecção de Ferramentas
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from watson_mcp_client import WatsonMCPClient


async def main():
    print("=" * 70)
    print("🧪 TESTE SIMPLES - DEBUG")
    print("=" * 70)
    print()
    
    # Inicializa cliente
    client = WatsonMCPClient()
    print("Inicializando cliente...\n")
    
    if not await client.initialize():
        print("❌ Falha ao inicializar")
        return
    
    print()
    print("=" * 70)
    print("📋 FERRAMENTAS DISPONÍVEIS:")
    print("=" * 70)
    for i, tool in enumerate(client.available_tools[:15], 1):
        print(f"{i}. {tool.name}")
    print()
    
    # Teste de detecção
    test_messages = [
        "liste os projetos disponíveis",
        "listar projetos",
        "mostrar projetos",
        "quais são os projetos?",
    ]
    
    print("=" * 70)
    print("🔍 TESTE DE DETECÇÃO DE KEYWORDS:")
    print("=" * 70)
    print()
    
    for msg in test_messages:
        print(f"Mensagem: '{msg}'")
        detected = client._detect_tool_by_keywords(msg)
        print(f"Resultado: {detected}")
        print("-" * 70)
        print()
    
    # Teste completo
    print("=" * 70)
    print("💬 TESTE COMPLETO DE CHAT:")
    print("=" * 70)
    print()
    
    message = "liste os projetos disponíveis"
    print(f"Você: {message}\n")
    
    response = await client.chat(message)
    
    print(f"\nWatson: {response}\n")
    print("=" * 70)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrompido")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()

# Made with Bob
