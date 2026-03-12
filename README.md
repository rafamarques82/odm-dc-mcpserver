# Servidor MCP para ODM Decision Center

Um servidor MCP (Model Context Protocol) que fornece ferramentas com IA para operações do IBM ODM Decision Center. Este servidor permite que assistentes de IA interajam com o ODM Decision Center através de um protocolo padronizado.

## 🎯 Visão Geral

Este projeto implementa um servidor MCP que expõe 8 ferramentas especializadas para gerenciar projetos do IBM ODM Decision Center, incluindo:
- Criação e gerenciamento de regras de negócio
- Tabelas de decisão
- Ruleflows (orquestração)
- Variáveis e vocabulário
- Geração de projetos com suporte a XOM

## 🚀 Interfaces Disponíveis

### 1. **Watson Orchestrate** (Recomendado para Produção)
Integração nativa com IBM Watson Orchestrate para automação de processos empresariais.

```bash
# Iniciar adaptador do Orchestrate
./start_orchestrate.sh  # Linux/Mac
start_orchestrate.bat   # Windows
```

[📖 Documentação completa do Watson Orchestrate](docs/WATSON_ORCHESTRATE_INTEGRATION.md)

### 2. **Interface Web (Streamlit)**
Interface web interativa para desenvolvimento e testes.

```bash
streamlit run watson_web_ui.py
```

### 3. **CLI (Linha de Comando)**
Cliente de linha de comando para automação e scripts.

```bash
python watson_mcp_client.py
```

## 📋 Pré-requisitos

- Python 3.8+
- IBM ODM Decision Center (instância em execução)
- Servidor Backend Java (ODMHttpServer) para operações de regras
- Cliente de IA compatível com MCP (Claude Desktop, etc.)

## 🚀 Início Rápido

### 1. Instalação

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd MEUMCP

# Crie o ambiente virtual
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate

# Instale as dependências
pip install fastmcp requests
```

### 2. Configuração

Configure as variáveis de ambiente:

```bash
# API do Decision Center
export DC_BASE_URL="http://seu-servidor-odm:9060/decisioncenter-api/v1"
export DC_USERNAME="odmAdmin"
export DC_PASSWORD="sua-senha"

# Servidor Backend Java (para operações de regras)
export OTHER_BASE_URL="http://localhost:8080"

# Servidor MCP
export MCP_TRANSPORT="stdio"  # ou "http"
export HTTP_HOST="0.0.0.0"    # se usar HTTP
export HTTP_PORT="8000"       # se usar HTTP
```

### 3. Execute o Servidor

```bash
python decision_center_mcp_server_Regras.py
```

## 📁 Estrutura do Projeto

```
MEUMCP/
├── decision_center_mcp_server_Regras.py  # Servidor MCP principal
├── tools/                                 # Ferramentas MCP (8 módulos)
│   ├── tools_variables.py                # Gerenciamento de variáveis
│   ├── tools_rules.py                    # Criação de regras
│   ├── tools_decisiontables.py           # Tabelas de decisão
│   ├── tools_ruleflows.py                # Orquestração de ruleflows
│   ├── tools_vocab.py                    # Consultas ao vocabulário BOM
│   ├── tools_decisioncenter.py           # API REST do DC
│   ├── tools_project_generator.py        # Geração de projetos
│   └── tools_chatbot.py                  # Integração com IA
├── helpers/                              # Clientes utilitários
│   ├── dc_rest_client.py                # Cliente REST do Decision Center
│   └── http_java_client.py              # Cliente do backend Java
├── examples/                             # Exemplos de uso
│   ├── criar_projeto_completo.py        # Criação de projeto completo
│   ├── criar_projeto_com_xom.py         # Projeto com XOM
│   ├── gerar_vocabulario.py             # Geração de vocabulário
│   └── list_tools.py                    # Listar ferramentas disponíveis
├── tests/                                # Scripts de teste
├── docs/                                 # Documentação
└── data/                                 # Arquivos de exemplo
```

## 🛠️ Ferramentas Disponíveis

### 1. **criar_variables** - Gerenciamento de Variáveis
Crie e gerencie variáveis de negócio com verbalizações adequadas.

### 2. **criar_regra** - Criação de Regras
Crie regras de negócio com sintaxe BAL (Business Action Language).

### 3. **criar_decision_table** - Tabelas de Decisão
Crie e gerencie tabelas de decisão.

### 4. **criar_ruleflow** - Orquestração de Ruleflows
Crie ruleflows para orquestrar a execução de regras.

### 5. **consultar_vocabulario_bom** - Consultas ao Vocabulário
Consulte o vocabulário e classes do BOM (Business Object Model).

### 6. **operacoes_decision_center** - API REST do DC
Acesso direto às operações da API REST do Decision Center.

### 7. **gerar_projeto_odm** - Geração de Projetos
Gere projetos ODM completos com suporte a XOM.

### 8. **integracao_chatbot** - Integração com IA
Integre com assistentes de IA para interações em linguagem natural.

## 📖 Documentação

- [Arquitetura](docs/ARCHITECTURE.md) - Arquitetura e design do sistema
- [Referência da API](docs/API_REFERENCE.md) - Documentação completa da API
- [Contribuindo](CONTRIBUTING.md) - Diretrizes de contribuição

## 🔧 Detalhes de Configuração

### Conexão com o Decision Center

O servidor se conecta ao IBM ODM Decision Center usando a API REST:

```python
DC_BASE_URL = "http://seu-servidor:9060/decisioncenter-api/v1"
DC_USERNAME = "odmAdmin"
DC_PASSWORD = "sua-senha"
```

### Servidor Backend Java

As operações de regras requerem um servidor backend Java (ODMHttpServer):

```python
OTHER_BASE_URL = "http://localhost:8080"
```

Este servidor gerencia:
- Criação e validação de regras
- Geração de XML de ruleflows
- Operações de tabelas de decisão
- Verbalização de variáveis

## 🎯 Exemplos de Uso

### Criar um Projeto Completo

```python
from examples.criar_projeto_completo import criar_projeto_completo

