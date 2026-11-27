import os
import logging
from typing import Optional, Dict, Any, List
import chromadb
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection
from chromadb.config import Settings

logger = logging.getLogger(__name__)


class ChromaDB:
    """
    ChromaDB client wrapper supporting Persistent (local disk),
    HTTP (remote Chroma server), and Ephemeral (in-memory) modes.
    """

    def __init__(
        self,
        mode: Optional[str] = None,
        persist_directory: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        ssl: Optional[bool] = None,
        settings: Optional[Settings] = None,
    ):
        """
        Initialize ChromaDB client.

        Args:
            mode: Client mode: 'persistent' (default), 'http', or 'ephemeral'.
                  Can also be configured via CHROMA_MODE environment variable.
            persist_directory: Local storage directory for 'persistent' mode.
                               Defaults to CHROMA_PERSIST_DIRECTORY or './data/chroma'.
            host: Server host for 'http' mode. Defaults to CHROMA_HOST or 'localhost'.
            port: Server port for 'http' mode. Defaults to CHROMA_PORT or 8000.
            ssl: Use SSL for 'http' mode. Defaults to CHROMA_SSL or False.
            settings: Optional chromadb.config.Settings override.
        """
        self.mode = (mode or os.getenv("CHROMA_MODE", "persistent")).lower()
        self.persist_directory = (
            persist_directory
            or os.getenv("CHROMA_PERSIST_DIRECTORY")
            or os.getenv("CHROMA_PATH", "./data/chroma")
        )
        self.host = host or os.getenv("CHROMA_HOST", "localhost")
        self.port = int(port or os.getenv("CHROMA_PORT", 8000))
        self.ssl = ssl if ssl is not None else os.getenv("CHROMA_SSL", "false").lower() == "true"

        # Initialize the underlying chromadb client based on mode
        if self.mode == "http":
            logger.info(f"Connecting to ChromaDB HTTP client at {self.host}:{self.port} (ssl={self.ssl})")
            self.client: ClientAPI = chromadb.HttpClient(
                host=self.host,
                port=self.port,
                ssl=self.ssl,
                settings=settings,
            )
        elif self.mode in ("ephemeral", "in_memory", "memory"):
            logger.info("Initializing ChromaDB Ephemeral (in-memory) client")
            self.client: ClientAPI = chromadb.EphemeralClient(settings=settings)
        else:
            # Default to PersistentClient
            os.makedirs(self.persist_directory, exist_ok=True)
            logger.info(f"Initializing ChromaDB PersistentClient at path: {self.persist_directory}")
            self.client: ClientAPI = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=settings,
            )

    def get_or_create_collection(
        self,
        name: str,
        metadata: Optional[Dict[str, Any]] = None,
        embedding_function: Optional[Any] = None,
    ) -> Collection:
        """
        Get an existing collection or create one if it does not exist.

        Args:
            name: Collection name.
            metadata: Optional collection metadata (e.g. {"hnsw:space": "cosine"}).
            embedding_function: Optional Chroma embedding function.
        """
        return self.client.get_or_create_collection(
            name=name,
            metadata=metadata,
            embedding_function=embedding_function,
        )

    def get_collection(
        self,
        name: str,
        embedding_function: Optional[Any] = None,
    ) -> Collection:
        """Get an existing collection by name. Raises ValueError if not found."""
        return self.client.get_collection(
            name=name,
            embedding_function=embedding_function,
        )

    def delete_collection(self, name: str) -> None:
        """Delete a collection by name."""
        self.client.delete_collection(name=name)
        logger.info(f"Deleted ChromaDB collection: {name}")

    def list_collections(self) -> List[Any]:
        """List all collections in ChromaDB."""
        return self.client.list_collections()

    def __getitem__(self, name: str) -> Collection:
        """
        Enable dictionary-style access: db['collection_name'].
        Returns an existing collection or creates it if it doesn't exist.
        This provides compatibility with VectorRepository (client[collection]).
        """
        return self.get_or_create_collection(name)

    def heartbeat(self) -> int:
        """Returns nanoseconds heartbeat timestamp from Chroma."""
        return self.client.heartbeat()

    def ping(self) -> bool:
        """Health check method verifying the Chroma client is responsive."""
        try:
            self.client.heartbeat()
            return True
        except Exception as e:
            logger.error(f"ChromaDB health check failed: {e}")
            return False


_chroma_instance: Optional[ChromaDB] = None


def get_chroma_db(
    mode: Optional[str] = None,
    persist_directory: Optional[str] = None,
) -> ChromaDB:
    """
    Get or create a singleton instance of ChromaDB.
    Useful for dependency injection or app lifespan events.
    """
    global _chroma_instance
    if _chroma_instance is None:
        _chroma_instance = ChromaDB(mode=mode, persist_directory=persist_directory)
    return _chroma_instance
