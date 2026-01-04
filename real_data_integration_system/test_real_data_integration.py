#!/usr/bin/env python3
"""
Real Data Integration - Comprehensive Test Suite
================================================

Tests all components before integration with your agents.

Usage:
    python test_real_data_integration.py

This will run all tests and provide a clear pass/fail report.
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any, List, Tuple


class TestResult:
    """Test result tracker."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def record_pass(self, test_name: str):
        """Record a passing test."""
        self.passed += 1
        print(f"  ✅ {test_name}")

    def record_fail(self, test_name: str, error: str):
        """Record a failing test."""
        self.failed += 1
        self.errors.append((test_name, error))
        print(f"  ❌ {test_name}")
        print(f"     Error: {error}")

    def print_summary(self):
        """Print test summary."""
        total = self.passed + self.failed
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed} ✅")
        print(f"Failed: {self.failed} ❌")

        if self.failed > 0:
            print(f"\nSuccess Rate: {(self.passed / total) * 100:.1f}%")
            print("\nFailed Tests:")
            for test_name, error in self.errors:
                print(f"  - {test_name}: {error}")
        else:
            print(f"\n🎉 ALL TESTS PASSED! 🎉")

        print("=" * 70)
        return self.failed == 0


# Global test result tracker
results = TestResult()


def test_dependencies():
    """Test 1: Check if required dependencies are installed."""
    print("\n" + "=" * 70)
    print("TEST 1: Dependencies")
    print("=" * 70)

    # Test requests
    try:
        import requests
        results.record_pass("requests library installed")
    except ImportError as e:
        results.record_fail("requests library", str(e))

    # Test pandas
    try:
        import pandas
        results.record_pass("pandas library installed")
    except ImportError as e:
        results.record_fail("pandas library", str(e))

    # Test yaml
    try:
        import yaml
        results.record_pass("yaml library installed")
    except ImportError as e:
        results.record_fail("yaml library", str(e))


def test_imports():
    """Test 2: Check if package can be imported."""
    print("\n" + "=" * 70)
    print("TEST 2: Package Imports")
    print("=" * 70)

    # Test base layer
    try:
        from src.data.base import (
            DataSourceType, DataCategory, DataFrequency, DataQuality,
            DataPoint, TimeSeries, DataRequest, DataResponse,
            DataSource, DataSourceRegistry
        )
        results.record_pass("Base layer imports")
    except Exception as e:
        results.record_fail("Base layer imports", str(e))
        return

    # Test providers
    try:
        from src.data.providers import WorldBankProvider, FileProvider
        results.record_pass("Providers imports")
    except Exception as e:
        results.record_fail("Providers imports", str(e))

    # Test services
    try:
        from src.data.services import DataService, CacheManager
        results.record_pass("Services imports")
    except Exception as e:
        results.record_fail("Services imports", str(e))

    # Test main package
    try:
        from src.data import DataService
        results.record_pass("Main package import")
    except Exception as e:
        results.record_fail("Main package import", str(e))


def test_configuration():
    """Test 3: Check if configuration file is valid."""
    print("\n" + "=" * 70)
    print("TEST 3: Configuration")
    print("=" * 70)

    try:
        import yaml

        # Check if config file exists
        config_path = 'real_data_integration_system/config/data_sources.yaml'
        if not os.path.exists(config_path):
            results.record_fail("Config file exists", f"File not found: {config_path}")
            return
        results.record_pass("Config file exists")

        # Load config
        with open(config_path) as f:
            config = yaml.safe_load(f)
        results.record_pass("Config file valid YAML")

        # Check required sections
        if 'cache' in config:
            results.record_pass("Cache configuration present")
        else:
            results.record_fail("Cache configuration", "Missing 'cache' section")

        if 'providers' in config:
            results.record_pass("Providers configuration present")
        else:
            results.record_fail("Providers configuration", "Missing 'providers' section")

    except Exception as e:
        results.record_fail("Configuration loading", str(e))


def test_data_models():
    """Test 4: Check if data models work correctly."""
    print("\n" + "=" * 70)
    print("TEST 4: Data Models")
    print("=" * 70)

    try:
        from src.data.base import DataPoint, TimeSeries, DataQuality

        # Test DataPoint creation
        point = DataPoint(
            value=100.5,
            timestamp=datetime.now(),
            country="Germany",
            indicator="gdp",
            source="test",
            quality=DataQuality.OFFICIAL
        )
        results.record_pass("DataPoint creation")

        # Test DataPoint serialization
        point_dict = point.to_dict()
        if 'value' in point_dict and 'country' in point_dict:
            results.record_pass("DataPoint serialization")
        else:
            results.record_fail("DataPoint serialization", "Missing keys in dict")

        # Test TimeSeries creation
        ts = TimeSeries(country="Germany", indicator="gdp")
        ts.add_point(point)
        results.record_pass("TimeSeries creation")

        # Test TimeSeries methods
        latest = ts.get_latest()
        if latest and latest.value == 100.5:
            results.record_pass("TimeSeries.get_latest()")
        else:
            results.record_fail("TimeSeries.get_latest()", "Incorrect value returned")

    except Exception as e:
        results.record_fail("Data models", str(e))


