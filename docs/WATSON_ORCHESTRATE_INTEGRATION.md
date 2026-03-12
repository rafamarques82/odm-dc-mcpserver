# Integração com Watson Orchestrate

## 🎯 Visão Geral

Este documento descreve como integrar o MCP Server com o **IBM Watson Orchestrate**, permitindo que você use as ferramentas do Decision Center como **Skills** no Orchestrate.

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    Watson Orchestrate                        │
│  (Interface de Automação de Processos)                      │
└────────────────────┬────────────────────────────────────────┘
                     │ REST API / OpenAPI
                     ↓
┌─────────────────────────────────────────────────────────────┐
│          Watson Orchestrate Adapter (Flask)                  │
│  - Expõe Skills via REST API                                │
│  - Converte chamadas para MCP Tools                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              Watson MCP Client                               │
│  - Agente conversacional (Watson AI)                        │
│  - Gerencia contexto e histórico                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                  MCP Server                                  │
│  - 8+ ferramentas para ODM Decision Center                  │
│  - Regras, Tabelas, Ruleflows, Variáveis, etc.             │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Início Rápido

### 1. Instalar Dependências

```bash
# Ative o ambiente virtual
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt
```

### 2. Configurar Watson

Edite `watsonaix/config.json`:

```json
{
  "ibm_watsonx": {
    "api_key": "SUA_API_KEY",
    "project_id": "SEU_PROJECT_ID",
    "region": "us-south",
    "model_id": "meta-llama/llama-3-3-70b-instruct"
  }
}
```

### 3. Iniciar o Adaptador

```bash
python watson_orchestrate_adapter.py
```

O servidor iniciará em `http://0.0.0.0:5000`

## 📋 Endpoints Disponíveis

### Health Check
```bash
GET /health
```

### Listar Skills
```bash
GET /api/v1/skills
```

Retorna todas as skills (ferramentas MCP) disponíveis.

### Detalhes de uma Skill
```bash
GET /api/v1/skills/{skill_id}
```

### Executar Skill
```bash
POST /api/v1/skills/{skill_id}/execute
Content-Type: application/json

{
  "parameters": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

### Chat Conversacional
```bash
POST /api/v1/chat
Content-Type: application/json

{
  "message": "Liste os projetos do Decision Center",
  "context": {}
}
```

### Especificação OpenAPI
```bash
GET /api/v1/openapi.json
```

Retorna a especificação OpenAPI 3.0 para integração com Watson Orchestrate.

## 🔗 Integrar com Watson Orchestrate

### Passo 1: Acessar Watson Orchestrate

1. Acesse [Watson Orchestrate](https://www.ibm.com/products/watson-orchestrate)
2. Faça login com suas credenciais IBM Cloud

### Passo 2: Adicionar Skill Customizada

1. No Watson Orchestrate, vá para **Skills**
2. Clique em **Add skill** → **Custom skill**
3. Selecione **OpenAPI specification**

### Passo 3: Configurar a Skill

1. **URL da especificação OpenAPI:**
   ```
   http://SEU_SERVIDOR:5000/api/v1/openapi.json
   ```

2. **Autenticação:** (se necessário)
   - Tipo: API Key ou Bearer Token
   - Configure conforme sua infraestrutura

3. **Nome da Skill:**
   ```
   ODM Decision Center Skills
   ```

4. **Descrição:**
   ```
   Ferramentas para gerenciar regras, tabelas de decisão e 
   ruleflows no IBM ODM Decision Center
   ```

### Passo 4: Testar a Skill

No Watson Orchestrate, teste a skill:

```
"Liste os projetos do Decision Center"
"Mostre as regras do projeto Crédito"
"Crie uma regra de validação de idade"
```

## 🛠️ Skills Disponíveis

### 1. Decision Center Operations
- **list_decision_services** - Lista projetos/decision services
- **get_project_details** - Detalhes de um projeto

### 2. Rules Management
- **get_rules** - Lista regras de um projeto
- **criar_regra** - Cria nova regra
- **update_rule** - Atualiza regra existente
- **delete_rule** - Remove regra

### 3. Decision Tables
- **get_decision_tables** - Lista tabelas de decisão
- **criar_decision_table** - Cria nova tabela
- **update_decision_table** - Atualiza tabela

### 4. Ruleflows
- **get_ruleflows** - Lista ruleflows
- **criar_ruleflow** - Cria novo ruleflow
- **update_ruleflow** - Atualiza ruleflow

### 5. Variables & Vocabulary
- **criar_variables** - Cria variáveis de negócio
- **consultar_vocabulario_bom** - Consulta vocabulário BOM

### 6. Project Generation
- **gerar_projeto_odm** - Gera projeto ODM completo

### 7. AI Integration
- **integracao_chatbot** - Integração com chatbot

## 💡 Exemplos de Uso

### Exemplo 1: Listar Projetos

**No Watson Orchestrate:**
```
"Quais projetos existem no Decision Center?"
```

**Chamada REST equivalente:**
```bash
curl -X POST http://localhost:5000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Liste os projetos do Decision Center"
  }'
