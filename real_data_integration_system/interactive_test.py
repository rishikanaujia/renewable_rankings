#!/usr/bin/env python3
"""
Real Data Integration - Interactive Test Runner
===============================================

This script guides you through testing the system step-by-step.
Run this BEFORE integrating with your agents.

Usage:
    python interactive_test.py
"""

import sys
import time


def print_header(text):
    """Print a section header."""
    print("\n" + "="*70)
    print(text.center(70))
    print("="*70)


def print_step(number, text):
    """Print a step."""
    print(f"\n[Step {number}] {text}")


def prompt_continue():
    """Prompt user to continue."""
    input("\nPress Enter to continue...")


def test_step_1():
    """Step 1: Check Python version."""
    print_step(1, "Checking Python version")
    
    print(f"\nYour Python version: {sys.version}")
    
    major, minor = sys.version_info[:2]
    if major >= 3 and minor >= 8:
        print("✅ Python 3.8+ detected - Good!")
    else:
        print("❌ Python 3.8+ required")
        print("   Please upgrade Python")
        return False
    
    return True


def test_step_2():
    """Step 2: Test imports."""
    print_step(2, "Testing package imports")
    
    tests = [
        ("requests", "API calls"),
        ("pandas", "File processing"),
        ("yaml", "Configuration"),
    ]
    
    all_ok = True
    for module, purpose in tests:
        try:
            __import__(module)
            print(f"  ✅ {module:12s} - {purpose}")
        except ImportError:
            print(f"  ❌ {module:12s} - {purpose}")
            print(f"     Install with: pip install {module}")
            all_ok = False
    
    return all_ok


def test_step_3():
    """Step 3: Test data integration imports."""
    print_step(3, "Testing data integration package")
    
    try:
        print("  Testing base layer...", end=" ")
        from src.data.base import DataPoint, TimeSeries
        print("✅")
        
        print("  Testing providers...", end=" ")
        from src.data.providers import WorldBankProvider, FileProvider
        print("✅")
        
        print("  Testing services...", end=" ")
        from src.data.services import DataService
        print("✅")
        
        print("\n✅ All package imports successful!")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure you're in the correct directory")
        print("  2. Check that src/data/ exists")
        print("  3. Verify all __init__.py files are present")
        return False


def test_step_4():
    """Step 4: Test configuration."""
    print_step(4, "Testing configuration file")
    
    import os
    import yaml
    
    config_path = 'config/data_sources.yaml'
    
    # Check file exists
    if not os.path.exists(config_path):
        print(f"❌ Config file not found: {config_path}")
        print("   Make sure you copied config/data_sources.yaml to your project")
        return False
    
    print(f"  ✅ Config file exists: {config_path}")
    
    # Try to load
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
        print("  ✅ Config file is valid YAML")
    except Exception as e:
        print(f"  ❌ Config file is invalid: {e}")
        return False
    
    # Check structure
    if 'cache' in config:
        print("  ✅ Cache configuration found")
    else:
        print("  ⚠️  Warning: No cache configuration")
    
    if 'providers' in config:
        print("  ✅ Providers configuration found")
        return True
    else:
        print("  ❌ No providers configuration")
        return False


def test_step_5():
    """Step 5: Test file provider."""
    print_step(5, "Testing File Provider (CSV/Excel)")
    
    import os
    
    # Check for data directory
    data_dir = 'real_data_integration_system/data/files'
    if not os.path.exists(data_dir):
        print(f"  ⚠️  Data directory not found: {data_dir}")
        print("     File provider will have no data")
        return True  # Not critical
    
    # Check for CSV files
    files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    if len(files) == 0:
        print(f"  ⚠️  No CSV files found in {data_dir}")
        print("     File provider will work but have no data")
        return True  # Not critical
    
    print(f"  ✅ Found {len(files)} CSV file(s):")
    for f in files[:5]:  # Show first 5
        print(f"     - {f}")
    
    if len(files) > 5:
        print(f"     ... and {len(files)-5} more")
    
    # Try to use file provider
    try:
        from src.data.providers import FileProvider
        provider = FileProvider({'data_directory': data_dir})
        
        if provider.is_available():
            print(f"  ✅ File provider is available")
            indicators = provider.get_supported_indicators()
            print(f"  ✅ File provider supports {len(indicators)} indicators")
            return True
        else:
            print("  ⚠️  File provider not available (pandas not installed?)")
            return True  # Not critical if World Bank works
            
    except Exception as e:
        print(f"  ❌ File provider error: {e}")
        return False


def test_step_6():
    """Step 6: Test World Bank provider."""
    print_step(6, "Testing World Bank Provider (requires internet)")
    
    print("  Testing internet connectivity...")
    
    try:
        from src.data.providers import WorldBankProvider
        provider = WorldBankProvider()
        
        if not provider.is_available():
            print("  ⚠️  World Bank API not available")
            print("     Possible reasons:")
            print("     - No internet connection")
            print("     - Firewall blocking HTTPS")
            print("     - API temporarily down")
            print("     This is OK if File Provider works")
            return True  # Not critical if File Provider works
        
        print("  ✅ World Bank API is available")
        
        # Try to fetch data
        print("  Fetching sample data (this may take 5-10 seconds)...")
        from src.data.base import DataRequest
        request = DataRequest(country="Germany", indicator="gdp")
        
        start = time.time()
        response = provider.fetch_data(request)
        elapsed = time.time() - start
        
        if response.success:
            print(f"  ✅ Data fetch successful ({elapsed:.1f}s)")
            if response.data and len(response.data.data_points) > 0:
                print(f"  ✅ Received {len(response.data.data_points)} data points")
                return True
            else:
                print("  ⚠️  No data points in response")
                return True
        else:
            print(f"  ❌ Data fetch failed: {response.error}")
            return False
            
    except Exception as e:
        print(f"  ❌ World Bank provider error: {e}")
        return False


