"""Parsers for Market Size & Fundamentals subcategory parameters.

Market parameters:
1. Power Market Size - Electricity demand and market size
2. Resource Availability - Solar/wind resource quality
3. Energy Dependence - Import dependency and energy security
4. Renewables Penetration - Current renewable share and growth
"""
from typing import Dict, Any
from .base_parser import BaseParser
import logging

logger = logging.getLogger(__name__)


class PowerMarketSizeParser(BaseParser):
    """Parser for Power Market Size - extracts electricity demand metrics."""

    def __init__(self):
        super().__init__(parameter_name="Power Market Size")

    def parse(self, research_doc) -> Dict[str, Any]:
        """Extract electricity market size and growth.

        Returns:
            {
                'annual_demand_twh': float,  # TWh per year
                'peak_demand_gw': float,
                'demand_growth_percent': float,  # Annual growth rate
                'per_capita_kwh': float,
                'source': 'research',
                ...
            }
        """
        metrics = self._get_metrics(research_doc)

        # Look for annual demand
        demand_keywords = ['annual demand', 'electricity demand', 'power demand', 'consumption', 'twh']
        demand_metric = self._find_metric(metrics, demand_keywords)
        annual_demand = self._extract_numeric_value(demand_metric, 100.0) if demand_metric else 100.0

        # Look for peak demand
        peak_keywords = ['peak demand', 'peak load', 'maximum demand']
        peak_metric = self._find_metric(metrics, peak_keywords)
        peak_demand = self._extract_numeric_value(peak_metric, 20.0) if peak_metric else 20.0

        # Look for growth rate
        growth_keywords = ['growth', 'demand growth', 'increase']
        growth_metric = self._find_metric(metrics, growth_keywords)
        demand_growth = self._extract_numeric_value(growth_metric, 3.0) if growth_metric else 3.0

        # Look for per capita
        capita_keywords = ['per capita', 'per person', 'kwh per capita']
        capita_metric = self._find_metric(metrics, capita_keywords)
        per_capita = self._extract_numeric_value(capita_metric, 5000.0) if capita_metric else 5000.0

        return self._create_base_response(
            research_doc,
            additional_data={
                'annual_demand_twh': annual_demand,
                'peak_demand_gw': peak_demand,
                'demand_growth_percent': demand_growth,
                'per_capita_kwh': per_capita
            }
        )


class ResourceAvailabilityParser(BaseParser):
    """Parser for Resource Availability - extracts solar/wind resource quality."""

    def __init__(self):
        super().__init__(parameter_name="Resource Availability")

    def parse(self, research_doc) -> Dict[str, Any]:
        """Extract renewable resource availability metrics.

        Returns:
            {
                'solar_irradiation_kwh_m2': float,  # kWh/m²/year
                'wind_speed_ms': float,  # m/s average
                'solar_capacity_factor_percent': float,
                'wind_capacity_factor_percent': float,
                'source': 'research',
                ...
            }
        """
        metrics = self._get_metrics(research_doc)

        # Look for solar irradiation
        solar_keywords = ['solar', 'irradiation', 'ghi', 'solar resource']
        solar_metric = self._find_metric(metrics, solar_keywords)
        solar_irradiation = self._extract_numeric_value(solar_metric, 1800.0) if solar_metric else 1800.0

        # Look for wind speed
        wind_keywords = ['wind speed', 'wind resource', 'm/s']
        wind_metric = self._find_metric(metrics, wind_keywords)
        wind_speed = self._extract_numeric_value(wind_metric, 6.5) if wind_metric else 6.5

        # Look for capacity factors
        solar_cf_keywords = ['solar capacity factor', 'pv capacity factor']
        solar_cf_metric = self._find_metric(metrics, solar_cf_keywords)
        solar_cf = self._extract_numeric_value(solar_cf_metric, 20.0) if solar_cf_metric else 20.0

        wind_cf_keywords = ['wind capacity factor', 'wind cf']
        wind_cf_metric = self._find_metric(metrics, wind_cf_keywords)
        wind_cf = self._extract_numeric_value(wind_cf_metric, 35.0) if wind_cf_metric else 35.0

        return self._create_base_response(
            research_doc,
            additional_data={
                'solar_irradiation_kwh_m2': solar_irradiation,
                'wind_speed_ms': wind_speed,
                'solar_capacity_factor_percent': solar_cf,
                'wind_capacity_factor_percent': wind_cf
            }
        )


