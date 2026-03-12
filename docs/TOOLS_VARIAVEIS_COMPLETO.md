# Tools MCP para Variáveis - Guia Completo

Este documento lista todas as tools MCP disponíveis para trabalhar com variáveis no Decision Center.

## 📋 Índice de Tools

### Em `tools/tools_variables.py`:
1. **listar_variables** - Lista todas as variáveis do projeto
2. **visualizar_variable** - Detalha uma variável específica
3. **criar_variable** - Cria UMA variável
4. **atualizar_variable** - Atualiza uma variável existente
5. **deletar_variable** - Remove uma variável
6. **criar_variaveis_do_bom** - Cria variáveis automaticamente baseadas no BOM

### Em `tools/tools_decisioncenter.py`:
7. **criar_variaveis_no_variable_set** - Cria variáveis dentro de um Variable Set (IBM ODM 9.5)

---

## 1️⃣ listar_variables

**Arquivo:** `tools/tools_variables.py`

**Descrição:** Lista todas as variáveis do projeto.

**Parâmetros:**
- `projectName` (obrigatório): Nome do projeto
- `baselineName` (opcional): Nome da baseline (padrão: "Main")

**Uso:**
```python
listar_variables(
    projectName="MeuProjeto",
    baselineName="Main"
)
```

**Retorno:**
```json
{
  "projectName": "MeuProjeto",
  "baselineName": "Main",
  "variableSets": [
    {
      "name": "variables",
      "packageName": "regras",
      "variables": [
        {
          "name": "cliente",
          "bomType": "com.example.Cliente",
          "verbalization": "o cliente"
        }
      ]
    }
  ]
}
```

**Ideal para:**
- Verificar existência de variáveis
- Evitar duplicações
- Validar baseline

---

## 2️⃣ visualizar_variable

**Arquivo:** `tools/tools_variables.py`

**Descrição:** Detalha uma variável específica.

**Parâmetros:**
- `projectName` (obrigatório): Nome do projeto
- `variableName` (obrigatório): Nome da variável
- `baselineName` (opcional): Nome da baseline (padrão: "Main")

**Uso:**
```python
visualizar_variable(
    projectName="MeuProjeto",
    variableName="cliente",
    baselineName="Main"
)
```

**Retorno:**
```json
{
  "name": "cliente",
  "bomType": "com.example.model.Cliente",
  "verbalization": "o cliente",
  "initialValue": null,
  "variableSetName": "variables",
  "packageName": "regras"
}
```

**Inclui:**
- Nome
- Tipo BOM
- Valor inicial
- Verbalização
- Metadados

---

## 3️⃣ criar_variable

**Arquivo:** `tools/tools_variables.py`

**Descrição:** Cria UMA variável de negócio no Decision Center.

**Parâmetros:**
- `projectName` (obrigatório): Nome do projeto
- `variableName` (obrigatório): Nome da variável
- `bomType` (obrigatório): Tipo BOM completo (ex: "com.example.Cliente" ou "int")
- `packageName` (opcional): Nome do pacote (padrão: "")
- `variableSetName` (opcional): Nome do Variable Set (padrão: "variables")
- `verbalization` (opcional): Frase de verbalização
- `initialValue` (opcional): Valor inicial em formato IRL
- `baselineName` (opcional): Nome da baseline (padrão: "Main")

**Uso:**
```python
criar_variable(
    projectName="MeuProjeto",
    variableName="cliente",
    bomType="com.example.model.Cliente",
    packageName="regras.credito",
    variableSetName="variables",
    verbalization="o cliente",
    initialValue=None,
    baselineName="Main"
)
```

**Características:**
- Cria apenas UMA variável por chamada
- Simples e direto
- Ideal para casos pontuais

---

## 4️⃣ atualizar_variable

**Arquivo:** `tools/tools_variables.py`

**Descrição:** Atualiza parcialmente uma variável existente.

**Parâmetros:**
- `projectName` (obrigatório): Nome do projeto
- `variableName` (obrigatório): Nome da variável
- `value` (opcional): Novo valor
- `varType` (opcional): Novo tipo
- `description` (opcional): Nova descrição
- `baselineName` (opcional): Nome da baseline (padrão: "Main")

