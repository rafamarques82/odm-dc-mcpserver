# -*- coding: utf-8 -*-
'''
Tools de Ruleflow:

- visualizar_ruleflow (visualizar ruleflow)
- criar_ruleflow (criar ruleflow)
- atualizar_ruleflow (atualizar ruleflow)
'''

from mcp.server.fastmcp import FastMCP
from helpers.http_java_client import JavaBackendClient
import os

java = JavaBackendClient(
    base_url=os.getenv("OTHER_BASE_URL", "http://localhost:8080")
)

import builtins
mcp: FastMCP = builtins.__dict__.get("mcp")


@mcp.tool()
def visualizar_ruleflow(projectName: str, packageName: str, ruleflowName: str, baselineName: str = "Main"):
    '''
    Recupera detalhes completos de um ruleflow (GET /ruleflows).

    Retorno típico:
      - baseline resolvida,
      - flags (ex.: mainFlowTask),
      - metadados,
      - preview do XML persistido (bodyPreview).

    Notas de uso:
      - Backend aceita 'action=view' via querystring, mas também infere da rota/método.
      - Use este método após criar/atualizar para inspecionar rapidamente o artefato.
    '''
    return java.get(
        "ruleflows",
        params={
            "action": "view",
            "projectName": projectName,
            "packageName": packageName,
            "ruleflowName": ruleflowName,
            "baselineName": baselineName
        }
    )