class EnergyDependenceParser(BaseParser):
    """Parser for Energy Dependence - extracts import dependency metrics."""

    def __init__(self):
        super().__init__(parameter_name="Energy Dependence")

    def parse(self, research_doc) -> Dict[str, Any]:
        """Extract energy import dependency and security metrics.

        Returns:
            {
                'import_dependency_percent': float,  # % of energy imported
                'energy_security_score': float,  # 0-10
                'domestic_production_percent': float,
                'diversification_score': float,  # Supply diversity
                'source': 'research',
                ...
            }
        """
        metrics = self._get_metrics(research_doc)

        # Look for import dependency
        import_keywords = ['import', 'dependency', 'import dependency', 'net import']
        import_metric = self._find_metric(metrics, import_keywords)
        import_dependency = self._extract_numeric_value(import_metric, 30.0) if import_metric else 30.0

        # Look for security score
        security_keywords = ['energy security', 'security score', 'security index']
        security_metric = self._find_metric(metrics, security_keywords)
        security_score = self._extract_numeric_value(security_metric, 6.0) if security_metric else 6.0

        # Calculate domestic production
        domestic_production = 100.0 - import_dependency

        # Look for diversification
        div_keywords = ['diversification', 'diversity', 'supply diversity']
        div_metric = self._find_metric(metrics, div_keywords)
        diversification = self._extract_numeric_value(div_metric, 5.0) if div_metric else 5.0

        return self._create_base_response(
            research_doc,
            additional_data={
                'import_dependency_percent': import_dependency,
                'energy_security_score': security_score,
                'domestic_production_percent': domestic_production,
                'diversification_score': diversification
            }
        )


class RenewablesPenetrationParser(BaseParser):
    """Parser for Renewables Penetration - extracts current renewable share."""

    def __init__(self):
        super().__init__(parameter_name="Renewables Penetration")

    def parse(self, research_doc) -> Dict[str, Any]:
        """Extract renewables penetration and growth metrics.

        Returns:
            {
                'renewable_share_percent': float,  # % of total generation
                'renewable_capacity_gw': float,
                'annual_growth_rate_percent': float,
                'solar_share_percent': float,
                'wind_share_percent': float,
                'source': 'research',
                ...
            }
        """
        metrics = self._get_metrics(research_doc)

        # Look for renewable share
        share_keywords = ['renewable share', 'renewables share', 'renewable penetration', 'green energy share']
        share_metric = self._find_metric(metrics, share_keywords)
        renewable_share = self._extract_numeric_value(share_metric, 25.0) if share_metric else 25.0

        # Look for total capacity
        capacity_keywords = ['renewable capacity', 'installed capacity', 'total capacity']
        capacity_metric = self._find_metric(metrics, capacity_keywords)
        renewable_capacity = self._extract_numeric_value(capacity_metric, 50.0) if capacity_metric else 50.0

        # Look for growth rate
        growth_keywords = ['growth rate', 'annual growth', 'increase']
        growth_metric = self._find_metric(metrics, growth_keywords)
        growth_rate = self._extract_numeric_value(growth_metric, 10.0) if growth_metric else 10.0

        # Look for technology breakdown
        solar_keywords = ['solar share', 'solar percent', 'pv share']
        solar_metric = self._find_metric(metrics, solar_keywords)
        solar_share = self._extract_numeric_value(solar_metric, 12.0) if solar_metric else 12.0

        wind_keywords = ['wind share', 'wind percent']
        wind_metric = self._find_metric(metrics, wind_keywords)
        wind_share = self._extract_numeric_value(wind_metric, 13.0) if wind_metric else 13.0

        return self._create_base_response(
            research_doc,
            additional_data={
                'renewable_share_percent': renewable_share,
                'renewable_capacity_gw': renewable_capacity,
                'annual_growth_rate_percent': growth_rate,
                'solar_share_percent': solar_share,
                'wind_share_percent': wind_share
            }
        )
