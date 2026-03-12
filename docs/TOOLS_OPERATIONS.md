# Tools de Decision Operations

Este documento descreve as tools disponíveis para gerenciar **Decision Operations** no IBM ODM via MCP Server.

## Visão Geral

Decision Operations definem o **contrato de execução** de um ruleset no ODM. Elas especificam:

- **Parâmetros de entrada/saída** (parameters): definem o contrato da operation
- **Ruleflow associado**: fluxo de regras a ser executado (OBRIGATÓRIO)
- **Variable Set**: conjunto de variáveis usado para descriptors, params e ruleset params (OBRIGATÓRIO)
- **Configurações de runtime**: nome do ruleset, parâmetros extras, etc.

## ⚠️ REQUISITOS OBRIGATÓRIOS

Toda Decision Operation DEVE ter:

1. **Ruleflow associado** (`ruleflowName`) - Define o fluxo de execução
2. **Variable Set** (`variableSetName`) - Usado automaticamente para descriptors, params e rulesetParams
3. **Parâmetros** (`parameters`) - Pelo menos um parâmetro IN, OUT ou INOUT
4. **Operations NÃO têm pacote específico** - São criadas no nível do projeto

## Estrutura de Referência

Baseado em `test_operation_ruleflow.json`:

```json
{
  "projectName": "DS-FinanciamentoImobiliario",
  "baselineName": "Main",
  "operationName": "CalcularFinanciamento",
  "variableSetName": "variaveis",
  "description": "Operação para calcular financiamento imobiliário",
  "ruleflow": {
    "ruleflowName": "Fluxo de Calculo de Financiamento"
  },
  "rulesetName": "FinanciamentoRuleset",
  "parameters": [
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
  "registry": {
    "descriptorSets": ["variaveis"],
    "paramsSets": ["variaveis"],
    "rulesetParamSets": ["variaveis"]
  }
}
```

## Tools Disponíveis

### 1. `criar_operation`

Cria uma nova Decision Operation no projeto.

**Parâmetros OBRIGATÓRIOS:**
- `projectName` (str): Nome do projeto/Decision Service
- `operationName` (str): Nome da operation a criar
- `ruleflowName` (str): Nome do ruleflow a associar
- `variableSetName` (str): Nome do Variable Set (usado para registry)
- `parameters` (list): Lista de parâmetros do contrato

**Parâmetros OPCIONAIS:**
- `baselineName` (str): Branch/baseline (padrão: "Main")
- `rulesetName` (str): Nome do ruleset para runtime (recomendado)
- `description` (str): Descrição da operation
- `rulesetParameters` (dict): Parâmetros extras para o ruleset

**Estrutura de parameters:**
Cada parâmetro é um dict com:
- `name` (str): Nome do parâmetro
- `direction` (str): **"IN", "OUT" ou "INOUT"** (maiúsculas)
- `bomType` (str): Tipo BOM (nome da classe do vocabulário)

**Exemplo correto:**
```python
criar_operation(
    projectName="DS-FinanciamentoImobiliario",
    operationName="CalcularFinanciamento",
    ruleflowName="Fluxo de Calculo de Financiamento",
    variableSetName="variaveis",
    parameters=[
        {"name": "credito", "direction": "IN", "bomType": "credito"},
        {"name": "elegivel", "direction": "OUT", "bomType": "booleano"},
        {"name": "financiamento", "direction": "INOUT", "bomType": "financiamento"}
    ],
    rulesetName="FinanciamentoRuleset",
    description="Operação para calcular financiamento imobiliário"
)
```

**O que acontece automaticamente:**
- O `variableSetName` é usado para criar o registry com:
  - `descriptorSets`: [variableSetName]
  - `paramsSets`: [variableSetName]
  - `rulesetParamSets`: [variableSetName]

---

### 2. `visualizar_operation`

Visualiza detalhes de uma Decision Operation existente.

**Parâmetros obrigatórios:**
- `projectName` (str): Nome do projeto
- `operationName` (str): Nome da operation

