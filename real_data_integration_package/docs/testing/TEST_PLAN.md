# Real Data Integration - Test Plan

## Overview

This test plan allows you to **verify the entire system works correctly** before integrating with your 18 agents. Testing first is best practice and will save time debugging later.

## Test Suite

The test suite (`test_real_data_integration.py`) runs **10 comprehensive tests** covering all components.

### Test 1: Dependencies ✅
**What it tests**: Required Python packages are installed
- `requests` - For API calls
- `pandas` - For file processing
- `yaml` - For configuration

**Expected result**: All 3 packages installed

**If it fails**:
```bash
pip install requests pandas pyyaml
```

---

### Test 2: Package Imports ✅
**What it tests**: All code can be imported correctly
- Base layer (data types, models, interfaces)
- Provider layer (World Bank, File providers)
- Services layer (DataService, CacheManager)

**Expected result**: All imports successful

**If it fails**: Check that you extracted the package correctly to `src/data/`

---

### Test 3: Configuration ✅
**What it tests**: Configuration file is valid
- File exists at `config/data_sources.yaml`
- YAML syntax is correct
- Required sections present (cache, providers)

**Expected result**: Configuration loaded successfully

**If it fails**: Verify `config/data_sources.yaml` exists and has valid YAML syntax

---

### Test 4: Data Models ✅
**What it tests**: Core data structures work correctly
- `DataPoint` creation and serialization
- `TimeSeries` creation and methods
- Data quality enums

**Expected result**: All model operations succeed

**If it fails**: This indicates a code issue - check error message

---

### Test 5: File Provider ✅
**What it tests**: CSV/Excel file reading
- Provider initializes correctly
- Finds CSV files in `data/files/`
- Can read and parse CSV data
- Returns data points correctly

**Expected result**: 
- Provider available (if pandas installed)
- Finds indicators (if CSV files exist)
- Can fetch data from files

**If it fails**:
- Check `pandas` is installed
- Verify CSV files exist in `data/files/`
- Check CSV format (columns: date, value)

---

### Test 6: World Bank Provider ✅
**What it tests**: World Bank API integration
- Provider initializes correctly
- Internet connection available
- Can fetch real data from API
- Parses response correctly

**Expected result**: 
- Provider available (requires internet)
- Successfully fetches GDP data for Germany

**If it fails**:
- Check internet connection
- Verify firewall allows HTTPS to api.worldbank.org
- Check `requests` library is installed
- World Bank API might be temporarily down (rare)

**Note**: This test takes 5-10 seconds due to API call

---

### Test 7: Cache Manager ✅
**What it tests**: Caching system
- Cache initialization
- Storing data in cache
- Retrieving cached data
- Cache statistics
- Cache clearing

**Expected result**: All cache operations work

**If it fails**: Check disk permissions for cache directory

---

### Test 8: Data Service ✅
**What it tests**: Main orchestration layer
- Service initialization
- Provider discovery
- Available indicators/countries
- Data fetching
- Cache integration

**Expected result**: 
- Service initializes
- Finds available data sources
- Can fetch data

**If it fails**: Check previous tests - this depends on all components

---

### Test 9: Agent Integration ✅
**What it tests**: How agents will use the system
- Mock agent creation
- Agent fetching data via DataService
- Data returned to agent correctly

**Expected result**: Mock agent successfully fetches data

**If it fails**: This indicates integration issues - check error message

---

### Test 10: Error Handling ✅
**What it tests**: System handles errors gracefully
- Invalid country names
- Invalid indicators
- Default values work
- No crashes on bad input

**Expected result**: System handles errors without crashing

**If it fails**: This indicates robustness issues - check error message

---

## Running the Tests

### Prerequisites
1. Extract the package:
```bash
tar -xzf real_data_integration_v1.0.0.tar.gz
cd real_data_integration_package/
```

2. Copy to your project (or test in package directory):
```bash
# Option 1: Test in package directory
cp ../test_real_data_integration.py .

# Option 2: Copy package to project and test there
cp -r src/data/ /path/to/project/src/
cp config/data_sources.yaml /path/to/project/config/
cp -r data/files/ /path/to/project/data/
cp ../test_real_data_integration.py /path/to/project/
```

3. Install dependencies:
```bash
pip install -r data_requirements.txt
```

### Running All Tests
```bash
python test_real_data_integration.py
```

### Expected Output
```
======================================================================
REAL DATA INTEGRATION - TEST SUITE
======================================================================
Testing all components before integration...

======================================================================
TEST 1: Dependencies
======================================================================
  ✅ requests library installed
  ✅ pandas library installed
  ✅ yaml library installed

======================================================================
TEST 2: Package Imports
======================================================================
  ✅ Base layer imports
  ✅ Providers imports
  ✅ Services imports
  ✅ Main package import

[... more tests ...]

======================================================================
TEST SUMMARY
======================================================================
Total Tests: 32
Passed: 32 ✅
Failed: 0 ❌

🎉 ALL TESTS PASSED! 🎉
======================================================================
```

## Interpreting Results

### All Tests Pass ✅
**Great!** The system is working correctly. You can proceed with confidence to integrate with your agents.

### Some Tests Fail ❌
**Don't panic!** The test suite is designed to help you identify exactly what's wrong.

1. **Read the error message** - It will tell you what failed
2. **Check the "If it fails" section** for that test
3. **Fix the issue** and re-run tests
4. **Repeat** until all tests pass

### Common Issues