def test_file_provider():
    """Test 5: Check if file provider works."""
    print("\n" + "=" * 70)
    print("TEST 5: File Provider")
    print("=" * 70)

    try:
        from src.data.providers import FileProvider
        from src.data.base import DataRequest

        # Create provider
        provider = FileProvider({'data_directory': 'real_data_integration_system/data/files'})
        results.record_pass("FileProvider initialization")

        # Check if provider is available
        if provider.is_available():
            results.record_pass("FileProvider available")
        else:
            results.record_fail("FileProvider available", "Provider not available (pandas missing?)")
            return

        # Check supported indicators
        indicators = provider.get_supported_indicators()
        if len(indicators) > 0:
            results.record_pass(f"FileProvider found {len(indicators)} indicators")
        else:
            results.record_fail("FileProvider indicators", "No indicators found (no CSV files?)")

        # Check supported countries
        countries = provider.get_supported_countries()
        if len(countries) > 0:
            results.record_pass(f"FileProvider found {len(countries)} countries")
        else:
            results.record_fail("FileProvider countries", "No countries found")

        # Try to fetch data if Germany ECR data exists
        if 'ecr_rating' in indicators and 'Germany' in countries:
            request = DataRequest(country="Germany", indicator="ecr_rating")
            response = provider.fetch_data(request)

            if response.success:
                results.record_pass("FileProvider data fetch successful")
                if response.data and len(response.data.data_points) > 0:
                    results.record_pass(f"FileProvider returned {len(response.data.data_points)} data points")
                else:
                    results.record_fail("FileProvider data points", "No data points in response")
            else:
                results.record_fail("FileProvider data fetch", response.error)

    except Exception as e:
        results.record_fail("File provider", str(e))


def test_world_bank_provider():
    """Test 6: Check if World Bank provider works."""
    print("\n" + "=" * 70)
    print("TEST 6: World Bank Provider")
    print("=" * 70)

    try:
        from src.data.providers import WorldBankProvider
        from src.data.base import DataRequest

        # Create provider
        provider = WorldBankProvider()
        results.record_pass("WorldBankProvider initialization")

        # Check if provider is available (requires internet)
        if provider.is_available():
            results.record_pass("WorldBankProvider available (internet OK)")
        else:
            results.record_fail("WorldBankProvider available",
                                "Provider not available (no internet or requests library?)")
            return

        # Check supported indicators
        indicators = provider.get_supported_indicators()
        if len(indicators) > 0:
            results.record_pass(f"WorldBankProvider supports {len(indicators)} indicators")
        else:
            results.record_fail("WorldBankProvider indicators", "No indicators found")

        # Check supported countries
        countries = provider.get_supported_countries()
        if len(countries) > 0:
            results.record_pass(f"WorldBankProvider supports {len(countries)} countries")
        else:
            results.record_fail("WorldBankProvider countries", "No countries found")

        # Try to fetch data (this requires internet)
        print("  ⏳ Fetching data from World Bank API (may take 5-10 seconds)...")
        request = DataRequest(country="Germany", indicator="gdp")
        response = provider.fetch_data(request)

        if response.success:
            results.record_pass("WorldBankProvider data fetch successful")
            if response.data and len(response.data.data_points) > 0:
                results.record_pass(f"WorldBankProvider returned {len(response.data.data_points)} data points")
            else:
                results.record_fail("WorldBankProvider data points", "No data points in response")
        else:
            results.record_fail("WorldBankProvider data fetch", response.error or "Unknown error")

    except Exception as e:
        results.record_fail("World Bank provider", str(e))


def test_cache_manager():
    """Test 7: Check if cache manager works."""
    print("\n" + "=" * 70)
    print("TEST 7: Cache Manager")
    print("=" * 70)

    try:
        from src.data.services import CacheManager
        from src.data.base import DataResponse, TimeSeries, DataPoint
        from datetime import datetime

        # Create cache manager with memory strategy
        cache = CacheManager({
            'enabled': True,
            'strategy': 'memory',
            'cache_dir': './data/cache_test'
        })
        results.record_pass("CacheManager initialization")

        # Create test data
        point = DataPoint(
            value=100.0,
            timestamp=datetime.now(),
            country="TestCountry",
            indicator="test_indicator",
            source="test"
        )
        ts = TimeSeries(country="TestCountry", indicator="test_indicator")
        ts.add_point(point)

        response = DataResponse(
            data=ts,
            success=True,
            source="test"
        )

        # Test cache set
        cache.set(response, ttl=60)
        results.record_pass("CacheManager.set()")

        # Test cache get
        cached = cache.get("TestCountry", "test_indicator", "test")
        if cached and cached.success:
            results.record_pass("CacheManager.get() - cache hit")
        else:
            results.record_fail("CacheManager.get()", "Cache miss when should hit")

        # Test cache stats
        stats = cache.get_stats()
        if 'enabled' in stats and stats['enabled']:
            results.record_pass("CacheManager.get_stats()")
        else:
            results.record_fail("CacheManager.get_stats()", "Invalid stats returned")

        # Test cache clear
        cache.clear()
        results.record_pass("CacheManager.clear()")

    except Exception as e:
        results.record_fail("Cache manager", str(e))


