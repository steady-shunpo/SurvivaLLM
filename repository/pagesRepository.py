import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

#this is currently mongo specific. abstract later and put the same code in mongoRepository class
class PagesRepository:
    """
    Repository for managing document pages stored in MongoDB.
    Provides CRUD operations for documents (titles, content, metadata).
    """

    def __init__(self, client, collection_name: str = "pages"):
        """
        Initialize PagesRepository.

        Args:
            client: MongoDB client wrapper, Database, or Collection instance.
            collection_name: Collection name if client is a MongoDB or Database instance.
        """
        self.client = client
        if hasattr(client, "insert_one"):
            # client is directly a MongoDB Collection instance
            self.collection = client
        elif hasattr(client, "get_collection"):
            # client is a MongoDB wrapper or Database instance
            self.collection = client.get_collection(collection_name)
        elif hasattr(client, "__getitem__"):
            self.collection = client[collection_name]
        else:
            self.collection = client

    def createDocument(self, document: Dict[str, Any]) -> Optional[str]:
        """
        Create or upsert a document page in the database.

        Args:
            document: Dictionary with at least 'title' and 'content'.

        Returns:
            The content string of the created document.
        """
        title = document.get("title")
        if not title:
            raise ValueError("Document must include a 'title' field.")

        doc_to_save = {
            **document,
            # "updated_at": datetime.utcnow(),
        }

        # Upsert by title to prevent duplicate entries for the same page
        self.collection.update_one(
            {"title": title},
            {"$set": doc_to_save},
            upsert=True,
        )
        logger.info(f"Document created/updated with title: {title}")
        return document.get("content")

    def fetchDocument(self, title: str) -> Optional[str]:
        """
        Fetch a single document's content by its title.

        Args:
            title: The title of the document to fetch.

        Returns:
            The content string if found, otherwise None.
        """
        doc = self.collection.find_one({"title": title}, {"content": 1, "_id": 0})
        if doc and "content" in doc:
            return doc["content"]
        return None

    def fetchDocuments(self, titles: List[str]) -> List[str]:
        """
        Fetch content for a list of document titles, preserving input order.

        Args:
            titles: List of titles to search for.

        Returns:
            List of content strings for the matched titles.
        """
        if not titles:
            return []

        # Batch query using MongoDB $in operator for efficiency
        cursor = self.collection.find(
            {"title": {"$in": titles}},
            {"title": 1, "content": 1, "_id": 0},
        )
        docs_map = {
            doc["title"]: doc.get("content", "")
            for doc in cursor
            if "title" in doc
        }

        # Preserve the original ranking order of titles
        contents = []
        for title in titles:
            if title in docs_map:
                contents.append(docs_map[title])

        return contents

    def updateDocument(self, title: str, newContent: str) -> bool:
        """
        Update the content of a document by title, or insert it if it does not exist.

        Args:
            title: Title of the document.
            newContent: New content string (e.g. freshly fetched from web).

        Returns:
            True if the update/upsert succeeded.
        """
        result = self.collection.update_one(
            {"title": title},
            {
                "$set": {
                    "content": newContent,
                    # "updated_at": datetime.utcnow(),
                }
            },
            upsert=True,
        )
        logger.info(f"Updated document title: {title}")
        return result.acknowledged

    def deleteDocument(self, title: str) -> bool:
        """
        Delete a document page by title.

        Args:
            title: Title of the document to delete.

        Returns:
            True if a document was deleted, False otherwise.
        """
        result = self.collection.delete_one({"title": title})
        return result.deleted_count > 0

    def listTitles(self, limit: int = 100) -> List[str]:
        """List all document titles up to the specified limit."""
        cursor = self.collection.find({}, {"title": 1, "_id": 0}).limit(limit)
        return [doc["title"] for doc in cursor if "title" in doc]

    def count(self) -> int:
        """Return total number of documents in collection."""
        return self.collection.count_documents({})

    # Aliases for snake_case naming style
    create_document = createDocument
    fetch_document = fetchDocument
    fetch_documents = fetchDocuments
    update_document = updateDocument
    delete_document = deleteDocument
