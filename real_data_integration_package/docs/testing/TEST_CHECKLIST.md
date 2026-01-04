# Pre-Integration Testing Checklist

Use this checklist to verify the system before integrating with your agents.

## Setup Phase

### 1. Package Extraction
```bash
tar -xzf real_data_integration_v1.0.0.tar.gz
cd real_data_integration_package/
```
- [ ] Package extracted successfully
- [ ] Directory structure looks correct
- [ ] All files present (check MANIFEST.txt)

### 2. Dependencies Installation
```bash
pip install -r data_requirements.txt
```
- [ ] `requests` installed
- [ ] `pandas` installed
- [ ] `pyyaml` installed
- [ ] No installation errors

### 3. File Verification
```bash
# Check source files
ls src/data/base/
ls src/data/providers/
ls src/data/services/

# Check config
ls config/data_sources.yaml

# Check sample data
ls data/files/
```
- [ ] Base layer files present (5 files)
- [ ] Provider files present (3 files)
- [ ] Service files present (3 files)
- [ ] Config file exists
- [ ] Sample CSV files exist

## Testing Phase

### 4. Run Full Test Suite
```bash
python test_real_data_integration.py
```

Expected: **32 tests, all passing ✅**

### 5. Test Results Review

#### Critical Tests (Must Pass)
- [ ] Test 1: Dependencies - All 3 packages ✅
- [ ] Test 2: Package Imports - All imports work ✅
- [ ] Test 3: Configuration - Config valid ✅
- [ ] Test 4: Data Models - Models work ✅
- [ ] Test 8: Data Service - Service works ✅

#### Data Source Tests (At Least One Must Pass)
- [ ] Test 5: File Provider ✅ OR
- [ ] Test 6: World Bank Provider ✅

#### Optional Tests (Nice to Have)
- [ ] Test 7: Cache Manager ✅
- [ ] Test 9: Agent Integration ✅
- [ ] Test 10: Error Handling ✅

### 6. Manual Verification Tests

#### Test A: Import Check
```python
python -c "from src.data import DataService; print('✅ Import OK')"
```
- [ ] No import errors

#### Test B: Config Load Check
```python
python -c "import yaml; yaml.safe_load(open('config/data_sources.yaml')); print('✅ Config OK')"
```
- [ ] Config loads successfully

#### Test C: Quick Data Fetch
```python
python -c "
import yaml
from src.data import DataService
with open('config/data_sources.yaml') as f:
    config = yaml.safe_load(f)
ds = DataService(config)
value = ds.get_value('Germany', 'ecr_rating')
print(f'✅ Fetched value: {value}')
"
```
- [ ] Data fetched successfully

## Scenario-Specific Checks

### If You Have Internet Connection
- [ ] Test 6 (World Bank) passes
- [ ] Can fetch GDP data
- [ ] API response time acceptable (<10s)

### If You're Offline
- [ ] Test 5 (File Provider) passes
- [ ] Can read local CSV files
- [ ] File provider finds indicators

### If You Have Sample Data Files
- [ ] Test 5 shows indicators found
- [ ] Can fetch data from files
- [ ] Data points returned correctly

## Performance Checks

### Test Execution Speed
- [ ] Total test time < 30 seconds
- [ ] No individual test hangs
- [ ] World Bank test completes in <15s

### Cache Performance
- [ ] Cache operations fast (<1ms)
- [ ] Cache directory created
- [ ] No permission errors

## Common Issues Checklist

### Issue: Import Errors
- [ ] Check you're in correct directory
- [ ] Verify `src/data/` exists
- [ ] Check `__init__.py` files present

### Issue: No CSV Files Found
- [ ] Check `data/files/` exists
- [ ] Verify CSV files present
- [ ] Check file naming: `{indicator}_{country}.csv`

### Issue: World Bank Fails
- [ ] Check internet connection
- [ ] Try accessing https://api.worldbank.org directly
- [ ] Check firewall settings

### Issue: Permission Errors
- [ ] Check directory permissions
- [ ] Verify cache directory writable
- [ ] Check Python has write access

## Pre-Integration Validation

### Before Moving to Integration
- [ ] All critical tests pass
- [ ] At least one data source works
- [ ] No blocking errors
- [ ] Performance acceptable
- [ ] Error handling works

### Documentation Review
- [ ] Read REAL_DATA_SUMMARY.md
- [ ] Understand architecture
- [ ] Review integration guide
- [ ] Know how to use DataService

### Ready for Integration?
Answer these questions:
1. Can you import the package? **Yes/No**
2. Can you fetch data? **Yes/No**
3. Do you understand how agents will use it? **Yes/No**
4. Have you reviewed the docs? **Yes/No**

**If all answers are YES**: ✅ Ready to integrate!
**If any answer is NO**: Review relevant documentation

## Post-Integration Testing

### After Adding to First Agent
```python
# Test agent with MOCK mode
agent = MyAgent(mode=AgentMode.MOCK)
result = agent.analyze("Germany", "Q1 2024")
# Should work unchanged

# Test agent with REAL mode
agent = MyAgent(mode=AgentMode.REAL, data_service=data_service)
result = agent.analyze("Germany", "Q1 2024")
# Should fetch real data
```
- [ ] MOCK mode still works
- [ ] REAL mode fetches data
- [ ] No errors or crashes

### After Full Integration
- [ ] All 18 agents work in MOCK mode
- [ ] All 18 agents work in REAL mode
- [ ] Data fetching works for all
- [ ] Performance acceptable
- [ ] No memory leaks

## Troubleshooting Reference

### Quick Fixes

**"ModuleNotFoundError: No module named 'src'"**
```bash
# Check you're in the right directory
pwd
ls src/data/
```

**"FileNotFoundError: config/data_sources.yaml"**
```bash
# Check config file exists
ls config/data_sources.yaml
# If not, copy it
cp config/data_sources.yaml /your/project/config/
```

**"ImportError: No module named 'requests'"**
```bash
pip install requests
```

**"ImportError: No module named 'pandas'"**
```bash
pip install pandas
```

### Re-run Tests After Fixes
```bash
python test_real_data_integration.py
```

## Success Metrics

### Minimum Success
- ✅ 25+ tests passing (out of 32)
- ✅ All critical tests pass
- ✅ At least one data source works

### Ideal Success
- ✅ All 32 tests passing
- ✅ Both data sources work
- ✅ Performance good
- ✅ No warnings

### Production Ready
- ✅ All tests pass
- ✅ Performance benchmarks met
- ✅ Error handling verified
- ✅ Documentation reviewed
- ✅ Integration plan ready

## Timeline

### Testing Phase: 15-35 minutes
- Extract package: 2 min
- Install dependencies: 3 min
- Run tests: 1 min
- Review results: 5 min
- Fix any issues: 10-20 min
- Re-test: 1 min

### Integration Phase: 1-2 days
- First agent: 30 min
- Next 5 agents: 2 hours
- Remaining 12 agents: 4 hours
- Testing & validation: 3 hours

## Checklist Complete?

Go through each section:
- [ ] Setup Phase complete
- [ ] Testing Phase complete
- [ ] Scenario checks done
- [ ] Performance verified
- [ ] Common issues reviewed
- [ ] Ready for integration

**When all checked**: You're ready to integrate! 🚀

---

**Remember**: Testing before integration saves time and prevents issues!
