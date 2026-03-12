# Correção do Bug de Variables no Backend Java

## 🐛 Problema

Erro ao criar variáveis:
```
java.lang.ClassCastException: class ilog.rules.teamserver.model.impl.IlrElementHandleImpl 
cannot be cast to class ilog.rules.teamserver.brm.IlrVariableSet
```

**Localização:** `ODMVariableService.java` linha 133

## 🔍 Causa Raiz

O método `session.createElement()` retorna um **handle** (`IlrElementHandleImpl`), não o objeto completo (`IlrVariableSet`).

Após o `session.commit()`, é necessário obter os detalhes completos do elemento usando `session.getElementDetails()`.

## ✅ Correção

### Arquivo: `ODMVariableService.java`

#### Método `createVariableSet` (linhas 128-141)

**ANTES (incorreto):**
```java
public IlrVariableSet createVariableSet(IlrSession session, IlrRulePackage pkg, String setName) throws Exception {
    IlrBrmPackage meta = session.getBrmPackage();

    // Instancia via sessão (padrão da API pública do DC)
    IlrVariableSet vset = (IlrVariableSet) session.createElement(meta.getVariableSet());

    // Preenche atributos/relacionamentos (IlrElementDetails) 
    vset.setRawValue(meta.getModelElement_Name(), setName);
    vset.setRawValue(meta.getPackageElement_RulePackage(), pkg);

    session.commit(vset);
    return vset;  // ❌ ERRO: retorna handle, não objeto completo
}
```

**DEPOIS (correto):**
```java
public IlrVariableSet createVariableSet(IlrSession session, IlrRulePackage pkg, String setName) throws Exception {
    IlrBrmPackage meta = session.getBrmPackage();

    // Instancia via sessão (padrão da API pública do DC)
    IlrVariableSet vset = (IlrVariableSet) session.createElement(meta.getVariableSet());

    // Preenche atributos/relacionamentos (IlrElementDetails) 
    vset.setRawValue(meta.getModelElement_Name(), setName);
    vset.setRawValue(meta.getPackageElement_RulePackage(), pkg);

    session.commit(vset);
    
    // ✅ CORREÇÃO: Obtém detalhes completos após commit
    return (IlrVariableSet) session.getElementDetails(vset);
}
```

#### Método `findVariableSetInPackage` (linhas 108-126)

**ANTES (incorreto):**
```java
public IlrVariableSet findVariableSetInPackage(IlrSession session, IlrRulePackage pkg, String setName) throws Exception {
    IlrBrmPackage meta = session.getBrmPackage();
    IlrDefaultSearchCriteria criteria = new IlrDefaultSearchCriteria(
        meta.getVariableSet(),
        Arrays.asList(meta.getModelElement_Name()),
        Arrays.asList(setName)
    );
    List<IlrVariableSet> sets = session.findElements(criteria, IlrModelConstants.ELEMENT_DETAILS);
    if (sets == null) return null;
    for (IlrVariableSet s : sets) {  // ❌ ERRO: 's' pode ser handle
        IlrRulePackage p = s.getRulePackage();
        if (p != null && pkg != null && pkg.getName() != null && pkg.getName().equals(p.getName())) {
            return s;
        }
    }
    return null;
}
```

**DEPOIS (correto):**
```java
public IlrVariableSet findVariableSetInPackage(IlrSession session, IlrRulePackage pkg, String setName) throws Exception {
    IlrBrmPackage meta = session.getBrmPackage();
    IlrDefaultSearchCriteria criteria = new IlrDefaultSearchCriteria(
        meta.getVariableSet(),
        Arrays.asList(meta.getModelElement_Name()),
        Arrays.asList(setName)
    );
    List<IlrVariableSet> sets = session.findElements(criteria, IlrModelConstants.ELEMENT_DETAILS);
    if (sets == null) return null;
    
    for (IlrVariableSet s : sets) {
        // ✅ CORREÇÃO: Garante que temos o objeto completo
        IlrVariableSet fullSet = (IlrVariableSet) session.getElementDetails(s);
        IlrRulePackage p = fullSet.getRulePackage();
        if (p != null && pkg != null && pkg.getName() != null && pkg.getName().equals(p.getName())) {
            return fullSet;
        }
    }
    return null;
}
```

## 📝 Explicação

### Por que isso acontece?

A API do Decision Center usa um padrão de **handles** para eficiência:

1. **Handle** (`IlrElementHandleImpl`): Referência leve ao elemento
2. **Element Details** (`IlrVariableSet`): Objeto completo com todos os dados

### Quando usar `getElementDetails()`?

- ✅ Após `session.createElement()` + `session.commit()`
- ✅ Após `session.findElements()` quando precisar acessar propriedades
- ✅ Sempre que receber um handle e precisar do objeto completo

### Métodos Afetados

1. ✅ `createVariableSet()` - linha 133
2. ✅ `findVariableSetInPackage()` - linha 119
3. ⚠️ Verificar outros métodos que usam `createElement()` ou `findElements()`

## 🧪 Como Testar

Após aplicar a correção:

```bash
# 1. Recompilar o backend Java
cd /Users/rafaelmarques/Documents/eclipse/ODM_TOOLS
javac -cp "libs/*" src/com/ibm/odm/regras/ODMVariableService.java

# 2. Reiniciar o servidor
# (parar e iniciar novamente)

# 3. Testar criação de variáveis
curl -X POST http://localhost:8080/variables \
  -H "Content-Type: application/json" \
  -d '{
    "projectName": "SistemaCredito",
    "packageName": "variaveis",
    "variableSetName": "variables",
    "baselineName": "Main",
    "variables": [
      {
        "name": "cliente",
        "bomType": "com.example.model.Cliente",
        "verbalization": "o cliente"
      }
    ]
  }'
```

**Resultado Esperado:**
```json
{
  "variableSetName": "variables",
  "packageName": "variaveis",
  "variables": [
    {
      "name": "cliente",
      "bomType": "com.example.model.Cliente",
      "verbalization": "o cliente",
      "initialValue": null
    }
  ],
  "projectName": "SistemaCredito",
  "baselineName": "Main",
  "operation": "createOrUpdate"
}
```

## 📚 Referências

- IBM ODM API Documentation: "Using Element Handles and Element Details"
- Stack Overflow: [How to create an object in Decision Center](https://stackoverflow.com/questions/25034462)
- Pattern: `createElement()` → `commit()` → `getElementDetails()`

## ✅ Checklist de Correção

- [ ] Aplicar correção em `createVariableSet()` (linha 133)
- [ ] Aplicar correção em `findVariableSetInPackage()` (linha 119)
- [ ] Recompilar o código Java
- [ ] Reiniciar o servidor HTTP
- [ ] Testar criação de variáveis via curl
- [ ] Testar criação de variáveis via Python tool
- [ ] Verificar outros métodos similares

---

**Data:** 28/01/2026  
**Arquivo:** `ODMVariableService.java`  
**Linhas Afetadas:** 133, 119