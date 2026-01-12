"""Version Manager - Handles semantic versioning of research documents

Implements versioning strategies for research documents with support for:
- Semantic versioning (1.0.0)
- Timestamp-based versioning
- Version comparison and history tracking
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import json
import logging
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class VersionStrategy(str, Enum):
    """Version numbering strategies."""
    SEMANTIC = "semantic"  # 1.0.0 format
    TIMESTAMP = "timestamp"  # 20240101_120000 format


class ChangeType(str, Enum):
    """Types of changes for semantic versioning."""
    MAJOR = "major"  # Breaking changes, complete re-research
    MINOR = "minor"  # New sections or significant updates
    PATCH = "patch"  # Small corrections or additions


@dataclass
class VersionMetadata:
    """Metadata for a research document version."""
    version: str
    created_at: str
    change_type: Optional[str] = None
    change_description: Optional[str] = None
    parameter: Optional[str] = None
    country: Optional[str] = None
    period: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    checksum: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class VersionManager:
    """Manages versioning of research documents."""

    def __init__(
        self,
        strategy: VersionStrategy = VersionStrategy.SEMANTIC,
        base_path: str = "research_system/data/research_documents"
    ):
        """Initialize version manager.

        Args:
            strategy: Versioning strategy to use
            base_path: Base path for research documents
        """
        self.strategy = strategy
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"VersionManager initialized with {strategy} strategy")

    def parse_version(self, version_str: str) -> Tuple[int, ...]:
        """Parse version string into tuple for comparison.

        Args:
            version_str: Version string (e.g., "1.2.3" or "20240101_120000")

        Returns:
            Tuple of version components
        """
        if self.strategy == VersionStrategy.SEMANTIC:
            try:
                parts = version_str.split('.')
                return tuple(int(p) for p in parts)
            except ValueError:
                logger.warning(f"Invalid semantic version: {version_str}, using (0,0,0)")
                return (0, 0, 0)
        else:  # TIMESTAMP
            return (version_str,)

    def compare_versions(self, v1: str, v2: str) -> int:
        """Compare two version strings.

        Args:
            v1: First version
            v2: Second version

        Returns:
            -1 if v1 < v2, 0 if equal, 1 if v1 > v2
        """
        parsed_v1 = self.parse_version(v1)
        parsed_v2 = self.parse_version(v2)

        if parsed_v1 < parsed_v2:
            return -1
        elif parsed_v1 > parsed_v2:
            return 1
        else:
            return 0

    def get_next_version(
        self,
        current_version: Optional[str],
        change_type: ChangeType = ChangeType.MINOR
    ) -> str:
        """Calculate next version number.

        Args:
            current_version: Current version string (None if first version)
            change_type: Type of change (for semantic versioning)

        Returns:
            Next version string
        """
        if self.strategy == VersionStrategy.TIMESTAMP:
            return datetime.now().strftime("%Y%m%d_%H%M%S")

        # Semantic versioning
        if current_version is None:
            return "1.0.0"

        try:
            major, minor, patch = self.parse_version(current_version)
        except (ValueError, TypeError):
            logger.warning(f"Could not parse version {current_version}, starting from 1.0.0")
            return "1.0.0"

        if change_type == ChangeType.MAJOR:
            return f"{major + 1}.0.0"
        elif change_type == ChangeType.MINOR:
            return f"{major}.{minor + 1}.0"
        else:  # PATCH
            return f"{major}.{minor}.{patch + 1}"

    def get_version_path(
        self,
        parameter: str,
        country: str,
        version: str
    ) -> Path:
        """Get the file system path for a specific version.

        Args:
            parameter: Parameter name
            country: Country name
            version: Version string

        Returns:
            Path to version directory
        """
        # Sanitize names for file system
        param_clean = parameter.lower().replace(' ', '_')
        country_clean = country.lower().replace(' ', '_')

        version_path = self.base_path / param_clean / country_clean / version
        return version_path

    def create_version_directory(
        self,
        parameter: str,
        country: str,
        version: str
    ) -> Path:
        """Create directory structure for a new version.

        Args:
            parameter: Parameter name
            country: Country name
            version: Version string

        Returns:
            Path to created version directory
        """
        version_path = self.get_version_path(parameter, country, version)
        version_path.mkdir(parents=True, exist_ok=True)

        logger.debug(f"Created version directory: {version_path}")
        return version_path

    def list_versions(
        self,
        parameter: str,
        country: str
    ) -> List[str]:
        """List all versions for a parameter-country combination.

        Args:
            parameter: Parameter name
            country: Country name

        Returns:
            List of version strings, sorted (newest first)
        """
        param_clean = parameter.lower().replace(' ', '_')
        country_clean = country.lower().replace(' ', '_')

        base_dir = self.base_path / param_clean / country_clean

        if not base_dir.exists():
            return []

        # Get all version directories
        versions = [d.name for d in base_dir.iterdir() if d.is_dir()]

        # Sort versions (newest first)
        versions.sort(key=lambda v: self.parse_version(v), reverse=True)

        return versions

    def get_latest_version(
        self,
        parameter: str,
        country: str
    ) -> Optional[str]:
        """Get the latest version for a parameter-country combination.

        Args:
            parameter: Parameter name
            country: Country name

        Returns:
            Latest version string, or None if no versions exist
        """
        versions = self.list_versions(parameter, country)
        return versions[0] if versions else None

    def load_version_metadata(
        self,
        parameter: str,
        country: str,
        version: str
    ) -> Optional[VersionMetadata]:
        """Load metadata for a specific version.

        Args:
            parameter: Parameter name
            country: Country name
            version: Version string

        Returns:
            VersionMetadata object, or None if not found
        """
        version_path = self.get_version_path(parameter, country, version)
        metadata_file = version_path / "metadata.json"

        if not metadata_file.exists():
            return None

        try:
            with open(metadata_file, 'r') as f:
                data = json.load(f)
            return VersionMetadata(**data)
        except Exception as e:
            logger.error(f"Error loading metadata from {metadata_file}: {e}")
            return None

    def save_version_metadata(
        self,
        parameter: str,
        country: str,
        version: str,
        metadata: VersionMetadata
    ) -> bool:
        """Save metadata for a specific version.

        Args:
            parameter: Parameter name
            country: Country name
            version: Version string
            metadata: VersionMetadata object

        Returns:
            True if successful
        """
        version_path = self.get_version_path(parameter, country, version)
        metadata_file = version_path / "metadata.json"

        try:
            with open(metadata_file, 'w') as f:
                json.dump(metadata.to_dict(), f, indent=2)
            logger.debug(f"Saved metadata to {metadata_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving metadata to {metadata_file}: {e}")
            return False

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
        versions = self.list_versions(parameter, country)

        if len(versions) <= keep_count:
            return 0

        # Delete old versions
        deleted = 0
        for version in versions[keep_count:]:
            version_path = self.get_version_path(parameter, country, version)
            try:
                import shutil
                shutil.rmtree(version_path)
                deleted += 1
                logger.info(f"Deleted old version: {version}")
            except Exception as e:
                logger.error(f"Error deleting {version_path}: {e}")

        return deleted

    def get_version_history(
        self,
        parameter: str,
        country: str
    ) -> List[VersionMetadata]:
        """Get complete version history with metadata.

        Args:
            parameter: Parameter name
            country: Country name

        Returns:
            List of VersionMetadata objects, sorted newest first
        """
        versions = self.list_versions(parameter, country)
        history = []

        for version in versions:
            metadata = self.load_version_metadata(parameter, country, version)
            if metadata:
                history.append(metadata)

        return history

    def version_exists(
        self,
        parameter: str,
        country: str,
        version: str
    ) -> bool:
        """Check if a specific version exists.

        Args:
            parameter: Parameter name
            country: Country name
            version: Version string

        Returns:
            True if version exists
        """
        version_path = self.get_version_path(parameter, country, version)
        return version_path.exists()