# Criar projeto com regras e ruleflow
criar_projeto_completo(
    project_name="AprovacaoCredito",
    branch_name="Main"
)
```

### Criar Regras de Negócio

```python
# Regras são criadas usando sintaxe BAL
regra_bal = """
se a idade do cliente é pelo menos 18
    e o score de crédito é pelo menos 650
então
    definir o status de aprovação como "APROVADO";
"""
```

### Criar Ruleflow

```python
# Ruleflows orquestram a execução de regras
ruleflow_xml = """
<Ruleflow xmlns="http://schemas.ilog.com/Rules/7.0/Ruleflow">
  <Body>
    <TaskList>
      <StartTask/>
      <RuleTask>
        <RuleList package="validacao"/>
      </RuleTask>
      <StopTask/>
    </TaskList>
  </Body>
</Ruleflow>
"""
```

## ⚠️ Notas Importantes

### Verbalizações de Variáveis
Sempre use verbalizações de variáveis nas regras, não nomes técnicos:
- ✅ CORRETO: `se 'a idade do cliente' é pelo menos 18`
- ❌ ERRADO: `se 'idadeCliente' é pelo menos 18`

### Organização de Pacotes
Agrupe regras relacionadas em pacotes lógicos:
- ✅ CORRETO: Pacote "Validacao" → Regra1, Regra2, Regra3
- ❌ ERRADO: Pacote "Regra1" → Regra1 (uma por pacote)

### Fluxo de Trabalho Recomendado
1. Criar projeto
2. Criar variáveis
3. Criar regras em pacotes
4. Criar ruleflow (obrigatório para execução)

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor, leia [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes.

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🔗 Projetos Relacionados

- [FastMCP](https://github.com/jlowin/fastmcp) - Framework de servidor MCP
- [IBM ODM](https://www.ibm.com/products/operational-decision-manager) - Plataforma de gerenciamento de decisões

## 📞 Suporte

Para problemas e questões:
1. Consulte a [documentação](docs/)
2. Revise os [exemplos](examples/)
3. Abra uma issue no GitHub

## 🎓 Recursos de Aprendizado

- [Protocolo MCP](https://modelcontextprotocol.io/) - Especificação do Model Context Protocol
- [Documentação do IBM ODM](https://www.ibm.com/docs/en/odm) - Documentação oficial do ODM
- [Guia da Linguagem BAL](https://www.ibm.com/docs/en/odm/8.12.0?topic=rules-business-action-language) - Referência da Business Action Language