#### Issue: "No module named 'requests'"
**Solution**:
```bash
pip install requests
```

#### Issue: "FileProvider not available"
**Solution**:
```bash
pip install pandas
```

#### Issue: "No CSV files found"
**Solution**:
```bash
# Check if sample files exist
ls data/files/

# If not, copy sample files
cp data/files/*.csv /your/project/data/files/
```

#### Issue: "WorldBankProvider not available"
**Possible causes**:
1. No internet connection
2. Firewall blocking HTTPS
3. World Bank API temporarily down

**Solution**: Check internet, try again later, or skip World Bank tests for now

#### Issue: "Config file not found"
**Solution**:
```bash
# Check if config exists
ls config/data_sources.yaml

# If not, copy it
cp config/data_sources.yaml /your/project/config/
```

## Test Scenarios

### Scenario 1: Offline Testing
If you don't have internet or can't access World Bank API:
- Tests 1-5, 7-10 will pass
- Test 6 (World Bank) will fail
- **This is OK** - File provider still works

### Scenario 2: No Sample Data
If you haven't added CSV files yet:
- Tests 1-4, 6-10 will pass
- Test 5 (File provider) might show 0 files
- **This is OK** - World Bank API still works

### Scenario 3: Minimal Dependencies
If you only installed `requests` (not `pandas`):
- Tests 1-4, 6-10 will pass
- Test 5 (File provider) will fail
- **This is OK** - World Bank API still works

## After Tests Pass

Once all tests pass (or you've confirmed expected failures are OK):

1. **Review test output** - Understand what's working
2. **Note any warnings** - Address if needed
3. **Proceed with integration** - Follow the integration guide
4. **Keep test script** - Use it to verify after integration

## Performance Benchmarks

Expected test execution times:
- Tests 1-5: <1 second each
- Test 6: 5-10 seconds (World Bank API call)
- Tests 7-10: <1 second each
- **Total**: ~15-20 seconds

If tests take much longer:
- Network might be slow
- API might be slow
- Cache directory might have permission issues

## Continuous Testing

### During Integration
Run tests after each change:
```bash
# Made changes to configuration?
python test_real_data_integration.py

# Added new CSV files?
python test_real_data_integration.py

# Modified agents?
python test_real_data_integration.py
```

### Before Production
Always run full test suite:
```bash
python test_real_data_integration.py
```

## Test Data Files

The test suite expects these sample files (included in package):
```
data/files/
├── ecr_rating_Germany.csv
└── ecr_rating_USA.csv
```

Format:
```csv
date,value,quality,unit
2024-12-31,0.8,official,rating
2023-12-31,0.9,official,rating
```

## Advanced Testing

### Test Specific Components Only

Edit `test_real_data_integration.py` and comment out tests you don't want:
```python
def main():
    # Run only tests you want
    test_dependencies()
    test_imports()
    # test_world_bank_provider()  # Skip this one
    test_data_service()
```

### Add Custom Tests

Add your own tests at the end of the file:
```python
def test_my_custom_data():
    """Test my custom data file."""
    print("\nTEST 11: My Custom Data")
    try:
        from src.data import DataService
        ds = DataService({})
        value = ds.get_value("MyCountry", "my_indicator")
        if value:
            results.record_pass("My custom data found")
        else:
            results.record_fail("My custom data", "Not found")
    except Exception as e:
        results.record_fail("My custom data", str(e))
```

## Troubleshooting Test Failures

### Test fails with "ModuleNotFoundError"
**Cause**: Python can't find the package
**Solution**: 
- Ensure you're running from the correct directory
- Check `src/data/` exists
- Verify `__init__.py` files are present

### Test fails with "FileNotFoundError"
**Cause**: Expected files are missing
**Solution**:
- Check file paths in error message
- Ensure you extracted full package
- Verify working directory is correct

### Test fails with "ConnectionError"
**Cause**: Network issue
**Solution**:
- Check internet connection
- Verify firewall settings
- Try again later

### All tests fail
**Cause**: Major issue with setup
**Solution**:
- Re-extract package from tar.gz
- Re-install dependencies
- Check Python version (need 3.8+)
- Review extraction guide

## Success Criteria

### Minimum for Production
These tests MUST pass:
- ✅ Test 1: Dependencies
- ✅ Test 2: Package Imports
- ✅ Test 3: Configuration
- ✅ Test 4: Data Models
- ✅ Test 8: Data Service

At least ONE of these MUST pass:
- ✅ Test 5: File Provider OR
- ✅ Test 6: World Bank Provider

### Recommended for Production
All tests should pass for best experience.

## Getting Help

If tests fail and you can't resolve:
1. Check error message carefully
2. Review "If it fails" section for that test
3. Check "Common Issues" section
4. Review package documentation
5. Ensure prerequisites are met

## Summary

**Why test first?**
- ✅ Identify issues before integration
- ✅ Verify system works correctly
- ✅ Build confidence
- ✅ Save debugging time later

**How long does it take?**
- Running tests: 15-20 seconds
- Reviewing output: 5 minutes
- Fixing issues: 10-30 minutes (if any)
- **Total**: 15-35 minutes

**What do I get?**
- ✅ Confidence system works
- ✅ Clear error identification
- ✅ Validation before integration
- ✅ Peace of mind

**Next steps after testing:**
1. ✅ All tests pass
2. ✅ Review integration guide
3. ✅ Start with 1-2 agents
4. ✅ Full rollout

---

**Test first, integrate with confidence!** 🧪✅
