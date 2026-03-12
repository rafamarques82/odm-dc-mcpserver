#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera arquivo de vocabulário (.voc) para verbalizações em português
"""

def gerar_vocabulario(classes, package_name, output_path):
    """
    Gera arquivo .voc com verbalizações em português
    
    Args:
        classes: Lista de classes com atributos e gêneros
        package_name: Nome do pacote Java
        output_path: Caminho para salvar o arquivo
    """
    import uuid
    
    voc_uuid = str(uuid.uuid4())
    
    content = f"""# Vocabulary Properties
uuid = {voc_uuid}

"""
    
    # Mapeia gêneros dos atributos
    generos = {}
    
    for cls in classes:
        for attr in cls.get('attributes', []):
            attr_name = attr['name']
            # Determina gênero baseado no nome ou tipo
            gender = determinar_genero(attr_name, attr.get('type', 'string'))
            generos[attr_name] = gender
            
            content += f"""# Term: {attr_name}
@{attr_name}#gender = {gender}

"""
    
    # Gera verbalizações para cada classe
    for cls in classes:
        class_name = cls['name']
        full_class_name = f"{package_name}.{class_name}"
        concept_label = cls.get('label', class_name).lower()
        
        content += f"""# {full_class_name}
{full_class_name}#concept.label = {concept_label}
"""
        
        for attr in cls.get('attributes', []):
            attr_name = attr['name']
            attr_label = attr.get('label', attr_name).lower()
            gender = generos.get(attr_name, 'MALE')
            
            # Artigo definido (o/a)
            artigo = 'a' if gender == 'FEMALE' else 'o'
            
            # Frase de ação (atribuir)
            content += f"""{full_class_name}.{attr_name}#phrase.action = atribuir {artigo} {attr_label} {{this, PARTITIVE_ARTICLE}} a {{{attr_name}}}
"""
            
            # Frase de navegação
            content += f"""{full_class_name}.{attr_name}#phrase.navigation = {{{attr_name}}} {{this, PARTITIVE_ARTICLE}}
"""
        
        content += "\n"
    
    # Salva arquivo
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return output_path


def determinar_genero(nome, tipo):
    """
    Determina o gênero gramatical de um termo em português
    
    Args:
        nome: Nome do atributo
        tipo: Tipo do atributo
    
    Returns:
        'FEMALE' ou 'MALE'
    """
    # Palavras femininas comuns
    femininas = [
        'idade', 'renda', 'taxa', 'mensagem', 'data', 'cidade',
        'observacao', 'observação', 'avaliacao', 'avaliação',
        'prestacao', 'prestação', 'entrada', 'divida', 'dívida'
    ]
    
    # Palavras masculinas comuns
    masculinas = [
        'nome', 'valor', 'prazo', 'score', 'credito', 'crédito',
        'juros', 'tipo', 'sexo', 'tempo', 'emprego', 'investimento'
    ]
    
    nome_lower = nome.lower()
    
    # Verifica listas específicas
    if nome_lower in femininas:
        return 'FEMALE'
    if nome_lower in masculinas:
        return 'MALE'
    
    # Regras gerais do português
    if nome_lower.endswith(('a', 'ade', 'ção', 'são', 'gem', 'ice', 'ez', 'dade')):
        return 'FEMALE'
    
    # Padrão: masculino
    return 'MALE'


if __name__ == '__main__':
    # Exemplo de uso
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
    
    output = gerar_vocabulario(
        classes,
        'com.credito.model',
        '/tmp/odm_projects/ProjetoComXOM/bom/modelo_pt_BR.voc'
    )
    
    print(f"✅ Vocabulário gerado: {output}")
    print("\nConteúdo:")
    with open(output, 'r', encoding='utf-8') as f:
        print(f.read())

# Made with Bob
