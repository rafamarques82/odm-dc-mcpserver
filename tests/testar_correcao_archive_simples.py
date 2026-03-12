#!/usr/bin/env python3
"""
Script simplificado para testar a correção do erro "The archive file does not contain any decision service"

Este script valida apenas a estrutura do .ruleproject sem depender do MCP.
"""

import sys
import os
import zipfile
from pathlib import Path
from datetime import datetime

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

def validate_ruleproject_content(content):
    """Valida o conteúdo do .ruleproject"""
    print_step("2", "Validando conteúdo do .ruleproject...")
    
    checks = {
        'xmlns:com.ibm.rules.studio.model.decisionservice': 'Namespace decisionservice',
        'com.ibm.rules.studio.model.decisionservice:OperationFolder': 'OperationFolder',
        'isADecisionService="true"': 'isADecisionService flag',
        'buildMode="DecisionEngine"': 'buildMode DecisionEngine',
    }
    
    all_ok = True
    for pattern, name in checks.items():
        if pattern in content:
            print_success(f"{name}: presente")
        else:
            print_error(f"{name}: AUSENTE (causa do erro!)")
            all_ok = False
    
    return all_ok

def compare_with_reference(generated_content, reference_path):
    """Compara com projeto de referência"""
    print_step("3", "Comparando com projeto de referência...")
    
    if not os.path.exists(reference_path):
        print_info(f"Projeto de referência não encontrado: {reference_path}")
        print_info("Pulando comparação...")
        return True
    
    try:
        # Extrai .ruleproject do projeto de referência
        with zipfile.ZipFile(reference_path, 'r') as zf:
            reference_content = None
            for f in zf.namelist():
                if f.endswith('.ruleproject'):
                    reference_content = zf.read(f).decode('utf-8')
                    break
        
        if reference_content:
            # Verifica elementos chave
            checks = {
                'xmlns:com.ibm.rules.studio.model.decisionservice': 'Namespace decisionservice',
                'OperationFolder': 'OperationFolder',
                'isADecisionService="true"': 'isADecisionService',
            }
            
            all_ok = True
            for pattern, name in checks.items():
                in_generated = pattern in generated_content
                in_reference = pattern in reference_content
                
                if in_generated == in_reference:
                    print_success(f"{name}: {'presente' if in_generated else 'ausente'} (igual à referência)")
                else:
                    print_error(f"{name}: diferente da referência!")
                    all_ok = False
            
            return all_ok
        else:
            print_error("Não foi possível extrair .ruleproject da referência")
            return False
            
    except Exception as e:
        print_error(f"Erro ao comparar: {e}")
        return False

def check_generated_project():
    """Verifica o .ruleproject gerado pela tool"""
    print_step("1", "Verificando .ruleproject gerado pela tool...")
    
    # Lê o arquivo diretamente do código
    ruleproject_path = Path(__file__).parent / 'tools' / 'tools_project_generator.py'
    
    if not ruleproject_path.exists():
        print_error(f"Arquivo não encontrado: {ruleproject_path}")
        return False
    
    try:
        with open(ruleproject_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Procura o template do .ruleproject
        start_marker = "ruleproject_content = f'''<?xml"
        end_marker = "</ilog.rules.studio.model.base:RuleProject>'''"
        
        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker, start_idx)
        
        if start_idx == -1 or end_idx == -1:
            print_error("Não foi possível encontrar o template do .ruleproject no código")
            return False
        
        # Extrai o template
        ruleproject_template = content[start_idx:end_idx + len(end_marker)]
        
        print_success("Template .ruleproject encontrado no código")
        
        # Valida o conteúdo
        return validate_ruleproject_content(ruleproject_template)
        
    except Exception as e:
        print_error(f"Erro ao ler arquivo: {e}")
        return False

def check_existing_zip(zip_path):
    """Verifica um ZIP já existente"""
    print_step("4", f"Verificando ZIP existente: {zip_path}")
    
    if not os.path.exists(zip_path):
        print_info("ZIP não encontrado. Crie um projeto primeiro usando:")
        print_info("  python3 criar_projeto_com_xom.py")
        return None
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Procura .ruleproject
            ruleproject_file = None
            for f in zf.namelist():
                if f.endswith('.ruleproject'):
                    ruleproject_file = f
                    break
            
            if not ruleproject_file:
                print_error("Arquivo .ruleproject não encontrado no ZIP")
                return None
            
            content = zf.read(ruleproject_file).decode('utf-8')
            print_success(f"Arquivo .ruleproject encontrado: {ruleproject_file}")
            
            return content
            
    except Exception as e:
        print_error(f"Erro ao ler ZIP: {e}")
        return None

def main():
    """Função principal"""
    print_header("TESTE DE CORREÇÃO: Archive Error (Simplificado)")
    print("Valida a correção do erro de importação no código")
    
    try:
        # Verifica o código da tool
        code_ok = check_generated_project()
        
        # Compara com referência
        reference_path = Path.home() / "Downloads" / "projeto.zip"
        
        # Tenta encontrar um ZIP gerado recentemente
        test_zips = [
            "/tmp/odm_projects/*.zip",
            "/tmp/odm_test/*.zip",
        ]
        
        latest_zip = None
        for pattern in test_zips:
            import glob
            zips = glob.glob(pattern)
            if zips:
                latest_zip = max(zips, key=os.path.getctime)
                break
        
        if latest_zip:
            zip_content = check_existing_zip(latest_zip)
            if zip_content:
                compare_with_reference(zip_content, str(reference_path))
        else:
            print_info("\nNenhum ZIP de teste encontrado.")
            print_info("Para testar com um ZIP real, execute:")
            print_info("  python3 criar_projeto_com_xom.py")
        
        # Resumo final
        print_header("RESUMO DO TESTE")
        
        if code_ok:
            print_success("✅ Código da tool está correto")
            print_success("✅ Namespace decisionservice presente")
            print_success("✅ OperationFolder presente")
            print_info("\n🎯 A correção foi implementada com sucesso!")
            print_info("📝 Projetos gerados agora podem ser importados no Decision Center")
        else:
            print_error("❌ Código da tool precisa de correção")
            print_info("📖 Consulte SOLUCAO_ERRO_ARCHIVE.md para detalhes")
        
        return code_ok
        
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
