import os
import logging
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

logger = logging.getLogger(__name__)


class MongoDB:
    """
    MongoDB connection manager and client wrapper.
    Supports connection pooling, database/collection access, and health checks.
    """

    def __init__(
        self,
        uri: Optional[str] = None,
        db_name: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize MongoDB client.

        Args:
            uri: MongoDB connection URI. Defaults to MONGO_URI env var or mongodb://localhost:27017.
            db_name: Target database name. Defaults to MONGO_DB_NAME env var or 'survivallm'.
            **kwargs: Extra arguments passed directly to MongoClient (e.g. serverSelectionTimeoutMS).
        """
        self.uri = uri or os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.db_name = db_name or os.getenv("MONGO_DB_NAME", "survivallm")

        # Set default server selection timeout to 5s if not specified
        kwargs.setdefault("serverSelectionTimeoutMS", 5000)

        self.client: MongoClient = MongoClient(self.uri, **kwargs)
        self.db: Database = self.client[self.db_name]
        logger.info(f"MongoDB client initialized for database: {self.db_name}")

    def get_database(self, name: Optional[str] = None) -> Database:
        """Return the specified database, or the default configured database."""
        if name:
            return self.client[name]
        return self.db

    def get_collection(self, name: str, db_name: Optional[str] = None) -> Collection:
        """
        Return a collection from the default or specified database.

        Args:
            name: Name of the collection.
            db_name: Optional database name override.
        """
        database = self.get_database(db_name)
        return database[name]

    def __getitem__(self, name: str) -> Collection:
        """Enable dictionary-style access: db['collection_name']."""
        return self.get_collection(name)

    def ping(self) -> bool:
        """Check if MongoDB server is reachable."""
        try:
            self.client.admin.command("ping")
            return True
        except Exception as e:
            logger.error(f"MongoDB ping failed: {e}")
            return False

    def close(self):
        """Close the MongoDB connection pool."""
        self.client.close()
        logger.info("MongoDB connection closed.")


_mongo_instance: Optional[MongoDB] = None


def get_mongo_db(uri: Optional[str] = None, db_name: Optional[str] = None) -> MongoDB:
    """
    Get or create a singleton instance of MongoDB.
    Useful for dependency injection or app lifespan events.
    """
    global _mongo_instance
    if _mongo_instance is None:
        _mongo_instance = MongoDB(uri=uri, db_name=db_name)
    return _mongo_instance
