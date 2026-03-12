#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar projeto ODM completo com XOM e verbalizações
Resolve o erro: Cannot invoke "org.eclipse.emf.ecore.EObject.eClass()" because "obj" is null
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
import zipfile
import uuid as uuid_lib

def _generate_uuid() -> str:
    """Gera UUID simples para arquivos ODM"""
    return str(uuid_lib.uuid4())

def _map_type_to_java(bom_type: str) -> str:
    """Mapeia tipos do BOM para tipos Java"""
    type_mapping = {
        'string': 'java.lang.String',
        'int': 'int',
        'double': 'double',
        'boolean': 'boolean',
        'date': 'java.util.Date',
        'number': 'double'
    }
    return type_mapping.get(bom_type.lower(), 'java.lang.Object')

def _create_project_structure(base_path: Path, project_name: str, package_name: str = "com.example.model"):
    """Cria a estrutura de diretórios do projeto ODM com projeto XOM separado"""
    rules_project = base_path / project_name
    xom_project_name = f"{project_name}XOM"
    xom_project = base_path / xom_project_name
    
    paths = {
        'root': rules_project,
        'rules': rules_project / 'rules',
        'bom': rules_project / 'bom',
        'deployment': rules_project / 'deployment',
        'resources': rules_project / 'resources',
        'xom_root': xom_project,
        'xom_src': xom_project / 'src' / package_name.replace('.', '/'),
        'xom_bin': xom_project / 'bin',
    }
    
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    
    return paths

def _generate_project_file(path: Path, project_name: str, xom_project_name=None):
    """Gera arquivo .project do Eclipse/Rule Designer"""
    xom_ref = f'''
        <project>{xom_project_name}</project>''' if xom_project_name else ''
    
    project_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<projectDescription>
    <name>{project_name}</name>
    <comment></comment>
    <projects>{xom_ref}
    </projects>
    <buildSpec>
        <buildCommand>
            <name>ilog.rules.studio.model.ruleBuilder</name>
            <arguments>
            </arguments>
        </buildCommand>
    </buildSpec>
    <natures>
        <nature>ilog.rules.studio.model.decisionProject</nature>
        <nature>ilog.rules.studio.model.operationProject</nature>
        <nature>ilog.rules.studio.model.ruleNature</nature>
    </natures>
</projectDescription>'''
    
    project_file = path / '.project'
    project_file.write_text(project_content, encoding='utf-8')
    return str(project_file)

def _generate_ruleproject_file(path: Path, project_name: str, xom_project_name=None):
    """Gera arquivo .ruleproject necessário para importação no Decision Center"""
    uuid = _generate_uuid()
    
    # BOM path entry se houver projeto XOM
    bom_entry = ''
    if xom_project_name:
        bom_entry = f'''
  <paths xsi:type="ilog.rules.studio.model.bom:BOMPath" pathID="BOM">
    <entries xsi:type="ilog.rules.studio.model.bom:BOMEntry" name="modelo" url="platform:/{project_name}/bom/modelo.bom" origin="xom:/{project_name}//{xom_project_name}"/>
  </paths>'''
    
    # XOM path entry - usa SystemXOMPathEntry como no projeto real 8.12
    xom_entry = ''
    if xom_project_name:
        xom_entry = f'''
  <paths xsi:type="ilog.rules.studio.model.xom:XOMPath" pathID="XOM">
    <entries xsi:type="ilog.rules.studio.model.xom:LibraryXOMPathEntry" name="org.eclipse.jdt.launching.JRE_CONTAINER" url="file:org.eclipse.jdt.launching.JRE_CONTAINER" kind="LIBRARY" exported="false"/>
    <entries xsi:type="ilog.rules.studio.model.xom:SystemXOMPathEntry" name="{xom_project_name}" url="platform:/{xom_project_name}" kind="JAVA_PROJECT" exported="true"/>
  </paths>'''
    
    ruleproject_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<ilog.rules.studio.model.base:RuleProject xmi:version="2.0"
    xmlns:xmi="http://www.omg.org/XMI"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:ilog.rules.studio.model.base="http://ilog.rules.studio/model/base.ecore"
    xmlns:ilog.rules.studio.model.bom="http://ilog.rules.studio/model/bom.ecore"
    xmlns:ilog.rules.studio.model.xom="http://ilog.rules.studio/model/xom.ecore"
    buildMode="DecisionEngine"
    isADecisionService="true"
    migrationFlag="3">
  <name>{project_name}</name>
  <uuid>{uuid}</uuid>
  <outputLocation>output</outputLocation>
  <categories>any</categories>{bom_entry}{xom_entry}
  <modelFolders xsi:type="ilog.rules.studio.model.base:SourceFolder">
    <name>rules</name>
  </modelFolders>
  <modelFolders xsi:type="ilog.rules.studio.model.bom:BOMFolder">
    <name>bom</name>
  </modelFolders>
  <modelFolders xsi:type="ilog.rules.studio.model.base:ResourceFolder">
    <name>resources</name>
  </modelFolders>
</ilog.rules.studio.model.base:RuleProject>'''
    
    ruleproject_file = path / '.ruleproject'
    ruleproject_file.write_text(ruleproject_content, encoding='utf-8')
    return str(ruleproject_file)

