@echo off
REM Script para iniciar o Watson Orchestrate Local no Windows

echo ==========================================
echo Watson Orchestrate Local
echo ==========================================
echo.

REM Verifica se o ambiente virtual existe
if not exist ".venv" (
    echo ❌ Ambiente virtual não encontrado!
    echo    Execute: python -m venv .venv
    exit /b 1
)

REM Ativa o ambiente virtual
echo 🔄 Ativando ambiente virtual...
call .venv\Scripts\activate.bat

REM Verifica se as dependências estão instaladas
echo 🔍 Verificando dependências...
python -c "import fastmcp" 2>nul
if errorlevel 1 (
    echo 📦 Instalando dependências...
    pip install -r requirements.txt
)

REM Verifica configuração do Watson
echo 🔍 Verificando configuração do Watson...
findstr /C:"YOUR_API_KEY" watsonaix\config.json >nul
if errorlevel 1 (
    echo ✅ Watson configurado
) else (
    echo ⚠️  Watson não configurado!
    echo    Edite: watsonaix\config.json
    echo.
)

REM Inicia o orchestrate local
echo.
echo 🚀 Iniciando Watson Orchestrate Local...
echo.
python watson_orchestrate_local.py

REM Made with Bob

@REM Made with Bob
