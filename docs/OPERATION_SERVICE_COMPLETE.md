# ODM Operation Service - Complete Implementation

## Overview

The `ODMOperationService` class has been enhanced to **actually create and manage operations** in IBM ODM Decision Center, not just configure metadata in Variable Sets.

## What Changed

### Before (Old Behavior)
- ❌ Only saved operation metadata to Variable Sets
- ❌ Did NOT create the actual IlrOperation object
- ❌ Operations had to be created manually in Decision Center
- ✅ Could configure parameters, ruleflow, and ruleset parameters in Variable Sets

### After (New Behavior)
- ✅ **Creates/updates the actual IlrOperation object** in Decision Center
- ✅ **Adds parameters (IN/OUT/INOUT)** with BOM types to the operation
- ✅ **Associates ruleflow** to the operation
- ✅ **Optionally saves metadata** to Variable Sets for reference
- ✅ **Supports package paths** for organizing operations
- ✅ **Adds descriptions** to operations

## New Features

### 1. Operation Creation
```java
IlrOperation operation = createOrUpdateOperation(
    session,
    project,
    "com.example.operations",  // Package path
    "approveCredit",            // Operation name
    "Approve credit application", // Description
    parameters,                 // List of parameters
    "creditApprovalFlow"        // Ruleflow name
);
```

### 2. Parameter Management
Parameters are now **actually added** to the operation with:
- **Name**: Parameter identifier
- **Direction**: IN, OUT, or INOUT
- **BOM Type**: Full class name (e.g., "com.example.CreditRequest")

### 3. Ruleflow Association
The ruleflow is **directly associated** with the operation object, not just stored as metadata.

### 4. Package Organization
Operations can be created in specific packages:
- `null` or empty → Root package
- `"operations"` → operations package
- `"com.example.operations"` → nested package structure

## API Usage

### HTTP Endpoint

**POST/PUT** `/operations?action=create` or `/operations?action=update`

#### Request Body
```json
{
  "projectName": "CreditApproval",
  "baselineName": "Main",
  "operationName": "approveCredit",
  "packagePath": "com.example.operations",
  "description": "Approve credit application based on risk analysis",
  "ruleflow": {
    "ruleflowName": "creditApprovalFlow"
  },
  "parameters": [
    {
      "name": "request",
      "direction": "IN",
      "bomType": "com.example.CreditRequest"
    },
    {
      "name": "response",
      "direction": "OUT",
      "bomType": "com.example.CreditResponse"
    },
    {
      "name": "context",
      "direction": "INOUT",
      "bomType": "com.example.Context"
    }
  ],
  "rulesetParameters": {
    "maxAmount": "100000",
    "minScore": "600"
  },
  "rulesetName": "creditApprovalRuleset"
}
```

#### Response
```json
{
  "operationCreated": true,
  "operationPath": "com.example.operations.approveCredit",
  "projectName": "CreditApproval",
  "baselineName": "Main",
  "operationName": "approveCredit",
  "ruleflowNameProvided": "creditApprovalFlow",
  "ruleflowValidated": true,
  "parametersUpdatedCount": 3,
  "parametersMissing": [],
  "descriptorUpdatedCount": 2,
  "descriptorMissing": [],
  "rulesetParametersUpdatedCount": 2,
  "rulesetParametersMissing": [],
  "status": "saved",
  "runtimeRulesetName": "creditApprovalRuleset",
  "operation": "create"
}
```

### Java API

#### Simple Usage (Backward Compatible)
```java
ODMOperationService service = new ODMOperationService(
    serverUrl, datasource, login, password
);

Map<String, Object> result = service.saveOperation(
    "CreditApproval",           // projectName
    "Main",                     // baselineName
    "approveCredit",            // operationName
    null,                       // ruleflowPackage (ignored)
    "creditApprovalFlow",       // ruleflowName
    parameters,                 // List<Map<String,String>>
    rulesetParameters,          // Map<String,String>
    null,                       // registryRootPackage (ignored)
    null,                       // descriptorSetNames
    null,                       // paramsSetNames
    null                        // rulesetParamSetNames
);
```

