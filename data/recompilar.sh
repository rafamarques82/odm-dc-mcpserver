#!/bin/bash

echo "=== Recompilando ODM_TOOLS ==="

# Caminho para o projeto
PROJECT_DIR="../eclipse/ODM_TOOLS"

# Encontra todos os arquivos .java
echo "Procurando arquivos Java..."
find "$PROJECT_DIR/src" -name "*.java" -type f

# Compila
echo ""
echo "Compilando..."
cd "$PROJECT_DIR"

# Se tiver um build.xml (Ant)
if [ -f "build.xml" ]; then
    echo "Usando Ant..."
    ant clean compile
# Se tiver um pom.xml (Maven)
elif [ -f "pom.xml" ]; then
    echo "Usando Maven..."
    mvn clean compile
# Compilação manual
else
    echo "Compilação manual com javac..."
    # Cria diretório bin se não existir
    mkdir -p bin
    
    # Compila todos os .java
    find src -name "*.java" > sources.txt
    javac -d bin -cp "lib/*:." @sources.txt
    rm sources.txt
    
    echo "Compilação concluída!"
fi

echo ""
echo "=== Recompilação finalizada ==="
echo "Agora reinicie o servidor HTTP Java!"

# Made with Bob
