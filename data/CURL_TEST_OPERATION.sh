#!/bin/bash

# ODM Operation Service - Test Script for ODM 9.5
# This script tests creating Decision Operations in Decision Center

SERVER="http://localhost:8080"

echo "=========================================="
echo "ODM 9.5 Decision Operation Creation Test"
echo "=========================================="
echo ""

# Test 1: Simple Operation
echo "Test 1: Creating simple operation..."
curl -X POST "${SERVER}/operations?action=create" \
  -H "Content-Type: application/json" \
  -d '{
    "projectName": "TestProject",
    "baselineName": "Main",
    "operationName": "simpleOperation",
    "rulesetName": "testRuleset",
    "parameters": [
      {
        "name": "input",
        "direction": "IN",
        "bomType": "java.lang.String"
      },
      {
        "name": "output",
        "direction": "OUT",
        "bomType": "java.lang.String"
      }
    ]
  }' | jq '.'

echo ""
echo "=========================================="
echo ""

# Test 2: Operation with Package Path
echo "Test 2: Creating operation in specific package..."
curl -X POST "${SERVER}/operations?action=create" \
  -H "Content-Type: application/json" \
  -d '{
    "projectName": "TestProject",
    "baselineName": "Main",
    "operationName": "packagedOperation",
    "packagePath": "com.example.operations",
    "description": "Operation in custom package",
    "rulesetName": "testRuleset",
    "parameters": [
      {
        "name": "request",
        "direction": "IN",
        "bomType": "java.lang.String"
      }
    ]
  }' | jq '.'

echo ""
echo "=========================================="
echo ""

# Test 3: Operation with Ruleflow
echo "Test 3: Creating operation with ruleflow..."
curl -X POST "${SERVER}/operations?action=create" \
  -H "Content-Type: application/json" \
  -d '{
    "projectName": "TestProject",
    "baselineName": "Main",
    "operationName": "operationWithFlow",
    "packagePath": "operations",
    "description": "Operation with associated ruleflow",
    "rulesetName": "testRuleset",
    "ruleflow": {
      "ruleflowName": "testFlow"
    },
    "parameters": [
      {
        "name": "data",
        "direction": "INOUT",
        "bomType": "java.lang.String"
      }
    ]
  }' | jq '.'

echo ""
echo "=========================================="
echo ""

# Test 4: View Operation
echo "Test 4: Viewing operation..."
curl -X GET "${SERVER}/operations?action=view&projectName=TestProject&operationName=simpleOperation" \
  -H "Content-Type: application/json" | jq '.'

echo ""
echo "=========================================="
echo "Tests completed!"
echo "=========================================="

# Made with Bob
