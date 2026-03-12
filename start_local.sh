#!/bin/bash
# Script para iniciar o Watson Orchestrate Local

echo "=========================================="
echo "Watson Orchestrate Local"
echo "=========================================="
echo ""

# Verifica se o ambiente virtual existe
if [ ! -d ".venv" ]; then
    echo "❌ Ambiente virtual não encontrado!"
    echo "   Execute: python -m venv .venv"
    exit 1
fi

# Ativa o ambiente virtual
echo "🔄 Ativando ambiente virtual..."
source .venv/bin/activate

# Verifica se as dependências estão instaladas
echo "🔍 Verificando dependências..."
python -c "import fastmcp" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Instalando dependências..."
    pip install -r requirements.txt
fi

# Verifica configuração do Watson
echo "🔍 Verificando configuração do Watson..."
if ! grep -q "YOUR_API_KEY" watsonaix/config.json; then
    echo "✅ Watson configurado"
else
    echo "⚠️  Watson não configurado!"
    echo "   Edite: watsonaix/config.json"
    echo ""
fi

# Inicia o orchestrate local
echo ""
echo "🚀 Iniciando Watson Orchestrate Local..."
echo ""
python watson_orchestrate_local.py

# Made with Bob