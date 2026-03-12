#!/bin/bash

# Script de Configuração do Chatbot IBM watsonx.ai
# ================================================

echo "🚀 Configurando Chatbot IBM watsonx.ai para MCP Server"
echo "======================================================="
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verifica se Python 3.13 está instalado
echo "📋 Verificando Python 3.13..."
if command -v python3.13 &> /dev/null; then
    PYTHON_CMD="python3.13"
    PIP_CMD="python3.13 -m pip"
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [[ "$PYTHON_VERSION" == "3.13" ]]; then
        PYTHON_CMD="python3"
        PIP_CMD="python3 -m pip"
    else
        echo -e "${YELLOW}⚠️  Python 3.13 não encontrado. Versão atual: Python $PYTHON_VERSION${NC}"
        echo "IBM watsonx.ai funciona melhor com Python 3.10-3.13"
        PYTHON_CMD="python3"
        PIP_CMD="python3 -m pip"
    fi
else
    echo -e "${RED}❌ Python 3 não encontrado. Por favor, instale Python 3.13.${NC}"
    exit 1
fi

PYTHON_FULL_VERSION=$($PYTHON_CMD --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Python $PYTHON_FULL_VERSION encontrado${NC}"
echo "   Usando: $PYTHON_CMD"
echo ""

# Instala dependências do watsonx.ai
echo "📦 Instalando dependências do IBM watsonx.ai..."
echo "   Comando: $PIP_CMD install -r watsonaix/requirements.txt"
$PIP_CMD install -r watsonaix/requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependências instaladas com sucesso${NC}"
else
    echo -e "${RED}❌ Erro ao instalar dependências${NC}"
    echo ""
    echo "Possíveis soluções:"
    echo "1. Atualize o pip: $PIP_CMD install --upgrade pip"
    echo "2. Tente instalar manualmente: $PIP_CMD install 'ibm-watsonx-ai<1.4.0' ibm-cloud-sdk-core"
    exit 1
fi
echo ""

# Verifica se o arquivo de configuração existe
echo "🔧 Verificando configuração..."
if [ ! -f "watsonaix/config.json" ]; then
    echo -e "${RED}❌ Arquivo watsonaix/config.json não encontrado${NC}"
    exit 1
fi

# Verifica se as credenciais foram configuradas
API_KEY=$(grep -o '"api_key": "[^"]*"' watsonaix/config.json | cut -d'"' -f4)
PROJECT_ID=$(grep -o '"project_id": "[^"]*"' watsonaix/config.json | cut -d'"' -f4)

if [ "$API_KEY" = "YOUR_API_KEY" ] || [ "$PROJECT_ID" = "YOUR_PROJECT_ID" ]; then
    echo -e "${YELLOW}⚠️  Credenciais não configuradas em watsonaix/config.json${NC}"
    echo ""
    echo "Por favor, configure suas credenciais IBM watsonx.ai:"
    echo "1. Edite o arquivo: watsonaix/config.json"
    echo "2. Substitua YOUR_API_KEY pela sua API key"
    echo "3. Substitua YOUR_PROJECT_ID pelo seu project ID"
    echo ""
    echo "Ou use variáveis de ambiente:"
    echo "  export IBM_WATSONX_API_KEY='sua_api_key'"
    echo "  export IBM_WATSONX_PROJECT_ID='seu_project_id'"
    echo ""
    echo "Consulte CHATBOT_SETUP_GUIDE.md para instruções detalhadas."
    echo ""
else
    echo -e "${GREEN}✅ Credenciais configuradas${NC}"
fi
echo ""

# Resumo
echo "📝 Resumo da Configuração"
echo "========================"
echo ""
echo "✅ Python $PYTHON_FULL_VERSION instalado"
echo "✅ Dependências instaladas"
echo "✅ Arquivo de configuração presente"
echo ""

if [ "$API_KEY" != "YOUR_API_KEY" ] && [ "$PROJECT_ID" != "YOUR_PROJECT_ID" ]; then
    echo -e "${GREEN}🎉 Configuração completa! Você pode iniciar o servidor:${NC}"
    echo ""
    echo "  $PYTHON_CMD decision_center_mcp_server_Regras.py"
    echo ""
    echo "Ou testar a configuração primeiro:"
    echo "  $PYTHON_CMD test_chatbot.py"
    echo ""
else
    echo -e "${YELLOW}⚠️  Configure suas credenciais antes de iniciar o servidor${NC}"
    echo ""
fi

echo "📚 Para mais informações, consulte: CHATBOT_SETUP_GUIDE.md"
echo ""

# Made with Bob
