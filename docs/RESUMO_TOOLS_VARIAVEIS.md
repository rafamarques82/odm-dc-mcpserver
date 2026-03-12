# Resumo: Tools de Variáveis no MCP Server

## Estrutura de Arquivos

### 1. `tools/tools_variables.py`
**Propósito**: Tools completas para gerenciamento de variáveis

**Tools Disponíveis**:
- ✅ `criar_variaveis_no_variable_set()` - Cria múltiplas variáveis em lote
- ✅ `listar_variables()` - Lista todas as variáveis do projeto
- ✅ `visualizar_variable()` - Detalha uma variável específica
- ✅ `atualizar_variable()` - Atualiza parcialmente uma variável existente
- ✅ `deletar_variable()` - Remove uma variável do projeto

**Tools Deprecadas** (comentadas):
- ❌ `criar_variable()` - DEPRECADO, use `criar_variaveis_no_variable_set`
- ❌ `criar_variaveis_do_bom()` - DEPRECADO, use `criar_variaveis_no_variable_set`

### 2. `tools/tools_decisioncenter.py`
**Propósito**: Tools gerais do Decision Center (projetos, vocabulários, etc.)

**Nota**: A tool `criar_variaveis_no_variable_set` foi movida para `tools_variables.py`

## Como Usar

### Criar Variáveis (Recomendado)

```python
from tools.tools_variables import criar_variaveis_no_variable_set

# Criar variáveis em lote
criar_variaveis_no_variable_set(
    projectName="MeuProjeto",
    variableSetName="variables",
    variables=[
        {
            "name": "idade",
            "bomType": "int",
            "verbalization": "a idade",
            "initialValue": "0"
        },
        {
            "name": "cliente",
            "bomType": "com.example.model.Cliente",
            "verbalization": "o cliente"
        }
    ]
)
```

**⚠️ IMPORTANTE**: Para Variable Sets novos (nunca commitados):
1. **Primeira execução** pode falhar com erro de commit
2. **Execute NOVAMENTE** com os mesmos parâmetros
3. **Segunda execução** funcionará corretamente

### Listar Variáveis

```python
from tools.tools_variables import listar_variables

# Listar todas as variáveis
result = listar_variables(
    projectName="MeuProjeto",
    baselineName="Main"
)
```

### Visualizar Variável Específica

```python
from tools.tools_variables import visualizar_variable

# Ver detalhes de uma variável
result = visualizar_variable(
    projectName="MeuProjeto",
    variableName="idade",
    baselineName="Main"
)
```

### Atualizar Variável

```python
from tools.tools_variables import atualizar_variable

# Atualizar valor de uma variável
result = atualizar_variable(
    projectName="MeuProjeto",
    variableName="idade",
    value="25",
    baselineName="Main"
)
```

### Deletar Variável

```python
from tools.tools_variables import deletar_variable

# Remover uma variável
result = deletar_variable(
    projectName="MeuProjeto",
    variableName="idade",
    baselineName="Main"
)
```

## Backend Java

### Endpoint: POST /variables

**Arquivo**: `../eclipse/ODM_TOOLS/src/com/ibm/odm/regras/ODMHttpServer.java`

**Serviço**: `ODMVariableService.java`
- Método principal: `addVariablesToSet()` - Adiciona múltiplas variáveis em lote
- Método legado: `addVariable()` - Deprecado, chama `addVariablesToSet()`

### Comportamento Técnico

1. **Variable Set Novo**:
   - Primeira tentativa: Tenta commitar VariableSet vazio → pode falhar
   - Segunda tentativa: VariableSet já inicializado → sucesso

2. **Variable Set Existente**:
   - Funciona na primeira tentativa

3. **Padrão ODM 9.5**:
   ```java
   // 1. Commit VariableSet vazio (se necessário)
   // 2. Criar CommitableObject
   // 3. Adicionar TODAS as variáveis
   // 4. Commit único com todas as variáveis
   ```

## Arquivos de Configuração

### Credenciais ODM
**Arquivo**: `../eclipse/ODM_TOOLS/src/com/ibm/odm/regras/ODMHttpServer.java`

```java
private static final String DC_USERNAME = "odmAdmin";
private static final String DC_PASSWORD = "odmAdmin";
private static final String DC_URL = "http://my-odm.ibm.com:9060/decisioncenter-api";
private static final String DC_DATASOURCE = "jdbc/ilogDataSource";
```

**Documentação**: Ver [`CONFIGURACAO_JAVA_MCP.md`](CONFIGURACAO_JAVA_MCP.md) para opções de configuração.

## Exemplos CURL

**Arquivo**: [`CURL_CRIAR_VARIAVEIS.sh`](CURL_CRIAR_VARIAVEIS.sh)

Contém 8 exemplos de uso:
1. Variáveis primitivas (int, String)
2. Variáveis com valores iniciais
3. Variáveis de tipos BOM customizados
4. Criação em pacotes específicos
5. Reset de variáveis existentes
6. Múltiplas variáveis em lote
7. Variáveis em pacotes aninhados
8. Variáveis com verbalizações complexas

## Documentação Adicional

- [`PROBLEMA_CRIACAO_VARIAVEIS.md`](PROBLEMA_CRIACAO_VARIAVEIS.md) - Análise do problema e solução
- [`TOOLS_VARIAVEIS_COMPLETO.md`](TOOLS_VARIAVEIS_COMPLETO.md) - Documentação completa
- [`exemplo_criar_variaveis.md`](exemplo_criar_variaveis.md) - Exemplos práticos
- [`CONFIGURACAO_JAVA_MCP.md`](CONFIGURACAO_JAVA_MCP.md) - Como configurar credenciais

## Status Atual

✅ **Funcional** - Requer duas execuções para Variable Sets novos (comportamento esperado do ODM 9.5)

### Próximas Melhorias Possíveis

1. Implementar retry automático no Python (tentar 2x automaticamente)
2. Adicionar validação de tipos BOM antes de criar
3. Suporte para variáveis com tipos genéricos (List<T>, Map<K,V>)
4. Importação em massa de variáveis de arquivo JSON/CSV