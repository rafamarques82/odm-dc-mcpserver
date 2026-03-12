#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo de uso das tools de Decision Operations.

Este script demonstra como criar Decision Operations baseado na estrutura
do arquivo test_operation_ruleflow.json.

REQUISITOS OBRIGATÓRIOS para uma Decision Operation:
1. Ruleflow associado
2. Variable Set (usado para descriptors, params e rulesetParams)
3. Parâmetros (pelo menos um IN, OUT ou INOUT)
4. Operations NÃO têm pacote específico
"""

import sys
import os

# Adiciona o diretório pai ao path para importar os módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.tools_operations import criar_operation, visualizar_operation, atualizar_operation


def exemplo_criar_operation_financiamento():
    """
    Exemplo baseado em test_operation_ruleflow.json:
    Criar uma Decision Operation para calcular financiamento imobiliário.
    """
    print("\n" + "="*80)
    print("EXEMPLO: Criar Decision Operation - Calcular Financiamento")
    print("="*80)
    print("\nEstrutura baseada em test_operation_ruleflow.json")
    
    resultado = criar_operation(
        projectName="DS-FinanciamentoImobiliario",
        operationName="CalcularFinanciamento",
        ruleflowName="Fluxo de Calculo de Financiamento",
        variableSetName="variaveis",
        parameters=[
            {
                "name": "credito",
                "direction": "IN",
                "bomType": "credito"
            },
            {
                "name": "elegivel",
                "direction": "OUT",
                "bomType": "booleano"
            },
            {
                "name": "financiamento",
                "direction": "INOUT",
                "bomType": "financiamento"
            }
        ],
        rulesetName="FinanciamentoRuleset",
        description="Operação para calcular financiamento imobiliário"
    )
    
    print("\n✅ Operation criada com sucesso!")
    print("\nDetalhes:")
    print(f"  - Operation: {resultado.get('operationName')}")
    print(f"  - Ruleflow: {resultado.get('dsmRuleflowLinked')}")
    print(f"  - Variable Set: variaveis (usado em descriptors, params e rulesetParams)")
    print(f"  - Parâmetros: {len(resultado.get('parameters', []))}")
    print(f"  - Ruleset: {resultado.get('runtimeRulesetName')}")
    
    return resultado


def exemplo_criar_operation_credito():
    """
    Exemplo 2: Criar uma Decision Operation para aprovar crédito.
    """
    print("\n" + "="*80)
    print("EXEMPLO: Criar Decision Operation - Aprovar Crédito")
    print("="*80)
    
    resultado = criar_operation(
        projectName="ProjetoCredito",
        operationName="AprovarCredito",
        ruleflowName="FluxoAprovacao",
        variableSetName="GlobalVariables",
        parameters=[
            {
                "name": "cliente",
                "direction": "IN",
                "bomType": "Cliente"
            },
            {
                "name": "aprovado",
                "direction": "OUT",
                "bomType": "booleano"
            },
            {
                "name": "motivo",
                "direction": "OUT",
                "bomType": "texto"
            }
        ],
        rulesetName="aprovar_credito_ruleset",
        description="Operation para aprovar crédito de clientes"
    )
    
    print("\n✅ Operation criada com sucesso!")
    print("\nDetalhes:")
    print(f"  - Operation: {resultado.get('operationName')}")
    print(f"  - Ruleflow: {resultado.get('dsmRuleflowLinked')}")
    print(f"  - Variable Set: GlobalVariables")
    print(f"  - Parâmetros: {len(resultado.get('parameters', []))}")
    
    return resultado


def exemplo_visualizar_operation():
    """
    Exemplo 3: Visualizar uma Decision Operation existente.
    """
    print("\n" + "="*80)
    print("EXEMPLO: Visualizar Decision Operation")
    print("="*80)
    
    resultado = visualizar_operation(
        projectName="DS-FinanciamentoImobiliario",
        operationName="CalcularFinanciamento",
        baselineName="Main"
    )
    
    print("\n📋 Detalhes da Operation:")
    print(f"\nNome: {resultado.get('operationName')}")
    print(f"Descrição: {resultado.get('description')}")
    print(f"Ruleflow: {resultado.get('dsmRuleflowLinked')}")
    print(f"Ruleset: {resultado.get('runtimeRulesetName')}")
    
    print("\n📝 Parâmetros:")
    for param in resultado.get('parameters', []):
        print(f"  - {param.get('name')} ({param.get('direction')}): {param.get('bomType')}")
    
    print("\n📦 Registry (Variable Sets):")
    registry = resultado.get('registry', {})
    print(f"  - Descriptors: {registry.get('descriptorSets', [])}")
    print(f"  - Params: {registry.get('paramsSets', [])}")
    print(f"  - Ruleset Params: {registry.get('rulesetParamSets', [])}")
    
    return resultado


def exemplo_atualizar_operation():
    """
    Exemplo 4: Atualizar uma Decision Operation existente.
    """
    print("\n" + "="*80)
    print("EXEMPLO: Atualizar Decision Operation")
    print("="*80)
    
    resultado = atualizar_operation(
        projectName="DS-FinanciamentoImobiliario",
        operationName="CalcularFinanciamento",
        ruleflowName="Fluxo de Calculo de Financiamento V2",  # Novo ruleflow
        variableSetName="variaveis",
        parameters=[
            {
                "name": "credito",
                "direction": "IN",
                "bomType": "credito"
            },
            {
                "name": "elegivel",
                "direction": "OUT",
                "bomType": "booleano"
            },
            {
                "name": "financiamento",
                "direction": "INOUT",
                "bomType": "financiamento"
            },
            {
                "name": "taxaJuros",  # Novo parâmetro
                "direction": "OUT",
                "bomType": "numero"
            }
        ],
        rulesetName="FinanciamentoRuleset_V2",
        description="Operação atualizada com cálculo de taxa de juros"
    )
    
    print("\n✅ Operation atualizada com sucesso!")
    print("\nMudanças:")
    print("  - Ruleflow atualizado para V2")
    print("  - Adicionado parâmetro 'taxaJuros' (OUT)")
    print("  - Ruleset atualizado para V2")
    print("  - Descrição atualizada")
    
    return resultado


def main():
    """
    Executa todos os exemplos.
    """
    print("\n" + "="*80)
    print("EXEMPLOS DE USO DAS TOOLS DE DECISION OPERATIONS")
    print("="*80)
    print("\n⚠️  REQUISITOS OBRIGATÓRIOS:")
    print("  1. Ruleflow associado")
    print("  2. Variable Set (usado para descriptors, params e rulesetParams)")
    print("  3. Parâmetros (pelo menos um IN, OUT ou INOUT)")
    print("  4. Operations NÃO têm pacote específico")
    
    try:
        # Exemplo 1: Operation de financiamento (baseado em test_operation_ruleflow.json)
        exemplo_criar_operation_financiamento()
        
        # Exemplo 2: Operation de crédito
        exemplo_criar_operation_credito()
        
        # Exemplo 3: Visualizar operation
        exemplo_visualizar_operation()
        
        # Exemplo 4: Atualizar operation
        exemplo_atualizar_operation()
        
        print("\n" + "="*80)
        print("✅ TODOS OS EXEMPLOS EXECUTADOS COM SUCESSO!")
        print("="*80)
        print("\n💡 Dica: Use visualizar_operation() para verificar os detalhes")
        print("   de qualquer operation criada ou atualizada.")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