```

### Exemplo 2: Criar Regra

**No Watson Orchestrate:**
```
"Crie uma regra chamada ValidarIdade que verifica se a idade é maior que 18"
```

**Chamada REST equivalente:**
```bash
curl -X POST http://localhost:5000/api/v1/skills/criar_regra/execute \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "decision_service_id": "abc-123",
      "rule_name": "ValidarIdade",
      "rule_content": "se a idade é pelo menos 18 então definir aprovado como verdadeiro;"
    }
  }'
```

### Exemplo 3: Workflow Completo

**No Watson Orchestrate, crie um workflow:**

1. **Skill 1:** Lista projetos
2. **Skill 2:** Obtém regras do projeto selecionado
3. **Skill 3:** Cria nova regra no projeto
4. **Skill 4:** Valida a regra criada

## 🔒 Segurança

### Autenticação

Para produção, adicione autenticação ao adaptador:

```python
from flask import request
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != 'SUA_API_KEY_SECRETA':
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/v1/skills', methods=['GET'])
@require_api_key
def list_skills():
    # ...
```

### HTTPS

Para produção, use HTTPS:

```bash
# Com certificado SSL
python watson_orchestrate_adapter.py --ssl-cert cert.pem --ssl-key key.pem
```

## 🐛 Troubleshooting

### Problema: Skills não aparecem no Orchestrate

**Solução:**
1. Verifique se o servidor está acessível
2. Teste o endpoint OpenAPI: `curl http://localhost:5000/api/v1/openapi.json`
3. Verifique logs do adaptador

### Problema: Erro ao executar skill

**Solução:**
1. Verifique se o Watson MCP Client está inicializado
2. Verifique logs: `tail -f watson_orchestrate.log`
3. Teste a ferramenta diretamente via REST

### Problema: Timeout nas chamadas

**Solução:**
1. Aumente o timeout no Watson Orchestrate
2. Otimize as ferramentas MCP
3. Use cache para respostas frequentes

## 📊 Monitoramento

### Logs

O adaptador gera logs em:
```
watson_orchestrate_adapter.log
```

### Métricas

Monitore:
- Número de chamadas por skill
- Tempo de resposta
- Taxa de erro
- Skills mais usadas

## 🔄 Atualizações

### Adicionar Nova Skill

1. Adicione a ferramenta no MCP Server
2. Reinicie o adaptador
3. A skill aparecerá automaticamente no Orchestrate

### Atualizar Skill Existente

1. Modifique a ferramenta no MCP Server
2. Reinicie o adaptador
3. No Orchestrate, atualize a skill (re-import OpenAPI)

## 📚 Recursos Adicionais

- [Watson Orchestrate Documentation](https://www.ibm.com/docs/en/watson-orchestrate)
- [OpenAPI Specification](https://swagger.io/specification/)
- [MCP Protocol](https://modelcontextprotocol.io/)

## 🤝 Suporte

Para problemas ou dúvidas:
1. Consulte a documentação
2. Verifique os logs
3. Abra uma issue no GitHub

---

**Made with Bob** 🤖