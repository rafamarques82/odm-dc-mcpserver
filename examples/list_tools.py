#!/usr/bin/env python3
"""
Lista todas as ferramentas (tools) disponíveis no MCP Server
=============================================================
"""

import sys
import asyncio
from pathlib import Path

# Adiciona o diretório do projeto ao path
project_path = Path(__file__).parent
sys.path.insert(0, str(project_path))


async def list_all_tools():
    """Lista todas as ferramentas registradas no MCP Server"""
    print("=" * 80)
    print("🛠️  FERRAMENTAS DISPONÍVEIS NO MCP SERVER")
    print("=" * 80)
    print()
    
    try:
        # Importa e configura o MCP
        import builtins
        from mcp.server.fastmcp import FastMCP
        
        # Cria instância MCP
        mcp = FastMCP("Decision Center MCP", json_response=False)
        builtins.mcp = mcp
        
        # Importa todos os módulos de tools
        print("📦 Carregando módulos de ferramentas...")
        import tools.tools_decisioncenter   # noqa: F401
        import tools.tools_rules            # noqa: F401
        import tools.tools_ruleflows        # noqa: F401
        import tools.tools_decisiontables   # noqa: F401
        import tools.tools_vocab            # noqa: F401
        import tools.tools_variables        # noqa: F401
        import tools.tools_chatbot          # noqa: F401
        
        print("✅ Módulos carregados\n")
        
        # Lista todas as ferramentas
        tools = await mcp.list_tools()
        
        # Agrupa por categoria
        categories = {
            'chatbot': [],
            'decision_center': [],
            'rules': [],
            'ruleflows': [],
            'decision_tables': [],
            'vocab': [],
            'variables': [],
            'other': []
        }
        
        for tool in tools:
            name = tool.name.lower()
            if 'chatbot' in name:
                categories['chatbot'].append(tool)
            elif 'decision' in name and 'center' in name:
                categories['decision_center'].append(tool)
            elif 'rule' in name and 'flow' not in name and 'table' not in name:
                categories['rules'].append(tool)
            elif 'ruleflow' in name or 'flow' in name:
                categories['ruleflows'].append(tool)
            elif 'table' in name or 'dt' in name:
                categories['decision_tables'].append(tool)
            elif 'vocab' in name or 'bom' in name:
                categories['vocab'].append(tool)
            elif 'variable' in name or 'var' in name:
                categories['variables'].append(tool)
            else:
                categories['other'].append(tool)
        
        # Imprime por categoria
        total_tools = 0
        
        for category_name, category_tools in categories.items():
            if not category_tools:
                continue
            
            # Nome da categoria formatado
            category_display = {
                'chatbot': '🤖 CHATBOT (IBM watsonx.ai)',
                'decision_center': '🏢 DECISION CENTER',
                'rules': '📋 REGRAS (RULES)',
                'ruleflows': '🔄 FLUXOS DE REGRAS (RULEFLOWS)',
                'decision_tables': '📊 TABELAS DE DECISÃO',
                'vocab': '📚 VOCABULÁRIO (BOM)',
                'variables': '🔢 VARIÁVEIS',
                'other': '🔧 OUTRAS'
            }
            
            print(f"\n{category_display.get(category_name, category_name.upper())}")
            print("-" * 80)
            
            for i, tool in enumerate(category_tools, 1):
                total_tools += 1
                print(f"\n{i}. {tool.name}")
                
                # Descrição
                if hasattr(tool, 'description') and tool.description:
                    desc_lines = tool.description.strip().split('\n')
                    first_line = desc_lines[0][:70]
                    print(f"   📝 {first_line}...")
                
                # Parâmetros
                if hasattr(tool, 'inputSchema') and tool.inputSchema:
                    schema = tool.inputSchema
                    if 'properties' in schema:
                        params = list(schema['properties'].keys())
                        required = schema.get('required', [])
                        
                        if params:
                            print(f"   📥 Parâmetros: {', '.join(params[:5])}")
                            if len(params) > 5:
                                print(f"      ... e mais {len(params) - 5}")
                            
                            if required:
                                print(f"   ⚠️  Obrigatórios: {', '.join(required)}")
        
        # Resumo
        print("\n" + "=" * 80)
        print(f"📊 RESUMO: {total_tools} ferramentas disponíveis")
        print("=" * 80)
        
        # Estatísticas por categoria
        print("\nFerramentas por categoria:")
        for category_name, category_tools in categories.items():
            if category_tools:
                category_display = {
                    'chatbot': 'Chatbot',
                    'decision_center': 'Decision Center',
                    'rules': 'Regras',
                    'ruleflows': 'Fluxos de Regras',
                    'decision_tables': 'Tabelas de Decisão',
                    'vocab': 'Vocabulário',
                    'variables': 'Variáveis',
                    'other': 'Outras'
                }
                name = category_display.get(category_name, category_name)
                count = len(category_tools)
                print(f"  • {name}: {count}")
        
        print()
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro ao importar módulos: {e}")
        print("\nVerifique se todas as dependências estão instaladas:")
        print("  pip install mcp")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(list_all_tools())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Made with Bob