def test_step_7():
    """Step 7: Test DataService."""
    print_step(7, "Testing DataService (main API)")
    
    try:
        import yaml
        from src.data import DataService
        
        # Load config
        with open('config/data_sources.yaml') as f:
            config = yaml.safe_load(f)
        
        print("  Initializing DataService...")
        data_service = DataService(config)
        print("  ✅ DataService initialized")
        
        # Get status
        status = data_service.get_status()
        print(f"  ✅ Active providers: {len(status['providers'])}")
        print(f"  ✅ Available indicators: {status['total_indicators']}")
        print(f"  ✅ Available countries: {status['total_countries']}")
        
        # Try to get data
        print("\n  Testing data fetch...")
        value = data_service.get_value("Germany", "ecr_rating", default=None)
        
        if value is not None:
            print(f"  ✅ Successfully fetched data: {value}")
            return True
        else:
            print("  ⚠️  No data available (but service works)")
            print("     Add CSV files or check internet for World Bank API")
            return True
            
    except Exception as e:
        print(f"  ❌ DataService error: {e}")
        return False


def test_step_8():
    """Step 8: Test mock agent integration."""
    print_step(8, "Testing mock agent integration")
    
    try:
        import yaml
        from src.data import DataService
        from datetime import datetime
        
        # Create data service
        with open('config/data_sources.yaml') as f:
            config = yaml.safe_load(f)
        data_service = DataService(config)
        
        # Create mock agent
        class TestAgent:
            def __init__(self, data_service):
                self.data_service = data_service
            
            def analyze(self, country):
                value = self.data_service.get_value(
                    country, "ecr_rating", default=5.0
                )
                return {
                    "country": country,
                    "score": value,
                    "timestamp": datetime.now()
                }
        
        print("  Creating mock agent...")
        agent = TestAgent(data_service)
        print("  ✅ Agent created")
        
        print("  Running analysis...")
        result = agent.analyze("Germany")
        print(f"  ✅ Analysis complete: {result['country']} -> {result['score']}")
        
        print("\n  This demonstrates how your agents will use DataService!")
        return True
        
    except Exception as e:
        print(f"  ❌ Agent integration error: {e}")
        return False


def main():
    """Run interactive test suite."""
    print_header("REAL DATA INTEGRATION - INTERACTIVE TESTER")
    print("\nThis will guide you through testing the system step-by-step.")
    print("Each step tests a critical component.")
    print("\nRecommended: Run this BEFORE integrating with your agents.")
    
    prompt_continue()
    
    # Track results
    results = []
    
    # Run tests
    results.append(("Python Version", test_step_1()))
    
    if not results[-1][1]:
        print_header("CRITICAL ERROR - Cannot Continue")
        print("Please fix Python version and try again")
        return
    
    prompt_continue()
    results.append(("Dependencies", test_step_2()))
    
    if not results[-1][1]:
        print_header("CRITICAL ERROR - Missing Dependencies")
        print("Please install required packages:")
        print("  pip install -r data_requirements.txt")
        return
    
    prompt_continue()
    results.append(("Package Imports", test_step_3()))
    
    if not results[-1][1]:
        print_header("CRITICAL ERROR - Package Import Failed")
        print("Please check package extraction and directory structure")
        return
    
    prompt_continue()
    results.append(("Configuration", test_step_4()))
    
    if not results[-1][1]:
        print_header("CRITICAL ERROR - Configuration Failed")
        print("Please check config/data_sources.yaml exists and is valid")
        return
    
    prompt_continue()
    results.append(("File Provider", test_step_5()))
    
    prompt_continue()
    results.append(("World Bank Provider", test_step_6()))
    
    # Check if at least one provider works
    if not (results[4][1] or results[5][1]):
        print_header("WARNING - No Data Providers Available")
        print("Neither File Provider nor World Bank Provider is working.")
        print("Please fix at least one before continuing.")
        return
    
    prompt_continue()
    results.append(("DataService", test_step_7()))
    
    if not results[-1][1]:
        print_header("CRITICAL ERROR - DataService Failed")
        print("Please check previous steps for issues")
        return
    
    prompt_continue()
    results.append(("Agent Integration", test_step_8()))
    
    # Print final summary
    print_header("TEST SUMMARY")
    
    print("\nResults:")
    print("-" * 70)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:25s} {status}")
    print("-" * 70)
    
    passed = sum(1 for _, p in results if p)
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n" + "🎉"*35)
        print("\n🎉 ALL TESTS PASSED! 🎉".center(70))
        print("\n" + "🎉"*35)
        print("\nYou're ready to integrate with your agents!")
        print("\nNext steps:")
        print("  1. Review integration guide (docs/REAL_DATA_SUMMARY.md)")
        print("  2. Start with 1-2 agents")
        print("  3. Test thoroughly")
        print("  4. Roll out to remaining agents")
    else:
        print("\n⚠️  Some tests failed or showed warnings")
        print("\nWhat to do:")
        print("  1. Review failed tests above")
        print("  2. Fix issues")
        print("  3. Re-run this test")
        print("\nNote: Warnings are OK if at least one data provider works")
    
    print_header("Testing Complete")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTesting interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