def test_data_service():
    """Test 8: Check if data service works."""
    print("\n" + "=" * 70)
    print("TEST 8: Data Service")
    print("=" * 70)

    try:
        import yaml
        from src.data import DataService

        # Load config
        with open('real_data_integration_system/config/data_sources.yaml') as f:
            config = yaml.safe_load(f)

        # Create data service
        data_service = DataService(config)
        results.record_pass("DataService initialization")

        # Test get_status
        status = data_service.get_status()
        if 'providers' in status:
            results.record_pass("DataService.get_status()")
        else:
            results.record_fail("DataService.get_status()", "Invalid status returned")

        # Test get_available_indicators
        indicators = data_service.get_available_indicators()
        if len(indicators) > 0:
            results.record_pass(f"DataService found {len(indicators)} available indicators")
        else:
            results.record_fail("DataService indicators", "No indicators available")

        # Test get_available_countries
        countries = data_service.get_available_countries()
        if len(countries) > 0:
            results.record_pass(f"DataService found {len(countries)} available countries")
        else:
            results.record_fail("DataService countries", "No countries available")

        # Test get_value (from file if available)
        value = data_service.get_value("Germany", "ecr", default=None)
        if value is not None:
            results.record_pass(f"DataService.get_value() returned {value}")
        else:
            results.record_fail("DataService.get_value()", "No value returned (check if sample data exists)")

        # Test get_data
        response = data_service.get_data("Germany", "ecr")
        if response.success:
            results.record_pass("DataService.get_data() successful")
        else:
            results.record_fail("DataService.get_data()", response.error or "Unknown error")

    except Exception as e:
        results.record_fail("Data service", str(e))


def test_agent_integration():
    """Test 9: Check if system works with a mock agent."""
    print("\n" + "=" * 70)
    print("TEST 9: Agent Integration (Mock)")
    print("=" * 70)

    try:
        import yaml
        from src.data import DataService
        from datetime import datetime

        # Load config
        with open('real_data_integration_system/config/data_sources.yaml') as f:
            config = yaml.safe_load(f)

        # Create data service
        data_service = DataService(config)

        # Create a mock agent
        class MockAgent:
            def __init__(self, data_service):
                self.data_service = data_service

            def fetch_data(self, country, indicator):
                """Simulate agent fetching data."""
                value = self.data_service.get_value(country, indicator, default=0.0)
                return {"value": value, "timestamp": datetime.now()}

        agent = MockAgent(data_service)
        results.record_pass("Mock agent created with data_service")

        # Test agent fetching data
        data = agent.fetch_data("Germany", "ecr")
        if data and 'value' in data:
            results.record_pass(f"Mock agent fetched data: {data['value']}")
        else:
            results.record_fail("Mock agent data fetch", "No data returned")

    except Exception as e:
        results.record_fail("Agent integration", str(e))


def test_error_handling():
    """Test 10: Check if error handling works correctly."""
    print("\n" + "=" * 70)
    print("TEST 10: Error Handling")
    print("=" * 70)

    try:
        import yaml
        from src.data import DataService

        # Load config
        with open('real_data_integration_system/config/data_sources.yaml') as f:
            config = yaml.safe_load(f)

        data_service = DataService(config)

        # Test with invalid country
        response = data_service.get_data("InvalidCountry123", "gdp")
        if not response.success:
            results.record_pass("Handles invalid country gracefully")
        else:
            results.record_fail("Error handling", "Should fail with invalid country")

        # Test with invalid indicator
        response = data_service.get_data("Germany", "invalid_indicator_xyz")
        if not response.success:
            results.record_pass("Handles invalid indicator gracefully")
        else:
            results.record_fail("Error handling", "Should fail with invalid indicator")

        # Test get_value with default
        value = data_service.get_value("InvalidCountry", "invalid", default=99.9)
        if value == 99.9:
            results.record_pass("Returns default value when data not found")
        else:
            results.record_fail("Default value", f"Expected 99.9, got {value}")

    except Exception as e:
        results.record_fail("Error handling", str(e))


def main():
    """Run all tests."""
    print("=" * 70)
    print("REAL DATA INTEGRATION - TEST SUITE")
    print("=" * 70)
    print("Testing all components before integration...")
    print()

    # Run all tests
    test_dependencies()
    test_imports()
    test_configuration()
    test_data_models()
    test_file_provider()
    test_world_bank_provider()
    test_cache_manager()
    test_data_service()
    test_agent_integration()
    test_error_handling()

    # Print summary
    success = results.print_summary()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
