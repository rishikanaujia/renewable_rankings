"""
QUICK START: Real Data Integration
===================================

This guide shows you how to enable real data fetching in 3 steps.
"""

# ==============================================================================
# STEP 1: Install Dependencies
# ==============================================================================

"""
Add to requirements.txt:
    requests>=2.31.0      # For API calls
    pandas>=2.0.0         # For file provider
"""

# Run:
# pip install requests pandas


# ==============================================================================
# STEP 2: Initialize Data Service (in your main app)
# ==============================================================================

import yaml
from src.data import DataService

# Load config
with open('config/data_sources.yaml') as f:
    config = yaml.safe_load(f)

# Create data service (ONCE at startup)
data_service = DataService(config)


# ==============================================================================
# STEP 3: Modify Agents to Accept data_service
# ==============================================================================

# BEFORE (MOCK only):
class MyAgent(BaseParameterAgent):
    def __init__(self, mode=AgentMode.MOCK, config=None):
        super().__init__("MyAgent", mode, config)

# AFTER (MOCK + REAL):
class MyAgent(BaseParameterAgent):
    def __init__(self, mode=AgentMode.MOCK, config=None, data_service=None):
        super().__init__("MyAgent", mode, config)
        self.data_service = data_service  # ADD THIS LINE


# ==============================================================================
# STEP 4: Update _fetch_data Method
# ==============================================================================

# BEFORE:
def _fetch_data(self, country, period):
    return self.MOCK_DATA.get(country, {})

# AFTER:
def _fetch_data(self, country, period):
    if self.mode == AgentMode.MOCK:
        return self.MOCK_DATA.get(country, {})
    
    elif self.mode == AgentMode.REAL:
        # Fetch real data
        data = {}
        data['indicator1'] = self.data_service.get_value(
            country, 'indicator1', default=0.0
        )
        data['indicator2'] = self.data_service.get_value(
            country, 'indicator2', default=0.0
        )
        return data


# ==============================================================================
# STEP 5: Use in Your Application
# ==============================================================================

# MOCK mode (no data service needed)
agent = MyAgent(mode=AgentMode.MOCK)
result = agent.analyze("Germany", "Q1 2024")

# REAL mode (pass data service)
agent = MyAgent(mode=AgentMode.REAL, data_service=data_service)
result = agent.analyze("Germany", "Q1 2024")


# ==============================================================================
# AVAILABLE DATA SOURCES
# ==============================================================================

"""
World Bank API (free, no auth):
  - GDP, GDP per capita, GDP growth
  - Inflation, unemployment
  - Energy use, electricity production
  - Renewable capacity
  - Interest rates
  
File Provider (CSV/Excel):
  - Put files in ./data/files/
  - Format: {indicator}_{country}.csv
  - Columns: date, value (required), quality, unit (optional)

To add more providers:
  1. Implement DataSource interface
  2. Register in DataService._initialize_providers()
  3. Configure in config/data_sources.yaml
"""


# ==============================================================================
# MINIMAL AGENT EXAMPLE
# ==============================================================================

from src.agents.base_agent import BaseParameterAgent, AgentMode
from src.data import DataService

class MinimalRealDataAgent(BaseParameterAgent):
    """Minimal example with real data support."""
    
    MOCK_DATA = {"Germany": {"value": 8.5}}
    
    def __init__(self, mode=AgentMode.MOCK, config=None, data_service=None):
        super().__init__("Minimal", mode, config)
        self.data_service = data_service
    
    def _fetch_data(self, country, period):
        if self.mode == AgentMode.MOCK:
            return self.MOCK_DATA.get(country, {"value": 5.0})
        return {"value": self.data_service.get_value(country, "gdp", 5.0)}
    
    def _calculate_score(self, data):
        return data.get("value", 5.0)
    
    def _generate_justification(self, score, data):
        return f"Score: {score}/10"


# ==============================================================================
# TESTING
# ==============================================================================

def test_agent():
    """Test agent in both modes."""
    import yaml
    
    # Setup
    with open('config/data_sources.yaml') as f:
        config = yaml.safe_load(f)
    data_service = DataService(config)
    
    # MOCK mode
    agent_mock = MinimalRealDataAgent(mode=AgentMode.MOCK)
    result_mock = agent_mock.analyze("Germany", "Q1 2024")
    print(f"MOCK: {result_mock.score}")
    
    # REAL mode
    agent_real = MinimalRealDataAgent(mode=AgentMode.REAL, data_service=data_service)
    result_real = agent_real.analyze("Germany", "Q1 2024")
    print(f"REAL: {result_real.score}")


# ==============================================================================
# SUMMARY
# ==============================================================================

"""
Changes per agent:
1. Add data_service parameter to __init__ (1 line)
2. Store data_service (1 line)
3. Update _fetch_data to check mode and fetch real data (5-10 lines)

Total: ~7-12 lines per agent

Backward compatible:
- Agents still work in MOCK mode without data_service
- No changes to _calculate_score or _generate_justification
- REAL mode is opt-in
"""