#### Advanced Usage (With Package and Description)
```java
Map<String, Object> result = service.saveOperation(
    "CreditApproval",           // projectName
    "Main",                     // baselineName
    "approveCredit",            // operationName
    null,                       // ruleflowPackage (ignored)
    "creditApprovalFlow",       // ruleflowName
    parameters,                 // List<Map<String,String>>
    rulesetParameters,          // Map<String,String>
    null,                       // registryRootPackage (ignored)
    null,                       // descriptorSetNames
    null,                       // paramsSetNames
    null,                       // rulesetParamSetNames
    "com.example.operations",   // packagePath
    "Approve credit application" // description
);
```

## Parameter Format

Each parameter in the `parameters` list should be a Map with:

```java
Map<String, String> param = new LinkedHashMap<>();
param.put("name", "request");
param.put("direction", "IN");  // IN, OUT, or INOUT
param.put("bomType", "com.example.CreditRequest");
```

## Key Methods

### `createOrUpdateOperation()`
Core method that creates or updates the IlrOperation object:
- Creates operation if it doesn't exist
- Updates existing operation if found
- Adds/replaces parameters
- Associates ruleflow
- Sets description

### `findOperationByName()`
Searches for an existing operation in a specific package.

### `resolveOrCreatePackage()`
Creates nested package structure if it doesn't exist.

### `findBomClass()`
Locates BOM classes by name for parameter types.

## Migration Guide

### If You Were Using the Old Service

**Old Code:**
```java
// Only saved metadata, didn't create operation
service.saveOperation(project, baseline, name, ...);
// You had to manually create the operation in Decision Center
```

**New Code:**
```java
// Now creates the actual operation!
service.saveOperation(project, baseline, name, ...);
// Operation is created with parameters and ruleflow
```

### No Breaking Changes
The API is **backward compatible**. Existing code will work, but now it will:
1. Create the actual operation (new!)
2. Add parameters to the operation (new!)
3. Associate the ruleflow (new!)
4. Save metadata to Variable Sets (as before)

## Benefits

1. **Complete Automation**: No manual steps in Decision Center
2. **Type Safety**: Parameters have proper BOM types
3. **Organization**: Operations in proper package structure
4. **Documentation**: Descriptions embedded in operations
5. **Integration**: Ruleflows directly linked
6. **Metadata**: Optional Variable Set storage for reference

## Testing

### Test Operation Creation
```bash
curl -X POST "http://localhost:8080/operations?action=create" \
  -H "Content-Type: application/json" \
  -d '{
    "projectName": "TestProject",
    "operationName": "testOperation",
    "packagePath": "test.operations",
    "description": "Test operation",
    "parameters": [
      {"name": "input", "direction": "IN", "bomType": "java.lang.String"},
      {"name": "output", "direction": "OUT", "bomType": "java.lang.String"}
    ]
  }'
```

### Verify in Decision Center
1. Open Decision Center
2. Navigate to the project
3. Go to the package path (e.g., `test.operations`)
4. Find the operation
5. Check parameters, ruleflow, and description

## Troubleshooting

### Operation Not Created
- Check that the project and baseline exist
- Verify user has write permissions
- Check server logs for errors

### Parameters Missing Types
- Ensure BOM classes exist in the project
- Use full class names (e.g., `com.example.MyClass`)
- Check BOM is properly deployed

### Ruleflow Not Associated
- Verify ruleflow exists in the project
- Check ruleflow name is correct
- Ruleflow must be in the same project

## Summary

The `ODMOperationService` is now a **complete operation management solution** that:
- ✅ Creates actual operations in Decision Center
- ✅ Manages parameters with proper types
- ✅ Associates ruleflows
- ✅ Organizes operations in packages
- ✅ Maintains backward compatibility
- ✅ Optionally stores metadata in Variable Sets

**No more manual operation creation needed!** 🎉