import uuid
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class VectorRepository:
    """
    Repository for managing vector embeddings and performing similarity searches in ChromaDB.
    """

    def __init__(self, client, collection: str = "pages"):
        """
        Initialize VectorRepository.

        Args:
            client: ChromaDB client wrapper, ClientAPI instance, or Collection.
            collection: Collection name string (default: 'pages').
        """
        self.client = client
        if hasattr(client, "get_or_create_collection"):
            self.collection = client.get_or_create_collection(collection)
        elif hasattr(client, "__getitem__"):
            self.collection = client[collection]
        elif hasattr(client, "get_collection"):
            self.collection = client.get_collection(collection)
        else:
            self.collection = client

    def add(
        self,
        chunks: List[str],
        embeddings: Any,
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Add or upsert text chunks and their embeddings into ChromaDB.

        Args:
            chunks: List of document/chunk strings.
            embeddings: Embeddings as a numpy array, torch tensor, or nested list of floats.
            metadatas: Optional list of metadata dictionaries corresponding to each chunk.
            ids: Optional list of unique IDs. If omitted, unique UUIDs are generated.

        Returns:
            The list of IDs assigned to the chunks.
        """
        if not chunks:
            return []

        # Convert numpy/tensor embeddings to python list if needed
        if hasattr(embeddings, "tolist"):
            emb_list = embeddings.tolist()
        else:
            emb_list = embeddings

        # Generate unique IDs if none provided to avoid collisions on repeated adds
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in range(len(chunks))]

        kwargs: Dict[str, Any] = {
            "ids": ids,
            "documents": chunks,
            "embeddings": emb_list,
        }
        if metadatas is not None:
            kwargs["metadatas"] = metadatas

        # Use upsert when available to prevent ID collision errors
        if hasattr(self.collection, "upsert"):
            self.collection.upsert(**kwargs)
        else:
            self.collection.add(**kwargs)

        logger.info(f"Added {len(chunks)} chunks to vector collection.")
        return ids

    def search(
        self,
        query_embedding: Any,
        top_k: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """
        Query nearest neighbor chunks for a query embedding.

        Args:
            query_embedding: Embedding of the query (numpy array or list of floats).
            top_k: Number of nearest chunks to retrieve.
            where: Optional metadata filter dict (e.g. {"title": "xyz"}).

        Returns:
            List of matching document chunk strings.
        """
        # Convert numpy embedding to python list
        if hasattr(query_embedding, "tolist"):
            emb = query_embedding.tolist()
        else:
            emb = query_embedding

        # Ensure query_embeddings is 2D: [[float, ...]]
        if isinstance(emb, list) and (len(emb) == 0 or not isinstance(emb[0], list)):
            query_embeddings = [emb]
        else:
            query_embeddings = emb

        count = self.count()
        if count == 0:
            return []

        # Clamp n_results to available items
        n_results = max(1, min(top_k, count))

        kwargs: Dict[str, Any] = {
            "query_embeddings": query_embeddings,
            "n_results": n_results,
        }
        if where:
            kwargs["where"] = where

        results = self.collection.query(**kwargs)

        if results and results.get("documents") and len(results["documents"]) > 0:
            return results["documents"][0]

        return []

    def search_with_metadata(
        self,
        query_embedding: Any,
        top_k: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, List[Any]]:
        """
        Query nearest neighbor chunks and return documents, metadatas, and distances.

        Args:
            query_embedding: Embedding of the query.
            top_k: Number of nearest chunks to retrieve.
            where: Optional metadata filter dict.

        Returns:
            Dictionary containing 'documents', 'metadatas', 'distances', and 'ids'.
        """
        if hasattr(query_embedding, "tolist"):
            emb = query_embedding.tolist()
        else:
            emb = query_embedding

        if isinstance(emb, list) and (len(emb) == 0 or not isinstance(emb[0], list)):
            query_embeddings = [emb]
        else:
            query_embeddings = emb

        count = self.count()
        if count == 0:
            return {"ids": [], "documents": [], "metadatas": [], "distances": []}

        n_results = max(1, min(top_k, count))
        kwargs: Dict[str, Any] = {
            "query_embeddings": query_embeddings,
            "n_results": n_results,
        }
        if where:
            kwargs["where"] = where

        results = self.collection.query(**kwargs)

        return {
            "ids": results.get("ids", [[]])[0] if results.get("ids") else [],
            "documents": results.get("documents", [[]])[0] if results.get("documents") else [],
            "metadatas": results.get("metadatas", [[]])[0] if results.get("metadatas") else [],
            "distances": results.get("distances", [[]])[0] if results.get("distances") else [],
        }

    def count(self) -> int:
        """Return total number of items in the vector collection."""
        return self.collection.count()

    def delete(
        self,
        ids: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Delete items from collection by IDs or metadata filter.

        Args:
            ids: Optional list of document IDs to delete.
            where: Optional metadata filter dict.
        """
        kwargs: Dict[str, Any] = {}
        if ids:
            kwargs["ids"] = ids
        if where:
            kwargs["where"] = where
        if kwargs:
            self.collection.delete(**kwargs)
            logger.info("Deleted items from vector collection.")
