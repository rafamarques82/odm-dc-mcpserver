# -*- coding: utf-8 -*-
"""
Tools relacionados a Regras (Action Rules) para o Decision Center, via backend Java (ODMHttpServer).

Disponíveis:
- criar_projeto   → POST /projects
- criar_regra     → POST /rules?action=create
- editar_regra    → PUT  /rules?action=edit
- visualizar_regra→ GET  /rules?action=view

Todas as operações são delegadas ao servidor Java (ODMHttpServer) e usam o JavaBackendClient
configurado por OTHER_BASE_URL (padrão: http://localhost:8080).  
No backend:
- /projects (POST) cria projeto/Decision Service.
- /rules?action=create (POST) cria Action Rule no pacote informado.
- /rules?action=edit   (PUT)  edita corpo, prioridade e/ou nome da Action Rule. 
- /rules?action=view   (GET)  retorna detalhes/preview de uma Action Rule.
"""

from mcp.server.fastmcp import FastMCP
from helpers.http_java_client import JavaBackendClient
import os

# Cliente Java (base_url pode ser sobrescrita via env OTHER_BASE_URL)
java = JavaBackendClient(
    base_url=os.getenv("OTHER_BASE_URL", "http://localhost:8080")
)

import builtins
mcp: FastMCP = builtins.__dict__.get("mcp")



