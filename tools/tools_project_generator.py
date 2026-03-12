# -*- coding: utf-8 -*-
"""
Tools para geração automática de projetos ODM Rule Designer
------------------------------------------------------------

Permite criar projetos completos do Rule Designer que podem ser importados
no Decision Center, incluindo:
- Estrutura de diretórios
- BOM (Business Object Model)
- XOM (Execution Object Model)
- Regras de negócio
- Decision Tables
- Ruleflows
- Arquivos de configuração

O projeto gerado pode ser exportado como .zip para importação no DC.
"""

import os
import json
import zipfile
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import builtins

mcp = builtins.__dict__.get("mcp")


def _create_project_structure(base_path: Path, project_name: str, package_name: str = "com.example.model") -> Dict[str, Path]:
    """Cria a estrutura de diretórios do projeto ODM com projeto XOM separado"""
    # Projeto de regras principal
    rules_project = base_path / project_name
    
    # Projeto XOM separado (Java)
    xom_project_name = f"{project_name}XOM"
    xom_project = base_path / xom_project_name
    
    # Estrutura do projeto de regras
    paths = {
        'root': rules_project,
        'rules': rules_project / 'rules',
        'bom': rules_project / 'bom',
        'deployment': rules_project / 'deployment',
        'resources': rules_project / 'resources',
        # Projeto XOM
        'xom_root': xom_project,
        'xom_src': xom_project / 'src' / package_name.replace('.', '/'),
        'xom_bin': xom_project / 'bin',
    }
    
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    
    return paths


def _generate_bom_file(path: Path, classes: List[Dict], package_name: str = "com.example.model", xom_project_name: Optional[str] = None) -> str:
    """Gera arquivo BOM (Business Object Model) em formato texto (não XML)"""
    bom_uuid = _generate_uuid()
    
    # Cabeçalho do BOM
    bom_content = f'''
property loadGetterSetterAsProperties "true"
property origin "xom:/{xom_project_name or 'project'}//{xom_project_name or 'XOM'}"
property uuid "{bom_uuid}"
package {package_name};

'''
    
    # Gera classes
    for cls in classes:
        class_name = cls['name']
        
        bom_content += f'''
public class {class_name}
{{
'''
        
        # Atributos
        for attr in cls.get('attributes', []):
            attr_name = attr['name']
            java_type = _map_type_to_java(attr['type'])
            
            # Converte tipo Java para tipo BOM
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
        
        # Construtor
        bom_content += f'''    public {class_name}();
}}
'''
    
    bom_file = path / 'modelo.bom'
    bom_file.write_text(bom_content, encoding='utf-8')
    return str(bom_file)


def _generate_xom_file(path: Path, classes: List[Dict], package_name: str = "com.example.model") -> str:
    """Gera arquivo XOM (Execution Object Model) - mapeamento BOM para Java"""
    xom_content = '''<?xml version="1.0" encoding="UTF-8"?>
<ilog.rules.studio.model.xom:XOMModel xmi:version="2.0"
    xmlns:xmi="http://www.omg.org/XMI"
    xmlns:ilog.rules.studio.model.xom="http://ilog.rules.studio/model/xom.ecore">
  <name>XOM</name>
  <uuid>''' + _generate_uuid() + '''</uuid>
'''
    
    for cls in classes:
        class_name = cls['name']
        java_class = f"{package_name}.{class_name}"
        
        xom_content += f'''  <classes name="{java_class}" label="{cls.get('label', class_name)}">
'''
        
        for attr in cls.get('attributes', []):
            attr_name = attr['name']
            java_type = _map_type_to_java(attr['type'])
            
            xom_content += f'''    <attributes name="{attr_name}" type="{java_type}"/>
'''
        
        xom_content += '''  </classes>
'''
    
    xom_content += '''</ilog.rules.studio.model.xom:XOMModel>'''
    
    xom_file = path / 'xom.xml'
    xom_file.write_text(xom_content, encoding='utf-8')
    return str(xom_file)


