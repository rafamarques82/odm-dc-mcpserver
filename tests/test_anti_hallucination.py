#!/usr/bin/env python3
"""
Script de Teste Anti-Alucinação
================================
Testa se o Watson está usando ferramentas corretamente e não alucinando.
"""

import asyncio
import sys
from pathlib import Path

# Adiciona o diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

from watson_mcp_client import WatsonMCPClient


async def test_tool_detection():
    """Testa detecção de ferramentas"""
    print("=" * 70)
    print("🧪 TESTE 1: Detecção de Ferramentas por Keywords")
    print("=" * 70)
    print()
    
    client = WatsonMCPClient()
    if not await client.initialize():
        print("❌ Falha ao inicializar cliente")
        return False
    
    # Testa detecção direta
    test_cases = [
        ("listar projetos", "list_decision_services"),
        ("mostrar regras do projeto X", "get_rules"),
        ("listar fluxos", "get_ruleflows"),
        ("olá, como vai?", None),
    ]
    
    print("Testando detecção por keywords:\n")
    for message, expected_tool in test_cases:
        detected = client._detect_tool_by_keywords(message)
        status = "✅" if detected == expected_tool else "❌"
        print(f"{status} '{message}'")
        print(f"   Esperado: {expected_tool}")
        print(f"   Detectado: {detected}")
        print()
    
    return True


async def test_list_projects():
    """Testa listagem de projetos"""
    print("=" * 70)
    print("🧪 TESTE 2: Listar Projetos (Deve Usar Tool)")
    print("=" * 70)
    print()
    
    client = WatsonMCPClient()
    if not await client.initialize():
        print("❌ Falha ao inicializar cliente")
        return False
    
    message = "liste os projetos disponíveis"
    print(f"📤 Pergunta: {message}\n")
    
    response = await client.chat(message)
    
    print(f"\n📥 Resposta:\n{response}\n")
    
    # Verifica se não está alucinando
    hallucination_indicators = [
        "por exemplo",
        "como o projeto",
        "incluindo",
        "tais como"
    ]
    
    has_hallucination = any(indicator in response.lower() for indicator in hallucination_indicators)
    
    if has_hallucination:
        print("⚠️  AVISO: Possível alucinação detectada!")
        print("   A resposta contém indicadores de exemplo sem dados reais")
        return False
    
    if "não tenho acesso" in response.lower() and "dados reais" in response.lower():
        print("⚠️  AVISO: Watson não usou a ferramenta corretamente!")
        print("   Ele deveria ter consultado list_decision_services")
        return False
    
    print("✅ Teste passou! Resposta baseada em dados reais ou erro claro")
    return True


async def test_empty_data():
    """Testa resposta quando dados estão vazios"""
    print("=" * 70)
    print("🧪 TESTE 3: Dados Vazios (Não Deve Alucinar)")
    print("=" * 70)
    print()
    
    client = WatsonMCPClient()
    if not await client.initialize():
        print("❌ Falha ao inicializar cliente")
        return False
    
    # Simula dados vazios
    client.conversation_history.append({
        "role": "system",
        "content": '[INÍCIO DOS DADOS REAIS DO DECISION CENTER]\n{"elements": []}\n[FIM DOS DADOS REAIS]'
    })
    
    message = "quais são os projetos?"
    print(f"📤 Pergunta: {message}\n")
    
    response = await client.chat(message)
    
    print(f"\n📥 Resposta:\n{response}\n")
    
    # Verifica se informa que não há dados
    correct_responses = [
        "não há dados",
        "não encontrei",
        "dados vazios",
        "nenhum projeto",
        "não disponível"
    ]
    
    is_correct = any(phrase in response.lower() for phrase in correct_responses)
    
    if not is_correct:
        print("❌ FALHA: Deveria informar que não há dados disponíveis")
        return False
    
    print("✅ Teste passou! Informou corretamente sobre dados vazios")
    return True


async def test_general_question():
    """Testa pergunta geral (não precisa de tool)"""
    print("=" * 70)
    print("🧪 TESTE 4: Pergunta Geral (Não Precisa de Tool)")
    print("=" * 70)
    print()
    
    client = WatsonMCPClient()
    if not await client.initialize():
        print("❌ Falha ao inicializar cliente")
        return False
    
    message = "olá, como você pode me ajudar?"
    print(f"📤 Pergunta: {message}\n")
    
    response = await client.chat(message)
    
    print(f"\n📥 Resposta:\n{response}\n")
    
    # Verifica se não menciona projetos específicos
    if any(word in response.lower() for word in ["projeto x", "regra y", "exemplo:"]):
        print("⚠️  AVISO: Mencionou exemplos específicos sem dados")
        return False
    
    print("✅ Teste passou! Resposta geral sem alucinação")
    return True


async def run_all_tests():
    """Executa todos os testes"""
    print("\n")
    print("🚀 INICIANDO TESTES ANTI-ALUCINAÇÃO")
    print("=" * 70)
    print()
    
    tests = [
        ("Detecção de Ferramentas", test_tool_detection),
        ("Listar Projetos", test_list_projects),
        ("Dados Vazios", test_empty_data),
        ("Pergunta Geral", test_general_question),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Erro no teste '{test_name}': {e}\n")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
        
        print()
    
    # Resumo
    print("=" * 70)
    print("📊 RESUMO DOS TESTES")
    print("=" * 70)
    print()
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status} - {test_name}")
    
    print()
    print(f"Total: {passed}/{total} testes passaram")
    print()
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("   O sistema está funcionando corretamente")
    else:
        print("⚠️  ALGUNS TESTES FALHARAM")
        print("   Revise as melhorias implementadas")
    
    print()
    return passed == total


def main():
    """Função principal"""
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Testes interrompidos pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
