"""Parsers for Profitability subcategory parameters.

Profitability parameters:
1. Expected Return - IRR, ROE, return metrics
2. Revenue Stream Stability - Revenue volatility, contract coverage
3. Offtaker Status - Offtaker creditworthiness, payment history
4. Long Term Interest Rates - Benchmark rates, cost of capital
"""
from typing import Dict, Any
from .base_parser import BaseParser
import logging

logger = logging.getLogger(__name__)


class ExpectedReturnParser(BaseParser):
    """Parser for Expected Return - extracts return metrics."""

    def __init__(self):
        super().__init__(parameter_name="Expected Return")

    def parse(self, research_doc) -> Dict[str, Any]:
        """Extract IRR, ROE, and other return metrics.

        Returns:
            {
                'irr_percent': float,  # Internal Rate of Return
                'roe_percent': float,  # Return on Equity
                'payback_period_years': float,
                'lcoe_usd_per_mwh': float,  # Levelized Cost of Energy
                'source': 'research',
                ...
            }
        """
        metrics = self._get_metrics(research_doc)

        # Look for IRR
        irr_keywords = ['irr', 'internal rate of return', 'project irr']
        irr_metric = self._find_metric(metrics, irr_keywords)
        irr_percent = self._extract_numeric_value(irr_metric, 8.0) if irr_metric else 8.0

        # Look for ROE
        roe_keywords = ['roe', 'return on equity']
        roe_metric = self._find_metric(metrics, roe_keywords)
        roe_percent = self._extract_numeric_value(roe_metric, 10.0) if roe_metric else 10.0

        # Look for payback period
        payback_keywords = ['payback', 'payback period', 'recovery period']
        payback_metric = self._find_metric(metrics, payback_keywords)
        payback_period = self._extract_numeric_value(payback_metric, 12.0) if payback_metric else 12.0

        # Look for LCOE
        lcoe_keywords = ['lcoe', 'levelized cost', 'cost of energy']
        lcoe_metric = self._find_metric(metrics, lcoe_keywords)
        lcoe = self._extract_numeric_value(lcoe_metric, 50.0) if lcoe_metric else 50.0

        return self._create_base_response(
            research_doc,
            additional_data={
                'irr_percent': irr_percent,
                'roe_percent': roe_percent,
                'payback_period_years': payback_period,
                'lcoe_usd_per_mwh': lcoe
            }
        )


class RevenueStreamStabilityParser(BaseParser):
    """Parser for Revenue Stream Stability - extracts revenue metrics."""

    def __init__(self):
        super().__init__(parameter_name="Revenue Stream Stability")

    def parse(self, research_doc) -> Dict[str, Any]:
        """Extract revenue stability metrics.

        Returns:
            {
                'contract_coverage_percent': float,  # % of revenue under contract
                'revenue_volatility_percent': float,  # Revenue volatility
                'merchant_exposure_percent': float,  # % exposed to merchant prices
                'avg_ppa_term_years': int,
                'source': 'research',
                ...
            }
        """
        metrics = self._get_metrics(research_doc)

        # Look for contract coverage
        coverage_keywords = ['contract coverage', 'contracted revenue', 'ppa coverage']
        coverage_metric = self._find_metric(metrics, coverage_keywords)
        contract_coverage = self._extract_numeric_value(coverage_metric, 70.0) if coverage_metric else 70.0

        # Look for volatility
        volatility_keywords = ['volatility', 'revenue risk', 'price risk']
        volatility_metric = self._find_metric(metrics, volatility_keywords)
        revenue_volatility = self._extract_numeric_value(volatility_metric, 15.0) if volatility_metric else 15.0

        # Merchant exposure
        merchant_keywords = ['merchant', 'spot market', 'market exposure']
        merchant_metric = self._find_metric(metrics, merchant_keywords)
        merchant_exposure = self._extract_numeric_value(merchant_metric, 30.0) if merchant_metric else 30.0

        # PPA term
        term_keywords = ['ppa term', 'contract term', 'ppa duration']
        term_metric = self._find_metric(metrics, term_keywords)
        avg_ppa_term = int(self._extract_numeric_value(term_metric, 15)) if term_metric else 15

        return self._create_base_response(
            research_doc,
            additional_data={
                'contract_coverage_percent': contract_coverage,
                'revenue_volatility_percent': revenue_volatility,
                'merchant_exposure_percent': merchant_exposure,
                'avg_ppa_term_years': avg_ppa_term
            }
        )


