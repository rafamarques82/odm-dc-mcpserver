# Como Passar Configurações Java para o Servidor MCP

## Visão Geral

O servidor MCP Python (`tools/tools_decisioncenter.py`) se comunica com um backend Java (`ODMHttpServer.java`) que contém as configurações de conexão com o IBM ODM Decision Center.

## Localização das Configurações

As configurações estão definidas no arquivo Java:
```
../eclipse/ODM_TOOLS/src/com/ibm/odm/regras/ODMHttpServer.java
```

Linhas 48-52:
```java
private static final String DC_USERNAME = "odmAdmin";
private static final String DC_PASSWORD = "odmAdmin";
private static final String DC_URL = "http://my-odm.ibm.com:9060/decisioncenter-api";
private static final String DC_DATASOURCE = "jdbc/ilogDataSource";
```

## Opções para Configurar

### Opção 1: Editar Diretamente o Arquivo Java (Atual)

**Vantagens:**
- Simples e direto
- Não requer mudanças na arquitetura

**Desvantagens:**
- Requer recompilação após cada mudança
- Credenciais ficam hardcoded no código

**Como fazer:**
1. Edite o arquivo `ODMHttpServer.java` com suas credenciais
2. Recompile o projeto Java
3. Reinicie o servidor Java

```bash
# Recompilar
cd ../eclipse/ODM_TOOLS
javac -cp "lib/*:." src/com/ibm/odm/regras/*.java

# Reiniciar servidor
java -cp "lib/*:bin" com.ibm.odm.regras.ODMHttpServer
```

### Opção 2: Usar Variáveis de Ambiente (Recomendado)

**Vantagens:**
- Mais seguro (credenciais não ficam no código)
- Flexível (pode mudar sem recompilar)
- Segue boas práticas de segurança

**Desvantagens:**
- Requer modificação no código Java

**Implementação:**

1. **Modificar ODMHttpServer.java:**

```java
// Substituir as constantes por:
private static final String DC_USERNAME = System.getenv().getOrDefault("ODM_USERNAME", "odmAdmin");
private static final String DC_PASSWORD = System.getenv().getOrDefault("ODM_PASSWORD", "odmAdmin");
private static final String DC_URL = System.getenv().getOrDefault("ODM_URL", "http://localhost:9060/decisioncenter-api");
private static final String DC_DATASOURCE = System.getenv().getOrDefault("ODM_DATASOURCE", "jdbc/ilogDataSource");
```

2. **Criar arquivo .env no projeto:**

```bash
# .env
ODM_USERNAME=odmAdmin
ODM_PASSWORD=odmAdmin
ODM_URL=http://my-odm.ibm.com:9060/decisioncenter-api
ODM_DATASOURCE=jdbc/ilogDataSource
```

3. **Iniciar servidor com variáveis:**

```bash
# Linux/Mac
export ODM_USERNAME=odmAdmin
export ODM_PASSWORD=odmAdmin
export ODM_URL=http://my-odm.ibm.com:9060/decisioncenter-api
export ODM_DATASOURCE=jdbc/ilogDataSource
java -cp "lib/*:bin" com.ibm.odm.regras.ODMHttpServer

# Ou carregar do .env
source .env
java -cp "lib/*:bin" com.ibm.odm.regras.ODMHttpServer
```

### Opção 3: Arquivo de Configuração JSON/Properties

**Vantagens:**
- Configuração centralizada
- Fácil de gerenciar múltiplos ambientes
- Pode incluir outras configurações

**Desvantagens:**
- Requer mais código para ler o arquivo

**Implementação:**

1. **Criar arquivo config.json:**

```json
{
  "odm": {
    "username": "odmAdmin",
    "password": "odmAdmin",
    "url": "http://my-odm.ibm.com:9060/decisioncenter-api",
    "datasource": "jdbc/ilogDataSource"
  },
  "server": {
    "port": 8080
  }
}
```