def _determinar_genero(nome: str, tipo: str) -> str:
    """
    Determina o gênero gramatical de um termo em português (FALLBACK automático)
    
    Args:
        nome: Nome do atributo (pode estar em camelCase)
        tipo: Tipo do atributo
    
    Returns:
        'FEMALE' ou 'MALE'
    """
    # Palavras femininas comuns (incluindo exceções que terminam em 'o')
    femininas = [
        'idade', 'renda', 'taxa', 'mensagem', 'data', 'cidade',
        'observacao', 'observação', 'avaliacao', 'avaliação',
        'prestacao', 'prestação', 'entrada', 'divida', 'dívida',
        'quantidade', 'porcentagem', 'margem', 'viagem', 'operacao', 'operação',
        'nota', 'conta', 'meta', 'venda', 'compra', 'forma', 'marca',
        'transacao', 'transação', 'situacao', 'situação', 'aprovacao', 'aprovação',
        'mao', 'mão'  # exceções que terminam em 'o' mas são femininas
    ]
    
    # Palavras masculinas comuns
    masculinas = [
        'nome', 'valor', 'prazo', 'score', 'credito', 'crédito',
        'juros', 'tipo', 'sexo', 'tempo', 'emprego', 'investimento',
        'numero', 'número', 'codigo', 'código', 'participante',
        'limite', 'saque', 'cheque', 'pacote', 'lote', 'desconto'
    ]
    
    nome_lower = nome.lower()
    
    # Verifica listas específicas primeiro
    if nome_lower in femininas:
        return 'FEMALE'
    if nome_lower in masculinas:
        return 'MALE'
    
    # Verifica se começa OU contém palavra feminina (para camelCase como dataOperacao ou OperacaoAtual)
    for palavra_fem in femininas:
        if nome_lower.startswith(palavra_fem) or palavra_fem in nome_lower:
            return 'FEMALE'
    
    # Verifica se começa OU contém palavra masculina (para camelCase como nomeCliente)
    for palavra_masc in masculinas:
        if nome_lower.startswith(palavra_masc) or palavra_masc in nome_lower:
            return 'MALE'
    
    # Regras gerais do português baseadas em terminações
    if nome_lower.endswith(('a', 'ade', 'ção', 'são', 'gem', 'ice', 'ez', 'dade')):
        return 'FEMALE'
    
    # Padrão: masculino
    return 'MALE'


def _generate_voc_file(path: Path, classes: List[Dict], package_name: str, locale: str = "pt_BR") -> str:
    """Gera arquivo de vocabulário (.voc) com verbalizações em português"""
    voc_uuid = _generate_uuid()
    
    content = f"""# Vocabulary Properties
uuid = {voc_uuid}

"""
    
    # Mapeia gêneros dos atributos
    generos = {}
    
    for cls in classes:
        for attr in cls.get('attributes', []):
            attr_name = attr['name']
            # PRIORIDADE: usa gender especificado pelo usuário, senão determina automaticamente
            gender = attr.get('gender', _determinar_genero(attr_name, attr.get('type', 'string')))
            generos[attr_name] = gender
            
            content += f"""# Term: {attr_name}
@{attr_name}#gender = {gender}

"""
    
    # Gera verbalizações para cada classe
    for cls in classes:
        class_name = cls['name']
        full_class_name = f"{package_name}.{class_name}"
        concept_label = cls.get('label', class_name).lower()
        
        # Determina o gênero da CLASSE (para PARTITIVE_ARTICLE funcionar)
        class_gender = cls.get('gender', _determinar_genero(class_name, 'class'))
        
        content += f"""# {full_class_name}
{full_class_name}#concept.label = {concept_label}
{full_class_name}#gender = {class_gender}
"""
        
        for attr in cls.get('attributes', []):
            attr_name = attr['name']
            attr_label = attr.get('label', attr_name).lower()
            gender = generos.get(attr_name, 'MALE')
            
            # Artigo definido (o/a)
            artigo = 'a' if gender == 'FEMALE' else 'o'
            
            # Frase de ação (atribuir)
            content += f"""{full_class_name}.{attr_name}#phrase.action = atribuir {artigo} {attr_label} de {{this}} a {{{attr_name}}}
"""
            
            # Frase de navegação
            content += f"""{full_class_name}.{attr_name}#phrase.navigation = {artigo} {attr_label} de {{this}}
"""
        
        content += "\n"
    
    voc_file = path / f'modelo_{locale}.voc'
    voc_file.write_text(content, encoding='utf-8')
    return str(voc_file)


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


def _generate_b2x_mapping(path: Path, bom_name: str = "modelo") -> str:
    """Gera arquivo de mapeamento BOM-to-XOM (.b2xa) - formato simplificado"""
    b2x_uuid = _generate_uuid()
    
    b2x_content = f'''<b2x:translation xmlns:b2x="http://schemas.ilog.com/JRules/1.3/Translation" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://schemas.ilog.com/JRules/1.3/Translation ilog/rules/schemas/1_3/b2x.xsd">
    <id>{b2x_uuid}</id>
    <lang>ARL</lang>
</b2x:translation>'''
    
    b2x_file = path / f'{bom_name}.b2xa'
    b2x_file.write_text(b2x_content, encoding='utf-8')
    return str(b2x_file)


def _generate_project_file(path: Path, project_name: str, xom_project_name: Optional[str] = None) -> str:
    """Gera arquivo .project do Eclipse/Rule Designer"""
    
    # Referência ao projeto XOM se houver
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


def _generate_ruleproject_file(path: Path, project_name: str, xom_project_name: Optional[str] = None) -> str:
    """Gera arquivo .ruleproject necessário para importação no Decision Center"""
    uuid = _generate_uuid()
    
    # BOM path entry se houver projeto XOM
    bom_entry = ''
    if xom_project_name:
        bom_entry = f'''
  <paths xsi:type="ilog.rules.studio.model.bom:BOMPath" pathID="BOM">
    <entries xsi:type="ilog.rules.studio.model.bom:BOMEntry" name="modelo" url="platform:/{project_name}/bom/modelo.bom" origin="xom:/{project_name}//{xom_project_name}"/>
  </paths>'''
    
    # XOM path entry se houver projeto XOM - usa SystemXOMPathEntry como no projeto real
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
    xmlns:com.ibm.rules.studio.model.decisionservice="http://com.ibm.rules.studio/model/decisionservice.ecore"
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
  <modelFolders xsi:type="com.ibm.rules.studio.model.decisionservice:OperationFolder">
    <name>deployment</name>
  </modelFolders>