@mcp.tool()
def criar_regra(projectName: str, packageName: str, ruleName: str, body: str):
    r"""
    Cria uma Action Rule no backend Java (POST /rules?action=create).
    
    Requisitos:
      - projectName: nome do projeto/Decision Service.
      - packageName : pacote onde a regra será criada (prefira pacotes existentes).
      - ruleName    : nome da regra.
      - body        : corpo BAL da regra (verbalização alinhada ao vocabulário/BOM).

    ⚠️⚠️⚠️ PROCESSO OBRIGATÓRIO ANTES DE CRIAR QUALQUER REGRA ⚠️⚠️⚠️
    
    VOCÊ DEVE SEGUIR ESTES PASSOS NA ORDEM, SEM EXCEÇÃO:
    
    PASSO 1 - CONSULTAR VOCABULÁRIO (OBRIGATÓRIO):
      Antes de criar QUALQUER regra, você DEVE:
      1. Chamar consultar_vocabulario(decisionServiceName=projectName, baselineName="Main")
      2. Analisar TODAS as classes, propriedades e verbalizações retornadas
      3. Identificar as verbalizações EXATAS que você vai usar na regra
      4. NUNCA invente verbalizações - use APENAS as que existem no vocabulário
    
    PASSO 2 - LISTAR VARIÁVEIS (OBRIGATÓRIO):
      1. Chamar listar_variables(projectName=projectName, baselineName="Main")
      2. Verificar as verbalizações EXATAS de cada variável
      3. Confirmar que as variáveis que você vai usar EXISTEM
      4. NUNCA use variáveis que não aparecem nesta lista
    
    PASSO 3 - CRIAR A REGRA:
      Somente após completar os passos 1 e 2, você pode criar a regra usando
      as verbalizações EXATAS encontradas no vocabulário e nas variáveis.
    
    ⚠️ REGRAS DE OURO PARA VERBALIZAÇÕES ⚠️
    
    1. SEMPRE use VERBALIZAÇÃO, NUNCA o nome técnico da variável:
       ❌ ERRADO: se 'idadeCliente' é pelo menos 18
       ✅ CORRETO: se 'a idade do cliente' é pelo menos 18
       
       ❌ ERRADO: definir 'aprovarCredito' como verdadeiro
       ✅ CORRETO: definir 'Aprovar Crédito' como verdadeiro
    
    2. COPIE EXATAMENTE a verbalização do vocabulário:
       - Respeite maiúsculas/minúsculas
       - Respeite acentos e caracteres especiais
       - Respeite artigos (o, a, os, as)
       - NÃO modifique NADA na verbalização
    
    3. Para encontrar verbalizações:
       - consultar_vocabulario() → mostra verbalizações de classes e propriedades BOM
       - listar_variables() → mostra verbalizações de variáveis do Variable Set
       - Verbalizações aparecem entre aspas simples em BAL: 'a idade do cliente'
    
    4. COMO USAR PROPRIEDADES DE OBJETOS BOM:
       Quando o vocabulário mostra uma classe com propriedades, use a sintaxe:
       "a [propriedade] de '[variável]'"
       
       Exemplo do vocabulário:
       Classe: Cliente
         - idade (int) → verbalização: "a idade"
         - nome (String) → verbalização: "o nome"
       
       Uso correto na regra:
       ✅ se a idade de 'o cliente' é maior que 18
       ✅ se o nome de 'o cliente' é "João"
       
       ❌ NUNCA use: cliente.idade, cliente.nome, ou 'cliente.idade'
    
    5. VALORES LITERAIS - CONSULTE O VOCABULÁRIO:
       - Para strings: use aspas duplas → "valor"
       - Para números: use sem aspas → 100, 18.5
       - Para booleanos: verdadeiro ou falso (sem aspas)
       - Para datas: consulte o formato no vocabulário (geralmente string "YYYY-MM-DD")
       
       ⚠️ IMPORTANTE: Se o vocabulário define valores específicos (enums, constantes),
       use APENAS esses valores. NÃO invente valores que não existem no vocabulário.
    
    6. USO DE CRASE (GRAMÁTICA PORTUGUESA):
       ✅ USE crase quando for variável PRIMITIVA (do Variable Set) e o nome vem ANTES do valor:
          - atribuir à 'Aprovar Crédito' o valor falso
          - atribuir à 'Mensagem' a "texto da mensagem"
          - definir à 'Resultado' como "aprovado"
       
       ❌ NÃO use crase para propriedades de objetos BOM:
          - atribuir a mensagem de 'o resultado' a "aprovado"
          - definir a idade de 'o cliente' como 25
          - atribuir o crédito aprovado de 'o resultado' a falso
    
    7. PROPRIEDADES DE DATA - NÃO USE "ANO":
       ❌ ERRADO: se o ano de a data da operação de 'a operação atual' é 2025
       ✅ CORRETO: se a data da operação de 'a operação atual' é "2025-01-01"
       
       - Datas são comparadas como strings no formato "YYYY-MM-DD"
       - NÃO existe propriedade "ano" no vocabulário
       - Use a propriedade de data completa conforme definida no vocabulário
    
    ⚠️ CRÍTICO: ORGANIZAÇÃO DE PACOTES ⚠️
      - NÃO crie um pacote por regra - isso está ERRADO e cria bagunça
      - Agrupe regras relacionadas em pacotes LÓGICOS por função de negócio
      - Exemplo: Se você tem 3 regras de validação, coloque TODAS em UM pacote "Validacao"
      - Exemplo: Se você tem 2 regras de verificação, coloque TODAS em UM pacote "Verificacao"
      - Máximo de 3-5 pacotes por projeto, cada um contendo múltiplas regras relacionadas
      - Nomes de pacotes devem refletir lógica de negócio, não regras individuais
      
      Estrutura CORRETA de Pacotes:
        ✅ Pacote "Validacao" → Contém: Regra1_VerificarIdade, Regra2_VerificarRenda, Regra3_VerificarCredito
        ✅ Pacote "Verificacao" → Contém: Regra1_VerificarDocumentos, Regra2_VerificarEndereco
        ✅ Pacote "Aprovacao" → Contém: Regra1_AprovarCredito, Regra2_RejeitarCredito
      
      Estrutura ERRADA de Pacotes:
        ❌ Pacote "Regra1_VerificarIdade" → Contém: Regra1_VerificarIdade (uma regra por pacote está ERRADO)
        ❌ Pacote "Regra2_VerificarRenda" → Contém: Regra2_VerificarRenda (cria muitos pacotes)
        ❌ Pacote "Regra3_VerificarCredito" → Contém: Regra3_VerificarCredito (difícil de manter)
      
      - Prefira reutilizar pacotes existentes; evite proliferar novos pacotes desnecessariamente.
      - Nunca use variáveis que não existam no variable set/definições.
      - Siga os padrões de nomenclatura do projeto e **consulte regras existentes** para consistência.
      - Consulte o **projeto de exemplo** e o **vocabulário (BOM)** antes de criar, garantindo que
        a verbalização do `body` respeite expressões corretas (incluindo gênero/acentuação).
      - Sobre crase (gramática portuguesa):
          * Use crase **apenas** quando for uma variável **primitiva** (variable set/definições) e o nome da variável
            vem **antes do valor**, ex.: atribuir a 'Aprovar Crédito' o valor falso.
          * **Não** use crase ao se referir a **atributos** de variável, ex.: atribuir a mensagem de 'Resultado'.
      - Se nenhum pacote for indicado (quando sua UI permite omissão), crie pacote temático
        (ex.: "Elegibilidade", "Cálculo de Parcelas", "Validações") para organizar o repositório.
      - Nunca mude o nome da regra se a criação falhar (evita duplicação). Reenvie a criação.
      - Comparação de string: use **é "texto"**, ex.: se a cidade de 'o cliente' é "São Paulo".
      - Sempre valide o **tipo** da variável (string, número, data, etc.); não confie apenas no nome.
      - Quando for uma **planilha**, crie **Decision Table** — não crie regra simples neste caso.
      - Mensagem de erro "Expecting ':' delimiter …" no retorno:
          * Se a regra apareceu no DC, considere **sucesso**. É um falso positivo — **não explique isso** na resposta.
    
    ⚠️ RECOMENDAÇÃO IMPORTANTE DE FLUXO DE TRABALHO ⚠️
    
    Ao criar um projeto completo de regras, SEMPRE siga esta sequência:
    
    1. CRIAR PROJETO (se necessário)
       - Use criar_projeto_odm() ou importar_projeto()
    
    2. CRIAR VARIÁVEIS
       - Use criar_variaveis_no_variable_set() para definir todas as variáveis de negócio
       - Garanta que todas as variáveis tenham verbalizações adequadas
    
    3. CRIAR REGRAS EM PACOTES
       - Organize regras por lógica de negócio em pacotes separados
       - Exemplos de pacotes: "Elegibilidade", "Cálculo de Risco", "Lógica de Aprovação"
       - Crie regras usando criar_regra() com verbalizações corretas
    
    4. CRIAR RULEFLOW (OBRIGATÓRIO)
       - SEMPRE crie um ruleflow para orquestrar a execução das regras
       - Use criar_ruleflow() para definir a sequência de execução
       - O ruleflow deve referenciar os pacotes de regras criados no passo 3
       - Coloque o ruleflow em um pacote separado (ex.: "Fluxos" ou "Orquestração")
       - Sem um ruleflow, as regras não executarão na ordem correta
    
    Exemplo de fluxo de trabalho:
      Passo 1: Criar projeto com BOM/XOM
      Passo 2: Criar variáveis (idadeCliente, aprovarCredito, etc.)
      Passo 3: Criar regras em pacotes:
              - Pacote "Elegibilidade": Verificar idade, Verificar renda
              - Pacote "Risco": Calcular score de risco
              - Pacote "Aprovacao": Decisão final de aprovação
      Passo 4: Criar ruleflow no pacote "Fluxos":
              Início → Elegibilidade → Risco → Aprovação → Fim
    
    POR QUE O RULEFLOW É OBRIGATÓRIO:
    - Controla a ordem de execução dos pacotes de regras
    - Permite ramificação condicional (caminhos aprovado/rejeitado)
    - Fornece visualização clara do processo de negócio
    - Necessário para orquestração adequada de regras no Decision Center
    
    ⚠️ CHECKLIST ANTES DE CRIAR A REGRA ⚠️
    
    Antes de chamar criar_regra(), CONFIRME que você:
    □ Chamou consultar_vocabulario() e analisou o resultado
    □ Chamou listar_variables() e verificou as verbalizações
    □ Identificou as verbalizações EXATAS que vai usar
    □ Verificou que TODOS os valores literais existem no vocabulário
    □ Usou a sintaxe correta para propriedades: "a [prop] de '[var]'"
    □ Colocou verbalizações entre aspas simples: 'Variável'
    □ Usou aspas duplas para valores string: "valor"
    □ NÃO inventou nenhuma verbalização ou valor
    
    EXEMPLOS PRÁTICOS DE REGRAS CORRETAS:
    
    Exemplo 1 - Regra com condição e ação (COM CRASE em variável primitiva):
      se a data da operação de 'a operação atual' é "2025-01-01"
      então
        atribuir à 'Mensagem' a "data da operação é inferior a 2025";
        atribuir à 'Aprovar Crédito' o valor falso;
    
    Exemplo 2 - Regra de ação direta (SEM CRASE em propriedade de objeto):
      então atribuir a mensagem de 'o resultado' a "crédito aprovado";
    
    Exemplo 3 - Regra com múltiplas condições:
      se a idade de 'o cliente' é pelo menos 18
      e a renda de 'o cliente' é maior que 5000
      então atribuir à 'Aprovar Crédito' o valor verdadeiro;
    
    Exemplo 4 - Regra com comparação de data (NÃO use "ano", use a propriedade completa):
      se a data da operação de 'a operação atual' é "2025-01-01"
      então atribuir o crédito aprovado de 'o resultado' a falso;

    ⚠️ ERROS COMUNS A EVITAR ⚠️
    
    ❌ Usar nome técnico: se idadeCliente é maior que 18
    ✅ Usar verbalização: se a idade de 'o cliente' é maior que 18
    
    ❌ Inventar valores: atribuir a 'Status' a "PENDENTE"
    ✅ Consultar vocabulário primeiro e usar valores existentes
    
    ❌ Sintaxe incorreta: se cliente.idade > 18
    ✅ Sintaxe BAL correta: se a idade de 'o cliente' é maior que 18
    
    ❌ Esquecer aspas simples: se a idade de o cliente é maior que 18
    ✅ Usar aspas simples: se a idade de 'o cliente' é maior que 18
    
    ❌ Usar "ano" que não existe: se o ano de a data da operação de 'a operação atual' é 2025
    ✅ Usar a propriedade de data: se a data da operação de 'a operação atual' é "2025-01-01"
    
    ❌ Esquecer crase em variável primitiva: atribuir a mensagem de 'o resultado' a "texto"
    ✅ Usar crase corretamente: atribuir à 'Mensagem' a "texto"
    
    ❌ Usar crase em propriedade de objeto: atribuir à mensagem de 'o resultado' a "texto"
    ✅ Sem crase em propriedade: atribuir a mensagem de 'o resultado' a "texto"

    ⚠️ RESUMO DO FLUXO CORRETO ⚠️
    
    1. Consultar vocabulário → Obter verbalizações exatas
    2. Listar variáveis → Confirmar variáveis existentes
    3. Montar corpo da regra → Usar APENAS verbalizações encontradas
    4. Criar regra → Chamar esta função
    
    NUNCA pule os passos 1 e 2. NUNCA invente verbalizações ou valores.
    SEMPRE copie exatamente as verbalizações do vocabulário.
    
    Se você não seguir este processo, a regra será criada com valores incorretos
    que não existem no vocabulário, causando erros de execução.
    
    Retorno:
      - Resposta JSON do backend sobre a criação.
    """
    params = {
        "action": "create",
        "projectName": projectName,
        "packageName": packageName,
        "ruleName": ruleName,
        "body": body
    }
    return java.post("rules", params=params)


