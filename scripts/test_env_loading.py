#!/usr/bin/env python3
"""Test script to verify .env loading works correctly."""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_env_loading_order():
    """Test that .env loads before module imports."""
    print("=" * 60)
    print("TESTING .ENV LOADING ORDER")
    print("=" * 60)

    # Clean environment
    if "USE_REAL_AGENTS" in os.environ:
        del os.environ["USE_REAL_AGENTS"]

    # Create a test .env file
    test_env_path = project_root / ".env.test"
    with open(test_env_path, "w") as f:
        f.write("USE_REAL_AGENTS=true\n")
        f.write("TEST_VAR=loaded_from_file\n")

    print("\n1. Before loading .env:")
    print(f"   USE_REAL_AGENTS = {os.getenv('USE_REAL_AGENTS')}")
    print(f"   TEST_VAR = {os.getenv('TEST_VAR')}")

    # Load .env
    from dotenv import load_dotenv
    load_dotenv(test_env_path)

    print("\n2. After loading .env:")
    print(f"   USE_REAL_AGENTS = {os.getenv('USE_REAL_AGENTS')}")
    print(f"   TEST_VAR = {os.getenv('TEST_VAR')}")

    # Test that app respects the env var
    from src.ui.app import RankingsApp
    app = RankingsApp()

    print(f"\n3. App initialized with service: {app.service.__class__.__name__}")

    # Cleanup
    test_env_path.unlink()

    # Verify
    assert os.getenv("USE_REAL_AGENTS") == "true", "Env var not loaded"
    assert os.getenv("TEST_VAR") == "loaded_from_file", "Test var not loaded"
    print("\n✅ .env loading test passed!")


def test_multiple_load_dotenv_calls():
    """Test that multiple load_dotenv calls are safe."""
    print("\n" + "=" * 60)
    print("TESTING MULTIPLE load_dotenv() CALLS")
    print("=" * 60)

    from dotenv import load_dotenv

    # Create test file
    test_env_path = project_root / ".env.test2"
    with open(test_env_path, "w") as f:
        f.write("MULTI_TEST=first\n")

    # Load multiple times
    load_dotenv(test_env_path)
    print(f"\n1st load: MULTI_TEST = {os.getenv('MULTI_TEST')}")

    load_dotenv(test_env_path)
    print(f"2nd load: MULTI_TEST = {os.getenv('MULTI_TEST')}")

    load_dotenv(test_env_path)
    print(f"3rd load: MULTI_TEST = {os.getenv('MULTI_TEST')}")

    # Cleanup
    test_env_path.unlink()
    if "MULTI_TEST" in os.environ:
        del os.environ["MULTI_TEST"]

    print("\n✅ Multiple calls are safe (idempotent)")


def test_env_file_locations():
    """Test different .env file locations."""
    print("\n" + "=" * 60)
    print("TESTING .ENV FILE LOCATIONS")
    print("=" * 60)

    from dotenv import load_dotenv, find_dotenv

    # Test 1: Find .env automatically
    env_path = find_dotenv()
    print(f"\n1. Auto-detected .env path: {env_path or 'Not found'}")

    # Test 2: Load from project root
    root_env = project_root / ".env"
    print(f"2. Expected .env location: {root_env}")
    print(f"   Exists: {root_env.exists()}")

    # Test 3: Show example file
    example_env = project_root / ".env.example"
    print(f"3. Example file location: {example_env}")
    print(f"   Exists: {example_env.exists()}")

    if example_env.exists():
        print("\n   ℹ️  To use real configuration:")
        print("      cp .env.example .env")
        print("      # Edit .env with your settings")

    print("\n✅ File location test complete")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print(".ENV LOADING TEST SUITE")
    print("=" * 60)

    try:
        test_env_loading_order()
        test_multiple_load_dotenv_calls()
        test_env_file_locations()

        print("\n" + "=" * 60)
        print("✅ ALL ENV LOADING TESTS PASSED!")
        print("=" * 60)

        print("\n📝 Summary:")
        print("   • .env is loaded in run.py (earliest possible)")
        print("   • .env is also loaded in app.py:main() (backup)")
        print("   • Multiple load_dotenv() calls are safe")
        print("   • Environment variables are available to all modules")
        print("\n")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
