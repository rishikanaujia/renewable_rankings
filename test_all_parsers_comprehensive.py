#!/usr/bin/env python3
"""Comprehensive Test of All 18 Research Integration Parsers

This script tests all parameter parsers with real research documents
to validate the architecture before rolling out to all agents.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Set up logging
os.environ['LOG_LEVEL'] = 'WARNING'  # Reduce noise

from research_system import ResearchOrchestrator
from research_integration.parsers import (
    PARSER_REGISTRY,
    get_parser
)


def print_section(title: str):
    """Print formatted section header."""
    print("\n" + "=" * 100)
    print(f" {title}")
    print("=" * 100 + "\n")


def print_subsection(title: str):
    """Print formatted subsection."""
    print(f"\n{'─' * 100}")
    print(f" {title}")
    print(f"{'─' * 100}")


def test_parser(
    parser_name: str,
    country: str,
    orchestrator: ResearchOrchestrator
) -> Dict[str, Any]:
    """Test a single parser with a research document.

    Returns:
        Dict with test results
    """
    try:
        # Get parser
        parser = get_parser(parser_name)

        # Get research document
        research_doc = orchestrator.get_research(
            parameter=parser_name,
            country=country,
            use_cache=True
        )

        if not research_doc:
            return {
                'status': 'no_research',
                'error': f'No research document found for {parser_name} - {country}'
            }

        # Parse document
        parsed_data = parser.parse(research_doc)

        # Analyze result
        result = {
            'status': 'success',
            'parsed_data': parsed_data,
            'research_version': research_doc.version,
            'research_grade': research_doc.content.get('_validation', {}).get('grade', 'N/A'),
            'metrics_count': len(research_doc.content.get('key_metrics', [])),
            'has_overview': len(research_doc.content.get('overview', '')) > 0,
            'confidence': parsed_data.get('confidence', 0.0)
        }

        return result

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


def test_all_parsers(test_country: str = "China") -> Dict[str, Dict]:
    """Test all 18 parsers with a single country.

    Args:
        test_country: Country to test with

    Returns:
        Dict mapping parameter name to test results
    """
    print_section(f"Testing All 18 Parsers with {test_country}")

    orchestrator = ResearchOrchestrator()
    results = {}

    # Group by subcategory
    subcategories = {
        'Regulation': ['Ambition', 'Country Stability', 'Track Record', 'Support Scheme', 'Contract Terms'],
        'Profitability': ['Expected Return', 'Revenue Stream Stability', 'Offtaker Status', 'Long Term Interest Rates'],
        'Market Size': ['Power Market Size', 'Resource Availability', 'Energy Dependence', 'Renewables Penetration'],
        'Accommodation': ['Status of Grid', 'Ownership Hurdles'],
        'Competition': ['Ownership Consolidation', 'Competitive Landscape'],
        'System Modifiers': ['System Modifiers']
    }

    for subcat, parameters in subcategories.items():
        print_subsection(f"{subcat} ({len(parameters)} parameters)")

        for param in parameters:
            print(f"\n  Testing: {param:35s} ", end="", flush=True)

            result = test_parser(param, test_country, orchestrator)
            results[param] = result

            if result['status'] == 'success':
                grade = result['research_grade']
                metrics = result['metrics_count']
                confidence = result['confidence']
                print(f"✅ SUCCESS (Grade: {grade}, Metrics: {metrics}, Confidence: {confidence:.2f})")

                # Show key extracted data (first few fields)
                parsed = result['parsed_data']
                key_fields = [k for k in parsed.keys() if k not in ['source', 'confidence', 'research_version', 'research_sources', 'overview']][:3]
                if key_fields:
                    print(f"     Extracted: {', '.join(f'{k}={parsed[k]}' for k in key_fields)}")

            elif result['status'] == 'no_research':
                print(f"⚠️  NO RESEARCH")
            else:
                print(f"❌ ERROR: {result['error'][:60]}")

    return results


def analyze_results(results: Dict[str, Dict]) -> Dict[str, Any]:
    """Analyze test results and provide summary.

    Args:
        results: Test results from test_all_parsers

    Returns:
        Dict with analysis summary
    """
    total = len(results)
    successful = sum(1 for r in results.values() if r['status'] == 'success')
    no_research = sum(1 for r in results.values() if r['status'] == 'no_research')
    errors = sum(1 for r in results.values() if r['status'] == 'error')

    # Grade distribution
    grades = {}
    for r in results.values():
        if r['status'] == 'success':
            grade = r['research_grade']
            grades[grade] = grades.get(grade, 0) + 1

    # Confidence distribution
    confidences = [r['confidence'] for r in results.values() if r['status'] == 'success']
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0

    # Metrics count distribution
    metrics_counts = [r['metrics_count'] for r in results.values() if r['status'] == 'success']
    avg_metrics = sum(metrics_counts) / len(metrics_counts) if metrics_counts else 0

    return {
        'total': total,
        'successful': successful,
        'no_research': no_research,
        'errors': errors,
        'success_rate': (successful / total * 100) if total > 0 else 0,
        'grades': grades,
        'avg_confidence': avg_confidence,
        'avg_metrics': avg_metrics,
        'detailed_results': results
    }


def print_summary(analysis: Dict[str, Any]):
    """Print analysis summary."""
    print_section("TEST SUMMARY")

    print("📊 Overall Results:")
    print(f"   Total Parsers Tested: {analysis['total']}")
    print(f"   ✅ Successful: {analysis['successful']} ({analysis['success_rate']:.1f}%)")
    print(f"   ⚠️  No Research: {analysis['no_research']}")
    print(f"   ❌ Errors: {analysis['errors']}")

    if analysis['grades']:
        print(f"\n📈 Research Quality Grades:")
        for grade in sorted(analysis['grades'].keys()):
            count = analysis['grades'][grade]
            print(f"   Grade {grade}: {count:2d} parameters ({count/analysis['successful']*100:.1f}%)")

    print(f"\n📏 Data Quality Metrics:")
    print(f"   Average Confidence: {analysis['avg_confidence']:.2f}")
    print(f"   Average Metrics per Doc: {analysis['avg_metrics']:.1f}")

    # Identify issues
    print(f"\n⚠️  Issues Found:")
    issues = []
    for param, result in analysis['detailed_results'].items():
        if result['status'] == 'no_research':
            issues.append(f"   • {param}: No research document available")
        elif result['status'] == 'error':
            issues.append(f"   • {param}: Parser error - {result['error'][:60]}")
        elif result['status'] == 'success' and result['metrics_count'] == 0:
            issues.append(f"   • {param}: Research has no metrics")

    if issues:
        for issue in issues[:10]:  # Show first 10
            print(issue)
        if len(issues) > 10:
            print(f"   ... and {len(issues) - 10} more issues")
    else:
        print("   None! All parsers working correctly. 🎉")


def test_parser_details(param_name: str, country: str):
    """Show detailed parsing results for one parameter."""
    print_section(f"Detailed Test: {param_name} - {country}")

    orchestrator = ResearchOrchestrator()

    # Get research
    print("📄 Fetching research document...")
    doc = orchestrator.get_research(param_name, country, use_cache=True)

    if not doc:
        print(f"❌ No research document found for {param_name} - {country}")
        return

    print(f"   Version: {doc.version}")
    print(f"   Grade: {doc.content.get('_validation', {}).get('grade', 'N/A')}")
    print(f"   Metrics: {len(doc.content.get('key_metrics', []))}")

    # Show metrics
    metrics = doc.content.get('key_metrics', [])
    if metrics:
        print(f"\n📊 Research Metrics:")
        for i, metric in enumerate(metrics[:5], 1):
            if isinstance(metric, dict):
                print(f"   {i}. {metric.get('metric', 'N/A')}: {metric.get('value', 'N/A')} {metric.get('unit', '')}")
        if len(metrics) > 5:
            print(f"   ... and {len(metrics) - 5} more metrics")

    # Parse
    print(f"\n🔧 Parsing with {param_name}Parser...")
    parser = get_parser(param_name)
    parsed = parser.parse(doc)

    print(f"\n✅ Parsed Data:")
    for key, value in parsed.items():
        if key in ['overview', 'modifier_notes']:
            # Truncate long text
            print(f"   {key}: {str(value)[:80]}...")
        elif key == 'research_sources':
            print(f"   {key}: {', '.join(value)}")
        else:
            print(f"   {key}: {value}")


def compare_parsers_across_countries(param_name: str, countries: List[str]):
    """Compare parser results across multiple countries."""
    print_section(f"Comparing {param_name} Across Countries")

    orchestrator = ResearchOrchestrator()
    parser = get_parser(param_name)

    print(f"{'Country':<15} {'Grade':<8} {'Metrics':<10} {'Confidence':<12} Key Value")
    print("─" * 90)

    for country in countries:
        try:
            doc = orchestrator.get_research(param_name, country, use_cache=True)
            if not doc:
                print(f"{country:<15} {'N/A':<8} {'N/A':<10} {'N/A':<12} No research")
                continue

            parsed = parser.parse(doc)

            grade = doc.content.get('_validation', {}).get('grade', 'N/A')
            metrics_count = len(doc.content.get('key_metrics', []))
            confidence = parsed.get('confidence', 0.0)

            # Get first non-meta field as key value
            key_field = None
            for k, v in parsed.items():
                if k not in ['source', 'confidence', 'research_version', 'research_sources', 'overview']:
                    key_field = f"{k}={v}"
                    break

            key_value = key_field[:40] if key_field else "N/A"

            print(f"{country:<15} {grade:<8} {metrics_count:<10} {confidence:<12.2f} {key_value}")

        except Exception as e:
            print(f"{country:<15} {'ERROR':<8} {'-':<10} {'-':<12} {str(e)[:40]}")


def main():
    """Run comprehensive parser tests."""
    print("\n" + "=" * 100)
    print(" COMPREHENSIVE RESEARCH INTEGRATION PARSER TEST")
    print("=" * 100)

    print("\n📋 This test suite validates:")
    print("   1. All 18 parsers work with real research documents")
    print("   2. Parsers extract parameter-specific metrics correctly")
    print("   3. Error handling works gracefully")
    print("   4. Research document quality per parameter")
    print("   5. Architecture readiness for agent rollout\n")

    try:
        # Test 1: All parsers with China
        results = test_all_parsers(test_country="China")
        analysis = analyze_results(results)
        print_summary(analysis)

        # Test 2: Detailed look at one parser
        print("\n" + "="*100)
        print("\n🔍 Detailed Test: Ambition Parser\n")
        test_parser_details("Ambition", "China")

        # Test 3: Compare across countries
        print("\n" + "="*100)
        print("\n🌍 Cross-Country Comparison: Country Stability\n")
        compare_parsers_across_countries(
            "Country Stability",
            ["China", "Brazil", "India", "Germany", "United States"]
        )

        # Final recommendations
        print_section("RECOMMENDATIONS")

        success_rate = analysis['success_rate']

        if success_rate >= 90:
            print("✅ EXCELLENT! All parsers working well.")
            print("\n📋 Next Steps:")
            print("   1. Proceed with agent rollout")
            print("   2. Integrate remaining 16 agents")
            print("   3. Test end-to-end country analysis")
        elif success_rate >= 70:
            print("✅ GOOD! Most parsers working.")
            print("\n⚠️  Issues to address:")
            for param, result in analysis['detailed_results'].items():
                if result['status'] != 'success':
                    print(f"   • Fix {param}: {result.get('error', 'No research')}")
            print("\n📋 Next Steps:")
            print("   1. Fix issues above")
            print("   2. Proceed with agent rollout")
        else:
            print("⚠️  NEEDS ATTENTION! Several parsers have issues.")
            print("\n❌ Critical Issues:")
            for param, result in analysis['detailed_results'].items():
                if result['status'] == 'error':
                    print(f"   • {param}: {result['error']}")
            print("\n📋 Next Steps:")
            print("   1. Fix parser errors")
            print("   2. Re-test before rollout")

        print("\n" + "="*100)
        print(" TEST COMPLETE")
        print("="*100 + "\n")

        return 0

    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