@mcp.tool()
def criar_ruleflow(projectName: str, packageName: str, ruleflowName: str,
                   bodyDRF: str, baselineName: str = "Main", mainFlowTask: bool = True):
    r'''
    Cria um ruleflow com definição XML no Decision Center.
    
    ⚠️ REGRAS CRÍTICAS DE ESTRUTURA DE RULEFLOW ⚠️
    
    ERRO COMUM - NÓS DESCONECTADOS:
    A imagem mostra um nó desconectado (losango cinza no topo). Isso acontece quando:
    1. Um nó é definido no NodeList mas NÃO tem transições de entrada ou saída
    2. Uma task é definida no TaskList mas NÃO é referenciada por nenhum nó
    3. IDs de nós não correspondem entre NodeList e TransitionList
    
    REQUISITOS DE ESTRUTURA CORRETA:
    
    1. TODA Task no TaskList DEVE ter um TaskNode correspondente no NodeList
    2. TODO Nó no NodeList DEVE ter pelo menos UMA transição (entrada ou saída)
    3. Nó Start DEVE ter transição(ões) de saída
    4. Nó Stop DEVE ter transição(ões) de entrada
    5. Nós Branch DEVEM ter UMA entrada e MÚLTIPLAS saídas
    6. Todos os Identifiers de nós devem ser únicos e corretamente referenciados
    
    CHECKLIST DE VALIDAÇÃO DE ESTRUTURA:
    ✓ TaskList: Definir todas as tasks (StartTask, StopTask, RuleTask, BranchNode NÃO é uma task)
    ✓ NodeList: Criar nós para TODAS as tasks (TaskNode para tasks, BranchNode para branches)
    ✓ TransitionList: Conectar TODOS os nós com transições
    ✓ Todo ID de nó nas transições deve existir no NodeList
    ✓ Todo ID de Task no TaskNode deve existir no TaskList
    ✓ Sem nós órfãos (nós sem transições)
    
    ⚠️ CRÍTICO: PRINCÍPIOS DE DESIGN DE RULEFLOW ⚠️
    
    IMPORTANTE: Analise os requisitos de negócio PRIMEIRO antes de desenhar o fluxo!
    Diferentes cenários de negócio requerem diferentes padrões de fluxo.
    
    PRINCÍPIOS GERAIS PARA DESIGN DE RULEFLOW:
    
    1. AGRUPE REGRAS RELACIONADAS EM PACOTES
       - Coloque regras com propósito de negócio similar no MESMO pacote
       - Exemplo: Todas as regras de validação → UM pacote "Validacao"
       - Exemplo: Todas as regras de cálculo → UM pacote "Calculo"
       - NÃO crie um pacote por regra
    
    2. USE BRANCHES COM SABEDORIA
       - Use branch quando o fluxo precisa DIVIDIR baseado em uma condição
       - Condição do branch deve verificar uma variável definida por regras anteriores
       - NÃO crie múltiplos branches para cada validação
       - Se múltiplas validações, agrupe-as em UM pacote, depois UM branch
    
    3. MANTENHA O FLUXO SIMPLES
       - Minimize o número de nós branch
       - Fluxo linear quando possível: Start → Pacote1 → Pacote2 → Stop
       - Use branch apenas quando realmente necessário para caminhos condicionais
    
    4. ESTRUTURA DE NÓ BRANCH
       - Branch é um NÓ, não uma TASK
       - Vai no NodeList, NÃO no TaskList
       - Deve ter UMA transição de entrada
       - Deve ter MÚLTIPLAS transições de saída (com condições)
       - Cada transição de saída precisa de uma condição em BAL
    
    PADRÕES COMUNS (use como referência, não regras rígidas):
    
    Padrão A: Sequencial Simples (sem branches)
    Start → Pacote1 → Pacote2 → Pacote3 → Stop
    Use quando: Todos os pacotes devem sempre executar em ordem
    
    Padrão B: Validação com Branch (um branch)
    Start → Validacao → Branch → Processamento → Stop
                          ↓
                        Stop
    Use quando: Precisa parar se a validação falhar
    
    Padrão C: Múltiplos Pontos de Decisão (múltiplos branches)
    Start → Check1 → Branch1 → Check2 → Branch2 → Final → Stop
                      ↓                   ↓
                    Stop                Stop
    Use quando: Múltiplos pontos de decisão independentes são necessários
    (Mas tente evitar se possível - geralmente pode ser simplificado)
    
    ❌ ERROS COMUNS A EVITAR:
    
    1. Um pacote por regra (cria bagunça)
    2. Um branch por validação (excessivamente complexo)
    3. Nós desconectados (nós sem transições)
    4. BranchTask no TaskList (branch é um nó, não uma task)
    5. Condições faltando nas transições de branch
    6. Identifiers de nó/task inconsistentes
    
    ✅ MELHORES PRÁTICAS:
    
    1. Analise a lógica de negócio PRIMEIRO
    2. Agrupe regras relacionadas em pacotes lógicos
    3. Use o número mínimo de branches necessário
    4. Garanta que todos os nós estejam conectados
    5. Use nomes claros e descritivos
    6. Adicione condições a todas as transições de branch
    7. Teste a lógica do fluxo antes da implementação
    
    EXEMPLO DE XML PARA FLUXO CORRETO COM BRANCH:
    <TaskList>
      <StartTask Identifier="start_1"/>
      <RuleTask Identifier="init_task" ExecutionMode="Sequential">
        <RuleList><Package Name="Inicializar"/></RuleList>
      </RuleTask>
      <RuleTask Identifier="validate_task" ExecutionMode="Sequential">
        <RuleList><Package Name="Validar"/></RuleList>
      </RuleTask>
      <RuleTask Identifier="approval_task" ExecutionMode="Sequential">
        <RuleList><Package Name="Logica de Aprovacao"/></RuleList>
      </RuleTask>
      <StopTask Identifier="stop_1"/>
    </TaskList>
    
    <NodeList>
      <TaskNode Identifier="node_start" Task="start_1"/>
      <TaskNode Identifier="node_init" Task="init_task"/>
      <TaskNode Identifier="node_validate" Task="validate_task"/>
      <BranchNode Identifier="node_branch"/>  <!-- Branch após validação -->
      <TaskNode Identifier="node_approval" Task="approval_task"/>
      <TaskNode Identifier="node_stop" Task="stop_1"/>
    </NodeList>
    
    <TransitionList>
      <Transition Source="node_start" Target="node_init"/>
      <Transition Source="node_init" Target="node_validate"/>
      <Transition Source="node_validate" Target="node_branch"/>
      <Transition Source="node_branch" Target="node_approval">
        <Conditions Language="bal"><![CDATA[creditoAprovado é verdadeiro]]></Conditions>
      </Transition>
      <Transition Source="node_branch" Target="node_stop">
        <Conditions Language="bal"><![CDATA[creditoAprovado é falso]]></Conditions>
      </Transition>
      <Transition Source="node_approval" Target="node_stop"/>
    </TransitionList>
    
    PRINCÍPIOS CHAVE:
    - Use UM branch após o pacote de validação
    - Branch verifica variável de decisão definida pelas regras de validação
    - Caminho aprovado continua para lógica de aprovação
    - Caminho rejeitado vai diretamente para stop
    - Mantenha simples: UM branch, não múltiplos
    
    EXEMPLO DE FLUXO SIMPLES CORRETO (SEM BRANCHES):
    Start → Pacote Validacao → Pacote Verificacao → Stop
    
    EXEMPLO DE FLUXO CONDICIONAL CORRETO (UM BRANCH):
    Start → Validacao → Branch → Aprovacao → Stop
                          ↓
                        Stop (caminho rejeitado)
    
    ESTRUTURA XML PARA FLUXO SIMPLES (SEM BRANCHES):
    <TaskList>
      <StartTask Identifier="start_1"/>
      <RuleTask Identifier="validation_task">
        <RuleList><Package Name="Validacao"/></RuleList>
      </RuleTask>
      <RuleTask Identifier="verification_task">
        <RuleList><Package Name="Verificacao"/></RuleList>
      </RuleTask>
      <StopTask Identifier="stop_1"/>
    </TaskList>
    
    <NodeList>
      <TaskNode Identifier="node_start" Task="start_1"/>
      <TaskNode Identifier="node_validation" Task="validation_task"/>
      <TaskNode Identifier="node_verification" Task="verification_task"/>
      <TaskNode Identifier="node_stop" Task="stop_1"/>
    </NodeList>
    
    <TransitionList>
      <Transition Source="node_start" Target="node_validation"/>
      <Transition Source="node_validation" Target="node_verification"/>
      <Transition Source="node_verification" Target="node_stop"/>
    </TransitionList>
    
    ESTRUTURA XML PARA FLUXO CONDICIONAL (UM BRANCH):
    <TaskList>
      <StartTask Identifier="start_1"/>
      <RuleTask Identifier="rule_1">...</RuleTask>
      <!-- BranchNode NÃO está aqui, está apenas no NodeList -->
      <RuleTask Identifier="rule_2">...</RuleTask>
      <StopTask Identifier="stop_1"/>
    </TaskList>
    
    <NodeList>
      <TaskNode Identifier="node_start" Task="start_1"/>
      <TaskNode Identifier="node_rule1" Task="rule_1"/>
      <BranchNode Identifier="node_branch"/>  <!-- Branch é um nó, não uma task -->
      <TaskNode Identifier="node_rule2" Task="rule_2"/>
      <TaskNode Identifier="node_stop" Task="stop_1"/>
    </NodeList>
    
    <TransitionList>
      <Transition Source="node_start" Target="node_rule1"/>
      <Transition Source="node_rule1" Target="node_branch"/>
      <Transition Source="node_branch" Target="node_rule2">
        <Conditions>...</Conditions>  <!-- Caminho aprovado -->
      </Transition>
      <Transition Source="node_branch" Target="node_stop">
        <Conditions>...</Conditions>  <!-- Caminho rejeitado -->
      </Transition>
      <Transition Source="node_rule2" Target="node_stop"/>
    </TransitionList>
    
    NOTAS IMPORTANTES:
    - SEMPRE VERIFIQUE O PROJETO DE EXEMPLO (GET_EXEMPLO) ANTES DE CRIAR/ATUALIZAR RULEFLOWS
    - O fluxo não deve estar no mesmo pacote que os pacotes de regras referenciados
    - Branch é um NÓ, não uma TASK - nunca coloque BranchTask no TaskList
    - Todos os nós devem estar conectados - sem nós flutuantes/desconectados
    - Verifique se todas as referências de Identifier correspondem exatamente
    
    Exemplo de chamada via curl:
curl -X POST \
  "http://localhost:8080/ruleflows?projectName=Risco&packageName=Fluxos&ruleflowName=Fluxo%20Principal%20de%20Cr%C3%A9dito&baselineName=Main&mainFlowTask=true" \
  -H "Content-Type: application/xml" \
  --data-binary @- <<'XML'
<?xml version="1.0" encoding="UTF-8"?>
<Ruleflow xmlns="http://schemas.ilog.com/Rules/7.0/Ruleflow">
  <Body>
    <TaskList>
      <StartTask Identifier="task_1"/>
      <RuleTask ExecutionMode="Sequential" ExitCriteria="None" Identifier="rule_0" Ordering="Default">
        <RuleList>
          <Package Name="01 - Elegibiliade"/>
        </RuleList>
      </RuleTask>
      <RuleTask ExecutionMode="RetePlus" ExitCriteria="None" Identifier="rule_1" Ordering="Default">
        <RuleList>
          <Package Name="02 - Calculo de risco"/>
        </RuleList>
      </RuleTask>
      <StopTask Identifier="task_2"/>
      <RuleTask ExecutionMode="Fastpath" ExitCriteria="None" Identifier="rule_2" Ordering="Default">
        <RuleList>
          <Package Name="03 - Calculo do financiamento"/>
        </RuleList>
      </RuleTask>
    </TaskList>

    <NodeList>
      <TaskNode Identifier="node_0" Task="task_1"/>
      <TaskNode Identifier="node_2" Task="rule_0"/>
      <BranchNode Identifier="node_3"/>
      <TaskNode Identifier="node_4" Task="rule_1"/>
      <TaskNode Identifier="node_5" Task="task_2"/>
      <TaskNode Identifier="node_1" Task="rule_2"/>
    </NodeList>

    <TransitionList>
      <Transition Identifier="transition_0" Source="node_0" Target="node_2"/>
      <Transition Identifier="transition_1" Source="node_2" Target="node_3"/>
      <Transition Identifier="transition_2" Source="node_3" Target="node_4"/>
      <Transition Identifier="transition_3" Source="node_3" Target="node_5">
        <Conditions Language="bal"><![CDATA[elegível é falso]]></Conditions>
      </Transition>
      <Transition Identifier="transition_4" Source="node_4" Target="node_1"/>
      <Transition Identifier="transition_5" Source="node_1" Target="node_5"/>
    </TransitionList>
  </Body>

  <Resources>
    <ResourceSet Locale="pt_BR">
      <Data Name="node_0#name">node_0</Data>
      <Data Name="node_0#x">-126.26032</Data><Data Name="node_0#y">90.84999</Data>
      <Data Name="node_2#label">Elegibilidade</Data>
      <Data Name="node_2#name">node_2</Data>
      <Data Name="node_2#x">-56.260323</Data><Data Name="node_2#y">85.84999</Data>
      <Data Name="node_3#label">É elegível?</Data>
      <Data Name="node_3#name">node_3</Data>
      <Data Name="node_3#x">113.739685</Data><Data Name="node_3#y">85.84999</Data>
      <Data Name="node_4#label">Avalia Risco</Data>
      <Data Name="node_4#name">node_4</Data>
      <Data Name="node_4#x">213.42749</Data><Data Name="node_4#y">85.84999</Data>
      <Data Name="node_5#name">node_5</Data>
      <Data Name="node_5#x">113.904045</Data><Data Name="node_5#y">170.84999</Data>
      <Data Name="node_1#label">Calcula Financiamento</Data>
      <Data Name="node_1#name">node_1</Data>
      <Data Name="node_1#x">183.90405</Data><Data Name="node_1#y">165.84999</Data>
      <Data Name="transition_3#label">Não elegível</Data>
    </ResourceSet>
  </Resources>

  <Properties><imports/></Properties>
</Ruleflow>
XML

 
    '''
    params = {
        "action": "create",
        "projectName": projectName,
        "packageName": packageName,
        "ruleflowName": ruleflowName,
        "baselineName": baselineName,
        "mainFlowTask": "true" if mainFlowTask else "false"
    }
    headers = {"Content-Type": "application/xml"}
    return java.post("ruleflows", params=params, data=bodyDRF, headers=headers)


