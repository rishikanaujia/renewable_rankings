"""Prompt Generator - Creates parameter-specific research prompts from parameters.yaml

Reads parameter definitions and scoring criteria to generate tailored research prompts
for each parameter-country combination.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class PromptGenerator:
    """Generates parameter-specific research prompts from configuration."""

    def __init__(
        self,
        parameters_config_path: str = "config/parameters.yaml",
        base_template_path: str = "research_system/prompts/base_research_template.txt",
        output_dir: str = "research_system/prompts/generated"
    ):
        """Initialize prompt generator.

        Args:
            parameters_config_path: Path to parameters.yaml
            base_template_path: Path to base research template
            output_dir: Directory to save generated prompts
        """
        self.parameters_config_path = Path(parameters_config_path)
        self.base_template_path = Path(base_template_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load configurations
        self.parameters = self._load_parameters()
        self.base_template = self._load_base_template()

        logger.info(f"PromptGenerator initialized with {len(self.parameters)} parameters")

    def _load_parameters(self) -> Dict[str, Any]:
        """Load parameters from parameters.yaml.

        Returns:
            Dictionary of parameter definitions
        """
        if not self.parameters_config_path.exists():
            raise FileNotFoundError(f"Parameters config not found: {self.parameters_config_path}")

        with open(self.parameters_config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Extract parameters from the config structure
        parameters = {}

        # Handle flat structure: parameters.yaml has parameters as top-level dict
        if 'parameters' in config:
            for param_key, param_data in config['parameters'].items():
                if isinstance(param_data, dict):
                    param_name = param_data.get('name', param_key.title().replace('_', ' '))
                    parameters[param_name] = {
                        'name': param_name,
                        'key': param_key,
                        'subcategory': param_data.get('subcategory', 'unknown'),
                        'level': param_data.get('level', 1),
                        'description': param_data.get('description', ''),
                        'scoring_levels': param_data.get('scoring', []),
                        'data_sources': param_data.get('data_sources', []),
                    }

        # Also handle nested structure if present (for backwards compatibility)
        elif 'categories' in config:
            for category_name, category_data in config['categories'].items():
                if 'parameters' in category_data:
                    for param in category_data['parameters']:
                        param_name = param.get('name')
                        if param_name:
                            parameters[param_name] = {
                                'name': param_name,
                                'category': category_name,
                                'description': param.get('description', ''),
                                'weight': param.get('weight', 1.0),
                                'scoring_levels': param.get('scoring_levels', []),
                                'data_sources': param.get('data_sources', []),
                                'subcategory': category_data.get('name', category_name)
                            }

        logger.debug(f"Loaded {len(parameters)} parameters from config")
        return parameters

    def _load_base_template(self) -> str:
        """Load base research template.

        Returns:
            Template string
        """
        if not self.base_template_path.exists():
            raise FileNotFoundError(f"Base template not found: {self.base_template_path}")

        with open(self.base_template_path, 'r') as f:
            template = f.read()

        return template

    def generate_prompt(
        self,
        parameter_name: str,
        country: str,
        period: str = None
    ) -> str:
        """Generate a research prompt for a specific parameter-country combination.

        Args:
            parameter_name: Name of the parameter (e.g., "Ambition")
            country: Country name
            period: Time period (e.g., "Q3 2024")

        Returns:
            Formatted research prompt string
        """
        if parameter_name not in self.parameters:
            raise ValueError(f"Parameter '{parameter_name}' not found in configuration")

        param = self.parameters[parameter_name]

        # Use current period if not specified
        if period is None:
            period = datetime.now().strftime("Q%m %Y")

        # Format parameter description
        description = self._format_description(param)

        # Format scoring criteria
        scoring_criteria = self._format_scoring_criteria(param)

        # Fill in the template
        prompt = self.base_template.format(
            parameter_name=parameter_name,
            country=country,
            period=period,
            parameter_description=description,
            scoring_criteria=scoring_criteria
        )

        return prompt

    def _format_description(self, param: Dict[str, Any]) -> str:
        """Format parameter description.

        Args:
            param: Parameter dictionary

        Returns:
            Formatted description string
        """
        description = param.get('description', 'No description available.')

        # Add category context
        subcategory = param.get('subcategory', 'Unknown')
        level = param.get('level', 'Unknown')

        formatted = f"{description}\n\n"
        formatted += f"Subcategory: {subcategory.title()}\n"
        formatted += f"Level: {level}\n"

        # Add weight if available (old format)
        if 'weight' in param:
            formatted += f"Weight: {param.get('weight', 1.0)}\n"

        # Add data sources if available
        data_sources = param.get('data_sources', [])
        if data_sources:
            formatted += f"\nTypical Data Sources:\n"
            for source in data_sources:
                formatted += f"  - {source}\n"

        return formatted

    def _format_scoring_criteria(self, param: Dict[str, Any]) -> str:
        """Format scoring criteria from parameter definition.

        Args:
            param: Parameter dictionary

        Returns:
            Formatted scoring criteria string
        """
        scoring_levels = param.get('scoring_levels', [])

        if not scoring_levels:
            return "No specific scoring criteria defined. Use general assessment based on parameter context."

        criteria = "SCORING RUBRIC (1-10 scale):\n\n"

        for level in scoring_levels:
            # Handle both old and new formats
            score = level.get('value') or level.get('score', '?')
            description = level.get('description', 'No description')

            # New format has 'range' field
            range_str = level.get('range', '')

            # Old format has 'threshold' field
            threshold = level.get('threshold', '')

            # Build criteria entry
            criteria += f"Score {score}: {description}\n"

            if range_str:
                criteria += f"           Range: {range_str}\n"
            elif threshold:
                criteria += f"           Threshold: {threshold}\n"

            # Add specific bounds if available
            if 'min_gw' in level or 'max_gw' in level:
                min_val = level.get('min_gw', '?')
                max_val = level.get('max_gw', '?')
                criteria += f"           [{min_val} - {max_val} GW]\n"

            criteria += "\n"

        return criteria

    def generate_all_prompts(self) -> Dict[str, str]:
        """Generate prompts for all parameters.

        Returns:
            Dictionary mapping parameter names to their base prompts
        """
        prompts = {}

        for param_name in self.parameters:
            # Generate a generic prompt (country and period as placeholders)
            prompt = self.generate_prompt(
                parameter_name=param_name,
                country="{country}",
                period="{period}"
            )
            prompts[param_name] = prompt

            # Save to file
            output_path = self.output_dir / f"{param_name.lower().replace(' ', '_')}_prompt.txt"
            with open(output_path, 'w') as f:
                f.write(prompt)

            logger.debug(f"Generated prompt for {param_name} -> {output_path}")

        logger.info(f"Generated {len(prompts)} parameter prompts")
        return prompts

    def get_parameter_info(self, parameter_name: str) -> Dict[str, Any]:
        """Get full parameter information.

        Args:
            parameter_name: Parameter name

        Returns:
            Parameter configuration dictionary
        """
        if parameter_name not in self.parameters:
            raise ValueError(f"Parameter '{parameter_name}' not found")

        return self.parameters[parameter_name]

    def list_parameters(self) -> list:
        """List all available parameters.

        Returns:
            List of parameter names
        """
        return list(self.parameters.keys())

    def get_parameters_by_category(self, category: str) -> list:
        """Get parameters in a specific category/subcategory.

        Args:
            category: Category or subcategory name

        Returns:
            List of parameter names in the category
        """
        category_lower = category.lower()
        return [
            name for name, param in self.parameters.items()
            if (param.get('category', '').lower() == category_lower or
                param.get('subcategory', '').lower() == category_lower)
        ]
