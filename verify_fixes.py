#!/usr/bin/env python3
"""
Verification Script - Run this immediately after extraction
This will verify all three critical fixes are present
"""
import sys
from pathlib import Path

def check_file_exists(filepath):
    """Check if file exists."""
    return Path(filepath).exists()

def check_file_contains(filepath, search_text):
    """Check if file contains specific text."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            return search_text in content
    except Exception as e:
        print(f"    Error reading {filepath}: {e}")
        return False

def get_line(filepath, line_num):
    """Get specific line from file."""
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
            if line_num <= len(lines):
                return lines[line_num - 1].rstrip()
    except:
        pass
    return None

def main():
    print("=" * 50)
    print("🔍 VERIFYING PACKAGE FIXES")
    print("=" * 50)
    print()
    
    failed = False
    
    # Check 1: ambition_agent.py
    print("✓ Check 1: ambition_agent.py extracts min_gw/max_gw from config")
    agent_file = "src/agents/parameter_agents/ambition_agent.py"
    if check_file_contains(agent_file, '"min_gw": item.get') and \
       check_file_contains(agent_file, '"max_gw": item.get'):
        print("  ✅ PASS - Found min_gw/max_gw extraction")
        line81 = get_line(agent_file, 81)
        line82 = get_line(agent_file, 82)
        if line81 and line82:
            print(f"  Line 81: {line81.strip()}")
            print(f"  Line 82: {line82.strip()}")
    else:
        print("  ❌ FAIL - min_gw/max_gw extraction NOT found")
        failed = True
    print()
    
    # Check 2: parameters.yaml
    print("✓ Check 2: parameters.yaml uses 10000 (not .inf)")
    config_file = "config/parameters.yaml"
    if check_file_contains(config_file, 'max_gw: 10000'):
        print("  ✅ PASS - Found max_gw: 10000")
        for line_num in [58, 59, 60]:
            line = get_line(config_file, line_num)
            if line:
                print(f"  Line {line_num}: {line.strip()}")
    else:
        print("  ❌ FAIL - max_gw: 10000 NOT found")
        failed = True
    print()
    
    # Check 3: demo script
    print("✓ Check 3: demo script uses 'from src.agents' imports")
    demo_file = "scripts/demo_ambition_agent.py"
    if check_file_contains(demo_file, 'from src.agents.parameter_agents'):
        print("  ✅ PASS - Found correct imports")
        line19 = get_line(demo_file, 19)
        if line19:
            print(f"  Line 19: {line19.strip()}")
    else:
        print("  ❌ FAIL - Correct imports NOT found")
        failed = True
    print()
    
    # Check 4: Timestamp
    print("✓ Check 4: Package timestamp")
    if check_file_exists("PACKAGE_TIMESTAMP.txt"):
        print("  ✅ Found timestamp:")
        with open("PACKAGE_TIMESTAMP.txt", 'r') as f:
            for line in f:
                print(f"    {line.rstrip()}")
    else:
        print("  ⚠️  No timestamp file (old package?)")
    print()
    
    # Summary
    print("=" * 50)
    if not failed:
        print("✅ ALL CHECKS PASSED!")
        print("Package is correct and ready to use.")
        print()
        print("Next step: Run this command to test:")
        print('  python -c "from src.agents.parameter_agents import analyze_ambition; print(f\'Brazil: {analyze_ambition(\\\"Brazil\\\").score}/10\')"')
        print()
        print("Expected output: Brazil: 7.0/10")
        return 0
    else:
        print("❌ SOME CHECKS FAILED!")
        print()
        print("This means you have an OLD package.")
        print("Please re-download the latest package.")
        return 1
    print("=" * 50)

if __name__ == "__main__":
    sys.exit(main())