2. **Modificar ODMHttpServer.java para ler o arquivo:**

```java
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.File;

public class ODMHttpServer {
    private static String DC_USERNAME;
    private static String DC_PASSWORD;
    private static String DC_URL;
    private static String DC_DATASOURCE;
    
    static {
        try {
            ObjectMapper mapper = new ObjectMapper();
            JsonNode config = mapper.readTree(new File("config.json"));
            DC_USERNAME = config.get("odm").get("username").asText();
            DC_PASSWORD = config.get("odm").get("password").asText();
            DC_URL = config.get("odm").get("url").asText();
            DC_DATASOURCE = config.get("odm").get("datasource").asText();
        } catch (Exception e) {
            // Valores padrão
            DC_USERNAME = "odmAdmin";
            DC_PASSWORD = "odmAdmin";
            DC_URL = "http://localhost:9060/decisioncenter-api";
            DC_DATASOURCE = "jdbc/ilogDataSource";
        }
    }
}
```

### Opção 4: Passar via Argumentos de Linha de Comando

**Vantagens:**
- Flexível para testes
- Não requer arquivo externo

**Desvantagens:**
- Credenciais visíveis no histórico de comandos
- Menos conveniente para uso regular

**Implementação:**

```java
public static void main(String[] args) throws IOException {
    String username = args.length > 0 ? args[0] : "odmAdmin";
    String password = args.length > 1 ? args[1] : "odmAdmin";
    String url = args.length > 2 ? args[2] : "http://localhost:9060/decisioncenter-api";
    String datasource = args.length > 3 ? args[3] : "jdbc/ilogDataSource";
    
    // Usar essas variáveis no código...
}
```

```bash
# Executar
java -cp "lib/*:bin" com.ibm.odm.regras.ODMHttpServer \
  odmAdmin \
  odmAdmin \
  http://my-odm.ibm.com:9060/decisioncenter-api \
  jdbc/ilogDataSource
```

## Recomendação

Para o seu caso, recomendo a **Opção 2 (Variáveis de Ambiente)** porque:

1. ✅ Mais seguro - credenciais não ficam no código
2. ✅ Flexível - pode mudar sem recompilar
3. ✅ Simples de implementar
4. ✅ Compatível com containers/Docker
5. ✅ Segue boas práticas de segurança

## Integração com o MCP Server Python

O servidor MCP Python não precisa saber das credenciais - ele apenas chama o endpoint Java:

```python
# tools/tools_decisioncenter.py
def criar_variaveis_no_variable_set(...):
    # Chama o backend Java que já tem as credenciais configuradas
    response = requests.post(
        "http://localhost:8080/variables",
        json=payload
    )
```

O fluxo é:
```
MCP Server (Python) → HTTP Request → Java Backend → ODM Decision Center
                                    ↑
                              Credenciais aqui
```

## Próximos Passos

1. Escolha a opção de configuração que prefere
2. Modifique o `ODMHttpServer.java` se necessário
3. Recompile o projeto Java
4. Configure as credenciais (arquivo .env, variáveis, etc.)
5. Reinicie o servidor Java
6. Teste com o MCP server Python

## Exemplo Completo com Variáveis de Ambiente

```bash
# 1. Criar .env
cat > .env << 'EOF'
ODM_USERNAME=odmAdmin
ODM_PASSWORD=odmAdmin
ODM_URL=http://my-odm.ibm.com:9060/decisioncenter-api
ODM_DATASOURCE=jdbc/ilogDataSource
EOF

# 2. Modificar ODMHttpServer.java (usar System.getenv)

# 3. Recompilar
cd ../eclipse/ODM_TOOLS
javac -cp "lib/*:." src/com/ibm/odm/regras/*.java

# 4. Iniciar com variáveis
source .env
java -cp "lib/*:bin" com.ibm.odm.regras.ODMHttpServer

# 5. Testar do Python
python -m tools.tools_decisioncenter