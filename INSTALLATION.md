# Installation Guide

## Prerequisites

- Python 3.8 or higher
- Existing Renewable Energy Rankings Platform project
- pip package manager

## Step-by-Step Installation

### Step 1: Install Dependencies

```bash
pip install -r data_requirements.txt
```

This installs:
- `requests` - For API calls (World Bank, etc.)
- `pandas` - For file-based data provider

### Step 2: Extract Files to Your Project

Assuming your project structure is:
```
your_project/
├── src/
│   ├── agents/
│   ├── models/
│   └── core/
├── config/
└── data/
```

Extract the package:

```bash
# Navigate to the package directory
cd real_data_integration_package

# Copy source code
cp -r src/data/ /path/to/your/project/src/

# Copy configuration
cp config/data_sources.yaml /path/to/your/project/config/

# Create data directory and copy samples
mkdir -p /path/to/your/project/data/files
cp data/files/*.csv /path/to/your/project/data/files/
```

### Step 3: Verify Installation

Check that files are in place:

```bash
cd /path/to/your/project

# Verify source files
ls src/data/base/
# Should show: data_types.py data_models.py data_source.py exceptions.py __init__.py

ls src/data/providers/
# Should show: world_bank_provider.py file_provider.py __init__.py

ls src/data/services/
# Should show: data_service.py cache_manager.py __init__.py

# Verify config
ls config/
# Should show: data_sources.yaml (among other files)

# Verify sample data
ls data/files/
# Should show: ecr_rating_Germany.csv ecr_rating_USA.csv
```

### Step 4: Test Installation

Create a test script:

```python
# test_data_integration.py
import yaml
from src.data import DataService

# Load configuration
with open('config/data_sources.yaml') as f:
    config = yaml.safe_load(f)

# Initialize data service
data_service = DataService(config)

# Check status
status = data_service.get_status()
print("Data Service Status:")
print(f"  Providers available: {len(status['providers'])}")
print(f"  Total indicators: {status['total_indicators']}")
print(f"  Total countries: {status['total_countries']}")

# Test fetching data
print("\nTesting data fetch:")
value = data_service.get_value("Germany", "ecr_rating")
if value:
    print(f"  ✓ Germany ECR Rating: {value}")
else:
    print("  ✗ No data found")

print("\n✅ Installation successful!")
```

Run the test:
```bash
python test_data_integration.py
```

Expected output:
```
Data Service Status:
  Providers available: 2
  Total indicators: 12
  Total countries: 13

Testing data fetch:
  ✓ Germany ECR Rating: 0.8

✅ Installation successful!
```

### Step 5: Update Your Application

In your main application file (e.g., `main.py` or `app.py`):

```python
# At the top
import yaml
from src.data import DataService

# In your initialization code
def initialize_app():
    # ... existing initialization ...
    
    # Initialize data service
    with open('config/data_sources.yaml') as f:
        config = yaml.safe_load(f)
    
    data_service = DataService(config)
    
    # Store for use in agents
    return data_service

# Pass to agents when creating them
data_service = initialize_app()

# Create agents with data service
agent = CountryStabilityAgent(
    mode=AgentMode.REAL,
    data_service=data_service  # Pass data service
)
```

## Configuration

### Basic Configuration

The default configuration in `config/data_sources.yaml` is production-ready:

```yaml
cache:
  enabled: true
  strategy: hybrid  # memory + disk
  cache_dir: ./data/cache
  max_size_mb: 100

providers:
  world_bank:
    enabled: true
    timeout: 30
  
  file:
    enabled: true
    data_directory: ./data/files
```

### Advanced Configuration

#### Disable Caching (for testing)
```yaml
cache:
  enabled: false
```

#### Memory-only Caching (faster but not persistent)
```yaml
cache:
  enabled: true
  strategy: memory
```

#### Custom Cache Directory
```yaml
cache:
  cache_dir: /var/cache/renewable_rankings
```

#### Add API Keys (for future providers)
```yaml
providers:
  irena:
    enabled: true
    api_key: ${IRENA_API_KEY}  # Use environment variable
```

Set environment variable:
```bash
export IRENA_API_KEY=your_api_key_here
```

## Adding Custom Data

### CSV Format

Create files in `data/files/` with format: `{indicator}_{country}.csv`

Example: `renewable_capacity_Germany.csv`
```csv
date,value,quality,unit
2024-12-31,150.5,official,GW
2023-12-31,145.2,official,GW
2022-12-31,138.7,official,GW
```

Required columns:
- `date` - ISO format (YYYY-MM-DD) or year (YYYY)
- `value` - Numeric value

Optional columns:
- `quality` - Data quality (verified, official, estimated, preliminary)
- `unit` - Unit of measurement

### Excel Format

Excel files work the same way:
- Filename: `{indicator}_{country}.xlsx`
- Same column structure as CSV

## Troubleshooting

### Issue: "No module named 'requests'"
**Solution**: Install dependencies
```bash
pip install -r data_requirements.txt
```

### Issue: "No data returned from World Bank"
**Solution**: Check internet connection and test API
```bash
curl "https://api.worldbank.org/v2/country/USA/indicator/NY.GDP.MKTP.CD?format=json&per_page=1"
```

### Issue: "File provider shows 0 files"
**Solution**: Check file naming and location
```bash
ls data/files/
# Files should be named: {indicator}_{country}.csv
```

### Issue: "Cache directory permission denied"
**Solution**: Create cache directory with proper permissions
```bash
mkdir -p data/cache
chmod 755 data/cache
```

### Issue: "Data service initialization fails"
**Solution**: Check configuration file syntax
```bash
python -c "import yaml; yaml.safe_load(open('config/data_sources.yaml'))"
```

## Verification Checklist

- [ ] Dependencies installed (`pip list | grep requests`)
- [ ] Source files in `src/data/`
- [ ] Configuration in `config/data_sources.yaml`
- [ ] Sample data in `data/files/`
- [ ] Test script runs successfully
- [ ] Data service initializes without errors
- [ ] Can fetch data from World Bank API
- [ ] Can fetch data from file provider
- [ ] Cache directory created

## Next Steps

1. Read `docs/REAL_DATA_SUMMARY.md` for complete overview
2. Review `examples/real_data_integration_example.py`
3. Test with 1-2 agents in MOCK mode
4. Switch to REAL mode for testing
5. Roll out to all agents

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review `docs/ARCHITECTURE.md` for technical details
3. Run the test script to diagnose problems
4. Check log files for error details

## Uninstallation

To remove the data integration system:

```bash
# Remove source files
rm -rf src/data/

# Remove configuration (backup first!)
cp config/data_sources.yaml config/data_sources.yaml.backup
rm config/data_sources.yaml

# Remove data files
rm -rf data/files/
rm -rf data/cache/
```

---

**Installation Time**: 15-30 minutes  
**Difficulty**: Easy  
**Support**: See documentation in `docs/`
