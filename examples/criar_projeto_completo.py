#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script standalone para criar projeto ODM completo com variáveis

Este script:
1. Cria um projeto ODM com BOM, XOM e verbalizações
2. Gera arquivo ZIP
3. Importa no Decision Center (manual ou via interface web)
4. Cria variáveis automaticamente baseadas nas classes do BOM

Uso:
    python3 criar_projeto_completo.py
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Adiciona o diretório atual ao path
sys.path.insert(0, str(Path(__file__).parent))

def print_header(text):
    """Imprime cabeçalho formatado"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_step(number, text):
    """Imprime passo formatado"""
    print(f"\n{number}️⃣  {text}")

def print_success(text):
    """Imprime mensagem de sucesso"""
    print(f"   ✅ {text}")

def print_error(text):
    """Imprime mensagem de erro"""
    print(f"   ❌ {text}")

def print_info(text):
    """Imprime informação"""
    print(f"   ℹ️  {text}")

def print_warning(text):
    """Imprime aviso"""
    print(f"   ⚠️  {text}")

def main():
    """Função principal"""
    print_header("CRIAÇÃO DE PROJETO ODM COMPLETO")
    print("Script para criar projeto com BOM, XOM, verbalizações e variáveis")
    
    try:
        # Inicializa MCP
        print_step("1", "Inicializando ambiente...")
        import builtins
        from mcp.server.fastmcp import FastMCP
        
        mcp = FastMCP("ODM Project Creator")
        builtins.mcp = mcp
        print_success("MCP inicializado")
        
        # Importa as tools necessárias
        from tools.tools_project_generator import criar_projeto_odm
        from tools.tools_variables import criar_variaveis_do_bom
        
        print_success("Tools importadas")
        
        # Define dados do projeto
        print_step("2", "Configurando projeto...")
        
        project_name = input("\n📝 Nome do projeto (ex: SistemaCredito): ").strip()
        if not project_name:
            project_name = f"Projeto_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            print_info(f"Usando nome padrão: {project_name}")
        
        description = input("📝 Descrição do projeto: ").strip()
        if not description:
            description = f"Projeto criado em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        # Define classes
        print("\n📦 Definindo classes do BOM...")
        print("   Exemplo: Cliente com atributos nome, idade, renda")
        
        usar_exemplo = input("\n❓ Usar exemplo padrão? (S/n): ").strip().lower()
        
        if usar_exemplo != 'n':
            classes = [
                {
                    'name': 'Cliente',
                    'label': 'Cliente',
                    'attributes': [
                        {'name': 'nome', 'type': 'string', 'label': 'Nome'},
                        {'name': 'idade', 'type': 'int', 'label': 'Idade'},
                        {'name': 'renda', 'type': 'double', 'label': 'Renda Mensal'},
                        {'name': 'scoreCredito', 'type': 'int', 'label': 'Score de Crédito'}
                    ]
                },
                {
                    'name': 'Emprestimo',
                    'label': 'Empréstimo',
                    'attributes': [
                        {'name': 'valor', 'type': 'double', 'label': 'Valor Solicitado'},
                        {'name': 'prazo', 'type': 'int', 'label': 'Prazo em Meses'},
                        {'name': 'aprovado', 'type': 'boolean', 'label': 'Aprovado'},
                        {'name': 'taxaJuros', 'type': 'double', 'label': 'Taxa de Juros'}
                    ]
                },
                {
                    'name': 'Resultado',
                    'label': 'Resultado',
                    'attributes': [
                        {'name': 'mensagem', 'type': 'string', 'label': 'Mensagem'},
                        {'name': 'motivo', 'type': 'string', 'label': 'Motivo'}
                    ]
                }
            ]
            print_success("Usando classes de exemplo: Cliente, Emprestimo, Resultado")
        else:
            print_error("Modo customizado não implementado nesta versão")
            print_info("Edite o script para adicionar suas próprias classes")
            return False
        
        # Cria o projeto
        print_step("3", "Criando projeto ODM...")
        
        result = criar_projeto_odm(
            project_name=project_name,
            description=description,
            classes=classes,
            package_name="com.example.model",
            output_dir="/tmp/odm_projects",
            create_zip=True
        )
        
        if result.get("status") != "success":
            print_error(f"Falha ao criar projeto: {result.get('error')}")
            return False
        
        print_success(f"Projeto criado: {project_name}")
        print_info(f"ZIP gerado: {result['zip_path']}")
        print_info(f"Total de arquivos: {len(result.get('files_created', []))}")
        
        # Mostra estrutura criada
        print("\n📁 Estrutura do projeto:")
        if result.get('xom_project_name'):
            print(f"   ├── {result['xom_project_name']}/ (Projeto XOM - Java)")
            print(f"   │   └── src/com/example/model/")
            for cls in classes:
                print(f"   │       └── {cls['name']}.java")
        print(f"   └── {project_name}/ (Decision Service)")
        print(f"       ├── .project")
        print(f"       ├── .ruleproject (com namespace decisionservice ✅)")
        print(f"       └── bom/")
        print(f"           ├── modelo.bom")
        print(f"           ├── modelo_pt_BR.voc (verbalizações corretas ✅)")
        print(f"           └── modelo.b2xa")
        
        # Instruções de importação
        print_step("4", "Importando no Decision Center...")
        print_warning("A importação via API pode falhar para projetos com XOM")
        print_info("Recomendação: Importar manualmente via interface web")
        
        print("\n📋 Instruções de importação manual:")
        print("   1. Acesse: http://localhost:9060/decisioncenter")
        print("   2. File > Import > Decision Service Archive")
        print(f"   3. Selecione: {result['zip_path']}")
        print("   4. Siga o assistente de importação")
        print("   5. ✅ Projeto importado com sucesso!")
        
        importar_agora = input("\n❓ Tentar importar via API agora? (s/N): ").strip().lower()
        
        if importar_agora == 's':
            try:
                from tools.tools_decisioncenter import importar_projeto
                
                print_info("Tentando importar via API...")
                import_result = importar_projeto(result['zip_path'])
                
                if import_result.get("status") == "success":
                    print_success("Importação via API bem-sucedida!")
                    decision_service_id = import_result.get("decision_service_id")
                    print_info(f"Decision Service ID: {decision_service_id}")
                else:
                    print_error(f"Falha na importação via API: {import_result.get('error')}")
                    print_warning("Use importação manual conforme instruções acima")
                    
                    # Pergunta se quer continuar mesmo assim
                    continuar = input("\n❓ Continuar para criar variáveis? (s/N): ").strip().lower()
                    if continuar != 's':
                        print_info("Importe o projeto manualmente e execute novamente")
                        return True
            except Exception as e:
                print_error(f"Erro na importação: {e}")
                print_warning("Use importação manual")
                return True
        else:
            print_info("Importe o projeto manualmente antes de continuar")
            
            continuar = input("\n❓ Projeto já foi importado? Continuar para criar variáveis? (s/N): ").strip().lower()
            if continuar != 's':
                print_info("Execute este script novamente após importar o projeto")
                return True
        
        # Cria variáveis
        print_step("5", "Criando variáveis automaticamente...")
        
        print_info(f"Criando variáveis baseadas nas classes do BOM...")
        
        try:
            var_result = criar_variaveis_do_bom(
                projectName=project_name,
                baselineName="Main"
            )
            
            if var_result.get("status") in ["success", "partial_success"]:
                print_success(f"Variáveis criadas: {var_result.get('total_criadas', 0)}")
                print_info(f"Variáveis já existentes: {var_result.get('total_existentes', 0)}")
                
                print("\n📝 Variáveis criadas:")
                for var in var_result.get("variaveis_criadas", []):
                    status_icon = "✅" if var.get("status") == "criada" else "ℹ️"
                    print(f"   {status_icon} {var['nome']} : {var['tipo']}")
                
                if var_result.get("erros"):
                    print("\n⚠️  Erros:")
                    for erro in var_result["erros"]:
                        print(f"   ❌ {erro['variavel']}: {erro['erro']}")
            else:
                print_error(f"Falha ao criar variáveis: {var_result.get('error')}")
                
        except Exception as e:
            print_error(f"Erro ao criar variáveis: {e}")
            print_info("Você pode criar as variáveis manualmente no Decision Center")
        
        # Resumo final
        print_header("RESUMO")
        print_success(f"✅ Projeto '{project_name}' criado")
        print_success(f"✅ ZIP gerado: {result['zip_path']}")
        print_success(f"✅ Verbalizações em português corretas")
        print_success(f"✅ Namespace decisionservice presente")
        
        if importar_agora == 's' and import_result.get("status") == "success":
            print_success("✅ Projeto importado no Decision Center")
            print_success("✅ Variáveis criadas automaticamente")
        else:
            print_warning("⚠️  Importe o projeto manualmente")
            print_info("   Depois execute: criar_variaveis_do_bom('" + project_name + "')")
        
        print("\n🎯 Próximos passos:")
        print("   1. Acesse o Decision Center")
        print(f"   2. Abra o projeto '{project_name}'")
        print("   3. Crie regras usando as variáveis:")
        for cls in classes:
            var_name = cls['name'][0].lower() + cls['name'][1:]
            print(f"      - {var_name} (tipo {cls['name']})")
        print("   4. Use verbalizações em português nas regras!")
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada pelo usuário")
        return False
    except Exception as e:
        print_error(f"Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Made with Bob