</ilog.rules.studio.model.base:RuleProject>'''
    
    ruleproject_file = path / '.ruleproject'
    ruleproject_file.write_text(ruleproject_content, encoding='utf-8')
    return str(ruleproject_file)


def _generate_decisionservice_file(path: Path, project_name: str, xom_project_name: Optional[str] = None) -> str:
    """Gera arquivo .decisionservice necessário para o Decision Center reconhecer como Decision Service"""
    ds_uuid = _generate_uuid()
    
    decisionservice_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<com.ibm.rules.studio.model.decisionservice:DecisionService xmi:version="2.0"
    xmlns:xmi="http://www.omg.org/XMI"
    xmlns:com.ibm.rules.studio.model.decisionservice="http://www.ibm.com/rules/studio/model/decisionservice.ecore">
  <name>{project_name}</name>
  <uuid>{ds_uuid}</uuid>
  <locales>pt_BR</locales>
  <defaultLocale>pt_BR</defaultLocale>
  <targetRuleProjectName>{project_name}</targetRuleProjectName>
'''
    
    if xom_project_name:
        decisionservice_content += f'''  <referencedProjects>{xom_project_name}</referencedProjects>
'''
    
    decisionservice_content += '''</com.ibm.rules.studio.model.decisionservice:DecisionService>'''
    
    ds_file = path / '.decisionservice'
    ds_file.write_text(decisionservice_content, encoding='utf-8')
    return str(ds_file)


def _generate_xom_project_file(path: Path, project_name: str) -> str:
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


def _generate_xom_classpath(path: Path) -> str:
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


def _generate_java_class(path: Path, class_info: Dict, package_name: str) -> str:
    """Gera arquivo .java para uma classe do XOM"""
    class_name = class_info['name']
    attributes = class_info.get('attributes', [])
    
    # Cabeçalho da classe
    java_content = f'''package {package_name};

import java.io.Serializable;
'''
    
    # Imports adicionais se necessário
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
    
    # Atributos
    for attr in attributes:
        attr_name = attr['name']
        java_type = _map_type_to_java(attr['type'])
        java_content += f'''    private {java_type} {attr_name};
'''
    
    java_content += '\n'
    
    # Construtor padrão
    java_content += f'''    public {class_name}() {{
    }}
    
'''
    
    # Getters e Setters
    for attr in attributes:
        attr_name = attr['name']
        java_type = _map_type_to_java(attr['type'])
        attr_name_cap = attr_name[0].upper() + attr_name[1:]
        
        # Getter
        java_content += f'''    public {java_type} get{attr_name_cap}() {{
        return {attr_name};
    }}
    
'''
        
        # Setter
        java_content += f'''    public void set{attr_name_cap}({java_type} {attr_name}) {{
        this.{attr_name} = {attr_name};
    }}
    
'''
    
    # toString
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
    
    # Salva arquivo
    java_file = path / f'{class_name}.java'
    java_file.write_text(java_content, encoding='utf-8')
    return str(java_file)


def _generate_uuid() -> str:
    """Gera UUID simples para arquivos ODM"""
    import uuid
    return str(uuid.uuid4())


def _create_zip_archive(source_dir: Path, output_path: Path) -> str:
    """Cria arquivo ZIP do projeto"""
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(source_dir.parent)
                zipf.write(file_path, arcname)
    
    return str(output_path)


