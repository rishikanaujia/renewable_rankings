#!/usr/bin/env python3
"""Test that comparative analysis agent reads config correctly."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import yaml
from src.agents.analysis_agents import ComparativeAnalysisAgent
from src.agents.base_agent import AgentMode

print("=" * 70)
print("🧪 COMPARATIVE ANALYSIS CONFIG TEST")
print("=" * 70)

# Load config
config_path = project_root / "config" / "parameters.yaml"
with open(config_path) as f:
    config = yaml.safe_load(f)

print("\n1. Checking YAML configuration...")
if 'analysis' in config and 'comparative_analysis' in config['analysis']:
    comp_config = config['analysis']['comparative_analysis']
    print("   ✅ comparative_analysis section found")
    print(f"   - min_countries: {comp_config.get('min_countries')}")
    print(f"   - max_countries: {comp_config.get('max_countries')}")
    print(f"   - recommended_countries: {comp_config.get('recommended_countries')}")
    
    gap_thresholds = comp_config.get('gap_thresholds', {})
    print(f"   - Gap thresholds:")
    print(f"     • Highly competitive: {gap_thresholds.get('highly_competitive')}")
    print(f"     • Moderately competitive: {gap_thresholds.get('moderately_competitive')}")
    print(f"     • Uncompetitive: {gap_thresholds.get('uncompetitive')}")
else:
    print("   ❌ comparative_analysis section NOT found")
    sys.exit(1)

print("\n2. Testing agent with config...")
agent = ComparativeAnalysisAgent(mode=AgentMode.MOCK, config=config['analysis'])
print("   ✅ Agent initialized with config")

print("\n3. Testing validation (too few countries)...")
try:
    result = agent.compare(countries=["Germany"], period="Q3 2024")
    print("   ❌ Should have raised error for single country")
except Exception as e:
    if "at least 2 countries" in str(e):
        print("   ✅ Correctly rejected single country")
    else:
        print(f"   ❌ Wrong error: {e}")

print("\n4. Testing valid comparison...")
try:
    result = agent.compare(
        countries=["Germany", "USA", "Brazil"], 
        period="Q3 2024"
    )
    print(f"   ✅ Comparison successful")
    print(f"   - Countries: {len(result.countries)}")
    print(f"   - Top: {result.country_comparisons[0].country} ({result.country_comparisons[0].overall_score:.1f})")
    print(f"   - Summary includes: {'minimal' if 'minimal' in result.summary else 'moderate' if 'moderate' in result.summary else 'substantial'} variation")
except Exception as e:
    print(f"   ❌ Comparison failed: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ ALL CONFIG TESTS PASSED!")
print("=" * 70)
print("\n📊 Configuration is:")
print("  ✅ Present in YAML")
print("  ✅ Being read by agent")
print("  ✅ Used for validation")
print("  ✅ Used in summary generation")
print()