**Uso:**
```python
atualizar_variable(
    projectName="MeuProjeto",
    variableName="cliente",
    value=None,
    varType="com.example.model.ClienteV2",
    description="Cliente atualizado",
    baselineName="Main"
)
```

**Características:**
- Atualização parcial (apenas campos informados)
- Não remove campos não especificados

---

## 5️⃣ deletar_variable

**Arquivo:** `tools/tools_variables.py`

**Descrição:** Remove uma variável do projeto.

**Parâmetros:**
- `projectName` (obrigatório): Nome do projeto
- `variableName` (obrigatório): Nome da variável
- `baselineName` (opcional): Nome da baseline (padrão: "Main")

**Uso:**
```python
deletar_variable(
    projectName="MeuProjeto",
    variableName="cliente",
    baselineName="Main"
)
```

**⚠️ ATENÇÃO:**
- Se regras dependem desta variável, podem ocorrer falhas no DC
- Use com cuidado!

---

## 6️⃣ criar_variaveis_do_bom

**Arquivo:** `tools/tools_variables.py`

**Descrição:** Cria variáveis automaticamente baseadas nas classes do BOM do projeto.

**Parâmetros:**
- `projectName` (obrigatório): Nome do projeto
- `baselineName` (opcional): Nome da baseline (padrão: "Main")
- `prefixo` (opcional): Prefixo para os nomes das variáveis

**Uso:**
```python
criar_variaveis_do_bom(
    projectName="MeuProjeto",
    baselineName="Main",
    prefixo=""
)
```

**Como funciona:**
1. Lista as classes do BOM do projeto
2. Para cada classe, cria uma variável com o tipo da classe
3. Usa nomes em camelCase (ex: "Cliente" → "cliente")

**Exemplo de resultado:**
```json
{
  "status": "success",
  "variaveis_criadas": [
    {"nome": "cliente", "tipo": "com.example.model.Cliente", "status": "criada"},
    {"nome": "emprestimo", "tipo": "com.example.model.Emprestimo", "status": "criada"}
  ],
  "total_criadas": 2,
  "total_existentes": 0,
  "erros": []
}
```

**Características:**
- Automático - não precisa especificar cada variável
- Pula variáveis que já existem
- Usa nome completo da classe como tipo

---

## 7️⃣ criar_variaveis_no_variable_set ⭐ NOVO!

**Arquivo:** `tools/tools_decisioncenter.py`

**Descrição:** Cria MÚLTIPLAS variáveis em lote usando o backend Java (ODMHttpServer).

**Parâmetros:**
- `projectName` (obrigatório): Nome do projeto
- `variableSetName` (obrigatório): Nome do Variable Set
- `variables` (obrigatório): Lista de dicionários com as variáveis
- `packageName` (opcional): Nome do pacote (padrão: "")
- `baselineName` (opcional): Nome da baseline (padrão: "Main")
- `resetIfExists` (opcional): Limpa variáveis existentes antes (padrão: false)

**Estrutura de cada variável:**
```python
{
    "name": "nomeVariavel",           # obrigatório
    "bomType": "tipo.completo.BOM",   # obrigatório
    "verbalization": "frase",         # opcional
    "initialValue": "valor IRL"       # opcional
}
```

**Uso:**
```python
criar_variaveis_no_variable_set(
    projectName="MeuProjeto",
    variableSetName="variables",
    packageName="regras.credito",
    variables=[
        {
            "name": "cliente",
            "bomType": "com.example.model.Cliente",
            "verbalization": "o cliente"
        },
        {
            "name": "emprestimo",
            "bomType": "com.example.model.Emprestimo",
            "verbalization": "o empréstimo"
        },
        {
            "name": "idade",
            "bomType": "int",
            "initialValue": "0"
        }
    ],
    resetIfExists=False
)
```

**Características:**
- ✅ Cria MÚLTIPLAS variáveis em uma única chamada
- ✅ Melhor performance para criação em massa
- ✅ Suporta tipos BOM complexos
- ✅ Opção de reset (limpar antes de criar)
- ✅ Upsert automático (cria ou atualiza)