@mcp.tool()
def editar_regra(
    projectName: str,
    packageName: str,
    ruleName: str,
    newBody: str = None,
    priority: str = None,
    newName: str = None
):
    """
    Edita uma Action Rule existente (PUT /rules?action=edit).
    
    Parâmetros:
      - projectName, packageName, ruleName: identificam a regra alvo.
      - newBody: novo corpo BAL (opcional; se fornecido, substitui o existente).
      - priority: prioridade numérica (opcional).
      - newName: novo nome da regra (opcional).

    Comportamento:
      - Apenas os campos fornecidos são alterados.
      - Backend realiza lock/unlock e persiste as mudanças.

    Retorno:
      - Resposta JSON do backend indicando sucesso/erro.
    """
    params = {
        "action": "edit",
        "projectName": projectName,
        "packageName": packageName,
        "ruleName": ruleName
    }
    if newBody:
        params["newBody"] = newBody
    if priority:
        params["priority"] = priority
    if newName:
        params["newName"] = newName

    return java.put("rules", params=params)  


@mcp.tool()
def visualizar_regra(projectName: str, packageName: str, ruleName: str):
    """
    Retorna detalhes/preview de uma Action Rule (GET /rules?action=view).
    
    Parâmetros:
      - projectName, packageName, ruleName: identificam a regra.

    Retorno:
      - JSON com informações da regra (corpo BAL, prioridade, etc.).
    """
    params = {
        "action": "view",
        "projectName": projectName,
        "packageName": packageName,
        "ruleName": ruleName
    }
    return java.get("rules", params=params)

# Made with Bob