@mcp.tool()
def criar_projeto_odm(
    project_name: str,
    description: str = "",
    classes: Optional[List[Dict]] = None,
    package_name: str = "com.example.model",
    output_dir: str = "/tmp/odm_projects",
    create_zip: bool = True
) -> Dict:
    """
    Cria um projeto completo do ODM Rule Designer com BOM, XOM e verbalizações.
    
    O projeto gerado inclui:
    - ✅ BOM (Business Object Model) com classes e verbalizações
    - ✅ XOM (Execution Object Model) com mapeamento para Java
    - ✅ Mapeamento BOM-to-XOM (.b2x)
    - ✅ Estrutura de diretórios completa
    - ✅ Arquivo .zip pronto para importação
    SEMPRE CONSULTE A TOOL consultar_vocabulario  que mostra um vocabulario de exemplo
    ⚠️⚠️⚠️ VOCABULÁRIO DE EXEMPLO - SEMPRE USE ESTE PADRÃO! ⚠️⚠️⚠️
    
    COPIE EXATAMENTE ESTE FORMATO para seus atributos:
    
    {
        "name": "OperacaoAtual",           # camelCase
        "label": "operacao atual",          # ⚠️ palavras SEPARADAS, minúsculas
        "gender": "FEMALE",                 # ⚠️ IMPORTANTE: gênero da CLASSE (a operacao)
        "attributes": [
            {
                "name": "dataOperacao",     # camelCase
                "type": "date",
                "label": "data da operação",  # ⚠️ FRASE COMPLETA com preposições!
                "gender": "FEMALE"          # a data (feminino)
            },
            {
                "name": "valorOperacao",
                "type": "double",
                "label": "valor da operação",  # ⚠️ FRASE COMPLETA!
                "gender": "MALE"            # o valor (masculino)
            },
            {
                "name": "nomeParticipante",
                "type": "string",
                "label": "nome do participante",  # ⚠️ FRASE COMPLETA!
                "gender": "MALE"            # o nome (masculino)
            }
        ]
    }
    
    ❌ NUNCA FAÇA:
    - label: "dataOperacao" (camelCase junto)
    - label: "data" (incompleto, falta "da operação")
    - label: "OperacaoAtual" (maiúsculas)
    
    ✅ SEMPRE FAÇA:
    - label: "data da operação" (palavras separadas + preposição)
    - label: "operacao atual" (palavras separadas, minúsculas)
    - label: "nome do participante" (frase completa)
    
    Args:
        project_name: Nome do projeto (ex: "AprovarCredito")
        description: Descrição do projeto
        classes: Lista de classes do BOM. Use o VOCABULÁRIO DE EXEMPLO acima!
            [
                {
                    "name": "Cliente",
                    "label": "Cliente",
                    "verbalizations": {
                        "article": "o",  # artigo: o/a
                        "singular": "cliente",
                        "plural": "clientes"
                    },
                    "attributes": [
                        {
                            "name": "nome",
                            "type": "string",
                            "label": "Nome",
                            "gender": "MALE",  # MALE (o nome)
                            "label": "nome do cliente"  # ⚠️ FRASE COMPLETA com preposições!
                        },
                        {
                            "name": "idade",
                            "type": "int",
                            "label": "idade do cliente",  # ⚠️ FRASE COMPLETA com preposições!
                            "gender": "FEMALE"  # FEMALE (a idade)
                        }
                    ]
                }
            ]
        package_name: Pacote Java para XOM (padrão: "com.example.model")
        output_dir: Diretório de saída (padrão: /tmp/odm_projects)
        create_zip: Se True, cria .zip (padrão: True)
    
    Returns:
        Dict com informações do projeto criado
    
    Tipos Suportados:
        - string → java.lang.String
        - int → int
        - double → double
        - boolean → boolean
        - date → java.util.Date
    
    📋 GÊNERO GRAMATICAL - RECOMENDADO ESPECIFICAR!
    
        O campo "gender" é ALTAMENTE RECOMENDADO para garantir verbalizações corretas.
        
        ✅ MELHOR PRÁTICA: Sempre especifique o gender manualmente quando souber:
        
        ⚙️ FALLBACK AUTOMÁTICO: Se você NÃO especificar, o sistema determinará automaticamente
        baseado nas regras abaixo. Mas é melhor especificar para garantir precisão!
        
        💡 DICA: Use consultar_vocabulario() para ver gêneros de projetos existentes!
        
        📚 REGRAS PARA IDENTIFICAR O GÊNERO (use quando especificar manualmente):
        
        🔴 FEMININO (FEMALE) - usa artigo "a":
        
        1. Palavras terminadas em 'A':
           - data, renda, taxa, entrada, saída, nota, conta, meta, venda, compra
           - regra, forma, norma, firma, marca, etapa, fase, área
           
        2. Palavras terminadas em 'ÇÃO' ou 'SÃO':
           - operação, avaliação, prestação, observação, transação, situação
           - aprovação, negação, decisão, revisão, divisão, precisão
           
        3. Palavras terminadas em 'GEM':
           - mensagem, viagem, margem, porcentagem, imagem, passagem
           
        4. Palavras terminadas em 'DADE':
           - idade, quantidade, cidade, qualidade, velocidade, capacidade
           
        5. Outras palavras femininas comuns:
           - dívida, divida, parte, classe, base, ordem, origem
        
        🔵 MASCULINO (MALE) - usa artigo "o":
        
        1. Palavras terminadas em 'O':
           - prazo, emprego, investimento, crédito, débito, saldo, período
           - tipo, sexo, tempo, número, código, método, processo
           
        2. Palavras terminadas em 'OR':
           - valor, participante, cliente, usuário, fornecedor, comprador
           
        3. Palavras terminadas em 'E' (maioria):
           - nome, score, limite, saque, cheque, pacote, lote
           
        4. Outras palavras masculinas comuns:
           - juros, desconto, acréscimo, total, subtotal, montante
        
        📝 COMO IDENTIFICAR EM PALAVRAS COMPOSTAS (camelCase):
        
        Para "dataOperacao":
        1. Identifique a primeira palavra: "data"
        2. "data" termina em 'a' → FEMININO
        3. gender = "FEMALE"
        
        Para "nomeCliente":
        1. Identifique a primeira palavra: "nome"
        2. "nome" termina em 'e' e é masculino → MASCULINO
        3. gender = "MALE"
        
        Para "valorOperacao":
        1. Identifique a primeira palavra: "valor"
        2. "valor" termina em 'or' → MASCULINO
        3. gender = "MALE"
        
        ✅ EXEMPLOS PRÁTICOS COM ANÁLISE:
        
        {"name": "dataOperacao", "gender": "FEMALE"}     # data (termina em 'a') = feminino
        {"name": "nomeCliente", "gender": "MALE"}        # nome (palavra masculina) = masculino
        {"name": "valorOperacao", "gender": "MALE"}      # valor (termina em 'or') = masculino
        {"name": "idadeCliente", "gender": "FEMALE"}     # idade (termina em 'dade') = feminino
        {"name": "mensagemErro", "gender": "FEMALE"}     # mensagem (termina em 'gem') = feminino
        {"name": "prazoVencimento", "gender": "MALE"}    # prazo (termina em 'o') = masculino
        {"name": "taxaJuros", "gender": "FEMALE"}        # taxa (termina em 'a') = feminino
        {"name": "scoreCredito", "gender": "MALE"}       # score (palavra masculina) = masculino
        {"name": "quantidadeItens", "gender": "FEMALE"}  # quantidade (termina em 'dade') = feminino
        {"name": "tipoOperacao", "gender": "MALE"}       # tipo (termina em 'o') = masculino
        
        ❌ NUNCA OMITA O CAMPO GENDER - SEMPRE ANALISE E ESPECIFIQUE!
    
    ⚠️⚠️⚠️  ATENÇÃO: LABELS SÃO OBRIGATÓRIOS PARA CLASSES E ATRIBUTOS! ⚠️⚠️⚠️
    
        VOCÊ DEVE SEMPRE FORNECER O CAMPO "label" TANTO PARA CLASSES QUANTO PARA ATRIBUTOS!
        
        Se você NÃO fornecer o label, o nome em camelCase será usado e ficará ERRADO (tudo junto).
        
        ❌ SE VOCÊ FIZER ISSO:
            {"name": "OperacaoAtual"}  # SEM label
        
        ❌ VAI GERAR ERRADO:
            "operacaoatual" (tudo junto)
        
        ✅ VOCÊ DEVE FAZER ASSIM:
            {"name": "OperacaoAtual", "label": "operacao atual"}
        
        ✅ VAI GERAR CORRETO:
            "operacao atual" (separado)
    
    ⚠️  REGRAS CRÍTICAS PARA LABELS (VERBALIZAÇÕES):
    
        O label deve conter a FRASE COMPLETA com preposições e palavras separadas.
        
        ❌ ERRADO - Palavras juntas ou sem preposições:
            {"name": "dataOperacao", "label": "dataOperacao"}     → gera "dataoperacao" (tudo junto)
            {"name": "dataOperacao", "label": "data"}             → gera "a data" (incompleto)
            {"name": "nomeCliente", "label": "nome"}              → gera "o nome" (incompleto)
        
        ✅ CORRETO - Frase completa com preposições:
            {"name": "dataOperacao", "label": "data da operação"}     → gera "a data da operação"
            {"name": "nomeCliente", "label": "nome do cliente"}       → gera "o nome do cliente"
            {"name": "valorOperacao", "label": "valor da operação"}   → gera "o valor da operação"
            {"name": "viagemCliente", "label": "viagem do cliente"}   → gera "a viagem do cliente"
        
        📋 IMPORTANTE TAMBÉM PARA NOMES DE CLASSES:
            O nome da classe também deve ter palavras separadas no label!
            
            ❌ ERRADO:
                {"name": "OperacaoAtual", "label": "OperacaoAtual"}  → gera "operacaoatual" (junto)
            
            ✅ CORRETO:
                {"name": "OperacaoAtual", "label": "operacao atual"} → gera "operacao atual"
                {"name": "ClienteVip", "label": "cliente vip"}       → gera "cliente vip"
        
        📝 Padrão para Criar Labels:
            1. Identifique as palavras no camelCase (ex: dataOperacao)
            2. Separe com espaços (ex: data operacao)
            3. Adicione preposições apropriadas (ex: data da operação)
            
            Exemplos Completos:
            - dataOperacao     → "data da operação"
            - nomeParticipante → "nome do participante"
            - valorOperacao    → "valor da operação"
            - viagemCliente    → "viagem do cliente"
            - scoreCredito     → "score de crédito"
            - OperacaoAtual    → "operacao atual"
            - ClienteVip       → "cliente vip"
    
    Example:
        >>> criar_projeto_odm(
        ...     project_name="AprovarCredito",
        ...     description="Sistema de aprovação de crédito",
        ...     classes=[
        ...         {
        ...             "name": "OperacaoAtual",
        ...             "label": "operacao atual",  # ✅ CORRETO: palavras separadas!
        ...             "attributes": [
        ...                 {
        ...                     "name": "dataOperacao",
        ...                     "type": "date",
        ...                     "label": "data da operação",
        ...                     "gender": "FEMALE"  # ✅ OBRIGATÓRIO!
        ...                 },
        ...                 {
        ...                     "name": "valorOperacao",
        ...                     "type": "double",
        ...                     "label": "valor da operação",
        ...                     "gender": "MALE"  # ✅ OBRIGATÓRIO!
        ...                 },
        ...                 {
        ...                     "name": "nomeParticipante",
        ...                     "type": "string",
        ...                     "label": "nome do participante",
        ...                     "gender": "MALE"  # ✅ OBRIGATÓRIO!
        ...                 }
        ...             ]
        ...         }
        ...     ],
        ...     package_name="com.credito.model"
        ... )
        
        >>> # Outro exemplo com classe ClienteVip
        >>> criar_projeto_odm(
        ...     project_name="GestaoClientes",
        ...     classes=[
        ...         {
        ...             "name": "ClienteVip",
        ...             "label": "cliente vip",  # ✅ CORRETO: palavras separadas!
        ...             "attributes": [
        ...                 {"name": "nomeCompleto", "type": "string", "label": "nome completo", "gender": "MALE"},
        ...                 {"name": "scoreCredito", "type": "int", "label": "score de crédito", "gender": "MALE"}
        ...             ]
        ...         }
        ...     ]
        ... )
    """
    try:
        # Valores padrão
        if classes is None:
            classes = []
        
        # Cria diretório de saída
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Cria estrutura do projeto (regras + XOM)
        paths = _create_project_structure(output_path, project_name, package_name)
        
        files_created = []
        xom_project_name = f"{project_name}XOM"
        
        # Gera arquivo .project do projeto de regras (com referência ao XOM)
        project_file = _generate_project_file(
            paths['root'],
            project_name,
            xom_project_name if classes else None
        )
        files_created.append(project_file)
        
        # Gera arquivo .ruleproject (com isADecisionService="true")
        ruleproject_file = _generate_ruleproject_file(
            paths['root'],
            project_name,
            xom_project_name if classes else None
        )
        files_created.append(ruleproject_file)
        
        # Gera BOM e XOM se houver classes definidas
        if classes:
            # BOM em formato texto (como no projeto real)
            bom_file = _generate_bom_file(
                paths['bom'],
                classes,
                package_name,
                xom_project_name
            )
            files_created.append(bom_file)
            
            # Mapeamento BOM-to-XOM (arquivo .b2xa simples)
            b2x_file = _generate_b2x_mapping(paths['bom'], "modelo")
            files_created.append(b2x_file)
            
            # Gera arquivo de vocabulário com verbalizações em português
            voc_file = _generate_voc_file(paths['bom'], classes, package_name, "pt_BR")
            files_created.append(voc_file)
            
            # ===== PROJETO XOM (Java) =====
            # Gera .project do XOM
            xom_project_file = _generate_xom_project_file(paths['xom_root'], xom_project_name)
            files_created.append(xom_project_file)
            
            # Gera .classpath do XOM
            xom_classpath_file = _generate_xom_classpath(paths['xom_root'])
            files_created.append(xom_classpath_file)
            
            # Gera classes Java
            for cls in classes:
                java_file = _generate_java_class(paths['xom_src'], cls, package_name)
                files_created.append(java_file)
        
        # Gera arquivo de metadados do projeto
        metadata = {
            "name": project_name,
            "xom_project_name": xom_project_name if classes else None,
            "description": description,
            "created": datetime.now().isoformat(),
            "version": "1.0.0",
            "classes_count": len(classes),
            "package_name": package_name,
            "has_bom": len(classes) > 0,
            "has_xom": len(classes) > 0,
            "has_xom_project": len(classes) > 0,
            "has_verbalizations": len(classes) > 0,
            "java_classes": [cls['name'] for cls in classes] if classes else []
        }
        
        metadata_file = paths['root'] / 'project_metadata.json'
        metadata_file.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
        files_created.append(str(metadata_file))
        
        result = {
            "status": "success",
            "project_name": project_name,
            "xom_project_name": xom_project_name if classes else None,
            "project_path": str(paths['root']),
            "xom_project_path": str(paths['xom_root']) if classes else None,
            "files_created": files_created,
            "metadata": metadata
        }
        
        # Cria arquivo ZIP com AMBOS os projetos (XOM + Decision Service)
        if create_zip:
            zip_path = output_path / f"{project_name}.zip"
            
            # Cria ZIP com ambos os projetos na ordem correta
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 1. PRIMEIRO: Adiciona projeto XOM (Java) se houver classes
                if classes:
                    for root, dirs, files in os.walk(paths['xom_root']):
                        for file in files:
                            file_path = Path(root) / file
                            arcname = file_path.relative_to(output_path)
                            zipf.write(file_path, arcname)
                
                # 2. DEPOIS: Adiciona projeto de regras (Decision Service)
                for root, dirs, files in os.walk(paths['root']):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(output_path)
                        zipf.write(file_path, arcname)
            
            result["zip_path"] = str(zip_path)
            
            xom_instructions = ""
            if classes:
                xom_instructions = f"""
✅ Projeto XOM incluído:
O projeto XOM '{xom_project_name}' está incluído no ZIP junto com o Decision Service.
O Decision Service referencia o XOM através da configuração "Required Java projects".
Ao importar no Decision Center, ambos os projetos serão importados automaticamente.
"""

            result["import_instructions"] = f"""
Para importar no Decision Center:
1. Acesse o Decision Center
2. Vá em File > Import > Decision Service Archive
3. Selecione o arquivo: {zip_path}
4. Siga o assistente de importação
5. O Decision Service '{project_name}' estará disponível com:
   - BOM com verbalizações em português
   - Mapeamento BOM-to-XOM (referencia '{xom_project_name if classes else 'N/A'}')
{xom_instructions}
Próximos passos após importação:
- Use 'criar_regra' para adicionar regras
- Use 'criar_decision_table' para adicionar tabelas de decisão
- Use 'criar_ruleflow' para adicionar fluxos
- Use 'criar_variable' para adicionar variáveis
"""
        
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "project_name": project_name
        }