**Retorno:**
```json
{
  "status": "success",
  "message": "Variáveis criadas/atualizadas no Variable Set 'variables'",
  "result": {
    "projectName": "MeuProjeto",
    "baselineName": "Main",
    "variableSetName": "variables",
    "variables": [...]
  },
  "totalVariables": 3
}
```

---

## 🔄 Comparação entre Tools

| Característica | criar_variable | criar_variaveis_no_variable_set | criar_variaveis_do_bom |
|----------------|----------------|--------------------------|------------------------|
| **Quantidade** | 1 variável | Múltiplas variáveis | Automático (todas do BOM) |
| **Performance** | Lenta (1 por vez) | Rápida (lote) | Média |
| **Controle** | Total | Total | Limitado |
| **Tipos BOM** | ✅ Sim | ✅ Sim | ✅ Sim |
| **Reset** | ❌ Não | ✅ Sim | ❌ Não |
| **Upsert** | ❌ Não | ✅ Sim | ❌ Não |
| **Backend** | Java HTTP | Java HTTP | Java HTTP + Vocab |

---

## 🎯 Quando usar cada tool?

### Use `listar_variables`:
- Verificar quais variáveis existem
- Antes de criar para evitar duplicação
- Auditoria de variáveis

### Use `visualizar_variable`:
- Ver detalhes de uma variável específica
- Verificar tipo e valor atual
- Debug

### Use `criar_variable`:
- Criar apenas 1 variável
- Casos simples e pontuais
- Quando não precisa de performance

### Use `atualizar_variable`:
- Modificar variável existente
- Alterar tipo ou valor
- Atualização parcial

### Use `deletar_variable`:
- Remover variável não utilizada
- Limpeza de projeto
- ⚠️ Cuidado com dependências!

### Use `criar_variaveis_do_bom`:
- Criar variáveis automaticamente
- Projeto novo com BOM definido
- Quer variável para cada classe do BOM

### Use `criar_variaveis_no_variable_set`: ⭐ RECOMENDADO
- Criar MÚLTIPLAS variáveis de uma vez
- Melhor performance
- Precisa de reset/upsert
- Criação em massa
- Tipos BOM complexos

---

## 📝 Exemplos Práticos

### Cenário 1: Criar projeto do zero

```python
# 1. Criar variáveis automaticamente do BOM
criar_variaveis_do_bom(
    projectName="NovoProjetoCredito"
)

# 2. Adicionar variáveis customizadas
criar_variaveis_no_variable_set(
    projectName="NovoProjetoCredito",
    variableSetName="variables",
    variables=[
        {"name": "resultado", "bomType": "java.lang.String"},
        {"name": "aprovado", "bomType": "boolean", "initialValue": "false"}
    ]
)
```

### Cenário 2: Atualizar variáveis existentes

```python
# 1. Listar para ver o que existe
variaveis = listar_variables(projectName="MeuProjeto")

# 2. Atualizar uma específica
atualizar_variable(
    projectName="MeuProjeto",
    variableName="cliente",
    varType="com.example.model.ClienteV2"
)
```

### Cenário 3: Reset completo de variáveis

```python
# Remove todas e cria novas
criar_variaveis_no_variable_set(
    projectName="MeuProjeto",
    variableSetName="variables",
    resetIfExists=True,  # ⚠️ Remove todas as existentes!
    variables=[
        {"name": "novaVar1", "bomType": "int"},
        {"name": "novaVar2", "bomType": "java.lang.String"}
    ]
)
```

---

## ⚙️ Configuração

Todas as tools de variáveis usam o backend Java. Configure:

```bash
# Variável de ambiente (opcional)
export OTHER_BASE_URL="http://localhost:8080"

# Padrão se não configurado
# http://localhost:8080
```

---

## 🔗 Arquivos Relacionados

- [`tools/tools_variables.py`](tools/tools_variables.py) - Tools 1-6
- [`tools/tools_decisioncenter.py`](tools/tools_decisioncenter.py) - Tool 7
- [`helpers/http_java_client.py`](helpers/http_java_client.py) - Cliente HTTP
- [`exemplo_criar_variaveis.md`](exemplo_criar_variaveis.md) - Exemplos detalhados