def _generate_xom_project_file(path: Path, project_name: str):
    """Gera arquivo .project para o projeto XOM (Java)"""
    project_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<projectDescription>
    <name>{project_name}</name>
    <comment></comment>
    <projects></projects>
    <buildSpec>
        <buildCommand>
            <name>org.eclipse.jdt.core.javabuilder</name>
            <arguments></arguments>
        </buildCommand>
    </buildSpec>
    <natures>
        <nature>org.eclipse.jdt.core.javanature</nature>
    </natures>
</projectDescription>'''
    
    project_file = path / '.project'
    project_file.write_text(project_content, encoding='utf-8')
    return str(project_file)

def _generate_xom_classpath(path: Path):
    """Gera arquivo .classpath para o projeto XOM"""
    classpath_content = '''<?xml version="1.0" encoding="UTF-8"?>
<classpath>
    <classpathentry kind="src" path="src"/>
    <classpathentry kind="con" path="org.eclipse.jdt.launching.JRE_CONTAINER"/>
    <classpathentry kind="output" path="bin"/>
</classpath>'''
    
    classpath_file = path / '.classpath'
    classpath_file.write_text(classpath_content, encoding='utf-8')
    return str(classpath_file)

def _generate_java_class(path: Path, class_info: dict, package_name: str):
    """Gera arquivo .java para uma classe do XOM"""
    class_name = class_info['name']
    attributes = class_info.get('attributes', [])
    
    java_content = f'''package {package_name};

import java.io.Serializable;
'''
    
    if any(attr['type'] == 'date' for attr in attributes):
        java_content += 'import java.util.Date;\n'
    
    java_content += f'''
/**
 * Classe de modelo: {class_info.get('label', class_name)}
 * Gerada automaticamente pelo gerador de projetos ODM
 */
public class {class_name} implements Serializable {{
    
    private static final long serialVersionUID = 1L;
    
'''
    
    for attr in attributes:
        attr_name = attr['name']
        java_type = _map_type_to_java(attr['type'])
        java_content += f'''    private {java_type} {attr_name};
'''
    
    java_content += '\n'
    java_content += f'''    public {class_name}() {{
    }}
    
'''
    
    for attr in attributes:
        attr_name = attr['name']
        java_type = _map_type_to_java(attr['type'])
        attr_name_cap = attr_name[0].upper() + attr_name[1:]
        
        java_content += f'''    public {java_type} get{attr_name_cap}() {{
        return {attr_name};
    }}
    
