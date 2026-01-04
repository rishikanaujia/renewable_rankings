"""Prompt Templates - Reusable templates for AI extraction tasks.

This module provides a library of prompt templates optimized for extracting
renewable energy investment parameters from documents.

Design Principles:
    - Few-shot learning examples
    - Clear output format specifications
    - Chain-of-thought reasoning
    - Confidence calibration
    - Source attribution

Template Categories:
    - Regulation parameters
    - Profitability parameters
    - Market fundamentals
    - Risk assessment
    - Infrastructure evaluation
"""
from typing import Dict, Any, Optional, List
from string import Template


class PromptTemplates:
    """Collection of prompt templates for parameter extraction."""
    
    # Base template with common instructions
    BASE_EXTRACTION_TEMPLATE = """You are an expert renewable energy investment analyst tasked with extracting specific data from documents.

**TASK**: Extract {parameter_name} for {country} from the provided documents.

**DOCUMENTS**:
{documents}

**EXTRACTION REQUIREMENTS**:
1. Extract the specific value for {parameter_name}
2. Provide your confidence level (0.0-1.0) in the extraction
3. Quote relevant text passages that support your finding
4. Explain your reasoning step-by-step
5. If information is not explicitly stated, make reasonable inferences based on context
6. If you cannot determine the value, explain why

**PARAMETER DEFINITION**:
{parameter_definition}

**SCORING RUBRIC**:
{scoring_rubric}

**OUTPUT FORMAT** (respond with valid JSON only):
{{
    "value": <extracted value>,
    "confidence": <0.0-1.0>,
    "justification": "<step-by-step reasoning>",
    "quotes": ["<relevant quote 1>", "<relevant quote 2>"],
    "inferences": ["<inference 1>", "<inference 2>"],
    "metadata": {{
        "data_year": "<year of data if mentioned>",
        "source_reliability": "<high|medium|low>"
    }}
}}

Think through this step-by-step before providing your final answer."""

    # Regulation-specific templates
    
    AMBITION_TEMPLATE = """Extract renewable energy targets/ambition for {country}.

**KEY INFORMATION TO FIND**:
- Renewable energy targets (%, GW, TWh)
- Target years (2030, 2050, etc.)
- Policy framework (Paris Agreement, NDCs, national plans)
- Legally binding vs. aspirational targets
- Sector-specific targets (electricity, transport, heating)

**EXAMPLE GOOD EXTRACTION**:
"Germany has a legally binding target of 80% renewable electricity by 2030 and 100% by 2035 
under the Renewable Energy Sources Act (EEG 2023). Overall renewable energy share target is 30% 
by 2030 across all sectors."

Confidence: 0.95 (explicit targets with legal framework cited)

**DOCUMENTS**:
{documents}

Respond with JSON containing: value (target %), confidence, justification, quotes, metadata."""

    SUPPORT_SCHEME_TEMPLATE = """Extract information about renewable energy support schemes for {country}.

**KEY INFORMATION TO FIND**:
- Feed-in Tariffs (FiT) - rates, duration, technologies
- Auction/tender mechanisms - frequency, volumes, clearing prices
- Tax incentives - ITC, PTC, accelerated depreciation
- Net metering policies
- Renewable Energy Certificates/Credits
- Policy stability and track record
- Recent policy changes

**SCORING GUIDANCE**:
- Score 9-10: Mature, stable, comprehensive support (Germany, UK, Denmark)
- Score 7-8: Solid support with some gaps or uncertainty
- Score 5-6: Developing framework, inconsistent application
- Score 3-4: Boom-bust cycles, policy instability
- Score 1-2: Minimal or absent support

**DOCUMENTS**:
{documents}

Respond with JSON containing: value (1-10 score), confidence, justification, quotes, metadata."""

    COUNTRY_STABILITY_TEMPLATE = """Assess political and economic stability for renewable energy investments in {country}.

**KEY FACTORS**:
- Political stability and governance
- Economic stability (inflation, currency, debt)
- Regulatory framework stability
- Contract sanctity and legal system
- Corruption levels
- Geopolitical risks
- Historical track record of honoring commitments

**RISK CATEGORIES**:
- Score 9-10: Very stable (Switzerland, Germany, Singapore)
- Score 7-8: Stable with minor concerns
- Score 5-6: Moderate risks
- Score 3-4: Elevated risks
- Score 1-2: High risk/unstable

**DOCUMENTS**:
{documents}

Respond with JSON containing: value (1-10 score), confidence, justification, quotes, metadata."""

    # Profitability templates
    
    EXPECTED_RETURN_TEMPLATE = """Extract expected returns for renewable energy projects in {country}.

**KEY INFORMATION**:
- Typical project IRR ranges
- Equity returns vs. debt returns
- Technology-specific returns (solar, wind, hydro)
- Recent auction clearing prices
- Power Purchase Agreement (PPA) prices
- Merchant market prices
- Developer margins
- Risk premiums

**RETURN BENCHMARKS**:
- Score 9-10: >12% IRR (highly attractive)
- Score 7-8: 9-12% IRR (attractive)
- Score 5-6: 7-9% IRR (moderate)
- Score 3-4: 5-7% IRR (below target)
- Score 1-2: <5% IRR (unattractive)

**DOCUMENTS**:
{documents}

Respond with JSON containing: value (1-10 score), confidence, justification, quotes, metadata."""

    REVENUE_STABILITY_TEMPLATE = """Assess revenue stream stability for renewable energy projects in {country}.

**KEY FACTORS**:
- PPA contract terms (duration, escalation)
- Offtaker types (utility, corporate, government)
- Payment history and track record
- Currency and inflation hedging
- Merchant vs. contracted exposure
- Grid curtailment risks
- Dispatch priority rules

**STABILITY LEVELS**:
- Score 9-10: Long-term PPAs (>15yr) with strong offtakers
- Score 7-8: Medium-term contracts (10-15yr)
- Score 5-6: Short-term contracts or mixed exposure
- Score 3-4: Significant merchant exposure
- Score 1-2: Unreliable payments or high curtailment

**DOCUMENTS**:
{documents}

Respond with JSON containing: value (1-10 score), confidence, justification, quotes, metadata."""

    # Market fundamentals templates
    
    POWER_MARKET_SIZE_TEMPLATE = """Extract power market size for {country}.

**KEY METRICS**:
- Total electricity consumption (TWh/year)
- Peak demand (GW)
- Electricity consumption per capita
- Growth rates (historical and projected)
- Sector breakdown (residential, commercial, industrial)

**SIZE CATEGORIES**:
- Score 9-10: >500 TWh/year (China, USA, India, Japan)
- Score 7-8: 200-500 TWh/year (Germany, Brazil, South Korea)
- Score 5-6: 50-200 TWh/year (Spain, Poland, Thailand)
- Score 3-4: 10-50 TWh/year (Chile, Portugal, Ireland)
- Score 1-2: <10 TWh/year (small markets)

**DOCUMENTS**:
{documents}

Respond with JSON containing: value (TWh and 1-10 score), confidence, justification, quotes, metadata."""

    RESOURCE_AVAILABILITY_TEMPLATE = """Assess renewable resource availability for {country}.

**KEY RESOURCES**:
- Solar: Global Horizontal Irradiance (GHI) in kWh/m²/day
- Wind: Wind speeds at hub height (m/s), capacity factors
- Hydro: River flows, precipitation, existing capacity
- Geographic suitability: land availability, terrain
- Seasonal variations

**QUALITY LEVELS**:
- Solar excellent: >5.5 kWh/m²/day (MENA, Australia, parts of India/China)
- Solar good: 4.5-5.5 (Southern Europe, US Southwest, Brazil)
- Wind excellent: >8 m/s (North Sea, Scotland, Patagonia)
- Wind good: 6-8 m/s

**DOCUMENTS**:
{documents}

Respond with JSON containing: value (resource metrics and 1-10 score), confidence, justification, quotes, metadata."""

    # Infrastructure templates
    
    GRID_STATUS_TEMPLATE = """Assess grid infrastructure quality and capacity for {country}.

**KEY FACTORS**:
- Grid capacity and robustness
- Transmission losses (%)
- Grid extension plans
- Interconnection capacity
- System stability (frequency, voltage)
- Smart grid deployment
- Connection timeframes and costs

**QUALITY LEVELS**:
- Score 9-10: Modern, low losses (<5%), high capacity
- Score 7-8: Good quality, moderate losses (5-8%)
- Score 5-6: Adequate but aging, losses 8-12%
- Score 3-4: Poor quality, high losses (12-18%)
- Score 1-2: Very poor, losses >18%, frequent outages

**DOCUMENTS**:
{documents}

Respond with JSON containing: value (1-10 score), confidence, justification, quotes, metadata."""

    # Competition templates
    
    COMPETITIVE_LANDSCAPE_TEMPLATE = """Analyze competitive landscape for renewable energy market in {country}.

**KEY FACTORS**:
- Number and diversity of developers
- Market concentration (HHI index if available)
- Barriers to entry (permits, licenses, land access)
- Foreign vs. domestic developers
- Technology competition (solar vs. wind vs. others)
- Recent market entrants
- Auction participation levels

**COMPETITIVENESS**:
- Score 9-10: Highly competitive, many players, low barriers
- Score 7-8: Competitive with moderate barriers
- Score 5-6: Moderately concentrated
- Score 3-4: Oligopolistic, high barriers
- Score 1-2: Monopolistic or closed market

**DOCUMENTS**:
{documents}

Respond with JSON containing: value (1-10 score), confidence, justification, quotes, metadata."""

    @staticmethod
    def get_template(parameter_name: str) -> str:
        """Get template for a specific parameter.
        
        Args:
            parameter_name: Name of the parameter
            
        Returns:
            Template string
        """
        templates = {
            'ambition': PromptTemplates.AMBITION_TEMPLATE,
            'support_scheme': PromptTemplates.SUPPORT_SCHEME_TEMPLATE,
            'country_stability': PromptTemplates.COUNTRY_STABILITY_TEMPLATE,
            'expected_return': PromptTemplates.EXPECTED_RETURN_TEMPLATE,
            'revenue_stream_stability': PromptTemplates.REVENUE_STABILITY_TEMPLATE,
            'power_market_size': PromptTemplates.POWER_MARKET_SIZE_TEMPLATE,
            'resource_availability': PromptTemplates.RESOURCE_AVAILABILITY_TEMPLATE,
            'status_of_grid': PromptTemplates.GRID_STATUS_TEMPLATE,
            'competitive_landscape': PromptTemplates.COMPETITIVE_LANDSCAPE_TEMPLATE,
        }
        
        return templates.get(parameter_name, PromptTemplates.BASE_EXTRACTION_TEMPLATE)
    
    @staticmethod
    def format_template(
        template: str,
        parameter_name: str,
        country: str,
        documents: str,
        **kwargs
    ) -> str:
        """Format template with parameters.
        
        Args:
            template: Template string
            parameter_name: Parameter being extracted
            country: Country name
            documents: Document content
            **kwargs: Additional template variables
            
        Returns:
            Formatted prompt string
        """
        return template.format(
            parameter_name=parameter_name,
            country=country,
            documents=documents,
            **kwargs
        )


# Convenience function
def get_extraction_prompt(
    parameter_name: str,
    country: str,
    documents: str,
    **kwargs
) -> str:
    """Get formatted extraction prompt for a parameter.
    
    Args:
        parameter_name: Name of parameter to extract
        country: Country name
        documents: Document content
        **kwargs: Additional template variables
        
    Returns:
        Formatted prompt string
    """
    template = PromptTemplates.get_template(parameter_name)
    return PromptTemplates.format_template(
        template,
        parameter_name,
        country,
        documents,
        **kwargs
    )
