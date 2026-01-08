"""Document retrieval chain using ChromaDB for similarity search."""

import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from functools import lru_cache

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logging.warning("ChromaDB not available. Install with: pip install chromadb")

from app.core.llm_client import get_embeddings_model
from app.core.config import settings

logger = logging.getLogger(__name__)


class DocumentRetrievalService:
    """Document retrieval service using ChromaDB for semantic similarity search."""

    def __init__(
        self,
        collection_name: str = "creditnexus_documents",
        persist_directory: Optional[str] = None,
    ) -> None:
        """Initialize document retrieval service.

        Args:
            collection_name: Name of the ChromaDB collection (default: "creditnexus_documents")
            persist_directory: Directory to persist ChromaDB data (default: ./chroma_db)
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError(
                "ChromaDB is not installed. Install with: pip install chromadb"
            )

        # Set default persist directory
        if persist_directory is None:
            persist_directory = getattr(settings, "CHROMADB_PERSIST_DIR", "./chroma_db")
        
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self.embeddings_model = None
        
        # Initialize ChromaDB client and collection
        self._initialize_client()
        self._initialize_embeddings()

    def _initialize_client(self) -> None:
        """Initialize ChromaDB client and collection."""
        try:
            self.client = chromadb.PersistentClient(
                path=str(self.persist_directory),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "CreditNexus document embeddings for similarity search"}
            )
            
            logger.info(
                f"Initialized ChromaDB collection '{self.collection_name}' "
                f"with {self.collection.count()} documents"
            )
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {e}")
            raise

    def _initialize_embeddings(self) -> None:
        """Initialize embeddings model."""
        try:
            self.embeddings_model = get_embeddings_model()
            logger.info("Initialized embeddings model for document retrieval")
        except Exception as e:
            logger.error(f"Failed to initialize embeddings model: {e}")
            raise

    def _cdm_to_text(self, cdm_data: Dict[str, Any]) -> str:
        """Convert CDM data to searchable text representation.
        
        Args:
            cdm_data: CDM data dictionary
            
        Returns:
            Text representation of CDM data for embedding
        """
        text_parts = []
        
        # Extract parties
        if "parties" in cdm_data and isinstance(cdm_data["parties"], list):
            for party in cdm_data["parties"]:
                if isinstance(party, dict):
                    name = party.get("name", "")
                    role = party.get("role", "")
                    if name:
                        text_parts.append(f"Party: {name} ({role})")
        
        # Extract facilities
        if "facilities" in cdm_data and isinstance(cdm_data["facilities"], list):
            for facility in cdm_data["facilities"]:
                if isinstance(facility, dict):
                    facility_name = facility.get("facility_name", "")
                    commitment = facility.get("commitment_amount", {})
                    amount = commitment.get("amount", "") if isinstance(commitment, dict) else ""
                    currency = commitment.get("currency", "") if isinstance(commitment, dict) else ""
                    if facility_name:
                        text_parts.append(f"Facility: {facility_name} {amount} {currency}")
        
        # Extract agreement details
        if "agreement_date" in cdm_data:
            text_parts.append(f"Agreement Date: {cdm_data['agreement_date']}")
        
        if "governing_law" in cdm_data:
            text_parts.append(f"Governing Law: {cdm_data['governing_law']}")
        
        if "deal_id" in cdm_data:
            text_parts.append(f"Deal ID: {cdm_data['deal_id']}")
        
        # Extract ESG data
        if "sustainability_linked" in cdm_data and cdm_data["sustainability_linked"]:
            text_parts.append("Sustainability-Linked Loan")
        
        if "esg_kpi_targets" in cdm_data and isinstance(cdm_data["esg_kpi_targets"], list):
            for kpi in cdm_data["esg_kpi_targets"]:
                if isinstance(kpi, dict):
                    kpi_type = kpi.get("kpi_type", "")
                    target_value = kpi.get("target_value", "")
                    if kpi_type:
                        text_parts.append(f"ESG KPI: {kpi_type} target {target_value}")
        
        # Fallback to JSON string if no structured data
        if not text_parts:
            return json.dumps(cdm_data, default=str)
        
        return " | ".join(text_parts)

    def add_document(
        self,
        document_id: int,
        cdm_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add or update a document in the vector store.
        
        Args:
            document_id: Document ID from database
            cdm_data: CDM data dictionary to index
            metadata: Additional metadata (title, borrower_name, etc.)
        """
        try:
            # Convert CDM data to text
            text = self._cdm_to_text(cdm_data)
            
            # Generate embedding
            embedding = self.embeddings_model.embed_query(text)
            
            # Prepare metadata
            doc_metadata = {
                "document_id": str(document_id),
                "text": text[:1000],  # Store first 1000 chars for reference
            }
            
            if metadata:
                # Add metadata fields (convert to strings for ChromaDB)
                for key, value in metadata.items():
                    if value is not None:
                        doc_metadata[key] = str(value)
            
            # Add or update document in collection
            # Use document_id as the unique ID
            self.collection.upsert(
                ids=[str(document_id)],
                embeddings=[embedding],
                documents=[text],
                metadatas=[doc_metadata]
            )
            
            logger.info(f"Indexed document {document_id} in ChromaDB")
            
        except Exception as e:
            logger.error(f"Failed to add document {document_id} to vector store: {e}")
            raise

    def retrieve_similar_documents(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve similar documents based on query text or CDM data.
        
        Args:
            query: Query text or CDM data (will be converted to text if dict)
            top_k: Number of similar documents to retrieve (default: 5)
            filter_metadata: Optional metadata filters (e.g., {"borrower_name": "ACME Corp"})
            
        Returns:
            List of similar documents with scores, CDM data, and metadata
        """
        try:
            # Convert query to text if it's a dict (CDM data)
            if isinstance(query, dict):
                query_text = self._cdm_to_text(query)
            else:
                query_text = str(query)
            
            # Generate query embedding
            query_embedding = self.embeddings_model.embed_query(query_text)
            
            # Prepare where clause for filtering
            where = None
            if filter_metadata:
                where = {k: str(v) for k, v in filter_metadata.items()}
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            similar_docs = []
            if results["ids"] and len(results["ids"][0]) > 0:
                for idx in range(len(results["ids"][0])):
                    doc_id = results["ids"][0][idx]
                    distance = results["distances"][0][idx]
                    metadata = results["metadatas"][0][idx] if results["metadatas"] else {}
                    document_text = results["documents"][0][idx] if results["documents"] else ""
                    
                    # Convert distance to similarity score (1 - distance for cosine similarity)
                    similarity_score = 1.0 - distance if distance <= 1.0 else 0.0
                    
                    similar_docs.append({
                        "document_id": int(metadata.get("document_id", doc_id)),
                        "similarity_score": similarity_score,
                        "distance": distance,
                        "metadata": metadata,
                        "document_text": document_text,
                    })
            
            logger.info(
                f"Retrieved {len(similar_docs)} similar documents for query: {query_text[:50]}..."
            )
            
            return similar_docs
            
        except Exception as e:
            logger.error(f"Failed to retrieve similar documents: {e}")
            raise

    def delete_document(self, document_id: int) -> None:
        """Delete a document from the vector store.
        
        Args:
            document_id: Document ID to delete
        """
        try:
            self.collection.delete(ids=[str(document_id)])
            logger.info(f"Deleted document {document_id} from ChromaDB")
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            raise

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "persist_directory": str(self.persist_directory),
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {
                "collection_name": self.collection_name,
                "document_count": 0,
                "error": str(e),
            }


@lru_cache(maxsize=1)
def get_document_retrieval_service() -> DocumentRetrievalService:
    """Get or create singleton document retrieval service instance.

    Returns:
        DocumentRetrievalService instance
    """
    return DocumentRetrievalService()


def create_document_retrieval_chain() -> DocumentRetrievalService:
    """Create document retrieval chain instance.

    Returns:
        DocumentRetrievalService instance
    """
    return get_document_retrieval_service()


def retrieve_similar_documents(
    query: str,
    top_k: int = 5,
    filter_metadata: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Retrieve similar documents based on query.

    Convenience function that creates a retrieval service and searches.

    Args:
        query: Query text or CDM data dictionary
        top_k: Number of similar documents to retrieve (default: 5)
        filter_metadata: Optional metadata filters

    Returns:
        List of similar documents with scores and metadata

    Raises:
        ImportError: If ChromaDB is not installed
    """
    service = get_document_retrieval_service()
    return service.retrieve_similar_documents(
        query=query,
        top_k=top_k,
        filter_metadata=filter_metadata,
    )












