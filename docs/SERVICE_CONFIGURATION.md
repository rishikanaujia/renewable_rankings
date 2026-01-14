# Service Configuration Guide

## Overview

The Renewable Rankings application supports two service modes:

1. **Mock Service** (Default) - Fast, uses sample data for UI testing
2. **Real Agents** (Production) - Slower, uses actual AI agents for analysis

## Switching Between Services

### Quick Start

**Option 1: Environment Variable**

```bash
# Use mock data (default, fast)
USE_REAL_AGENTS=false python run.py

# Use real AI agents (slower, production)
USE_REAL_AGENTS=true python run.py
```

**Option 2: .env File**

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and set:
   ```
   USE_REAL_AGENTS=true    # For real agents
   # or
   USE_REAL_AGENTS=false   # For mock data
   ```

3. Run the application:
   ```bash
   python run.py
   ```

## Service Comparison

| Feature | Mock Service | Real Agents |
|---------|-------------|-------------|
| **Speed** | Very fast (~instant) | Slower (seconds per country) |
| **Data** | Hardcoded sample data | Real-time AI analysis |
| **Accuracy** | Fixed sample scores | Dynamic, based on actual data |
| **Use Case** | Development, demos, UI testing | Production, real analysis |
| **API Calls** | None | Requires LLM API access |
| **Cost** | Free | API costs apply |

## When to Use Each Service

### Use Mock Service When:
- ✅ Developing the UI
- ✅ Testing new features quickly
- ✅ Demonstrating the interface
- ✅ You don't need real analysis
- ✅ Want to avoid API costs

### Use Real Agents When:
- ✅ Running production analysis
- ✅ Need actual country rankings
- ✅ Presenting real results to stakeholders
- ✅ Testing agent logic and reasoning
- ✅ Validating parameter calculations

## How It Works

### Architecture

```
┌─────────────┐
│   app.py    │
└──────┬──────┘
       │
       ├── USE_REAL_AGENTS=false ──► mock_service.py
       │                              └─► Returns hardcoded data
       │
       └── USE_REAL_AGENTS=true  ──► ranking_service_adapter.py
                                      └─► agent_service.py
                                          └─► 18 Parameter Agents
                                              └─► Real AI Analysis
```

### Service Adapter

The `ranking_service_adapter.py` wraps the `agent_service` to provide the same interface as `mock_service`, allowing seamless switching without code changes.

**Both services implement:**
- `get_rankings(period)` - Get global rankings
- `get_country_ranking(country_name, period)` - Get single country
- `apply_correction(correction)` - Apply expert corrections
- `search_countries(query)` - Search for countries

## Configuration Details

### Environment Variables

| Variable | Values | Default | Description |
|----------|--------|---------|-------------|
| `USE_REAL_AGENTS` | `true` / `false` | `false` | Switch between mock and real agents |
| `LOG_LEVEL` | `DEBUG` / `INFO` / `WARNING` | `INFO` | Logging verbosity |
| `GRADIO_SERVER_PORT` | Integer | `7860` | Web server port |
| `DEBUG` | `true` / `false` | `false` | Debug mode |

### Logging Output

The application logs which service is active:

```
INFO: RankingsApp initialized with MOCK SERVICE (sample data)
INFO: Active service: MockRankingService
```

or

```
INFO: RankingsApp initialized with REAL AGENTS (AI-powered analysis)
INFO: Active service: RankingServiceAdapter
```

## Default Countries

When using real agents, the system analyzes these countries by default:

- Brazil
- Germany
- United States
- China
- India
- United Kingdom
- Spain
- Australia
- Chile
- Vietnam

To change this list, edit `DEFAULT_COUNTRIES` in `ranking_service_adapter.py`.

## Performance Considerations

### Mock Service
- **Response Time:** < 100ms
- **Memory Usage:** Low
- **API Calls:** 0

### Real Agents
- **Response Time:** 5-30 seconds per country
- **For 10 countries:** 50-300 seconds total
- **API Calls:** ~18 per country (one per parameter)
- **Memory Usage:** Moderate

## Troubleshooting

### Service Not Switching

1. Check environment variable:
   ```bash
   echo $USE_REAL_AGENTS
   ```

2. Check .env file exists and is loaded:
   ```bash
   cat .env | grep USE_REAL_AGENTS
   ```

3. Check logs for service initialization message

### Real Agents Not Working

1. Verify API credentials are set (if using AI models)
2. Check agent service is properly initialized
3. Review logs for agent errors
4. Ensure all parameter agents are implemented

## Examples

### Development Workflow

```bash
# Start with mock data for fast UI development
USE_REAL_AGENTS=false python run.py

# Test with real agents when ready
USE_REAL_AGENTS=true python run.py
```

### Production Deployment

```bash
# Set in .env file
echo "USE_REAL_AGENTS=true" >> .env

# Deploy
python run.py
```

## Future Enhancements

Planned improvements:
- UI toggle to switch services without restart
- Hybrid mode (mock + selective real analysis)
- Caching of real agent results
- Progressive loading (show results as they complete)
- Service health monitoring dashboard