@mcp.tool()
def criar_projeto_exemplo(
    project_name: str = "ExemploCredito",
    output_dir: str = "/tmp/odm_projects"
) -> Dict:
    """
    Cria um projeto de exemplo com BOM básico para aprovação de crédito.
    
    Este projeto contém apenas a estrutura e o BOM (classes).
    Após importar no Decision Center, use as outras tools para adicionar
    regras, decision tables e ruleflows.
    
    Args:
        project_name: Nome do projeto (padrão: "ExemploCredito")
        output_dir: Diretório de saída (padrão: /tmp/odm_projects)
    
    Returns:
        Dict com informações do projeto gerado
    
    Example:
        >>> criar_projeto_exemplo("MeuProjetoCredito")
        {
            "status": "success",
            "project_name": "MeuProjetoCredito",
            "zip_path": "/tmp/odm_projects/MeuProjetoCredito.zip",
            ...
        }
    """
    
    # Define classes do BOM
    classes = [
        {
            "name": "Cliente",
            "label": "Cliente",
            "attributes": [
                {"name": "nome", "type": "string", "label": "Nome", "gender": "MALE"},
                {"name": "idade", "type": "int", "label": "Idade", "gender": "FEMALE"},
                {"name": "renda", "type": "double", "label": "Renda Mensal", "gender": "FEMALE"},
                {"name": "scoreCredito", "type": "int", "label": "Score de Crédito", "gender": "MALE"}
            ]
        },
        {
            "name": "Emprestimo",
            "label": "Empréstimo",
            "attributes": [
                {"name": "valor", "type": "double", "label": "Valor Solicitado", "gender": "MALE"},
                {"name": "prazo", "type": "int", "label": "Prazo em Meses", "gender": "MALE"},
                {"name": "aprovado", "type": "boolean", "label": "Aprovado", "gender": "MALE"},
                {"name": "taxaJuros", "type": "double", "label": "Taxa de Juros", "gender": "FEMALE"}
            ]
        },
        {
            "name": "Resultado",
            "label": "Resultado",
            "attributes": [
                {"name": "mensagem", "type": "string", "label": "Mensagem", "gender": "FEMALE"},
                {"name": "motivo", "type": "string", "label": "Motivo", "gender": "MALE"}
            ]
        }
    ]
    
    return criar_projeto_odm(
        project_name=project_name,
        description="Projeto de exemplo para aprovação de crédito - Use as outras tools para adicionar regras",
        classes=classes,
        output_dir=output_dir,
        create_zip=True
    )


