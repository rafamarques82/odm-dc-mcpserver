# Contribuindo para o Servidor MCP do ODM Decision Center

Obrigado pelo seu interesse em contribuir para o projeto Servidor MCP do ODM Decision Center!

## 🚀 Começando

### Pré-requisitos

- Python 3.8 ou superior
- IBM ODM Decision Center 9.0+
- Servidor backend Java (ODMHttpServer) em execução
- Git

### Configuração de Desenvolvimento

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd MEUMCP
```

2. **Crie o ambiente virtual**
```bash
python3 -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
```

3. **Instale as dependências**
```bash
pip install fastmcp requests
```

4. **Configure as variáveis de ambiente**
```bash
# Decision Center
export DC_BASE_URL="http://seu-servidor-odm:9060/decisioncenter-api/v1"
export DC_USERNAME="odmAdmin"
export DC_PASSWORD="odmAdmin"

# Backend Java
export OTHER_BASE_URL="http://localhost:8080"

# Watson AI (opcional)
export IBM_WATSONX_API_KEY="sua-chave-api"
export IBM_WATSONX_PROJECT_ID="seu-id-projeto"
```

5. **Execute o servidor MCP**
```bash
python decision_center_mcp_server_Regras.py
```

## 📁 Estrutura do Projeto

```
MEUMCP/
├── decision_center_mcp_server_Regras.py  # Servidor MCP principal
├── watson_mcp_client.py                  # Cliente MCP Watson
├── watson_web_ui.py                      # Interface Web
│
├── tools/                                # Ferramentas MCP (8 módulos)
│   ├── tools_variables.py               # Gerenciamento de variáveis
│   ├── tools_rules.py                   # Regras de ação
│   ├── tools_decisiontables.py          # Tabelas de decisão
│   ├── tools_ruleflows.py               # Ruleflows
│   ├── tools_vocab.py                   # Vocabulário
│   ├── tools_decisioncenter.py          # API REST do DC
│   ├── tools_project_generator.py       # Geração de projetos
│   └── tools_chatbot.py                 # Chatbot Watson AI
│
├── helpers/                              # Módulos auxiliares
│   ├── dc_rest_client.py                # Cliente REST do DC
│   └── http_java_client.py              # Cliente do backend Java
│
├── watsonaix/                            # Integração Watson AI
├── docs/                                 # Documentação
├── examples/                             # Scripts de exemplo
├── tests/                                # Scripts de teste
└── data/                                 # Arquivos de dados
```

## 🛠️ Diretrizes de Desenvolvimento

### Estilo de Código

- Siga o guia de estilo PEP 8
- Use type hints quando possível
- Escreva docstrings em português
- Mantenha funções focadas e com propósito único

### Documentação

- Todas as docstrings devem estar em português
- Inclua descrições de parâmetros
- Forneça exemplos de uso
- Documente valores de retorno

### Formato de Docstring de Exemplo

```python
@mcp.tool()
def funcao_exemplo(param1: str, param2: int = 10) -> dict:
    """
    Breve descrição do que a função faz.
    
    Explicação detalhada se necessário, incluindo:
    - Notas importantes
    - Diretrizes de uso
    - Melhores práticas
    
    Args:
        param1: Descrição do param1
        param2: Descrição do param2 (padrão: 10)
    
    Returns:
        Dict com resultado contendo:
        - status: "success" ou "error"
        - data: Dados do resultado
    
    Example:
        >>> funcao_exemplo("teste", 20)
        {"status": "success", "data": {...}}
    
    Notes:
        - Informações adicionais importantes
        - Avisos ou ressalvas
    """
    # Implementação
    pass
```

## 🧪 Testes

### Executando Testes

```bash
# Executar todos os testes
python -m pytest tests/

# Executar arquivo de teste específico
python tests/test_mcp_server.py

# Executar com cobertura
python -m pytest --cov=tools tests/
```

### Escrevendo Testes

- Coloque testes no diretório `tests/`
- Nomeie arquivos de teste com prefixo `test_`
- Use nomes descritivos para funções de teste
- Inclua casos de teste positivos e negativos

## 📝 Diretrizes de Commit

### Formato de Mensagem de Commit

```
<tipo>(<escopo>): <assunto>

<corpo>

<rodapé>
```

### Tipos

- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Mudanças na documentação
- `style`: Mudanças de estilo de código (formatação, etc.)
- `refactor`: Refatoração de código
- `test`: Adição ou atualização de testes
- `chore`: Tarefas de manutenção

### Exemplos

```bash
feat(tools): adicionar suporte para validação de tabela de decisão

- Implementar lógica de validação
- Adicionar tratamento de erros
- Atualizar documentação

Closes #123
```

```bash
fix(rules): corrigir sintaxe BAL na criação de regras

A verbalização estava faltando aspas adequadas ao redor dos nomes das variáveis.
Esta correção garante que todas as variáveis sejam devidamente citadas.
```

## 🔧 Adicionando Novas Ferramentas

### Passos para Adicionar uma Nova Ferramenta MCP

1. **Criar arquivo de ferramenta** no diretório `tools/`
```python
# tools/tools_nova_funcionalidade.py

from mcp.server.fastmcp import FastMCP
import builtins

mcp: FastMCP = builtins.__dict__.get("mcp")

@mcp.tool()
def nova_funcao_ferramenta(param: str) -> dict:
    """
    Descrição da ferramenta em português.
    
    Args:
        param: Descrição do parâmetro
    
    Returns:
        Dict com resultado
    """
    # Implementação
    return {"status": "success"}
```

2. **Importar no servidor principal**
```python
# decision_center_mcp_server_Regras.py

from tools import tools_nova_funcionalidade
```

3. **Adicionar documentação**
- Atualizar README.md
- Adicionar exemplos
- Documentar parâmetros

4. **Escrever testes**
```python
# tests/test_nova_funcionalidade.py

def test_nova_funcao_ferramenta():
    result = nova_funcao_ferramenta("teste")
    assert result["status"] == "success"
```

## 🐛 Reportando Problemas

### Relatórios de Bugs

Inclua:
- Descrição clara do problema
- Passos para reproduzir
- Comportamento esperado vs real
- Detalhes do ambiente (SO, versão Python, versão ODM)
- Mensagens de erro e stack traces

### Solicitações de Funcionalidades

Inclua:
- Descrição clara da funcionalidade
- Casos de uso e benefícios
- Implementação proposta (se houver)
- Exemplos de funcionalidades similares

## 📚 Recursos

- [Documentação do IBM ODM](https://www.ibm.com/docs/en/odm)
- [Especificação do Protocolo MCP](https://modelcontextprotocol.io/)
- [Documentação do FastMCP](https://github.com/jlowin/fastmcp)
- [Guia de Estilo Python (PEP 8)](https://pep8.org/)

## 🤝 Processo de Revisão de Código

1. Criar um branch de funcionalidade
2. Fazer suas mudanças
3. Escrever/atualizar testes
4. Atualizar documentação
5. Submeter pull request
6. Abordar feedback da revisão
7. Merge após aprovação

## 📄 Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a mesma licença do projeto.

## 💬 Dúvidas?

- Abra uma issue para perguntas
- Consulte a documentação existente
- Revise issues fechadas para perguntas similares

Obrigado por contribuir! 🎉