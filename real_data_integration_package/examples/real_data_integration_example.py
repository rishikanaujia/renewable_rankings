"""
Complete Example: Real Data Integration with Agents
====================================================

This example shows how to:
1. Initialize the data service
2. Modify agents to use real data
3. Switch between MOCK and REAL modes
4. Handle data fetching and caching
"""

import yaml
from datetime import datetime
from src.data import DataService
from src.agents.base_agent import BaseParameterAgent, AgentMode
from src.models.parameter import ParameterScore


# ==============================================================================
# PART 1: Initialize Data Service (ONCE at application startup)
# ==============================================================================

def setup_data_service():
    """Initialize data service with configuration."""
    # Load configuration
    with open('config/data_sources.yaml') as f:
        config = yaml.safe_load(f)
    
    # Create data service
    data_service = DataService(config)
    
    # Check status
    status = data_service.get_status()
    print(f"Data service initialized:")
    print(f"  Providers: {len(status['providers'])}")
    print(f"  Indicators: {status['total_indicators']}")
    print(f"  Countries: {status['total_countries']}")
    
    return data_service


# ==============================================================================
# PART 2: Modify Agent to Use Real Data
# ==============================================================================

class CountryStabilityAgentWithRealData(BaseParameterAgent):
    """Country Stability Agent that can use MOCK or REAL data."""
    
    # Mock data (for MOCK mode)
    MOCK_DATA = {
        "Germany": {"ecr_rating": 0.8},
        "USA": {"ecr_rating": 1.2},
        "India": {"ecr_rating": 3.2},
    }
    
    def __init__(
        self, 
        mode: AgentMode = AgentMode.MOCK, 
        config=None,
        data_service=None  # ADD THIS
    ):
        super().__init__("Country Stability", mode, config)
        self.data_service = data_service  # Store data service
    
    def _fetch_data(self, country: str, period: str) -> dict:
        """Fetch data (MOCK or REAL based on mode)."""
        if self.mode == AgentMode.MOCK:
            # Use mock data
            return self.MOCK_DATA.get(country, {"ecr_rating": 5.0})
        
        elif self.mode == AgentMode.REAL:
            # Use real data service
            if not self.data_service:
                raise ValueError("Real mode requires data_service")
            
            # Fetch data from real sources
            data = {}
            
            # Get ECR rating (from file provider)
            ecr = self.data_service.get_value(
                country=country,
                indicator='ecr_rating',
                default=5.0
            )
            data['ecr_rating'] = ecr
            
            # Get GDP growth (from World Bank)
            gdp_growth = self.data_service.get_value(
                country=country,
                indicator='gdp_growth',
                default=0.0
            )
            data['gdp_growth'] = gdp_growth
            
            # Get additional context
            population = self.data_service.get_value(
                country=country,
                indicator='population',
                default=0
            )
            data['population'] = population
            
            return data
        
        else:
            raise ValueError(f"Unknown mode: {self.mode}")
    
    def _calculate_score(self, data: dict) -> float:
        """Calculate score from data."""
        ecr = data.get('ecr_rating', 5.0)
        
        # Score based on ECR rating
        if ecr < 1.0: return 10.0
        elif ecr < 2.0: return 9.0
        elif ecr < 3.0: return 8.0
        elif ecr < 4.0: return 7.0
        else: return 6.0
    
    def _generate_justification(self, score: float, data: dict) -> str:
        """Generate justification."""
        ecr = data.get('ecr_rating', 0)
        justification = f"ECR Rating: {ecr:.1f}, Score: {score}/10"
        
        # Add real data context if available
        if 'gdp_growth' in data:
            justification += f". GDP Growth: {data['gdp_growth']:.1f}%"
        
        return justification


# ==============================================================================
# PART 3: Usage Examples
# ==============================================================================

def main():
    print("="*70)
    print("Real Data Integration Example")
    print("="*70)
    
    # 1. Initialize data service
    print("\n1. Initializing data service...")
    data_service = setup_data_service()
    
    # 2. Create agent in MOCK mode (default, no data service needed)
    print("\n2. Testing MOCK mode...")
    agent_mock = CountryStabilityAgentWithRealData(mode=AgentMode.MOCK)
    result_mock = agent_mock.analyze("Germany", "Q1 2024")
    print(f"   MOCK Result: {result_mock.score}/10")
    print(f"   {result_mock.justification}")
    
    # 3. Create agent in REAL mode (requires data service)
    print("\n3. Testing REAL mode...")
    agent_real = CountryStabilityAgentWithRealData(
        mode=AgentMode.REAL,
        data_service=data_service  # Pass data service
    )
    result_real = agent_real.analyze("Germany", "Q1 2024")
    print(f"   REAL Result: {result_real.score}/10")
    print(f"   {result_real.justification}")
    
    # 4. Direct data service usage
    print("\n4. Direct data service usage...")
    
    # Get latest GDP for Germany
    gdp = data_service.get_value("Germany", "gdp")
    print(f"   Germany GDP: ${gdp:,.0f}" if gdp else "   No data")
    
    # Get GDP growth time series
    response = data_service.get_data("Germany", "gdp_growth")
    if response.success:
        latest = response.data.get_latest()
        print(f"   GDP Growth: {latest.value:.2f}% ({latest.timestamp.year})")
    
    # 5. Cache statistics
    print("\n5. Cache statistics...")
    cache_stats = data_service.cache.get_stats()
    print(f"   Memory entries: {cache_stats['memory_entries']}")
    if 'disk_entries' in cache_stats:
        print(f"   Disk entries: {cache_stats['disk_entries']}")
    
    print("\n" + "="*70)
    print("✅ Real data integration working!")
    print("="*70)


# ==============================================================================
# PART 4: Integration Pattern for Existing Agents
# ==============================================================================

"""
To add real data to ANY existing agent:

1. Add data_service parameter to __init__:
   def __init__(self, mode=AgentMode.MOCK, config=None, data_service=None):
       super().__init__("Agent Name", mode, config)
       self.data_service = data_service

2. Modify _fetch_data to check mode:
   def _fetch_data(self, country, period):
       if self.mode == AgentMode.MOCK:
           return self.MOCK_DATA.get(country, {})
       elif self.mode == AgentMode.REAL:
           return self._fetch_real_data(country, period)

3. Implement _fetch_real_data:
   def _fetch_real_data(self, country, period):
       data = {}
       data['indicator1'] = self.data_service.get_value(country, 'indicator1')
       data['indicator2'] = self.data_service.get_value(country, 'indicator2')
       return data

That's it! Agent now works in both MOCK and REAL modes.
"""


if __name__ == "__main__":
    main()
