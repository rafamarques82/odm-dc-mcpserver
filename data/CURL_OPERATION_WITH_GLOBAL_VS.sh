#!/bin/bash

# Criar operação usando Variable Set "global" existente

SERVER="http://localhost:8080"

echo "Criando operação usando Variable Set 'global' existente..."

curl -X POST "${SERVER}/operations?action=create" \
  -H "Content-Type: application/json" \
  -d '{
    "projectName": "SistemaCredito",
    "baselineName": "Main",
    "operationName": "testOperation",
    "rulesetName": "testRuleset",
    "ruleflow": {
      "ruleflowName": "Principal"
    },
    "parameters": [
      {
        "name": "iddade",
        "direction": "IN",
        "bomType": "cadeia"
      }
    ],
    "descriptorSets": ["global"],
    "paramsSets": ["global"],
    "rulesetParamSets": ["global"]
  }' | jq '.'

echo ""
echo "✅ Operação criada usando Variable Set 'global'!"

# Made with Bob