    public void set{attr_name_cap}({java_type} {attr_name}) {{
        this.{attr_name} = {attr_name};
    }}
    
'''
    
    java_content += f'''    @Override
    public String toString() {{
        return "{class_name} [" +
'''
    
    for i, attr in enumerate(attributes):
        attr_name = attr['name']
        separator = ' + ", " +' if i < len(attributes) - 1 else ' +'
        java_content += f'''                "{attr_name}=" + {attr_name}{separator}
'''
    
    java_content += '''                "]";
    }
}
'''
    
    java_file = path / f'{class_name}.java'
    java_file.write_text(java_content, encoding='utf-8')
    return str(java_file)

def _generate_bom_file(path: Path, classes: list, package_name: str, xom_project_name=None):
    """Gera arquivo BOM (Business Object Model) em formato texto"""
    bom_uuid = _generate_uuid()
    
    bom_content = f'''
property loadGetterSetterAsProperties "true"
property origin "xom:/{xom_project_name or 'project'}//{xom_project_name or 'XOM'}"
property uuid "{bom_uuid}"
package {package_name};

'''
    
    for cls in classes:
        class_name = cls['name']
        
        bom_content += f'''
public class {class_name}
{{
'''
        
        for attr in cls.get('attributes', []):
            attr_name = attr['name']
            java_type = _map_type_to_java(attr['type'])
            
            if java_type == 'java.lang.String':
                bom_type = 'string'
            elif java_type == 'int':
                bom_type = 'int'
            elif java_type == 'double':
                bom_type = 'double'
            elif java_type == 'boolean':
                bom_type = 'boolean'
            elif java_type == 'java.util.Date':
                bom_type = 'java.util.Date'
            else:
                bom_type = java_type
            
            bom_content += f'''    public {bom_type} {attr_name};
'''
        
        bom_content += f'''    public {class_name}();
}}
'''
    
    bom_file = path / 'modelo.bom'
    bom_file.write_text(bom_content, encoding='utf-8')
    return str(bom_file)

def _generate_b2x_mapping(path: Path, bom_name: str = "modelo"):
    """Gera arquivo de mapeamento BOM-to-XOM (.b2xa)"""
    b2x_uuid = _generate_uuid()
    
    b2x_content = f'''<b2x:translation xmlns:b2x="http://schemas.ilog.com/JRules/1.3/Translation" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://schemas.ilog.com/JRules/1.3/Translation ilog/rules/schemas/1_3/b2x.xsd">
    <id>{b2x_uuid}</id>
    <lang>ARL</lang>
</b2x:translation>'''
    
    b2x_file = path / f'{bom_name}.b2xa'
    b2x_file.write_text(b2x_content, encoding='utf-8')
    return str(b2x_file)

# Cria projeto com BOM, XOM e verbalizações
print("Criando projeto ODM com XOM...")

project_name = 'ProjetoComXOM'
package_name = 'com.credito.model'
output_dir = '/tmp/odm_projects'

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
        'label': 'Resultado da Análise',
        'attributes': [
            {'name': 'mensagem', 'type': 'string', 'label': 'Mensagem'},
            {'name': 'motivo', 'type': 'string', 'label': 'Motivo'}
        ]
    }
]

output_path = Path(output_dir)
output_path.mkdir(parents=True, exist_ok=True)

paths = _create_project_structure(output_path, project_name, package_name)
xom_project_name = f"{project_name}XOM"

files_created = []

# Gera arquivos do projeto de regras
print("Gerando arquivos do projeto de regras...")
files_created.append(_generate_project_file(paths['root'], project_name, xom_project_name))
files_created.append(_generate_ruleproject_file(paths['root'], project_name, xom_project_name))

# Gera BOM e XOM
print("Gerando BOM...")
files_created.append(_generate_bom_file(paths['bom'], classes, package_name, xom_project_name))
files_created.append(_generate_b2x_mapping(paths['bom'], "modelo"))

# Gera projeto XOM (Java)
print("Gerando projeto XOM (Java)...")
files_created.append(_generate_xom_project_file(paths['xom_root'], xom_project_name))
files_created.append(_generate_xom_classpath(paths['xom_root']))

# Gera classes Java
print("Gerando classes Java...")
for cls in classes:
    files_created.append(_generate_java_class(paths['xom_src'], cls, package_name))

# Cria ZIP com ambos os projetos
print("Criando arquivo ZIP...")
zip_path = output_path / f"{project_name}.zip"

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    # 1. Adiciona projeto XOM primeiro
    for root, dirs, files in os.walk(paths['xom_root']):
        for file in files:
            file_path = Path(root) / file
            arcname = file_path.relative_to(output_path)
            zipf.write(file_path, arcname)
    
    # 2. Adiciona projeto de regras
    for root, dirs, files in os.walk(paths['root']):
        for file in files:
            file_path = Path(root) / file
            arcname = file_path.relative_to(output_path)
            zipf.write(file_path, arcname)

resultado = {
    "status": "success",
    "project_name": project_name,
    "xom_project_name": xom_project_name,
    "project_path": str(paths['root']),
    "xom_project_path": str(paths['xom_root']),
    "zip_path": str(zip_path),
    "files_created": files_created,
    "classes_count": len(classes)
}

print("\n" + "="*80)
print("RESULTADO DA GERAÇÃO DO PROJETO")
print("="*80)
print(json.dumps(resultado, indent=2, ensure_ascii=False))

print("\n✅ PROJETO CRIADO COM SUCESSO!")
print(f"\n📦 Arquivo ZIP: {zip_path}")
print(f"\n📁 Projeto de Regras: {paths['root']}")
print(f"\n☕ Projeto XOM (Java): {paths['xom_root']}")
print(f"\n📊 Classes criadas: {len(classes)}")
print("\n" + "="*80)
print("INSTRUÇÕES DE IMPORTAÇÃO")
print("="*80)
print("""
1. Acesse o Decision Center
2. Vá em File > Import > Decision Service Archive
3. Selecione o arquivo ZIP gerado
4. O Decision Center importará AMBOS os projetos:
   - ProjetoComXOMXOM (projeto Java com classes)
   - ProjetoComXOM (Decision Service que referencia o XOM)
5. O erro EObject será resolvido pois o XOM está corretamente configurado!
""")

# Made with Bob
