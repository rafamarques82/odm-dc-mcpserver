#!/bin/bash

# ============================================================================
# Exemplos de Criação de Variáveis via CURL
# Endpoint: POST http://localhost:8080/variables
# ============================================================================

# Configurações
BASE_URL="http://localhost:8080"
PROJECT_NAME="MeuProjeto"
BASELINE_NAME="Main"

echo "=========================================="
echo "Exemplos de Criação de Variáveis via CURL"
echo "=========================================="
echo ""

# ============================================================================
# Exemplo 1: Criar variáveis de tipos primitivos
# ============================================================================
echo "1. Criando variáveis de tipos primitivos..."
echo ""

curl -X POST "${BASE_URL}/variables" \
  -H "Content-Type: application/json" \
  -d '{
    "projectName": "'"${PROJECT_NAME}"'",
    "packageName": "",
    "variableSetName": "variables",
    "baselineName": "'"${BASELINE_NAME}"'",
    "resetIfExists": false,
    "variables": [
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
        "initialValue": "\"\""
      },
      {
        "name": "ativo",
        "bomType": "boolean",
        "verbalization": "está ativo",
        "initialValue": "false"
      },
      {
        "name": "salario",
        "bomType": "double",
        "verbalization": "o salário",
        "initialValue": "0.0"
      }
    ]
  }'

echo ""
echo ""

# ============================================================================
# Exemplo 2: Criar variáveis de tipos BOM customizados
# ============================================================================
echo "2. Criando variáveis de tipos BOM customizados..."
echo ""

curl -X POST "${BASE_URL}/variables" \
  -H "Content-Type: application/json" \
  -d '{
    "projectName": "'"${PROJECT_NAME}"'",
    "packageName": "regras.credito",
    "variableSetName": "variables",
    "baselineName": "'"${BASELINE_NAME}"'",
    "resetIfExists": false,
    "variables": [
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
  }'

echo ""
echo ""

# ============================================================================
# Exemplo 3: Criar variáveis com reset (remove todas as existentes)
# ============================================================================
echo "3. Criando variáveis com RESET (remove todas as existentes)..."
echo ""

curl -X POST "${BASE_URL}/variables" \
  -H "Content-Type: application/json" \
  -d '{
    "projectName": "'"${PROJECT_NAME}"'",
    "packageName": "",
    "variableSetName": "variables",
    "baselineName": "'"${BASELINE_NAME}"'",
    "resetIfExists": true,
    "variables": [
      {
        "name": "novaVariavel1",
        "bomType": "java.lang.String",
        "verbalization": "a nova variável 1"
      },
      {
        "name": "novaVariavel2",
        "bomType": "int",
        "verbalization": "a nova variável 2",
        "initialValue": "100"
      }
    ]
  }'

echo ""
echo ""

# ============================================================================
# Exemplo 4: Criar variável única (formato simplificado)
# ============================================================================
echo "4. Criando uma única variável..."
echo ""

curl -X POST "${BASE_URL}/variables" \
  -H "Content-Type: application/json" \
  -d '{
    "projectName": "'"${PROJECT_NAME}"'",
    "packageName": "",
    "variableSetName": "variables",
    "baselineName": "'"${BASELINE_NAME}"'",
    "variables": [
      {
        "name": "contador",
        "bomType": "int",
        "verbalization": "o contador",
        "initialValue": "0"
      }
    ]
  }'

echo ""
echo ""

# ============================================================================
# Exemplo 5: Criar variáveis em pacote aninhado
# ============================================================================
echo "5. Criando variáveis em pacote aninhado..."
echo ""

curl -X POST "${BASE_URL}/variables" \
  -H "Content-Type: application/json" \
  -d '{
    "projectName": "'"${PROJECT_NAME}"'",
    "packageName": "regras.validacao.entrada",
    "variableSetName": "variables",
    "baselineName": "'"${BASELINE_NAME}"'",
    "variables": [
      {
        "name": "dadosEntrada",
        "bomType": "com.example.DadosEntrada",
        "verbalization": "os dados de entrada"
      },
      {
        "name": "validado",
        "bomType": "boolean",
        "verbalization": "foi validado",
        "initialValue": "false"
      }
    ]
  }'

echo ""
echo ""

# ============================================================================
# Exemplo 6: Criar variáveis com valores iniciais complexos
# ============================================================================
echo "6. Criando variáveis com valores iniciais..."
echo ""

curl -X POST "${BASE_URL}/variables" \
  -H "Content-Type: application/json" \
  -d '{
    "projectName": "'"${PROJECT_NAME}"'",
    "packageName": "",
    "variableSetName": "variables",
    "baselineName": "'"${BASELINE_NAME}"'",
    "variables": [
      {
        "name": "mensagem",
        "bomType": "java.lang.String",
        "verbalization": "a mensagem",
        "initialValue": "\"Bem-vindo ao sistema\""
      },
      {
        "name": "limiteCredito",
        "bomType": "double",
        "verbalization": "o limite de crédito",
        "initialValue": "5000.00"
      },
      {
        "name": "dataAtual",
        "bomType": "java.util.Date",
        "verbalization": "a data atual"
      }
    ]
  }'

echo ""
echo ""

# ============================================================================
# Exemplo 7: Listar variáveis (GET)
# ============================================================================
echo "7. Listando todas as variáveis do projeto..."
echo ""

curl -X GET "${BASE_URL}/variables?projectName=${PROJECT_NAME}&baselineName=${BASELINE_NAME}" \
  -H "Content-Type: application/json"

echo ""
echo ""

# ============================================================================
# Exemplo 8: Visualizar uma variável específica (GET)
# ============================================================================
echo "8. Visualizando variável específica 'cliente'..."
echo ""

curl -X GET "${BASE_URL}/variables?projectName=${PROJECT_NAME}&baselineName=${BASELINE_NAME}&packageName=regras.credito&variableSetName=variables" \
  -H "Content-Type: application/json"

echo ""
echo ""

echo "=========================================="
echo "Exemplos concluídos!"
echo "=========================================="

# Made with Bob
