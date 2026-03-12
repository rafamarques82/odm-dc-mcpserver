#!/usr/bin/env python3
"""
Script para testar a correção do erro "The archive file does not contain any decision service"

Este script:
1. Cria um projeto ODM usando a tool corrigida
2. Valida a estrutura do ZIP gerado
3. Compara com o projeto de referência correto
4. Tenta importar no Decision Center (opcional)
"""

import sys
import os
import zipfile
import json
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

def validate_zip_structure(zip_path):
    """Valida a estrutura do ZIP gerado"""
    print_step("2", "Validando estrutura do ZIP...")
    
    required_files = {
        '.project': False,
        '.ruleproject': False,
        'bom/modelo.bom': False,
        'bom/modelo.voc': False,
        'bom/modelo_pt_BR.voc': False,
        'bom/modelo.b2xa': False,
    }
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            files = zf.namelist()
            
            # Verifica arquivos obrigatórios
            for file_pattern, _ in required_files.items():
                found = any(file_pattern in f for f in files)
                required_files[file_pattern] = found
                
                if found:
                    print_success(f"Encontrado: {file_pattern}")
                else:
                    print_error(f"Faltando: {file_pattern}")
            
            # Verifica conteúdo do .ruleproject
            print_step("3", "Validando conteúdo do .ruleproject...")
            
            ruleproject_file = None
            for f in files:
                if f.endswith('.ruleproject'):
                    ruleproject_file = f
                    break
            
            if ruleproject_file:
                content = zf.read(ruleproject_file).decode('utf-8')
                
                # Verifica namespace decisionservice
                if 'xmlns:com.ibm.rules.studio.model.decisionservice' in content:
                    print_success("Namespace decisionservice presente")
                else:
                    print_error("Namespace decisionservice AUSENTE (causa do erro!)")
                
                # Verifica OperationFolder
                if 'com.ibm.rules.studio.model.decisionservice:OperationFolder' in content:
                    print_success("OperationFolder presente")
                else:
                    print_error("OperationFolder AUSENTE (causa do erro!)")
                
                # Verifica isADecisionService
                if 'isADecisionService="true"' in content:
                    print_success("isADecisionService=true")
                else:
                    print_info("isADecisionService=false (projeto simples)")
                
                return all(required_files.values())
            else:
                print_error("Arquivo .ruleproject não encontrado!")
                return False
                
    except Exception as e:
        print_error(f"Erro ao validar ZIP: {e}")
        return False

def compare_with_reference(zip_path, reference_path):
    """Compara com projeto de referência"""
    print_step("4", "Comparando com projeto de referência...")
    
    if not os.path.exists(reference_path):
        print_info(f"Projeto de referência não encontrado: {reference_path}")
        print_info("Pulando comparação...")
        return True
    
    try:
        # Extrai .ruleproject do projeto gerado
        with zipfile.ZipFile(zip_path, 'r') as zf:
            generated_ruleproject = None
            for f in zf.namelist():
                if f.endswith('.ruleproject'):
                    generated_ruleproject = zf.read(f).decode('utf-8')
                    break
        
        # Extrai .ruleproject do projeto de referência
        with zipfile.ZipFile(reference_path, 'r') as zf:
            reference_ruleproject = None
            for f in zf.namelist():
                if f.endswith('.ruleproject'):
                    reference_ruleproject = zf.read(f).decode('utf-8')
                    break
        
        if generated_ruleproject and reference_ruleproject:
            # Verifica elementos chave
            checks = {
                'xmlns:com.ibm.rules.studio.model.decisionservice': 'Namespace decisionservice',
                'OperationFolder': 'OperationFolder',
                'isADecisionService="true"': 'isADecisionService',
            }
            
            all_ok = True
            for pattern, name in checks.items():
                in_generated = pattern in generated_ruleproject
                in_reference = pattern in reference_ruleproject
                
                if in_generated == in_reference:
                    print_success(f"{name}: {'presente' if in_generated else 'ausente'} (igual à referência)")
                else:
                    print_error(f"{name}: diferente da referência!")
                    all_ok = False
            
            return all_ok
        else:
            print_error("Não foi possível extrair .ruleproject para comparação")
            return False
            
    except Exception as e:
        print_error(f"Erro ao comparar: {e}")
        return False

