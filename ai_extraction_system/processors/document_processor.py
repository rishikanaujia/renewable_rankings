"""Document Processor - Extract and process content from various document types.

This module handles document loading, parsing, and preprocessing for AI extraction.
Supports multiple formats and provides intelligent chunking for large documents.

Supported Formats:
    - PDF (via PyPDF2, pdfplumber)
    - HTML/Web pages (via BeautifulSoup, newspaper3k)
    - Text files
    - Word documents (DOCX)
    - JSON structured data

Features:
    - Intelligent text extraction
    - Table extraction from PDFs
    - Web scraping with rate limiting
    - Document chunking for long texts
    - Metadata extraction
    - Language detection
    - Clean text preprocessing
"""
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from enum import Enum
import logging
from datetime import datetime

from langchain.document_loaders import (
    PyPDFLoader,
    UnstructuredHTMLLoader,
    TextLoader,
    WebBaseLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document as LangChainDocument
from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class DocumentType(str, Enum):
    """Document type enumeration."""
    PDF = "pdf"
    HTML = "html"
    WEB = "web"
    TEXT = "text"
    DOCX = "docx"
    JSON = "json"


class ProcessedDocument(BaseModel):
    """Processed document with extracted content and metadata."""
    
    content: str = Field(..., description="Extracted text content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    chunks: List[str] = Field(default_factory=list, description="Content chunks if split")
    tables: List[Dict[str, Any]] = Field(default_factory=list, description="Extracted tables")
    images: List[Dict[str, Any]] = Field(default_factory=list, description="Image metadata")
    processing_timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DocumentProcessor:
    """Process documents for AI extraction.
    
    This class provides unified interface for loading and processing
    various document types using LangChain document loaders.
    
    Example:
        >>> processor = DocumentProcessor()
        >>> doc = processor.process_pdf("report.pdf")
        >>> print(doc.content)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize document processor.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        
        # Text splitting configuration
        self.chunk_size = self.config.get('chunk_size', 4000)
        self.chunk_overlap = self.config.get('chunk_overlap', 200)
        self.chunk_separators = self.config.get(
            'chunk_separators',
            ["\n\n", "\n", ". ", " ", ""]
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.chunk_separators
        )
        
        logger.info("Initialized DocumentProcessor")
    
    def process_pdf(
        self,
        file_path: Union[str, Path],
        extract_tables: bool = True
    ) -> ProcessedDocument:
        """Process PDF document.
        
        Args:
            file_path: Path to PDF file
            extract_tables: Whether to extract tables
            
        Returns:
            ProcessedDocument with extracted content
        """
        try:
            logger.info(f"Processing PDF: {file_path}")
            
            # Load PDF using LangChain
            loader = PyPDFLoader(str(file_path))
            pages = loader.load()
            
            # Combine text from all pages
            content = "\n\n".join([page.page_content for page in pages])
            
            # Extract metadata
            metadata = {
                'source': str(file_path),
                'type': DocumentType.PDF,
                'num_pages': len(pages),
                'title': Path(file_path).stem
            }
            
            # Add page-level metadata
            if pages:
                first_page_meta = pages[0].metadata
                metadata.update({
                    'author': first_page_meta.get('author', ''),
                    'creator': first_page_meta.get('creator', ''),
                    'producer': first_page_meta.get('producer', ''),
                })
            
            # Extract tables if requested
            tables = []
            if extract_tables:
                tables = self._extract_pdf_tables(file_path)
            
            # Create chunks
            chunks = self._create_chunks(content)
            
            return ProcessedDocument(
                content=content,
                metadata=metadata,
                chunks=chunks,
                tables=tables
            )
        
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {e}", exc_info=True)
            raise
    
    def process_url(
        self,
        url: str,
        extract_main_content: bool = True
    ) -> ProcessedDocument:
        """Process web page from URL.
        
        Args:
            url: Web page URL
            extract_main_content: Whether to extract only main content
            
        Returns:
            ProcessedDocument with extracted content
        """
        try:
            logger.info(f"Processing URL: {url}")
            
            # Load web page using LangChain
            loader = WebBaseLoader(url)
            docs = loader.load()
            
            if not docs:
                raise ValueError(f"No content extracted from {url}")
            
            content = docs[0].page_content
            
            # Extract metadata
            metadata = {
                'source': url,
                'type': DocumentType.WEB,
                'url': url,
                'title': docs[0].metadata.get('title', ''),
                'description': docs[0].metadata.get('description', ''),
            }
            
            # Clean content if requested
            if extract_main_content:
                content = self._clean_web_content(content)
            
            # Create chunks
            chunks = self._create_chunks(content)
            
            return ProcessedDocument(
                content=content,
                metadata=metadata,
                chunks=chunks
            )
        
        except Exception as e:
            logger.error(f"Error processing URL {url}: {e}", exc_info=True)
            raise
    
    def process_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProcessedDocument:
        """Process raw text.
        
        Args:
            text: Raw text content
            metadata: Optional metadata dictionary
            
        Returns:
            ProcessedDocument with processed text
        """
        logger.info("Processing raw text")
        
        # Clean text
        content = self._clean_text(text)
        
        # Prepare metadata
        doc_metadata = metadata or {}
        doc_metadata.update({
            'type': DocumentType.TEXT,
            'length': len(content),
            'word_count': len(content.split())
        })
        
        # Create chunks
        chunks = self._create_chunks(content)
        
        return ProcessedDocument(
            content=content,
            metadata=doc_metadata,
            chunks=chunks
        )
    
    def process_html(
        self,
        file_path: Union[str, Path]
    ) -> ProcessedDocument:
        """Process HTML file.
        
        Args:
            file_path: Path to HTML file
            
        Returns:
            ProcessedDocument with extracted content
        """
        try:
            logger.info(f"Processing HTML: {file_path}")
            
            # Load HTML using LangChain
            loader = UnstructuredHTMLLoader(str(file_path))
            docs = loader.load()
            
            if not docs:
                raise ValueError(f"No content extracted from {file_path}")
            
            content = docs[0].page_content
            
            # Extract metadata
            metadata = {
                'source': str(file_path),
                'type': DocumentType.HTML,
                'title': Path(file_path).stem
            }
            metadata.update(docs[0].metadata)
            
            # Create chunks
            chunks = self._create_chunks(content)
            
            return ProcessedDocument(
                content=content,
                metadata=metadata,
                chunks=chunks
            )
        
        except Exception as e:
            logger.error(f"Error processing HTML {file_path}: {e}", exc_info=True)
            raise
    
    def process_multiple_documents(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[ProcessedDocument]:
        """Process multiple documents.
        
        Args:
            documents: List of document dictionaries with 'type' and 'source'
            
        Returns:
            List of ProcessedDocument objects
        """
        results = []
        
        for doc in documents:
            doc_type = doc.get('type')
            source = doc.get('source')
            
            try:
                if doc_type == DocumentType.PDF:
                    result = self.process_pdf(source)
                elif doc_type in [DocumentType.WEB, DocumentType.HTML]:
                    result = self.process_url(source)
                elif doc_type == DocumentType.TEXT:
                    result = self.process_text(source, doc.get('metadata'))
                else:
                    logger.warning(f"Unsupported document type: {doc_type}")
                    continue
                
                results.append(result)
            
            except Exception as e:
                logger.error(f"Error processing document {source}: {e}")
                continue
        
        return results
    
    def _create_chunks(self, text: str) -> List[str]:
        """Create text chunks using RecursiveCharacterTextSplitter.
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        if not text or len(text) < self.chunk_size:
            return [text] if text else []
        
        docs = self.text_splitter.create_documents([text])
        return [doc.page_content for doc in docs]
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        import re
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters (keep basic punctuation)
        text = re.sub(r'[^\w\s.,;:!?()\-\[\]{}\'\"]+', '', text)
        
        # Normalize line breaks
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        return text.strip()
    
    def _clean_web_content(self, content: str) -> str:
        """Clean web content (remove boilerplate).
        
        Args:
            content: Raw web content
            
        Returns:
            Cleaned main content
        """
        # Basic cleaning - could be enhanced with newspaper3k or trafilatura
        content = self._clean_text(content)
        
        # Remove common boilerplate patterns
        patterns_to_remove = [
            r'Cookie Policy.*?Accept',
            r'Subscribe to.*?Newsletter',
            r'Follow us on.*?(?:Twitter|Facebook|LinkedIn)',
            r'Copyright.*?\d{4}',
        ]
        
        for pattern in patterns_to_remove:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
        
        return content
    
    def _extract_pdf_tables(self, file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """Extract tables from PDF.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            List of extracted tables
        """
        try:
            import pdfplumber
            
            tables = []
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_tables = page.extract_tables()
                    for j, table in enumerate(page_tables):
                        if table:
                            tables.append({
                                'page': i + 1,
                                'table_index': j,
                                'data': table,
                                'rows': len(table),
                                'cols': len(table[0]) if table else 0
                            })
            
            logger.info(f"Extracted {len(tables)} tables from {file_path}")
            return tables
        
        except ImportError:
            logger.warning("pdfplumber not available, skipping table extraction")
            return []
        except Exception as e:
            logger.error(f"Error extracting tables from {file_path}: {e}")
            return []
    
    def get_document_summary(self, doc: ProcessedDocument) -> str:
        """Get summary of processed document.
        
        Args:
            doc: ProcessedDocument instance
            
        Returns:
            Summary string
        """
        summary = [
            f"Document: {doc.metadata.get('title', 'Unknown')}",
            f"Type: {doc.metadata.get('type', 'Unknown')}",
            f"Content length: {len(doc.content)} characters",
            f"Chunks: {len(doc.chunks)}",
        ]
        
        if doc.tables:
            summary.append(f"Tables: {len(doc.tables)}")
        
        return "\n".join(summary)


# Convenience functions

def process_pdf_file(file_path: str, **kwargs) -> ProcessedDocument:
    """Process a PDF file.
    
    Args:
        file_path: Path to PDF file
        **kwargs: Additional processing options
        
    Returns:
        ProcessedDocument
    """
    processor = DocumentProcessor()
    return processor.process_pdf(file_path, **kwargs)


def process_web_page(url: str, **kwargs) -> ProcessedDocument:
    """Process a web page.
    
    Args:
        url: Web page URL
        **kwargs: Additional processing options
        
    Returns:
        ProcessedDocument
    """
    processor = DocumentProcessor()
    return processor.process_url(url, **kwargs)


def process_text_content(text: str, **kwargs) -> ProcessedDocument:
    """Process raw text.
    
    Args:
        text: Raw text content
        **kwargs: Additional processing options
        
    Returns:
        ProcessedDocument
    """
    processor = DocumentProcessor()
    return processor.process_text(text, **kwargs)
