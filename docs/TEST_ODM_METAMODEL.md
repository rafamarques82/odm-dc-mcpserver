# Test: Discover Available ODM Metamodel Elements

To find out if "Decision Operation" exists in your ODM version, we need to test the metamodel.

## Quick Test Script

Add this temporary endpoint to your ODMHttpServer to discover available elements:

```java
// Add to ODMHttpServer.java
server.createContext("/test/metamodel", (ex) -> {
    try {
        ODMOperationService svc = new ODMOperationService(DC_URL, DC_DATASOURCE, DC_USERNAME, DC_PASSWORD);
        IlrSession session = svc.openSession();
        IlrBrmPackage meta = session.getBrmPackage();
        
        StringBuilder sb = new StringBuilder();
        sb.append("Available Metamodel Elements:\n\n");
        
        // Test common elements
        try { sb.append("✓ getActionRule: ").append(meta.getActionRule()).append("\n"); } catch (Exception e) { sb.append("✗ getActionRule\n"); }
        try { sb.append("✓ getDecisionTable: ").append(meta.getDecisionTable()).append("\n"); } catch (Exception e) { sb.append("✗ getDecisionTable\n"); }
        try { sb.append("✓ getRuleflow: ").append(meta.getRuleflow()).append("\n"); } catch (Exception e) { sb.append("✗ getRuleflow\n"); }
        try { sb.append("✓ getVariableSet: ").append(meta.getVariableSet()).append("\n"); } catch (Exception e) { sb.append("✗ getVariableSet\n"); }
        
        // Test operation-related elements
        try { sb.append("✓ getOperation: ").append(meta.getOperation()).append("\n"); } catch (Exception e) { sb.append("✗ getOperation: ").append(e.getMessage()).append("\n"); }
        try { sb.append("✓ getDecisionOperation: ").append(meta.getDecisionOperation()).append("\n"); } catch (Exception e) { sb.append("✗ getDecisionOperation: ").append(e.getMessage()).append("\n"); }
        try { sb.append("✓ getFunction: ").append(meta.getFunction()).append("\n"); } catch (Exception e) { sb.append("✗ getFunction: ").append(e.getMessage()).append("\n"); }
        
        session.close();
        
        ex.sendResponseHeaders(200, sb.toString().getBytes().length);
        ex.getResponseBody().write(sb.toString().getBytes());
        ex.getResponseBody().close();
    } catch (Exception e) {
        String error = "Error: " + e.getMessage();
        ex.sendResponseHeaders(500, error.getBytes().length);
        ex.getResponseBody().write(error.getBytes());
        ex.getResponseBody().close();
    }
});
```

## Run Test

```bash
curl http://localhost:8080/test/metamodel
```

## Alternative: Check ODM Version

Decision Operations were introduced in specific ODM versions. Please provide:

1. Your ODM version (e.g., 8.10, 8.11, 9.0)
2. The exact artifact type you see in Decision Center UI

## Common ODM Artifact Types

Different ODM versions support different artifacts:

- **Action Rules** (`getActionRule`) - Standard business rules
- **Decision Tables** (`getDecisionTable`) - Tabular rules
- **Ruleflows** (`getRuleflow`) - Rule orchestration
- **Functions** (`getFunction`) - Reusable functions (ODM 8.9+)
- **Decision Operations** (`getDecisionOperation`) - Service operations (ODM 8.10+)
- **Variable Sets** (`getVariableSet`) - Variable collections

## If Decision Operations Don't Exist

If your ODM version doesn't have Decision Operations as artifacts, the current approach (storing metadata in Variable Sets) is the correct pattern. Operations would then be defined at deployment time via:

1. **RuleApp deployment descriptor**
2. **REST API configuration**
3. **Rule Execution Server console**

Please run the test or provide your ODM version so I can implement the correct solution.