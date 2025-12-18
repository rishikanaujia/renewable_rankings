"""ChromaDB implementation of memory store."""
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import chromadb
from chromadb.config import Settings

from ..base.memory_store import MemoryStore, MemoryStoreRegistry
from ..base.memory_entry import (
    BaseMemoryEntry, MemoryQuery, EpisodicMemoryEntry,
    SemanticMemoryEntry, ProceduralMemoryEntry, FeedbackMemoryEntry
)
from ..base.memory_types import (
    MemoryType, DEFAULT_SIMILARITY_THRESHOLD, 
    DEFAULT_TOP_K_RETRIEVAL, DEFAULT_EMBEDDING_MODEL
)
from ..core.logger import get_logger

logger = get_logger(__name__)


class ChromaDBMemoryStore(MemoryStore):
    """ChromaDB-based memory storage.
    
    Uses vector similarity for efficient retrieval of relevant memories.
    Supports multiple collections for different memory types.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize ChromaDB memory store.
        
        Config options:
            - persist_directory: Path to persist data (default: ./chroma_memory)
            - embedding_model: Sentence transformer model name
            - collection_name: Base collection name (default: renewable_rankings_memory)
            - use_separate_collections: One collection per memory type (default: False)
        """
        super().__init__(config)
        
        self.persist_directory = config.get('persist_directory', './chroma_memory')
        self.embedding_model = config.get('embedding_model', DEFAULT_EMBEDDING_MODEL)
        self.collection_name = config.get('collection_name', 'renewable_rankings_memory')
        self.use_separate_collections = config.get('use_separate_collections', False)
        
        self.client: Optional[chromadb.Client] = None
        self.collections: Dict[str, Any] = {}
        
    def initialize(self) -> None:
        """Initialize ChromaDB client and collections."""
        try:
            # Create persistent client
            self.client = chromadb.Client(Settings(
                persist_directory=self.persist_directory,
                anonymized_telemetry=False
            ))
            
            if self.use_separate_collections:
                # Create separate collection for each memory type
                for memory_type in MemoryType:
                    collection_name = f"{self.collection_name}_{memory_type.value}"
                    self.collections[memory_type.value] = self.client.get_or_create_collection(
                        name=collection_name,
                        metadata={"memory_type": memory_type.value}
                    )
            else:
                # Single collection for all memories
                self.collections['default'] = self.client.get_or_create_collection(
                    name=self.collection_name
                )
            
            self._initialized = True
            logger.info(
                f"ChromaDB memory store initialized at {self.persist_directory} "
                f"with {len(self.collections)} collection(s)"
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB memory store: {e}")
            raise
    
    def _get_collection(self, memory_type: Optional[MemoryType] = None):
        """Get appropriate collection for memory type."""
        if self.use_separate_collections and memory_type:
            return self.collections.get(memory_type.value)
        return self.collections.get('default')
    
    def _entry_to_document(self, entry: BaseMemoryEntry) -> Dict[str, Any]:
        """Convert memory entry to ChromaDB document format."""
        # Create searchable text from entry content
        content_str = json.dumps(entry.content, default=str)
        
        # Prepare metadata (ChromaDB requires string/int/float values)
        metadata = {
            'memory_type': entry.memory_type.value,
            'category': entry.category.value,
            'timestamp': entry.timestamp.isoformat(),
            'source': entry.metadata.source,
            'confidence': float(entry.metadata.confidence),
            'access_count': int(entry.metadata.access_count),
            'version': int(entry.metadata.version),
        }
        
        # Add optional fields
        if entry.parent_memory_id:
            metadata['parent_memory_id'] = entry.parent_memory_id
        
        if entry.expires_at:
            metadata['expires_at'] = entry.expires_at.isoformat()
        
        # Add content-specific searchable fields
        if 'country' in entry.content:
            metadata['country'] = str(entry.content['country'])
        
        if 'agent_name' in entry.content:
            metadata['agent_name'] = str(entry.content['agent_name'])
        
        return {
            'id': entry.id,
            'document': content_str,
            'metadata': metadata,
            'embedding': entry.embedding
        }
    
    def _document_to_entry(self, doc_id: str, document: str, metadata: Dict) -> BaseMemoryEntry:
        """Convert ChromaDB document back to memory entry."""
        memory_type = MemoryType(metadata['memory_type'])
        content = json.loads(document)
        
        # Reconstruct appropriate entry type
        if memory_type == MemoryType.EPISODIC:
            entry = EpisodicMemoryEntry(
                agent_name=content['agent_name'],
                country=content['country'],
                period=content['period'],
                input_data=content['input_data'],
                output_data=content['output_data'],
                execution_time_ms=content['execution_time_ms'],
                success=content.get('success', True),
                error_message=content.get('error_message')
            )
        elif memory_type == MemoryType.SEMANTIC:
            entry = SemanticMemoryEntry(
                subject=content['subject'],
                fact_type=content['fact_type'],
                fact_content=content['fact_content'],
                source=content['source']
            )
        elif memory_type == MemoryType.PROCEDURAL:
            entry = ProceduralMemoryEntry(
                pattern_name=content['pattern_name'],
                pattern_type=content['pattern_type'],
                context=content['context'],
                action=content['action'],
                outcome=content.get('outcome'),
                confidence_score=content.get('confidence_score', 0.5)
            )
        elif memory_type == MemoryType.FEEDBACK:
            from ..base.memory_types import FeedbackType
            entry = FeedbackMemoryEntry(
                feedback_type=FeedbackType(content['feedback_type']),
                original_analysis_id=content['original_analysis_id'],
                expert_id=content['expert_id'],
                original_value=content['original_value'],
                corrected_value=content['corrected_value'],
                reasoning=content['reasoning'],
                impact_scope=content.get('impact_scope', 'specific')
            )
        else:
            # Fallback to base entry
            from ..base.memory_entry import BaseMemoryEntry as BaseEntry
            entry = BaseEntry()
            entry.content = content
        
        # Restore ID and metadata
        entry.id = doc_id
        entry.timestamp = datetime.fromisoformat(metadata['timestamp'])
        entry.metadata.source = metadata['source']
        entry.metadata.confidence = metadata['confidence']
        entry.metadata.access_count = metadata['access_count']
        entry.metadata.version = metadata['version']
        
        if metadata.get('parent_memory_id'):
            entry.parent_memory_id = metadata['parent_memory_id']
        
        if metadata.get('expires_at'):
            entry.expires_at = datetime.fromisoformat(metadata['expires_at'])
        
        return entry
    
    def store(self, entry: BaseMemoryEntry) -> str:
        """Store a memory entry in ChromaDB."""
        self.ensure_initialized()
        
        try:
            collection = self._get_collection(entry.memory_type)
            doc = self._entry_to_document(entry)
            
            # Add to collection
            collection.add(
                ids=[doc['id']],
                documents=[doc['document']],
                metadatas=[doc['metadata']],
                embeddings=[doc['embedding']] if doc['embedding'] else None
            )
            
            logger.debug(f"Stored memory {entry.id} of type {entry.memory_type.value}")
            return entry.id
            
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            raise
    
    def retrieve(self, memory_id: str) -> Optional[BaseMemoryEntry]:
        """Retrieve a specific memory by ID."""
        self.ensure_initialized()
        
        try:
            # Try all collections if using separate collections
            collections = self.collections.values()
            
            for collection in collections:
                result = collection.get(ids=[memory_id])
                
                if result['ids']:
                    entry = self._document_to_entry(
                        result['ids'][0],
                        result['documents'][0],
                        result['metadatas'][0]
                    )
                    entry.update_access()
                    
                    # Update access stats in store
                    self.update(memory_id, {
                        'access_count': entry.metadata.access_count,
                        'last_accessed': entry.metadata.last_accessed.isoformat()
                    })
                    
                    return entry
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve memory {memory_id}: {e}")
            return None
    
    def search(self, query: MemoryQuery) -> List[BaseMemoryEntry]:
        """Search for memories matching query."""
        self.ensure_initialized()
        
        try:
            # Build where clause from filters
            where = {}
            
            if query.memory_types:
                where['memory_type'] = {'$in': [mt.value for mt in query.memory_types]}
            
            if query.categories:
                where['category'] = {'$in': [c.value for c in query.categories]}
            
            if query.countries:
                where['country'] = {'$in': query.countries}
            
            if query.agents:
                where['agent_name'] = {'$in': query.agents}
            
            # Time range filter
            if query.time_range:
                start, end = query.time_range
                where['timestamp'] = {
                    '$gte': start.isoformat(),
                    '$lte': end.isoformat()
                }
            
            # Expired filter
            if not query.include_expired:
                where['$or'] = [
                    {'expires_at': {'$eq': None}},
                    {'expires_at': {'$gt': datetime.now().isoformat()}}
                ]
            
            # Query collection(s)
            collections = self.collections.values()
            all_results = []
            
            for collection in collections:
                if query.query_text:
                    # Text-based query
                    results = collection.query(
                        query_texts=[query.query_text],
                        n_results=query.top_k,
                        where=where if where else None
                    )
                elif query.query_embedding:
                    # Embedding-based query
                    results = collection.query(
                        query_embeddings=[query.query_embedding],
                        n_results=query.top_k,
                        where=where if where else None
                    )
                else:
                    # Just filter-based retrieval
                    results = collection.get(
                        where=where if where else None,
                        limit=query.top_k
                    )
                
                # Convert to memory entries
                if results.get('ids') and results['ids'][0]:
                    for i, doc_id in enumerate(results['ids'][0]):
                        entry = self._document_to_entry(
                            doc_id,
                            results['documents'][0][i],
                            results['metadatas'][0][i]
                        )
                        
                        # Check similarity threshold if applicable
                        if results.get('distances'):
                            similarity = 1.0 - results['distances'][0][i]
                            if similarity >= query.similarity_threshold:
                                all_results.append(entry)
                        else:
                            all_results.append(entry)
            
            # Sort by timestamp (most recent first) and limit
            all_results.sort(key=lambda x: x.timestamp, reverse=True)
            return all_results[:query.top_k]
            
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return []
    
    def search_similar(
        self,
        embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[tuple[BaseMemoryEntry, float]]:
        """Search for similar memories using vector similarity."""
        self.ensure_initialized()
        
        try:
            collections = self.collections.values()
            all_results = []
            
            for collection in collections:
                results = collection.query(
                    query_embeddings=[embedding],
                    n_results=top_k,
                    where=filters
                )
                
                if results.get('ids') and results['ids'][0]:
                    for i, doc_id in enumerate(results['ids'][0]):
                        entry = self._document_to_entry(
                            doc_id,
                            results['documents'][0][i],
                            results['metadatas'][0][i]
                        )
                        similarity = 1.0 - results['distances'][0][i]
                        all_results.append((entry, similarity))
            
            # Sort by similarity
            all_results.sort(key=lambda x: x[1], reverse=True)
            return all_results[:top_k]
            
        except Exception as e:
            logger.error(f"Failed to search similar memories: {e}")
            return []
    
    def update(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing memory entry."""
        self.ensure_initialized()
        
        try:
            # Find which collection contains this memory
            for collection in self.collections.values():
                result = collection.get(ids=[memory_id])
                
                if result['ids']:
                    # Update metadata
                    current_metadata = result['metadatas'][0]
                    current_metadata.update(updates)
                    
                    collection.update(
                        ids=[memory_id],
                        metadatas=[current_metadata]
                    )
                    
                    logger.debug(f"Updated memory {memory_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to update memory {memory_id}: {e}")
            return False
    
    def delete(self, memory_id: str) -> bool:
        """Delete a memory entry."""
        self.ensure_initialized()
        
        try:
            for collection in self.collections.values():
                result = collection.get(ids=[memory_id])
                
                if result['ids']:
                    collection.delete(ids=[memory_id])
                    logger.debug(f"Deleted memory {memory_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            return False
    
    def delete_expired(self) -> int:
        """Delete all expired memories."""
        self.ensure_initialized()
        
        count = 0
        now = datetime.now().isoformat()
        
        try:
            for collection in self.collections.values():
                # Get all expired memories
                results = collection.get(
                    where={
                        'expires_at': {'$lt': now},
                        '$ne': None
                    }
                )
                
                if results['ids']:
                    collection.delete(ids=results['ids'])
                    count += len(results['ids'])
            
            logger.info(f"Deleted {count} expired memories")
            return count
            
        except Exception as e:
            logger.error(f"Failed to delete expired memories: {e}")
            return count
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count memories matching filters."""
        self.ensure_initialized()
        
        try:
            total = 0
            for collection in self.collections.values():
                result = collection.get(where=filters)
                total += len(result['ids'])
            return total
            
        except Exception as e:
            logger.error(f"Failed to count memories: {e}")
            return 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored memories."""
        self.ensure_initialized()
        
        try:
            stats = {
                'total_memories': 0,
                'by_type': {},
                'by_category': {},
                'collections': len(self.collections)
            }
            
            for collection in self.collections.values():
                # Get all entries
                result = collection.get()
                stats['total_memories'] += len(result['ids'])
                
                # Count by type and category
                for metadata in result['metadatas']:
                    memory_type = metadata.get('memory_type', 'unknown')
                    category = metadata.get('category', 'unknown')
                    
                    stats['by_type'][memory_type] = stats['by_type'].get(memory_type, 0) + 1
                    stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def clear_all(self) -> bool:
        """Clear all memories from storage."""
        self.ensure_initialized()
        
        try:
            for name, collection in self.collections.items():
                self.client.delete_collection(name=collection.name)
            
            # Reinitialize collections
            self.collections.clear()
            self._initialized = False
            self.initialize()
            
            logger.warning("Cleared all memories from storage")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear memories: {e}")
            return False


# Register the ChromaDB store
MemoryStoreRegistry.register('chromadb', ChromaDBMemoryStore)
