"""Parameter Configurations - Complete configuration for all 18 parameters.

This module contains extraction configurations for all renewable energy
investment parameters. Each configuration defines:
    - Parameter metadata
    - Output type and range
    - Key factors to extract
    - Prompt templates
    - Required documents
    - Validation rules

Adding a new parameter is as simple as adding a new configuration dict!
"""
from typing import Dict, Any, List


# ============================================================================
# PARAMETER CONFIGURATION SCHEMA
# ============================================================================

PARAMETER_CONFIG_SCHEMA = {
    'parameter_name': str,        # Unique parameter identifier
    'display_name': str,          # Human-readable name
    'subcategory': str,           # Subcategory (Regulation, Profitability, etc.)
    'output_type': str,           # 'score', 'percentage', 'value', 'composite'
    'score_range': tuple,         # (min, max) for scores
    'definition': str,            # Parameter definition
    'key_factors': List[str],     # List of factors to consider
    'prompt_template': str,       # Name of prompt template (optional)
    'required_documents': List[str],  # Recommended document types
    'recommended_sources': List[Dict[str, str]],  # Data sources
    'validation_rules': Dict[str, Any],  # Validation configuration
    'scoring_rubric': List[Dict[str, Any]],  # Scoring guidelines
}


# ============================================================================
# COMPLETE PARAMETER CONFIGURATIONS
# ============================================================================

