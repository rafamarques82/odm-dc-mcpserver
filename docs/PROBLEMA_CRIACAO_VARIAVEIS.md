# Problema na Criação de Variáveis no IBM ODM 9.5

## Sintoma
Erro: `The property 'name' cannot be empty` ao tentar criar variáveis via API Java.

## Causa Raiz
O método `setRawValue()` em `IlrElementDetails` não persiste os valores corretamente quando usado com `getElementDetailsForThisHandle()`.

## Tentativas Realizadas

### 1. Usar getElementDetails() ❌
```java
IlrVariable var = (IlrVariable) session.getElementDetails(varHandle);
var.setRawValue(meta.getTypedElement_Name(), name);
// Problema: getRootDetails() retorna null no commit
```

### 2. Usar getElementDetailsForThisHandle() ❌
```java
IlrElementDetails varDetails = session.getElementDetailsForThisHandle(varHandle);
varDetails.setRawValue(meta.getTypedElement_Name(), name);
// Problema: Valores não são persistidos, name fica vazio
```

### 3. Commit em duas etapas ❌
```java
// Etapa 1: Commit do VariableSet vazio
// Etapa 2: Adicionar variável
// Problema: Mesmo erro - name vazio
```

## Solução Recomendada

Baseado no exemplo fornecido pelo usuário, o padrão correto é:

```java
IlrBrmPackage brmPackage = session.getBrmPackage();

// 1. Criar VariableSet
IlrElementHandle vSet = session.createElement(brmPackage.getVariableSet());
IlrElementDetails vSetDetails = session.getElementDetailsForThisHandle(vSet);
vSetDetails.setRawValue(brmPackage.getModelElement_Name(), "Variable Set");

// 2. Commit do VariableSet vazio
IlrCommitableObject co = new IlrCommitableObject(vSetDetails);
co.setRootDetails(vSetDetails);
vSet = session.commit(branch, co);

// 3. Criar novo CommitableObject para adicionar variáveis
co = new IlrCommitableObject(vSet);

// 4. Para cada variável
for (int i = 0; i < 3; i++) {
    IlrElementHandle variable = session.createElement(brmPackage.getVariable());
    IlrElementDetails varDetails = session.getElementDetailsForThisHandle(variable);
    varDetails.setRawValue(brmPackage.getTypedElement_BomType(), "java.lang.String");
    varDetails.setRawValue(brmPackage.getTypedElement_Name(), "myVariable" + i);
    varDetails.setRawValue(brmPackage.getTypedElement_Verbalization(), "myVariable" + i);
    
    // Adiciona ao CommitableObject (NÃO faz commit individual)
    co.addModifiedElement(brmPackage.getVariableSet_Variables(), varDetails);
}

// 5. Commit único com todas as variáveis
session.commit(branch, co);
```

## Diferença Chave

**ERRADO** (nossa implementação atual):
- Cria variável
- Seta valores
- Cria CommitableObject
- setRootDetails
- addModifiedElement
- Commit ❌ (valores não persistem)

**CORRETO** (padrão IBM):
- Cria VariableSet
- Commit do VariableSet vazio
- Cria NOVO CommitableObject do VariableSet commitado
- Para cada variável:
  - Cria handle
  - Seta valores
  - addModifiedElement (SEM commit individual)
- Commit único com TODAS as variáveis ✅

## Próximos Passos

1. Refatorar `addVariable()` para seguir o padrão correto
2. Separar em dois métodos:
   - `createVariableSet()` - Cria e commita VariableSet vazio
   - `addVariablesToSet()` - Adiciona múltiplas variáveis em lote
3. Modificar o endpoint POST /variables para usar o novo padrão

## Código Sugerido

```java
// Método 1: Criar VariableSet vazio
public IlrVariableSet createEmptyVariableSet(IlrSession session, 
                                             IlrRulePackage pkg,
                                             String setName,
                                             Object branch) {
    IlrBrmPackage meta = session.getBrmPackage();
    IlrElementHandle vSet = session.createElement(meta.getVariableSet());
    IlrElementDetails vSetDetails = session.getElementDetailsForThisHandle(vSet);
    vSetDetails.setRawValue(meta.getModelElement_Name(), setName);
    
    IlrCommitableObject co = new IlrCommitableObject(vSetDetails);
    co.setRootDetails(vSetDetails);
    return (IlrVariableSet) session.commit(branch, co);
}

// Método 2: Adicionar variáveis em lote
public void addVariablesToSet(IlrSession session,
                               IlrVariableSet vset,
                               List<VariableData> variables,
                               Object branch) {
    IlrBrmPackage meta = session.getBrmPackage();
    IlrCommitableObject co = new IlrCommitableObject(vset);
    
    for (VariableData varData : variables) {
        IlrElementHandle varHandle = session.createElement(meta.getVariable());
        IlrElementDetails varDetails = session.getElementDetailsForThisHandle(varHandle);
        
        varDetails.setRawValue(meta.getTypedElement_BomType(), varData.bomType);
        varDetails.setRawValue(meta.getTypedElement_Name(), varData.name);
        varDetails.setRawValue(meta.getTypedElement_Verbalization(), varData.verbalization);
        
        co.addModifiedElement(meta.getVariableSet_Variables(), varDetails);
    }
    
    session.commit(branch, co);
}
```

## Conclusão

O problema não é com `setRootDetails()` ou materialização do VariableSet.
O problema é que estamos tentando fazer commit individual de cada variável.
O padrão correto do IBM ODM é:
1. Commit do VariableSet vazio
2. Adicionar TODAS as variáveis ao CommitableObject
3. Commit único com todas as variáveis juntas