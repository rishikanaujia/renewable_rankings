"""Research Orchestrator - High-level coordinator for research system

Coordinates between ResearchAgent, ResearchStore, and VersionManager to:
- Generate research on-demand or from cache
- Manage versioning and storage
- Provide convenient API for agents
"""
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
from pathlib import Path
import yaml

from .research_agent import ResearchAgent
from .storage.research_store import ResearchStore, ResearchDocument
from .version_manager import ChangeType, VersionStrategy
from .prompt_generator import PromptGenerator

logger = logging.getLogger(__name__)


class ResearchOrchestrator:
    """High-level orchestrator for the research system."""

    def __init__(
        self,
        config_path: str = "research_system/config/research_config.yaml",
        force_new_research: bool = False
    ):
        """Initialize research orchestrator.

        Args:
            config_path: Path to research configuration file
            force_new_research: If True, always generate new research (ignore cache)
        """
        self.config = self._load_config(config_path)
        self.force_new_research = force_new_research

        # Initialize components
        self.prompt_generator = PromptGenerator()
        self.research_agent = ResearchAgent(
            llm_config=self.config.get('llm'),
            prompt_generator=self.prompt_generator
        )
        self.research_store = ResearchStore(
            base_path=self.config.get('storage', {}).get('base_path',
                                                          'research_system/data/research_documents'),
            cache_ttl=self.config.get('cache', {}).get('ttl', 604800),
            version_strategy=VersionStrategy(
                self.config.get('storage', {}).get('versioning', {}).get('strategy', 'semantic')
            )
        )

        logger.info("ResearchOrchestrator initialized")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load research system configuration.

        Args:
            config_path: Path to config file

        Returns:
            Configuration dictionary
        """
        config_file = Path(config_path)

        if not config_file.exists():
            logger.warning(f"Config not found: {config_path}, using defaults")
            return {}

        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)

        return config

    def get_research(
        self,
        parameter: str,
        country: str,
        period: Optional[str] = None,
        use_cache: bool = True,
        additional_context: Optional[str] = None
    ) -> ResearchDocument:
        """Get research document for parameter-country combination.

        This is the main entry point. It will:
        1. Check cache if use_cache=True
        2. Generate new research if needed
        3. Store and version the result

        Args:
            parameter: Parameter name
            country: Country name
            period: Time period (defaults to current quarter)
            use_cache: Whether to use cached research
            additional_context: Additional research context

        Returns:
            ResearchDocument with content and metadata
        """
        if period is None:
            period = datetime.now().strftime("Q%m %Y")

        logger.info(f"Getting research: {parameter}/{country} ({period})")

        # Check cache
        if use_cache and not self.force_new_research:
            if self.research_store.is_cache_valid(parameter, country):
                logger.info(f"Using cached research for {parameter}/{country}")
                cached = self.research_store.load(parameter, country)
                if cached:
                    return cached

        # Generate new research
        logger.info(f"Generating new research for {parameter}/{country}")
        research_content = self.research_agent.conduct_research(
            parameter=parameter,
            country=country,
            period=period,
            additional_context=additional_context
        )

        # Validate quality
        validation = self.research_agent.validate_research_quality(research_content)
        research_content['_validation'] = validation

        logger.info(
            f"Research quality: {validation['grade']} "
            f"(overall: {validation['scores']['overall']:.2f})"
        )

        # Determine change type based on existing version
        existing_version = self.research_store.version_manager.get_latest_version(parameter, country)
        if existing_version is None:
            change_type = ChangeType.MAJOR  # First version
        else:
            # For now, default to MINOR for updates
            # In future, could compare content to determine change type
            change_type = ChangeType.MINOR

        # Store research
        version = self.research_store.save(
            parameter=parameter,
            country=country,
            period=period,
            content=research_content,
            change_type=change_type,
            change_description=f"Research for {period}"
        )

        # Load and return the stored document
        return self.research_store.load(parameter, country, version)

    def batch_generate_research(
        self,
        parameters: List[str],
        countries: List[str],
        period: Optional[str] = None,
        use_cache: bool = True
    ) -> Dict[str, ResearchDocument]:
        """Generate research for multiple parameter-country combinations.

        Args:
            parameters: List of parameter names
            countries: List of country names
            period: Time period
            use_cache: Whether to use cached research

        Returns:
            Dictionary mapping "parameter|country" to ResearchDocument
        """
        results = {}
        total = len(parameters) * len(countries)
        current = 0

        logger.info(f"Starting batch research: {len(parameters)} params × {len(countries)} countries = {total} total")

        for parameter in parameters:
            for country in countries:
                current += 1
                key = f"{parameter}|{country}"

                logger.info(f"[{current}/{total}] Processing {key}")

                try:
                    doc = self.get_research(
                        parameter=parameter,
                        country=country,
                        period=period,
                        use_cache=use_cache
                    )
                    results[key] = doc
                except Exception as e:
                    logger.error(f"Failed to get research for {key}: {e}")
                    # Continue with next item
                    continue

        success_count = len(results)
        logger.info(f"Batch research complete: {success_count}/{total} successful")

        return results

    def generate_all_prompts(self) -> Dict[str, str]:
        """Generate and save prompts for all parameters.

        Returns:
            Dictionary mapping parameter names to prompt templates
        """
        logger.info("Generating prompts for all parameters...")
        prompts = self.prompt_generator.generate_all_prompts()
        logger.info(f"Generated {len(prompts)} parameter prompts")
        return prompts

    def get_available_research(self) -> List[Dict[str, str]]:
        """Get list of all available research documents.

        Returns:
            List of dictionaries with parameter, country, version
        """
        return self.research_store.list_all_research()

    def search_research(
        self,
        parameter: Optional[str] = None,
        country: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Search for research by parameter or country.

        Args:
            parameter: Filter by parameter (None for all)
            country: Filter by country (None for all)

        Returns:
            List of matching research documents
        """
        if parameter:
            return self.research_store.search_by_parameter(parameter)
        elif country:
            return self.research_store.search_by_country(country)
        else:
            return self.research_store.list_all_research()

    def get_version_history(
        self,
        parameter: str,
        country: str
    ) -> List[Dict[str, Any]]:
        """Get version history for a parameter-country combination.

        Args:
            parameter: Parameter name
            country: Country name

        Returns:
            List of version metadata dictionaries
        """
        history = self.research_store.get_version_history(parameter, country)
        return [h.to_dict() for h in history]

    def cleanup_old_versions(self, keep_count: int = 5) -> Dict[str, int]:
        """Clean up old versions across all research documents.

        Args:
            keep_count: Number of versions to keep per document

        Returns:
            Dictionary with cleanup statistics
        """
        logger.info(f"Cleaning up old versions (keeping {keep_count} per document)...")

        all_research = self.research_store.list_all_research()
        total_deleted = 0
        cleaned_docs = 0

        for item in all_research:
            deleted = self.research_store.cleanup_old_versions(
                parameter=item['parameter'],
                country=item['country'],
                keep_count=keep_count
            )
            if deleted > 0:
                total_deleted += deleted
                cleaned_docs += 1

        logger.info(f"Cleanup complete: {total_deleted} versions deleted from {cleaned_docs} documents")

        return {
            'total_deleted': total_deleted,
            'cleaned_documents': cleaned_docs,
            'total_documents': len(all_research)
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics.

        Returns:
            Dictionary with statistics from all components
        """
        storage_stats = self.research_store.get_statistics()
        agent_stats = self.research_agent.get_stats()

        return {
            'storage': storage_stats,
            'agent': agent_stats,
            'cache': {
                'ttl_seconds': self.research_store.cache_ttl,
                'enabled': self.config.get('cache', {}).get('enabled', True)
            }
        }

    def export_research(
        self,
        parameter: str,
        country: str,
        version: Optional[str] = None,
        format: str = 'json'
    ) -> str:
        """Export research document to string format.

        Args:
            parameter: Parameter name
            country: Country name
            version: Version (None for latest)
            format: Export format ('json' or 'markdown')

        Returns:
            Formatted research string
        """
        doc = self.research_store.load(parameter, country, version)

        if doc is None:
            raise ValueError(f"No research found for {parameter}/{country}")

        if format == 'json':
            import json
            return json.dumps(doc.to_dict(), indent=2)
        elif format == 'markdown':
            return self._format_as_markdown(doc)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _format_as_markdown(self, doc: ResearchDocument) -> str:
        """Format research document as markdown.

        Args:
            doc: ResearchDocument

        Returns:
            Markdown formatted string
        """
        content = doc.content
        md = f"# {content.get('parameter', 'Unknown')} - {content.get('country', 'Unknown')}\n\n"
        md += f"**Period:** {content.get('period', 'Unknown')}  \n"
        md += f"**Version:** {doc.version}  \n"
        md += f"**Research Date:** {content.get('research_date', 'Unknown')}  \n\n"

        sections = [
            ('Overview', 'overview'),
            ('Current Status', 'current_status'),
            ('Historical Trends', 'historical_trends'),
            ('Policy Framework', 'policy_framework'),
            ('Challenges', 'challenges'),
            ('Opportunities', 'opportunities'),
            ('Future Outlook', 'future_outlook')
        ]

        for title, key in sections:
            if key in content and content[key]:
                md += f"## {title}\n\n{content[key]}\n\n"

        # Add key metrics
        if 'key_metrics' in content and content['key_metrics']:
            md += "## Key Metrics\n\n"
            for metric in content['key_metrics']:
                if isinstance(metric, dict):
                    md += f"- **{metric.get('metric', 'N/A')}:** {metric.get('value', 'N/A')} {metric.get('unit', '')} "
                    md += f"*(Source: {metric.get('source', 'N/A')})*\n"
            md += "\n"

        # Add sources
        if 'sources' in content and content['sources']:
            md += "## Sources\n\n"
            for i, source in enumerate(content['sources'], 1):
                if isinstance(source, dict):
                    md += f"{i}. [{source.get('name', 'N/A')}]({source.get('url', '#')})\n"
            md += "\n"

        return md