**Parâmetros opcionais:**
- `baselineName` (str): Branch/baseline (padrão: "Main")
- `descriptorSets` (list): Variable Sets adicionais para incluir
- `paramsSets` (list): Variable Sets adicionais para incluir
- `rulesetParamSets` (list): Variable Sets adicionais para incluir

**Exemplo:**
```python
visualizar_operation(
    projectName="DS-FinanciamentoImobiliario",
    operationName="CalcularFinanciamento"
)
```

**Retorno típico:**
```json
{
  "operationName": "CalcularFinanciamento",
  "dsmRuleflowLinked": "Fluxo de Calculo de Financiamento",
  "parameters": [
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
  "registry": {
    "descriptorSets": ["variaveis"],
    "paramsSets": ["variaveis"],
    "rulesetParamSets": ["variaveis"]
  },
  "description": "Operação para calcular financiamento imobiliário",
  "runtimeRulesetName": "FinanciamentoRuleset"
}
```

---

### 3. `atualizar_operation`

Atualiza uma Decision Operation existente.

**Parâmetros obrigatórios:**
- `projectName` (str): Nome do projeto
- `operationName` (str): Nome da operation a atualizar
- `ruleflowName` (str): Nome do ruleflow
- `variableSetName` (str): Nome do Variable Set
- `parameters` (list): Lista de parâmetros

**Parâmetros opcionais:**
(mesmos de `criar_operation`)

**Exemplo:**
```python
atualizar_operation(
    projectName="DS-FinanciamentoImobiliario",
    operationName="CalcularFinanciamento",
    ruleflowName="Fluxo de Calculo de Financiamento V2",
    variableSetName="variaveis",
    parameters=[
        {"name": "credito", "direction": "IN", "bomType": "credito"},
        {"name": "elegivel", "direction": "OUT", "bomType": "booleano"},
        {"name": "financiamento", "direction": "INOUT", "bomType": "financiamento"},
        {"name": "taxaJuros", "direction": "OUT", "bomType": "numero"}  # Novo
    ],
    rulesetName="FinanciamentoRuleset_V2",
    description="Operação atualizada com cálculo de taxa de juros"
)
```

---

## Fluxo de Trabalho Completo

### Passo 1: Preparar o projeto

```python
# 1. Criar projeto (se não existir)
criar_projeto(
    projectName="DS-FinanciamentoImobiliario",
    decisionServiceName="DS-FinanciamentoImobiliario"
)

# 2. Criar vocabulário (classes BOM)
criar_vocabulario(
    decisionServiceName="DS-FinanciamentoImobiliario",
    packageName="modelo",
    className="credito",
    properties=[
        {"name": "valor", "type": "double"},
        {"name": "prazo", "type": "int"}
    ]
)

criar_vocabulario(
    decisionServiceName="DS-FinanciamentoImobiliario",
    packageName="modelo",
    className="financiamento",
    properties=[
        {"name": "valorTotal", "type": "double"},
        {"name": "parcelas", "type": "int"}
    ]
)
```

### Passo 2: Criar Variable Set

```python
# Criar Variable Set que será usado pela operation
criar_variable(
    projectName="DS-FinanciamentoImobiliario",
    variableName="credito",
    varType="modelo.credito",
    verbalization="o crédito"
)

criar_variable(
    projectName="DS-FinanciamentoImobiliario",
    variableName="financiamento",
    varType="modelo.financiamento",
    verbalization="o financiamento"
)

criar_variable(
    projectName="DS-FinanciamentoImobiliario",
    variableName="elegivel",
    varType="boolean",
    verbalization="elegível"
)
```

### Passo 3: Criar Ruleflow

```python
criar_ruleflow(
    projectName="DS-FinanciamentoImobiliario",
    packageName="fluxos",
    ruleflowName="Fluxo de Calculo de Financiamento",
    tasks=[
        {"name": "ValidarCredito", "type": "rule"},
        {"name": "CalcularParcelas", "type": "rule"},
        {"name": "DefinirElegibilidade", "type": "rule"}
    ]
)
```

### Passo 4: Criar Decision Operation