@mcp.tool()
def criar_e_importar_projeto(
    project_name: str,
    description: str = "",
    classes: Optional[List[Dict]] = None,
    output_dir: str = "/tmp/odm_projects"
) -> Dict:
    """
    Cria um projeto ODM e importa automaticamente no Decision Center.
    
    ⚠️⚠️⚠️ VOCABULÁRIO DE EXEMPLO - SEMPRE USE ESTE PADRÃO! ⚠️⚠️⚠️
    
    COPIE EXATAMENTE ESTE FORMATO para seus atributos:
    
    classes=[
        {
            "name": "OperacaoAtual",           # camelCase
            "label": "operacao atual",          # ⚠️ palavras SEPARADAS, minúsculas
            "gender": "FEMALE",                 # ⚠️ IMPORTANTE: gênero da CLASSE (a operacao)
            "attributes": [
                {
                    "name": "dataOperacao",     # camelCase
                    "type": "date",
                    "label": "data da operação",  # ⚠️ FRASE COMPLETA com preposições!
                    "gender": "FEMALE"          # a data (feminino)
                },
                {
                    "name": "valorOperacao",
                    "type": "double",
                    "label": "valor da operação",  # ⚠️ FRASE COMPLETA!
                    "gender": "MALE"            # o valor (masculino)
                },
                {
                    "name": "nomeParticipante",
                    "type": "string",
                    "label": "nome do participante",  # ⚠️ FRASE COMPLETA!
                    "gender": "MALE"            # o nome (masculino)
                }
            ]
        }
    ]
    
    ❌ NUNCA FAÇA:
    - label: "dataOperacao" (camelCase junto)
    - label: "data" (incompleto, falta "da operação")
    - label: "OperacaoAtual" (maiúsculas)
    
    ✅ SEMPRE FAÇA:
    - label: "data da operação" (palavras separadas + preposição)
    - label: "operacao atual" (palavras separadas, minúsculas)
    - label: "nome do participante" (frase completa)
    
    ⚠️ IMPORTANTE - WORKFLOW OBRIGATÓRIO APÓS IMPORTAÇÃO:
    Quando um documento (PDF, DOCX, XLSX) for fornecido pelo usuário:
    1. ✅ Analise o documento para identificar regras de negócio
    2. ✅ Crie TODAS as regras encontradas usando criar_regra()
    3. ✅ Crie decision tables se houver tabelas de decisão usando criar_decision_table()
    4. ✅ Crie ruleflows para organizar a execução usando criar_ruleflow()
    5. ✅ Valide que todas as regras foram criadas com sucesso
    
    NÃO deixe o projeto vazio após importação se houver regras no documento!
    
    Esta é uma tool de conveniência que combina:
    1. criar_projeto_odm() - Cria o projeto e gera .zip
    2. importar_projeto() - Importa o .zip no Decision Center
    3. [OBRIGATÓRIO] Criar regras/DTs/flows se documento fornecido
    
    Args:
        project_name: Nome do projeto
        description: Descrição do projeto
        classes: Lista de classes do BOM (opcional)
        output_dir: Diretório de saída (padrão: /tmp/odm_projects)
    
    Returns:
        Dict com resultado completo:
        {
            "status": "success",
            "project_created": {...},
            "project_imported": {...},
            "decision_service_id": "ID do DS no DC",
            "next_steps": "Instruções..."
        }
    
    Workflow Automático:
        1. ✅ Cria estrutura do projeto
        2. ✅ Gera BOM com classes
        3. ✅ Cria arquivo .zip
        4. ✅ Importa no Decision Center
        5. ⚠️ [OBRIGATÓRIO] Analisa documento e cria regras/DTs/flows
        6. ✅ Valida criação completa
    
    Example:
        >>> criar_e_importar_projeto(
        ...     project_name="SistemaCredito",
        ...     description="Sistema de análise de crédito",
        ...     classes=[
        ...         {
        ...             "name": "Cliente",
        ...             "attributes": [
        ...                 {"name": "nome", "type": "string"},
        ...                 {"name": "idade", "type": "int"}
        ...             ]
        ...         }
        ...     ]
        ... )
    """
    # Importa a tool de importação
    from tools.tools_decisioncenter import importar_projeto
    
    # Passo 1: Criar projeto
    create_result = criar_projeto_odm(
        project_name=project_name,
        description=description,
        classes=classes,
        output_dir=output_dir,
        create_zip=True
    )
    
    if create_result.get("status") != "success":
        return {
            "status": "error",
            "error": "Falha ao criar projeto",
            "details": create_result
        }
    
    # Passo 2: Importar no Decision Center
    import_result = importar_projeto(create_result["zip_path"])
    
    if import_result.get("status") != "success":
        return {
            "status": "partial_success",
            "message": "Projeto criado mas falha na importação",
            "project_created": create_result,
            "import_error": import_result,
            "manual_import": f"Importe manualmente: {create_result['zip_path']}"
        }
    
    # Sucesso completo
    return {
        "status": "success",
        "message": f"Projeto '{project_name}' criado e importado com sucesso!",
        "project_created": create_result,
        "project_imported": import_result,
        "decision_service_id": import_result.get("decision_service_id"),
        "classes_in_bom": classes if classes else [],
        "next_steps": f"""
Projeto '{project_name}' está pronto no Decision Center!

⚠️ AÇÃO OBRIGATÓRIA - Se você recebeu um documento (PDF/DOCX/XLSX):
   VOCÊ DEVE AGORA:
   1. Analisar o documento para identificar TODAS as regras de negócio
   2. Criar CADA regra usando criar_regra()
   3. Criar decision tables se houver usando criar_decision_table()
   4. Criar ruleflow para organizar execução usando criar_ruleflow()
   5. Validar que TODAS as regras foram criadas

Próximos passos para adicionar conteúdo:
1. Adicionar regras:
   criar_regra(projectName="{project_name}", packageName="...", ruleName="...", body="...")

2. Adicionar Decision Tables:
   criar_decision_table(projectName="{project_name}", packageName="...", tableName="...", model={{...}})

3. Adicionar Ruleflows:
   criar_ruleflow(projectName="{project_name}", packageName="...", ruleflowName="...", bodyDRF="...")

4. Adicionar Variáveis:
   criar_variable(projectName="{project_name}", variableName="...", value=..., varType="...")
"""
    }


# Log de inicialização
import logging
log = logging.getLogger(__name__)
log.info("Módulo tools_project_generator carregado com sucesso")

# Made with Bob