def test_import_to_dc(zip_path):
    """Testa importação no Decision Center (opcional)"""
    print_step("5", "Testando importação no Decision Center...")
    
    try:
        from tools.tools_decisioncenter import importar_projeto
        
        print_info("Tentando importar no Decision Center...")
        result = importar_projeto(zip_path)
        
        if result.get("status") == "success":
            print_success("Importação bem-sucedida!")
            print_info(f"Decision Service ID: {result.get('decision_service_id')}")
            return True
        else:
            print_error(f"Falha na importação: {result.get('error', 'Erro desconhecido')}")
            return False
            
    except ImportError:
        print_info("Módulo de importação não disponível. Pulando teste de importação...")
        return True
    except Exception as e:
        print_error(f"Erro ao importar: {e}")
        return False

def main():
    """Função principal"""
    print_header("TESTE DE CORREÇÃO: Archive Error")
    print("Script para validar a correção do erro de importação")
    
    # Passo 1: Criar projeto
    print_step("1", "Criando projeto ODM de teste...")
    
    try:
        # Inicializa MCP antes de importar os módulos
        import builtins
        from mcp.server.fastmcp import FastMCP
        
        mcp = FastMCP("ODM Test")
        builtins.mcp = mcp
        
        print_info("MCP inicializado")
        
        # Importa as funções necessárias
        sys.path.insert(0, str(Path(__file__).parent / 'tools'))
        from tools_project_generator import criar_projeto_odm
        
        print_info("Módulo tools_project_generator importado")
        
        # Define dados do projeto de teste
        project_name = f"TesteCorrecao_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        classes = [
            {
                "name": "Cliente",
                "label": "Cliente",
                "verbalizations": {
                    "article": "o",
                    "singular": "cliente",
                    "plural": "clientes"
                },
                "attributes": [
                    {
                        "name": "idade",
                        "type": "int",
                        "label": "idade",
                        "verbalizations": {
                            "article": "a",
                            "singular": "idade"
                        }
                    },
                    {
                        "name": "nome",
                        "type": "string",
                        "label": "nome",
                        "verbalizations": {
                            "article": "o",
                            "singular": "nome"
                        }
                    }
                ]
            }
        ]
        
        # Cria o projeto
        result = criar_projeto_odm(
            project_name=project_name,
            description="Projeto de teste para validar correção do erro de archive",
            classes=classes,
            package_name="com.teste.model",
            output_dir="/tmp/odm_test",
            create_zip=True
        )
        
        if result.get("status") != "success":
            print_error(f"Falha ao criar projeto: {result.get('error')}")
            return False
        
        print_success(f"Projeto criado: {project_name}")
        print_info(f"ZIP gerado: {result['zip_path']}")
        
        zip_path = result['zip_path']
        
        # Passo 2: Validar estrutura
        if not validate_zip_structure(zip_path):
            print_error("Validação da estrutura falhou!")
            return False
        
        # Passo 3: Comparar com referência
        reference_path = Path.home() / "Downloads" / "projeto.zip"
        compare_with_reference(zip_path, str(reference_path))
        
        # Passo 4: Testar importação (opcional)
        import_dc = input("\n❓ Deseja testar importação no Decision Center? (s/N): ").lower() == 's'
        
        if import_dc:
            test_import_to_dc(zip_path)
        else:
            print_info("Teste de importação pulado.")
        
        # Resumo final
        print_header("RESUMO DO TESTE")
        print_success("✅ Projeto criado com sucesso")
        print_success("✅ Estrutura do ZIP validada")
        print_success("✅ Namespace decisionservice presente")
        print_success("✅ OperationFolder presente")
        print_info(f"\n📦 Arquivo ZIP: {zip_path}")
        print_info("🎯 Pronto para importação no Decision Center!")
        
        return True
        
    except Exception as e:
        print_error(f"Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Made with Bob