class OfftakerStatusParser(BaseParser):
    """Parser for Offtaker Status - extracts creditworthiness metrics."""

    def __init__(self):
        super().__init__(parameter_name="Offtaker Status")

    def parse(self, research_doc) -> Dict[str, Any]:
        """Extract offtaker credit and payment metrics.

        Returns:
            {
                'credit_rating': str,  # AAA, AA, A, BBB, etc.
                'payment_history_score': float,  # 0-10
                'default_risk_percent': float,
                'offtaker_type': str,  # utility, corporate, government
                'source': 'research',
                ...
            }
        """
        metrics = self._get_metrics(research_doc)

        # Look for credit rating
        rating_keywords = ['credit rating', 'creditworthiness', 'credit score']
        rating_metric = self._find_metric(metrics, rating_keywords)

        if rating_metric:
            credit_rating = str(rating_metric.get('value', 'BBB'))
        else:
            credit_rating = "BBB"  # Default investment grade

        # Look for payment history
        payment_keywords = ['payment history', 'payment performance', 'on-time payment']
        payment_metric = self._find_metric(metrics, payment_keywords)
        payment_score = self._extract_numeric_value(payment_metric, 7.0) if payment_metric else 7.0

        # Look for default risk
        risk_keywords = ['default risk', 'credit risk', 'payment risk']
        risk_metric = self._find_metric(metrics, risk_keywords)
        default_risk = self._extract_numeric_value(risk_metric, 5.0) if risk_metric else 5.0

        # Infer offtaker type from overview
        overview = self._get_overview(research_doc).lower()
        if 'utility' in overview or 'power company' in overview:
            offtaker_type = "Utility"
        elif 'corporate' in overview or 'company' in overview:
            offtaker_type = "Corporate"
        elif 'government' in overview or 'state' in overview:
            offtaker_type = "Government"
        else:
            offtaker_type = "Mixed"

        return self._create_base_response(
            research_doc,
            additional_data={
                'credit_rating': credit_rating,
                'payment_history_score': payment_score,
                'default_risk_percent': default_risk,
                'offtaker_type': offtaker_type
            }
        )


class LongTermInterestRatesParser(BaseParser):
    """Parser for Long Term Interest Rates - extracts benchmark rates."""

    def __init__(self):
        super().__init__(parameter_name="Long Term Interest Rates")

    def parse(self, research_doc) -> Dict[str, Any]:
        """Extract long-term interest rates and cost of capital.

        Returns:
            {
                'benchmark_rate_percent': float,  # 10-year government bond
                'corporate_bond_rate_percent': float,
                'inflation_rate_percent': float,
                'real_rate_percent': float,  # Nominal - inflation
                'source': 'research',
                ...
            }
        """
        metrics = self._get_metrics(research_doc)

        # Look for benchmark rate (10-year government bond)
        benchmark_keywords = ['10-year', 'government bond', 'treasury', 'benchmark rate']
        benchmark_metric = self._find_metric(metrics, benchmark_keywords)
        benchmark_rate = self._extract_numeric_value(benchmark_metric, 4.0) if benchmark_metric else 4.0

        # Look for corporate bond rate
        corporate_keywords = ['corporate bond', 'corporate rate', 'investment grade']
        corporate_metric = self._find_metric(metrics, corporate_keywords)
        corporate_rate = self._extract_numeric_value(corporate_metric, 5.0) if corporate_metric else 5.0

        # Look for inflation
        inflation_keywords = ['inflation', 'cpi', 'consumer price']
        inflation_metric = self._find_metric(metrics, inflation_keywords)
        inflation_rate = self._extract_numeric_value(inflation_metric, 2.5) if inflation_metric else 2.5

        # Calculate real rate
        real_rate = benchmark_rate - inflation_rate

        return self._create_base_response(
            research_doc,
            additional_data={
                'benchmark_rate_percent': benchmark_rate,
                'corporate_bond_rate_percent': corporate_rate,
                'inflation_rate_percent': inflation_rate,
                'real_rate_percent': real_rate
            }
        )