PARAMETER_CONFIGS = {
    
    # ========================================================================
    # REGULATION SUBCATEGORY (5 parameters)
    # ========================================================================
    
    'ambition': {
        'parameter_name': 'ambition',
        'display_name': 'Renewable Energy Ambition/Targets',
        'subcategory': 'Regulation',
        'output_type': 'percentage',
        'score_range': (0, 100),
        'definition': (
            'Government renewable energy targets and ambitions including percentage '
            'targets, capacity goals (GW), and legally binding commitments'
        ),
        'key_factors': [
            'Renewable energy targets (%, GW, TWh)',
            'Target years (2030, 2050, net zero)',
            'Legal status (binding vs. aspirational)',
            'Policy framework (NDCs, national plans)',
            'Sector-specific targets',
            'Historical target achievement'
        ],
        'prompt_template': 'ambition',
        'required_documents': [
            'national_energy_plan',
            'ndc_submission',
            'climate_action_plan',
            'renewable_energy_strategy'
        ],
        'recommended_sources': [
            {
                'name': 'UNFCCC NDC Registry',
                'url': 'https://unfccc.int/NDCREG',
                'description': 'National Determined Contributions'
            },
            {
                'name': 'IEA Policies Database',
                'url': 'https://www.iea.org/policies',
                'description': 'Energy policies and measures'
            }
        ],
        'validation_rules': {
            'min_justification_length': 30,
            'min_confidence': 0.3
        },
        'scoring_rubric': [
            {'score': 10, 'description': '90-100% renewable target by 2030'},
            {'score': 9, 'description': '70-90% renewable target by 2030'},
            {'score': 8, 'description': '50-70% renewable target by 2030'},
            {'score': 7, 'description': '40-50% renewable target by 2030'},
            {'score': 6, 'description': '30-40% renewable target by 2030'},
            {'score': 5, 'description': '20-30% renewable target'},
            {'score': 4, 'description': '10-20% renewable target'},
            {'score': 3, 'description': '5-10% renewable target'},
            {'score': 2, 'description': 'Minimal targets (<5%)'},
            {'score': 1, 'description': 'No formal targets'}
        ]
    },
    
    'support_scheme': {
        'parameter_name': 'support_scheme',
        'display_name': 'Support Scheme Quality',
        'subcategory': 'Regulation',
        'output_type': 'score',
        'score_range': (1, 10),
        'definition': (
            'Quality and effectiveness of renewable energy support mechanisms including '
            'feed-in tariffs, auctions, tax incentives, net metering, and RECs'
        ),
        'key_factors': [
            'Feed-in Tariff (FiT) design and rates',
            'Auction/tender mechanisms',
            'Tax incentives (ITC, PTC, depreciation)',
            'Net metering policies',
            'Renewable Energy Certificates',
            'Policy stability and track record',
            'Recent policy changes'
        ],
        'prompt_template': 'support_scheme',
        'required_documents': [
            'fit_schedules',
            'auction_results',
            'tax_code',
            'policy_documents'
        ],
        'recommended_sources': [
            {
                'name': 'IEA Policies Database',
                'url': 'https://www.iea.org/policies'
            },
            {
                'name': 'IRENA Policy Database',
                'url': 'https://www.irena.org/policies'
            }
        ],
        'validation_rules': {
            'min_justification_length': 30
        },
        'scoring_rubric': [
            {'score': 10, 'description': 'Highly mature, comprehensive support'},
            {'score': 9, 'description': 'Strong but limited scale'},
            {'score': 8, 'description': 'Broad but uneven application'},
            {'score': 7, 'description': 'Solid but policy uncertainty'},
            {'score': 6, 'description': 'Developing framework'},
            {'score': 5, 'description': 'Basic mechanisms'},
            {'score': 4, 'description': 'Boom-bust cycles'},
            {'score': 3, 'description': 'Policy distortions'},
            {'score': 2, 'description': 'Emerging but ineffective'},
            {'score': 1, 'description': 'Minimal or absent'}
        ]
    },
    
    'track_record': {
        'parameter_name': 'track_record',
        'display_name': 'Deployment Track Record',
        'subcategory': 'Regulation',
        'output_type': 'score',
        'score_range': (1, 10),
        'definition': (
            'Historical renewable energy deployment including installed capacity, '
            'growth rates, and project success'
        ),
        'key_factors': [
            'Total installed RE capacity (GW)',
            'Historical growth rates (CAGR)',
            'Number of operational projects',
            'Project completion rates',
            'Technology diversity',
            'Years of deployment history'
        ],
        'required_documents': [
            'irena_statistics',
            'national_statistics',
            'project_databases'
        ],
        'recommended_sources': [
            {
                'name': 'IRENA Statistics',
                'url': 'https://www.irena.org/Statistics'
            }
        ],
        'validation_rules': {
            'min_justification_length': 25
        },
        'scoring_rubric': [
            {'score': 10, 'description': '>50 GW, mature market'},
            {'score': 9, 'description': '25-50 GW, strong growth'},
            {'score': 8, 'description': '10-25 GW, proven track record'},
            {'score': 7, 'description': '5-10 GW, emerging market'},
            {'score': 6, 'description': '2-5 GW, developing'},
            {'score': 5, 'description': '1-2 GW, early stage'},
            {'score': 4, 'description': '0.5-1 GW, nascent'},
            {'score': 3, 'description': '100-500 MW, minimal'},
            {'score': 2, 'description': '<100 MW, very limited'},
            {'score': 1, 'description': 'No meaningful deployment'}
        ]
    },
    
    'contract_terms': {
        'parameter_name': 'contract_terms',
        'display_name': 'PPA Contract Terms',
        'subcategory': 'Regulation',
        'output_type': 'score',
        'score_range': (1, 10),
        'definition': (
            'PPA contract bankability including term length, price escalation, '
            'termination rights, and risk allocation'
        ),
        'key_factors': [
            'Standard PPA term length (years)',
            'Price escalation mechanisms',
            'Termination rights and penalties',
            'Force majeure provisions',
            'Payment security',
            'Dispute resolution',
            'Contract enforceability'
        ],
        'required_documents': [
            'ppa_templates',
            'regulatory_framework',
            'legal_code'
        ],
        'validation_rules': {
            'min_justification_length': 30
        },
        'scoring_rubric': [
            {'score': 10, 'description': '25+ year PPAs, strong security'},
            {'score': 9, 'description': '20-25 year PPAs, good terms'},
            {'score': 8, 'description': '15-20 year PPAs, bankable'},
            {'score': 7, 'description': '12-15 year PPAs, adequate'},
            {'score': 6, 'description': '10-12 year PPAs, moderate'},
            {'score': 5, 'description': '7-10 year PPAs, limited'},
            {'score': 4, 'description': '5-7 year PPAs, weak'},
            {'score': 3, 'description': '<5 year PPAs, very weak'},
            {'score': 2, 'description': 'Unfavorable terms'},
            {'score': 1, 'description': 'No standard PPAs'}
        ]
    },
    
    'country_stability': {
        'parameter_name': 'country_stability',
        'display_name': 'Political & Economic Stability',
        'subcategory': 'Regulation',
        'output_type': 'score',
        'score_range': (1, 10),
        'definition': (
            'Political and economic stability assessment for renewable energy '
            'investments including governance, regulatory stability, and risk factors'
        ),
        'key_factors': [
            'Political stability index',
            'Governance quality',
            'Economic stability',
            'Currency stability',
            'Regulatory framework stability',
            'Contract sanctity',
            'Corruption levels',
            'Geopolitical risks'
        ],
        'prompt_template': 'country_stability',
        'required_documents': [
            'country_risk_reports',
            'governance_indicators',
            'political_analysis'
        ],
        'recommended_sources': [
            {
                'name': 'World Bank Governance Indicators',
                'url': 'https://info.worldbank.org/governance/wgi/'
            },
            {
                'name': 'Transparency International CPI',
                'url': 'https://www.transparency.org/cpi'
            }
        ],
        'validation_rules': {
            'min_justification_length': 30
        },
        'scoring_rubric': [
            {'score': 10, 'description': 'Very stable (Switzerland, Singapore)'},
            {'score': 9, 'description': 'Highly stable (Germany, Netherlands)'},
            {'score': 8, 'description': 'Stable (USA, UK, France)'},
            {'score': 7, 'description': 'Generally stable (Spain, Italy)'},
            {'score': 6, 'description': 'Moderately stable (Brazil, India)'},
            {'score': 5, 'description': 'Some concerns (South Africa)'},
            {'score': 4, 'description': 'Notable risks (Egypt, Kenya)'},
            {'score': 3, 'description': 'Elevated risks (Pakistan)'},
            {'score': 2, 'description': 'High risk (Venezuela)'},
            {'score': 1, 'description': 'Extreme risk'}
        ]
    },
    
    # ========================================================================
    # PROFITABILITY SUBCATEGORY (4 parameters)
    # ========================================================================
    
    'revenue_stream_stability': {
        'parameter_name': 'revenue_stream_stability',
        'display_name': 'Revenue Stream Stability',
        'subcategory': 'Profitability',
        'output_type': 'score',
        'score_range': (1, 10),
        'definition': (
            'Revenue stream stability including PPA contract terms, offtaker quality, '
            'payment track record, and merchant exposure'
        ),
        'key_factors': [
            'PPA contract duration',
            'Offtaker creditworthiness',
            'Payment history and DSO',
            'Currency and inflation hedging',
            'Merchant vs contracted exposure',
            'Curtailment risks',
            'Dispatch priority'
        ],
        'prompt_template': 'revenue_stability',
        'required_documents': [
            'ppa_terms',
            'utility_reports',
            'payment_statistics'
        ],
        'validation_rules': {
            'min_justification_length': 30
        },
        'scoring_rubric': [
            {'score': 10, 'description': '20+ year PPAs, AAA offtakers'},
            {'score': 9, 'description': '15-20 year PPAs, strong offtakers'},
            {'score': 8, 'description': '12-15 year PPAs, good offtakers'},
            {'score': 7, 'description': '10-12 year PPAs, adequate'},
            {'score': 6, 'description': '7-10 year PPAs, moderate'},
            {'score': 5, 'description': 'Mixed contract/merchant'},
            {'score': 4, 'description': 'Significant merchant exposure'},
            {'score': 3, 'description': 'Weak contracts, payment delays'},
            {'score': 2, 'description': 'High curtailment, poor payments'},
            {'score': 1, 'description': 'Predominantly merchant, unreliable'}
        ]
    },
    
    'offtaker_status': {
        'parameter_name': 'offtaker_status',
        'display_name': 'Offtaker Creditworthiness',
        'subcategory': 'Profitability',
        'output_type': 'score',
        'score_range': (1, 10),
        'definition': (
            'Creditworthiness and payment reliability of power offtakers '
            '(utilities, corporates, government)'
        ),
        'key_factors': [
            'Offtaker credit ratings',
            'Financial health indicators',
            'Payment track record',
            'Days Sales Outstanding (DSO)',
            'Government backing/guarantees',
            'Regulatory rate recovery',
            'Historical payment delays'
        ],
        'required_documents': [
            'utility_financials',
            'credit_ratings',
            'payment_data'
        ],
        'validation_rules': {
            'min_justification_length': 25
        },
        'scoring_rubric': [
            {'score': 10, 'description': 'AAA rated, government-backed'},
            {'score': 9, 'description': 'AA rated, excellent track record'},
            {'score': 8, 'description': 'A rated, strong financials'},
            {'score': 7, 'description': 'BBB rated, solid performance'},
            {'score': 6, 'description': 'BB rated, adequate'},
            {'score': 5, 'description': 'B rated, some delays'},
            {'score': 4, 'description': 'CCC rated, frequent delays'},
            {'score': 3, 'description': 'Weak financials, major delays'},
            {'score': 2, 'description': 'Very poor payment record'},
            {'score': 1, 'description': 'Default risk, unreliable'}
        ]
    },
    
    'expected_return': {
        'parameter_name': 'expected_return',
        'display_name': 'Expected Project Returns',
        'subcategory': 'Profitability',
        'output_type': 'score',
        'score_range': (1, 10),
        'definition': (
            'Expected returns for renewable energy projects including IRR, '
            'PPA prices, auction prices, and merchant rates'
        ),
        'key_factors': [
            'Typical project IRR ranges',
            'Equity vs debt returns',
            'Recent auction clearing prices',
            'PPA price levels',
            'Merchant market prices',
            'Developer margins',
            'Risk premiums'
        ],
        'prompt_template': 'expected_return',
        'required_documents': [
            'auction_results',
            'ppa_pricing',
            'market_reports',
            'irr_benchmarks'
        ],
        'validation_rules': {
            'min_justification_length': 30
        },
        'scoring_rubric': [
            {'score': 10, 'description': '>15% IRR, very attractive'},
            {'score': 9, 'description': '12-15% IRR, highly attractive'},
            {'score': 8, 'description': '10-12% IRR, attractive'},
            {'score': 7, 'description': '9-10% IRR, good'},
            {'score': 6, 'description': '8-9% IRR, adequate'},
            {'score': 5, 'description': '7-8% IRR, moderate'},
            {'score': 4, 'description': '6-7% IRR, below target'},
            {'score': 3, 'description': '5-6% IRR, low'},
            {'score': 2, 'description': '4-5% IRR, very low'},
            {'score': 1, 'description': '<4% IRR, unattractive'}
        ]
    },
    
    'long_term_interest_rates': {
        'parameter_name': 'long_term_interest_rates',
        'display_name': 'Long-term Interest Rates',
        'subcategory': 'Profitability',
        'output_type': 'score',
        'score_range': (1, 10),
        'definition': (
            'Long-term interest rates and financing costs for renewable projects'
        ),
        'key_factors': [
            '10-year government bond yields',
            'Project finance lending rates',
            'Debt margin over risk-free rate',
            'Central bank policy rates',
            'Inflation expectations',
            'Currency stability'
        ],
        'required_documents': [
            'central_bank_data',
            'bond_yields',
            'project_finance_terms'
        ],
        'validation_rules': {
            'min_justification_length': 20
        },
        'scoring_rubric': [
            {'score': 10, 'description': '<2% long-term rates'},
            {'score': 9, 'description': '2-3% long-term rates'},
            {'score': 8, 'description': '3-4% long-term rates'},
            {'score': 7, 'description': '4-5% long-term rates'},
            {'score': 6, 'description': '5-6% long-term rates'},
            {'score': 5, 'description': '6-8% long-term rates'},
            {'score': 4, 'description': '8-10% long-term rates'},
            {'score': 3, 'description': '10-12% long-term rates'},
            {'score': 2, 'description': '12-15% long-term rates'},
            {'score': 1, 'description': '>15% long-term rates'}
        ]
    },
    
    # ========================================================================
    # ACCOMMODATION SUBCATEGORY (2 parameters)
    # ========================================================================
    
    'status_of_grid': {
        'parameter_name': 'status_of_grid',
        'display_name': 'Grid Infrastructure Status',
        'subcategory': 'Accommodation',
        'output_type': 'score',
        'score_range': (1, 10),
        'definition': (
            'Grid infrastructure quality, capacity, and reliability for renewable '
            'energy integration'
        ),
        'key_factors': [
            'Transmission and distribution losses (%)',
            'Grid capacity and robustness',
            'System stability',
            'Interconnection capacity',
            'Smart grid deployment',
            'Grid extension plans',
            'Connection timeframes'
        ],
        'prompt_template': 'grid_status',
        'required_documents': [
            'grid_operator_reports',
            'transmission_data',
            'infrastructure_plans'
        ],
        'validation_rules': {
            'min_justification_length': 25
        },
        'scoring_rubric': [
            {'score': 10, 'description': 'Modern, <3% losses, high capacity'},
            {'score': 9, 'description': 'Excellent, 3-5% losses'},
            {'score': 8, 'description': 'Good quality, 5-7% losses'},
            {'score': 7, 'description': 'Adequate, 7-9% losses'},
            {'score': 6, 'description': 'Fair, 9-11% losses'},
            {'score': 5, 'description': 'Moderate, 11-13% losses'},
            {'score': 4, 'description': 'Aging, 13-15% losses'},
            {'score': 3, 'description': 'Poor, 15-18% losses'},
            {'score': 2, 'description': 'Very poor, 18-22% losses'},
            {'score': 1, 'description': 'Critical, >22% losses'}
        ]
    },
    
    'ownership_hurdles': {
        'parameter_name': 'ownership_hurdles',
        'display_name': 'Foreign Ownership Restrictions',
        'subcategory': 'Accommodation',
        'output_type': 'score',
        'score_range': (1, 10),
        'definition': (
            'Foreign ownership restrictions and market access barriers'
        ),
        'key_factors': [
            'Foreign ownership limits (%)',
            'Licensing requirements',
            'Local content requirements',
            'Land acquisition rules',
            'Approval timeframes',
            'Joint venture requirements',
            'Repatriation restrictions'
        ],
        'required_documents': [
            'fdi_regulations',
            'licensing_requirements',
            'investment_laws'
        ],
        'validation_rules': {
            'min_justification_length': 25
        },
        'scoring_rubric': [
            {'score': 10, 'description': '100% FDI allowed, no restrictions'},
            {'score': 9, 'description': '100% FDI, minimal requirements'},
            {'score': 8, 'description': '100% FDI, some local content'},
            {'score': 7, 'description': '75-100% FDI allowed'},
            {'score': 6, 'description': '51-75% FDI allowed'},
            {'score': 5, 'description': '49-51% FDI, JV required'},
            {'score': 4, 'description': '25-49% FDI, strict JV'},
            {'score': 3, 'description': '<25% FDI, major barriers'},
            {'score': 2, 'description': 'Severe restrictions'},
            {'score': 1, 'description': 'Closed to foreign investment'}
        ]
    },
    
    # ========================================================================
    # MARKET SIZE & FUNDAMENTALS SUBCATEGORY (4 parameters)
    # ========================================================================
    
    'power_market_size': {
        'parameter_name': 'power_market_size',
        'display_name': 'Power Market Size',
        'subcategory': 'Market Size & Fundamentals',
        'output_type': 'score',
        'score_range': (1, 10),
        'definition': (
            'Total electricity market size and consumption'
        ),
        'key_factors': [
            'Total electricity consumption (TWh/year)',
            'Peak demand (GW)',
            'Per capita consumption',
            'Growth rates (historical and projected)',
            'Sector breakdown',
            'Market size trends'
        ],
        'prompt_template': 'power_market_size',
        'required_documents': [
            'energy_statistics',
            'market_reports',
            'demand_forecasts'
        ],
        'validation_rules': {
            'min_justification_length': 25
        },
        'scoring_rubric': [
            {'score': 10, 'description': '>1000 TWh/year'},
            {'score': 9, 'description': '500-1000 TWh/year'},
            {'score': 8, 'description': '200-500 TWh/year'},
            {'score': 7, 'description': '100-200 TWh/year'},
            {'score': 6, 'description': '50-100 TWh/year'},
            {'score': 5, 'description': '20-50 TWh/year'},
            {'score': 4, 'description': '10-20 TWh/year'},
            {'score': 3, 'description': '5-10 TWh/year'},
            {'score': 2, 'description': '1-5 TWh/year'},
            {'score': 1, 'description': '<1 TWh/year'}
        ]
    },
    
    'resource_availability': {
        'parameter_name': 'resource_availability',
        'display_name': 'Renewable Resource Quality',
        'subcategory': 'Market Size & Fundamentals',
        'output_type': 'score',
        'score_range': (1, 10),
        'definition': (
            'Quality and availability of renewable energy resources (solar, wind, hydro)'
        ),
        'key_factors': [
            'Solar: GHI in kWh/m²/day',
            'Wind: Wind speeds at hub height (m/s)',
            'Hydro: River flows and precipitation',
            'Land availability and suitability',
            'Geographic diversity',
            'Seasonal variations'
        ],
        'prompt_template': 'resource_availability',
        'required_documents': [
            'resource_atlas',
            'gis_data',
            'meteorological_data'
        ],
        'validation_rules': {
            'min_justification_length': 25
        },
        'scoring_rubric': [
            {'score': 10, 'description': 'Excellent resources (solar >6 or wind >9 m/s)'},
            {'score': 9, 'description': 'Very good (solar 5.5-6 or wind 8-9)'},
            {'score': 8, 'description': 'Good (solar 5-5.5 or wind 7-8)'},
            {'score': 7, 'description': 'Above average (solar 4.5-5 or wind 6-7)'},
            {'score': 6, 'description': 'Average (solar 4-4.5 or wind 5-6)'},
            {'score': 5, 'description': 'Below average (solar 3.5-4 or wind 4-5)'},
            {'score': 4, 'description': 'Fair (solar 3-3.5 or wind 3-4)'},
            {'score': 3, 'description': 'Poor (solar 2.5-3 or wind 2-3)'},
            {'score': 2, 'description': 'Very poor (solar 2-2.5 or wind 1-2)'},
            {'score': 1, 'description': 'Minimal (solar <2 or wind <1)'}
        ]
    },
    
    'energy_dependence': {
        'parameter_name': 'energy_dependence',
        'display_name': 'Energy Import Dependency',
        'subcategory': 'Market Size & Fundamentals',
        'output_type': 'score',
        'score_range': (1, 10),
        'definition': (
            'Energy import dependency and security concerns'
        ),
        'key_factors': [
            'Energy import dependency (%)',
            'Fossil fuel import reliance',
            'Domestic resource availability',
            'Energy security concerns',
            'Trade balance impact',
            'Supply chain vulnerabilities'
        ],
        'required_documents': [
            'energy_statistics',
            'import_data',
            'security_assessments'
        ],
        'validation_rules': {
            'min_justification_length': 25
        },
        'scoring_rubric': [
            {'score': 10, 'description': '>80% import dependent, high urgency'},
            {'score': 9, 'description': '70-80% import dependent'},
            {'score': 8, 'description': '60-70% import dependent'},
            {'score': 7, 'description': '50-60% import dependent'},
            {'score': 6, 'description': '40-50% import dependent'},
            {'score': 5, 'description': '30-40% import dependent'},
            {'score': 4, 'description': '20-30% import dependent'},
            {'score': 3, 'description': '10-20% import dependent'},
            {'score': 2, 'description': '5-10% import dependent'},
            {'score': 1, 'description': '<5% import dependent, self-sufficient'}
        ]
    },
    
    'renewables_penetration': {
        'parameter_name': 'renewables_penetration',
        'display_name': 'Current Renewables Share',
        'subcategory': 'Market Size & Fundamentals',
        'output_type': 'percentage',
        'score_range': (0, 100),
        'definition': (
            'Current renewable energy share in electricity generation'
        ),
        'key_factors': [
            'RE share in electricity (%)',
            'RE share in total energy (%)',
            'Technology breakdown',
            'Growth trajectory',
            'Seasonal variations',
            'Grid integration levels'
        ],
        'required_documents': [
            'generation_statistics',
            'grid_data',
            'energy_mix_reports'
        ],
        'validation_rules': {
            'min_justification_length': 20
        },
        'scoring_rubric': [
            {'score': 10, 'description': '>80% renewables'},
            {'score': 9, 'description': '60-80% renewables'},
            {'score': 8, 'description': '50-60% renewables'},
            {'score': 7, 'description': '40-50% renewables'},
            {'score': 6, 'description': '30-40% renewables'},
            {'score': 5, 'description': '20-30% renewables'},
            {'score': 4, 'description': '15-20% renewables'},
            {'score': 3, 'description': '10-15% renewables'},
            {'score': 2, 'description': '5-10% renewables'},
            {'score': 1, 'description': '<5% renewables'}
        ]
    },
    
    # ========================================================================
    # COMPETITION & EASE SUBCATEGORY (2 parameters)
    # ========================================================================
    
    'ownership_consolidation': {
        'parameter_name': 'ownership_consolidation',
        'display_name': 'Market Concentration',
        'subcategory': 'Competition & Ease of Business',
        'output_type': 'score',
        'score_range': (1, 10),
        'definition': (
            'Market concentration and competition level in renewable energy sector'
        ),
        'key_factors': [
            'Market share of top 3 players',
            'HHI index (if available)',
            'Number of active developers',
            'Barriers to entry',
            'Vertical integration',
            'Market dynamics'
        ],
        'required_documents': [
            'market_reports',
            'developer_databases',
            'competition_analysis'
        ],
        'validation_rules': {
            'min_justification_length': 25
        },
        'scoring_rubric': [
            {'score': 10, 'description': 'Highly fragmented, many players'},
            {'score': 9, 'description': 'Competitive, diverse players'},
            {'score': 8, 'description': 'Good competition'},
            {'score': 7, 'description': 'Moderate competition'},
            {'score': 6, 'description': 'Some concentration'},
            {'score': 5, 'description': 'Moderately concentrated'},
            {'score': 4, 'description': 'Concentrated, few players'},
            {'score': 3, 'description': 'Oligopolistic'},
            {'score': 2, 'description': 'Highly concentrated'},
            {'score': 1, 'description': 'Monopolistic'}
        ]
    },
    
    'competitive_landscape': {
        'parameter_name': 'competitive_landscape',
        'display_name': 'Market Entry Ease',
        'subcategory': 'Competition & Ease of Business',
        'output_type': 'score',
        'score_range': (1, 10),
        'definition': (
            'Ease of market entry and competitive dynamics'
        ),
        'key_factors': [
            'Number of auction participants',
            'Foreign vs domestic developers',
            'Technology competition',
            'Permit and licensing ease',
            'Land availability',
            'Barriers to entry'
        ],
        'prompt_template': 'competitive_landscape',
        'required_documents': [
            'auction_data',
            'market_reports',
            'regulatory_analysis'
        ],
        'validation_rules': {
            'min_justification_length': 25
        },
        'scoring_rubric': [
            {'score': 10, 'description': 'Very easy entry, highly competitive'},
            {'score': 9, 'description': 'Easy entry, competitive'},
            {'score': 8, 'description': 'Accessible, good competition'},
            {'score': 7, 'description': 'Moderate barriers, fair competition'},
            {'score': 6, 'description': 'Some barriers'},
            {'score': 5, 'description': 'Notable barriers'},
            {'score': 4, 'description': 'Significant barriers'},
            {'score': 3, 'description': 'High barriers'},
            {'score': 2, 'description': 'Very high barriers'},
            {'score': 1, 'description': 'Closed/restricted market'}
        ]
    },
    
    # ========================================================================
    # SYSTEM MODIFIERS SUBCATEGORY (1 composite parameter)
    # ========================================================================
    
    'system_modifiers': {
        'parameter_name': 'system_modifiers',
        'display_name': 'System/External Modifiers',
        'subcategory': 'System/External Modifiers',
        'output_type': 'score',
        'score_range': (1, 10),
        'definition': (
            'Composite assessment of external factors: cannibalization, curtailment, '
            'queue dynamics, and supply chain'
        ),
        'key_factors': [
            'Price cannibalization risk',
            'Curtailment rates and frequency',
            'Interconnection queue length',
            'Queue processing time',
            'Supply chain constraints',
            'Component availability',
            'Logistics and infrastructure'
        ],
        'required_documents': [
            'grid_reports',
            'market_data',
            'supply_chain_analysis'
        ],
        'validation_rules': {
            'min_justification_length': 30
        },
        'scoring_rubric': [
            {'score': 10, 'description': 'Minimal issues, favorable conditions'},
            {'score': 9, 'description': 'Very good conditions'},
            {'score': 8, 'description': 'Good conditions, minor issues'},
            {'score': 7, 'description': 'Adequate, manageable issues'},
            {'score': 6, 'description': 'Moderate challenges'},
            {'score': 5, 'description': 'Notable challenges'},
            {'score': 4, 'description': 'Significant issues'},
            {'score': 3, 'description': 'Major challenges'},
            {'score': 2, 'description': 'Severe constraints'},
            {'score': 1, 'description': 'Critical issues'}
        ]
    }
}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_config(parameter_name: str) -> Dict[str, Any]:
    """Get configuration for a parameter.
    
    Args:
        parameter_name: Parameter name
        
    Returns:
        Parameter configuration dictionary
        
    Raises:
        KeyError: If parameter not found
    """
    if parameter_name not in PARAMETER_CONFIGS:
        raise KeyError(
            f"Parameter '{parameter_name}' not found. "
            f"Available: {list(PARAMETER_CONFIGS.keys())}"
        )
    
    return PARAMETER_CONFIGS[parameter_name]


def list_parameters() -> List[str]:
    """Get list of all configured parameters.
    
    Returns:
        List of parameter names
    """
    return list(PARAMETER_CONFIGS.keys())


def get_parameters_by_subcategory(subcategory: str) -> List[str]:
    """Get parameters for a specific subcategory.
    
    Args:
        subcategory: Subcategory name
        
    Returns:
        List of parameter names in that subcategory
    """
    return [
        param_name
        for param_name, config in PARAMETER_CONFIGS.items()
        if config['subcategory'] == subcategory
    ]


def validate_config(config: Dict[str, Any]) -> bool:
    """Validate a parameter configuration.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        True if valid, raises ValueError otherwise
    """
    required_fields = [
        'parameter_name', 'subcategory', 'output_type',
        'definition', 'key_factors'
    ]
    
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required field: {field}")
    
    return True


# Summary statistics
TOTAL_PARAMETERS = len(PARAMETER_CONFIGS)
SUBCATEGORIES = list(set(config['subcategory'] for config in PARAMETER_CONFIGS.values()))

print(f"Loaded {TOTAL_PARAMETERS} parameter configurations")
print(f"Subcategories: {', '.join(SUBCATEGORIES)}")
