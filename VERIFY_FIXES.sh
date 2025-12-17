#!/bin/bash
# Verification Script - Run this immediately after extraction
# This will verify all three critical fixes are present

echo "=================================="
echo "🔍 VERIFYING PACKAGE FIXES"
echo "=================================="
echo ""

FAIL=0

# Check 1: ambition_agent.py has min_gw/max_gw extraction
echo "✓ Check 1: ambition_agent.py extracts min_gw/max_gw from config"
if grep -q '"min_gw": item.get' src/agents/parameter_agents/ambition_agent.py && \
   grep -q '"max_gw": item.get' src/agents/parameter_agents/ambition_agent.py; then
    echo "  ✅ PASS - Found min_gw/max_gw extraction"
    echo "  Lines 81-82:"
    sed -n '81,82p' src/agents/parameter_agents/ambition_agent.py | sed 's/^/    /'
else
    echo "  ❌ FAIL - min_gw/max_gw extraction NOT found"
    FAIL=1
fi
echo ""

# Check 2: parameters.yaml has max_gw: 10000
echo "✓ Check 2: parameters.yaml uses 10000 (not .inf)"
if grep -q 'max_gw: 10000' config/parameters.yaml; then
    echo "  ✅ PASS - Found max_gw: 10000"
    echo "  Lines 58-60:"
    sed -n '58,60p' config/parameters.yaml | sed 's/^/    /'
else
    echo "  ❌ FAIL - max_gw: 10000 NOT found"
    FAIL=1
fi
echo ""

# Check 3: demo script uses src.agents
echo "✓ Check 3: demo script uses 'from src.agents' imports"
if grep -q 'from src.agents.parameter_agents' scripts/demo_ambition_agent.py; then
    echo "  ✅ PASS - Found correct imports"
    echo "  Line 19:"
    sed -n '19p' scripts/demo_ambition_agent.py | sed 's/^/    /'
else
    echo "  ❌ FAIL - Correct imports NOT found"
    FAIL=1
fi
echo ""

# Check 4: Package timestamp
echo "✓ Check 4: Package timestamp"
if [ -f PACKAGE_TIMESTAMP.txt ]; then
    echo "  ✅ Found timestamp:"
    cat PACKAGE_TIMESTAMP.txt | sed 's/^/    /'
else
    echo "  ⚠️  No timestamp file (old package?)"
fi
echo ""

echo "=================================="
if [ $FAIL -eq 0 ]; then
    echo "✅ ALL CHECKS PASSED!"
    echo "Package is correct and ready to use."
    echo ""
    echo "Next step: Run this command to test:"
    echo "  python -c \"from src.agents.parameter_agents import analyze_ambition; print(f'Brazil: {analyze_ambition(\\\"Brazil\\\").score}/10')\""
    echo ""
    echo "Expected output: Brazil: 7.0/10"
else
    echo "❌ SOME CHECKS FAILED!"
    echo ""
    echo "This means you have an OLD package."
    echo "Please download: renewable_rankings_VERIFIED_$(date +%Y%m%d).tar.gz"
fi
echo "=================================="
