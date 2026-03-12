# Exemplo de Uso: criar_variaveis_no_variable_set

Esta tool expõe a API Java do ODMHttpServer para criar variáveis dentro de um Variable Set no IBM ODM 9.5.

## Endpoint Java Correspondente

```
POST http://localhost:8080/variables
Content-Type: application/json
```

## Estrutura do Payload

```json
{
  "projectName": "NomeDoProjeto",
  "packageName": "pacote.opcional",
  "variableSetName": "variables",
  "baselineName": "Main",
  "resetIfExists": false,
  "variables": [
    {
      "name": "nomeVariavel",
      "bomType": "tipo.completo.BOM",
      "verbalization": "frase de verbalização",
      "initialValue": "valor inicial em IRL"
    }
  ]
}
```

## Exemplos de Uso

### 1. Criar Variáveis de Tipos Primitivos

```python
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
            "name": "nome",
            "bomType": "java.lang.String",
            "verbalization": "o nome",
            "initialValue": '""'
        },
        {
            "name": "ativo",
            "bomType": "boolean",
            "verbalization": "está ativo",
            "initialValue": "false"
        }
    ]
)
```

### 2. Criar Variáveis de Tipos BOM Customizados

```python
criar_variaveis_no_variable_set(
    projectName="AprovarCredito",
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
            "name": "resultado",
            "bomType": "com.example.model.ResultadoAnalise",
            "verbalization": "o resultado da análise"
        }
    ]
)
```

### 3. Resetar e Recriar Variáveis

```python
# Remove todas as variáveis existentes e cria novas
criar_variaveis_no_variable_set(
    projectName="MeuProjeto",
    variableSetName="variables",
    resetIfExists=True,  # ATENÇÃO: Remove todas as variáveis existentes!
    variables=[
        {
            "name": "novaVariavel",
            "bomType": "java.lang.String",
            "verbalization": "a nova variável"
        }
    ]
)
```

### 4. Criar Variáveis em Pacote Específico

```python
criar_variaveis_no_variable_set(
    projectName="MeuProjeto",
    variableSetName="variables",
    packageName="regras.validacao.entrada",  # Pacote aninhado
    variables=[
        {
            "name": "dadosEntrada",
            "bomType": "com.example.DadosEntrada",
            "verbalization": "os dados de entrada"
        }
    ]
)
```

## Tipos BOM Comuns

### Tipos Primitivos Java
- `int` - Inteiro
- `long` - Inteiro longo
- `double` - Número decimal
- `boolean` - Booleano
- `java.lang.String` - String
- `java.util.Date` - Data

### Tipos Customizados
Use o nome completo da classe do XOM:
- `com.example.model.Cliente`
- `com.example.model.Emprestimo`
- `com.ibm.rules.samples.loanvalidation.Borrower`

## Formato do initialValue (IRL)

O valor inicial deve estar em formato IRL (Ilog Rule Language):

- **String**: `"\"texto\""`  (aspas duplas escapadas)
- **Número**: `"42"` ou `"3.14"`
- **Boolean**: `"true"` ou `"false"`
- **Null**: `null` ou omitir o campo
- **Objeto**: Geralmente `null` para objetos complexos

## Resposta de Sucesso

```json
{
  "status": "success",
  "message": "Variáveis criadas/atualizadas no Variable Set 'variables'",
  "result": {
    "projectName": "MeuProjeto",
    "baselineName": "Main",
    "operation": "createOrUpdate",
    "variableSetName": "variables",
    "variables": [...]
  },
  "projectName": "MeuProjeto",
  "baselineName": "Main",
  "variableSetName": "variables",
  "totalVariables": 3
}
```

## Resposta de Erro

```json
{
  "status": "error",
  "error": "Mensagem de erro detalhada",
  "payload": {...}
}
```

## Configuração

Certifique-se de que:

1. O servidor Java está rodando:
   ```bash
   # Padrão: http://localhost:8080
   ```

2. Configure a variável de ambiente se necessário:
   ```bash
   export OTHER_BASE_URL="http://localhost:8080"
   ```

3. O projeto existe no Decision Center

4. Os tipos BOM existem no XOM do projeto

## Diferenças entre as Tools

### `criar_variable` (tools_variables.py)
- Cria UMA variável por vez
- Usa API REST do Decision Center diretamente
- Mais simples para casos básicos

### `criar_variaveis_no_variable_set` (tools_decisioncenter.py)
- Cria MÚLTIPLAS variáveis em lote
- Usa backend Java (ODMHttpServer)
- Suporta tipos BOM complexos
- Melhor performance para criação em massa
- Suporta reset de Variable Set

## Notas Importantes

⚠️ **ATENÇÃO**: 
- `resetIfExists=True` remove TODAS as variáveis do Variable Set antes de criar as novas
- Tipos BOM devem existir no XOM do projeto
- O formato do `initialValue` deve ser IRL válido
- Variáveis com mesmo nome são atualizadas (upsert)