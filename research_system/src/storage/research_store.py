"""Research Store - Persistent storage for versioned research documents

Handles saving, loading, and querying research documents with:
- Versioned storage
- Metadata tracking
- Cache management
- Query capabilities
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime, timedelta
import json
import hashlib
import logging
from dataclasses import dataclass, asdict

from ..version_manager import VersionManager, VersionMetadata, ChangeType, VersionStrategy

logger = logging.getLogger(__name__)


@dataclass
class ResearchDocument:
    """Research document with metadata."""
    parameter: str
    country: str
    period: str
    version: str
    content: Dict[str, Any]
    created_at: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class ResearchStore:
    """Persistent storage for research documents with versioning."""

    def __init__(
        self,
        base_path: str = "research_system/data/research_documents",
        cache_ttl: int = 604800,  # 7 days
        version_strategy: VersionStrategy = VersionStrategy.SEMANTIC
    ):
        """Initialize research store.

        Args:
            base_path: Base directory for research documents
            cache_ttl: Cache time-to-live in seconds
            version_strategy: Versioning strategy
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.cache_ttl = cache_ttl

        # Initialize version manager
        self.version_manager = VersionManager(
            strategy=version_strategy,
            base_path=str(self.base_path)
        )

        logger.info(f"ResearchStore initialized at {self.base_path}")

    def save(
        self,
        parameter: str,
        country: str,
        period: str,
        content: Dict[str, Any],
        change_type: ChangeType = ChangeType.MINOR,
        change_description: Optional[str] = None
    ) -> str:
        """Save a new research document with automatic versioning.

        Args:
            parameter: Parameter name
            country: Country name
            period: Time period
            content: Research document content
            change_type: Type of change (for semantic versioning)
            change_description: Description of changes

        Returns:
            Version string of saved document
        """
        # Get latest version and calculate next
        current_version = self.version_manager.get_latest_version(parameter, country)
        new_version = self.version_manager.get_next_version(current_version, change_type)

        # Create version directory
        version_path = self.version_manager.create_version_directory(
            parameter, country, new_version
        )

        # Save research content
        content_file = version_path / "research.json"
        try:
            with open(content_file, 'w') as f:
                json.dump(content, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving research content: {e}")
            raise

        # Calculate checksum
        checksum = self._calculate_checksum(content)

        # Create and save metadata
        metadata = VersionMetadata(
            version=new_version,
            created_at=datetime.now().isoformat(),
            change_type=change_type.value if isinstance(change_type, ChangeType) else change_type,
            change_description=change_description,
            parameter=parameter,
            country=country,
            period=period,
            file_path=str(content_file),
            file_size=content_file.stat().st_size,
            checksum=checksum
        )

        self.version_manager.save_version_metadata(
            parameter, country, new_version, metadata
        )

        logger.info(
            f"Saved research document: {parameter}/{country} "
            f"version {new_version} ({change_type.value if isinstance(change_type, ChangeType) else change_type})"
        )

        return new_version

    def load(
        self,
        parameter: str,
        country: str,
        version: Optional[str] = None
    ) -> Optional[ResearchDocument]:
        """Load a research document.

        Args:
            parameter: Parameter name
            country: Country name
            version: Specific version (None for latest)

        Returns:
            ResearchDocument or None if not found
        """
        # Get version
        if version is None:
            version = self.version_manager.get_latest_version(parameter, country)
            if version is None:
                logger.debug(f"No research found for {parameter}/{country}")
                return None

        # Load content
        version_path = self.version_manager.get_version_path(parameter, country, version)
        content_file = version_path / "research.json"

        if not content_file.exists():
            logger.warning(f"Research content not found: {content_file}")
            return None

        try:
            with open(content_file, 'r') as f:
                content = json.load(f)
        except Exception as e:
            logger.error(f"Error loading research content: {e}")
            return None

        # Load metadata
        metadata = self.version_manager.load_version_metadata(parameter, country, version)
        if metadata is None:
            logger.warning(f"Metadata not found for {parameter}/{country}/{version}")
            metadata_dict = {}
        else:
            metadata_dict = metadata.to_dict()

        # Create document
        document = ResearchDocument(
            parameter=parameter,
            country=country,
            period=metadata_dict.get('period', 'unknown'),
            version=version,
            content=content,
            created_at=metadata_dict.get('created_at', ''),
            metadata=metadata_dict
        )

        logger.debug(f"Loaded research: {parameter}/{country} v{version}")
        return document

    def exists(
        self,
        parameter: str,
        country: str,
        version: Optional[str] = None
    ) -> bool:
        """Check if research document exists.

        Args:
            parameter: Parameter name
            country: Country name
            version: Specific version (None for any version)

        Returns:
            True if document exists
        """
        if version is None:
            version = self.version_manager.get_latest_version(parameter, country)
            if version is None:
                return False

        return self.version_manager.version_exists(parameter, country, version)

    def is_cache_valid(
        self,
        parameter: str,
        country: str,
        version: Optional[str] = None
    ) -> bool:
        """Check if cached research is still valid (within TTL).

        Args:
            parameter: Parameter name
            country: Country name
            version: Specific version (None for latest)

        Returns:
            True if cache is valid
        """
        if not self.exists(parameter, country, version):
            return False

        if version is None:
            version = self.version_manager.get_latest_version(parameter, country)

        metadata = self.version_manager.load_version_metadata(parameter, country, version)
        if metadata is None:
            return False

        # Parse creation time
        try:
            created_at = datetime.fromisoformat(metadata.created_at)
            age = datetime.now() - created_at
            return age.total_seconds() < self.cache_ttl
        except Exception as e:
            logger.error(f"Error checking cache validity: {e}")
            return False

    def list_all_research(self) -> List[Dict[str, str]]:
        """List all available research documents.

        Returns:
            List of dictionaries with parameter, country, and latest version
        """
        research_list = []

        # Iterate through all parameters
        for param_dir in self.base_path.iterdir():
            if not param_dir.is_dir():
                continue

            parameter = param_dir.name.replace('_', ' ').title()

            # Iterate through countries
            for country_dir in param_dir.iterdir():
                if not country_dir.is_dir():
                    continue

                country = country_dir.name.replace('_', ' ').title()

                # Get latest version
                latest_version = self.version_manager.get_latest_version(parameter, country)
                if latest_version:
                    research_list.append({
                        'parameter': parameter,
                        'country': country,
                        'version': latest_version
                    })

        return research_list

    def get_version_history(
        self,
        parameter: str,
        country: str
    ) -> List[VersionMetadata]:
        """Get version history for a parameter-country combination.

        Args:
            parameter: Parameter name
            country: Country name

        Returns:
            List of version metadata, newest first
        """
        return self.version_manager.get_version_history(parameter, country)

    def cleanup_old_versions(
        self,
        parameter: str,
        country: str,
        keep_count: int = 5
    ) -> int:
        """Remove old versions, keeping only the most recent N.

        Args:
            parameter: Parameter name
            country: Country name
            keep_count: Number of versions to keep

        Returns:
            Number of versions deleted
        """
        return self.version_manager.cleanup_old_versions(parameter, country, keep_count)

    def search_by_parameter(self, parameter: str) -> List[Dict[str, str]]:
        """Find all research for a specific parameter.

        Args:
            parameter: Parameter name

        Returns:
            List of countries with research for this parameter
        """
        param_clean = parameter.lower().replace(' ', '_')
        param_dir = self.base_path / param_clean

        if not param_dir.exists():
            return []

        results = []
        for country_dir in param_dir.iterdir():
            if not country_dir.is_dir():
                continue

            country = country_dir.name.replace('_', ' ').title()
            latest_version = self.version_manager.get_latest_version(parameter, country)

            if latest_version:
                results.append({
                    'parameter': parameter,
                    'country': country,
                    'version': latest_version
                })

        return results

    def search_by_country(self, country: str) -> List[Dict[str, str]]:
        """Find all research for a specific country.

        Args:
            country: Country name

        Returns:
            List of parameters with research for this country
        """
        country_clean = country.lower().replace(' ', '_')
        results = []

        for param_dir in self.base_path.iterdir():
            if not param_dir.is_dir():
                continue

            parameter = param_dir.name.replace('_', ' ').title()
            country_dir = param_dir / country_clean

            if country_dir.exists():
                latest_version = self.version_manager.get_latest_version(parameter, country)
                if latest_version:
                    results.append({
                        'parameter': parameter,
                        'country': country,
                        'version': latest_version
                    })

        return results

    def _calculate_checksum(self, content: Dict[str, Any]) -> str:
        """Calculate SHA-256 checksum of content.

        Args:
            content: Content dictionary

        Returns:
            Hex checksum string
        """
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()

    def get_statistics(self) -> Dict[str, Any]:
        """Get storage statistics.

        Returns:
            Dictionary with statistics
        """
        all_research = self.list_all_research()

        # Count by parameter
        param_counts = {}
        for item in all_research:
            param = item['parameter']
            param_counts[param] = param_counts.get(param, 0) + 1

        # Count by country
        country_counts = {}
        for item in all_research:
            country = item['country']
            country_counts[country] = country_counts.get(country, 0) + 1

        # Calculate total size
        total_size = 0
        for param_dir in self.base_path.rglob("research.json"):
            total_size += param_dir.stat().st_size

        return {
            'total_documents': len(all_research),
            'unique_parameters': len(param_counts),
            'unique_countries': len(country_counts),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'parameters': param_counts,
            'countries': country_counts
        }