@mcp.tool()
def atualizar_ruleflow(projectName: str, packageName: str, ruleflowName: str,
                       bodyDRF: str, baselineName: str = "Main", mainFlowTask: bool = True):
    '''
    Atualiza um ruleflow existente (PUT /ruleflows).

    Formato de submissão:
      - Padrão para esta tool: corpo XML bruto (Content-Type: application/xml) e parâmetros em querystring.
      - Alternativa (fora desta tool): JSON com XML em "bodyDRF" (string), escapando apenas aspas internas.

    Regras cruciais de modelagem XML (mesmas da criação):
      - Branch é nó, não task: use <BranchNode ID="..."/> no NodeList; nunca <BranchTask .../> no TaskList.
      - IDs técnicos: use ID="..." em tasks, nós e transições; TaskNode.Task/Transition.Source/Target devem
        apontar para IDs existentes.
      - Pacotes: ruleflow deve estar em pacote diferente dos pacotes de regras referenciados por RuleTask.
 
    Nota:
      - Esta tool apenas encaminha o que você envia (não altera pacote ou XML).
      - Após atualizar, use visualizar_ruleflow para validar o artefato persistido.
    '''
    params = {
        "action": "update",
        "projectName": projectName,
        "packageName": packageName,
        "ruleflowName": ruleflowName,
        "baselineName": baselineName,
        "mainFlowTask": "true" if mainFlowTask else "false"
    }
    headers = {"Content-Type": "application/xml"}
    return java.put("ruleflows", params=params, data=bodyDRF, headers=headers)

# Made with Bob