```python
criar_operation(
    projectName="DS-FinanciamentoImobiliario",
    operationName="CalcularFinanciamento",
    ruleflowName="Fluxo de Calculo de Financiamento",
    variableSetName="variaveis",
    parameters=[
        {"name": "credito", "direction": "IN", "bomType": "credito"},
        {"name": "elegivel", "direction": "OUT", "bomType": "booleano"},
        {"name": "financiamento", "direction": "INOUT", "bomType": "financiamento"}
    ],
    rulesetName="FinanciamentoRuleset",
    description="Operação para calcular financiamento imobiliário"
)
```

### Passo 5: Verificar

```python
resultado = visualizar_operation(
    projectName="DS-FinanciamentoImobiliario",
    operationName="CalcularFinanciamento"
)
print(resultado)
```

---

## Direções de Parâmetros

- **IN**: Parâmetro de entrada (somente leitura)
- **OUT**: Parâmetro de saída (somente escrita)
- **INOUT**: Parâmetro de entrada/saída (leitura e escrita)

**Importante:** Use maiúsculas (IN, OUT, INOUT) conforme o padrão do ODM.

---

## Tipos BOM Comuns

Ao definir parâmetros, use tipos BOM válidos do seu vocabulário:

**Tipos primitivos:**
- `booleano` (boolean)
- `numero` (int/double)
- `texto` (String)
- `data` (Date)

**Tipos customizados:**
- Use o nome da classe BOM: `credito`, `financiamento`, `cliente`
- Ou com pacote: `modelo.credito`, `modelo.financiamento`

---

## Troubleshooting

### ❌ Erro: "Ruleflow é obrigatório"
**Solução:** Sempre forneça `ruleflowName`. Crie o ruleflow antes se necessário.

### ❌ Erro: "Variable Set é obrigatório"
**Solução:** Sempre forneça `variableSetName`. Crie as variáveis antes se necessário.

### ❌ Erro: "Parâmetros são obrigatórios"
**Solução:** Forneça pelo menos um parâmetro na lista `parameters`.

### ❌ Erro: "Ruleflow não encontrado"
**Solução:** 
- Verifique se o ruleflow existe: `listar_ruleflows(projectName)`
- Confirme o nome exato (case-sensitive)
- Crie o ruleflow se necessário

### ❌ Erro: "Variable Set não encontrado"
**Solução:**
- Verifique se as variáveis existem: `listar_variables(projectName)`
- Crie as variáveis necessárias antes de criar a operation

### ❌ Erro: "Tipo BOM inválido"
**Solução:**
- Verifique se a classe existe: `consultar_vocabulario(projectName)`
- Use o nome exato da classe BOM
- Para tipos primitivos, use: `booleano`, `numero`, `texto`, `data`

---

## Integração com Backend Java

As tools comunicam-se com o endpoint `/operations` do `ODMHttpServer.java`:

- **POST /operations?action=create** → `criar_operation`
- **PUT /operations?action=update** → `atualizar_operation`
- **GET /operations?action=view** → `visualizar_operation`

O backend Java (`ODMOperationService.java`) gerencia:
- Criação/atualização via DSM API
- Associação com Ruleflows
- Registro automático do Variable Set em descriptors, params e rulesetParams
- Persistência de configurações

---

## Exemplos Práticos

Veja o arquivo `examples/criar_operation.py` para exemplos completos baseados em `test_operation_ruleflow.json`.

Para executar:
```bash
cd /Users/rafaelmarques/Documents/MEUMCP
python examples/criar_operation.py
```

---

## Referências

- [test_operation_ruleflow.json](../eclipse/ODM_TOOLS/test_operation_ruleflow.json) - Estrutura de referência
- [API_REFERENCE.md](API_REFERENCE.md) - Referência completa da API
- [TOOLS_VARIAVEIS_COMPLETO.md](TOOLS_VARIAVEIS_COMPLETO.md) - Tools de variáveis
- [OPERATION_SERVICE_COMPLETE.md](OPERATION_SERVICE_COMPLETE.md) - Detalhes do serviço Java