from datetime import datetime
from typing import Optional

import numpy as np
import time
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.operations import SearchIndexModel
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError
import bcrypt
import secrets

from src.domain.interfaces import FaceDatabase
from src.domain.models import VectorSearchResult, APIKey
from src.utils.logging import logger


class MongoDBFaceDatabase(FaceDatabase):
    """
    MongoDB implementation of the FaceDatabase interface.

    This class manages face embeddings, organizations, and API keys using MongoDB,
    including vector search capabilities for facial recognition.
    """

    vector_search_index_definition = {
        "fields": [
            {
                "type": "vector",
                "path": "embedding",
                "similarity": "cosine",
                "numDimensions": 512,
            },
        ]
    }

    def __init__(self, connection_string: str):
        """
        Initialize the MongoDB database connection.

        Args:
            connection_string (str): MongoDB connection string
        """
        self.client = MongoClient(connection_string, server_api=ServerApi("1"))
        self._verify_connection()

    def _verify_connection(self) -> None:
        """
        Verify that the MongoDB connection is working.

        Raises:
            Exception: If connection to MongoDB fails
        """
        try:
            self.client.admin.command("ping")
            logger.info("Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise

    def _get_organization_db(self, organization: str) -> Database:
        """
        Get the MongoDB database object for an organization.

        Args:
            organization (str): Organization name

        Returns:
            Database: MongoDB database object
        """
        return self.client[organization]

    def database_exists(self, database_name: str) -> bool:
        """
        Check if a database exists in MongoDB.

        Args:
            database_name (str): Name of the database to check

        Returns:
            bool: True if the database exists, False otherwise
        """
        return database_name in self.client.list_database_names()

    def vector_index_exists(self, organization: str, index_name: str) -> bool:
        """
        Check if a vector search index exists for a collection.

        Args:
            organization (str): Organization name
            index_name (str): Name of the vector index to check

        Returns:
            bool: True if the vector index exists, False otherwise

        Raises:
            RuntimeError: If checking for index existence fails
        """
        try:
            indexes = (
                self.client[organization]
                .get_collection("embeddings")
                .list_search_indexes()
            )
            return any(index["name"] == index_name for index in indexes)
        except Exception as e:
            raise RuntimeError(f"Failed to verify vector index: {str(e)}")

    def create_organization(self, organization: str) -> bool:
        """
        Create a new organization with required collections and indexes.

        Args:
            organization (str): Name of the organization to create

        Returns:
            bool: True if creation was successful or organization already exists
        """
        if self.database_exists(organization):
            print(f"Organization '{organization}' already exists.")
            return True

        db = self._get_organization_db(organization)

        # Create `api_keys` collection with indexes
        if "api_keys" not in db.list_collection_names():
            db.create_collection("api_keys")
            db["api_keys"].create_index(
                [("user", 1), ("api_key_name", 1), ("organization", 1)], unique=True
            )

        # Create `embeddings` collection
        if "embeddings" not in db.list_collection_names():
            db.create_collection("embeddings")
            if not self.vector_index_exists(organization, f"face_embbedings"):
                print(f"Creating vector index for '{organization}'")
                db["embeddings"].create_search_index(
                    SearchIndexModel(
                        definition=self.vector_search_index_definition,
                        name="face_embbedings",
                        type="vectorSearch",
                    )
                )
                time.sleep(2)  # Wait for index creation

        return True

    def generate_api_key(
        self, user: str, api_key_name: str, organization: str
    ) -> APIKey:
        """
        Generate a new API key for a user in an organization.

        Args:
            user (str): Username requesting the API key
            api_key_name (str): Name/identifier for the API key
            organization (str): Organization the key is associated with

        Returns:
            APIKey: Generated API key information

        Raises:
            ValueError: If organization doesn't exist or API key already exists
            RuntimeError: If API key creation fails
        """
        api_key = secrets.token_urlsafe(32)
        hashed_key = bcrypt.hashpw(api_key.encode(), bcrypt.gensalt())

        if not self.database_exists(organization):
            raise ValueError(
                f"Database '{organization}' does not exist. Create it first."
            )

        db = self._get_organization_db(organization)
        api_keys_collection = db["api_keys"]

        # Manual check to avoid duplicates
        existing_key = api_keys_collection.find_one(
            {"user": user, "api_key_name": api_key_name, "organization": organization}
        )

        if existing_key:
            raise ValueError(
                f"API key for '{user}' with name '{api_key_name}' already exists in '{organization}'."
            )

        api_key_doc = {
            "user": user,
            "api_key_name": api_key_name,
            "organization": organization,
            "created_at": datetime.now(),
            "last_used": None,
            "is_active": True,
        }
        try:
            api_keys_collection.insert_one(
                {**api_key_doc, "key": str(hashed_key.decode())}
            )
            print(f"API key generated for '{user}' in organization '{organization}'")
        except Exception as e:
            raise RuntimeError(f"Failed to create API key: {str(e)}")

        return APIKey(**api_key_doc, key=api_key)

    def validate_api_key(
        self, api_key: str, user: str, api_key_name: str, organization: str
    ) -> bool:
        """
        Validate if an API key is authentic and active.

        Args:
            api_key (str): The API key to validate
            user (str): Username that owns the key
            api_key_name (str): Name/identifier of the API key
            organization (str): Organization the key belongs to

        Returns:
            bool: True if the API key is valid, False otherwise

        Raises:
            ValueError: If organization doesn't exist
        """
        if not self.database_exists(organization):
            raise ValueError(f"Database '{organization}' does not exist.")

        db = self._get_organization_db(organization)

        key_doc = db["api_keys"].find_one(
            {"user": user, "api_key_name": api_key_name, "is_active": True}
        )

        logger.info(
            f"Validating {api_key} API key for '{user}' in organization '{organization}'"
        )
        print(
            f"Validating {api_key} API key for '{user}' in organization '{organization}'"
        )

        if not key_doc:
            print(
                f"No {api_key} API key found for user '{user}' in organization '{organization}'"
            )
            return False

        is_valid = bcrypt.checkpw(
            api_key.encode("utf-8"), key_doc["key"].encode("utf-8")
        )
        if is_valid:
            db["api_keys"].update_one(
                {"_id": key_doc["_id"]}, {"$set": {"last_used": datetime.now()}}
            )
        else:
            print(f"Hash mismatch for API key: {api_key}")

        print(f"API key validated for {user} in org:'{organization}'")

        return is_valid

    def revoke_api_key(
        self, api_key: str, user: str, api_key_name: str, organization: str
    ) -> bool:
        """
        Revoke an existing API key.

        Args:
            api_key (str): The API key to revoke
            user (str): Username that owns the key
            api_key_name (str): Name/identifier of the API key
            organization (str): Organization the key belongs to

        Returns:
            bool: True if revocation was successful, False otherwise
        """
        if not self.validate_api_key(api_key, user, api_key_name, organization):
            return False

        logger.info(f"Revoking API key for {user} in organization '{organization}'")
        print(f"Revoking API key for {user} in organization '{organization}'")

        db = self._get_organization_db(organization)
        db["api_keys"].delete_one({"user": user, "api_key_name": api_key_name})

        return True

    def save_embedding(
        self, name: str, organization: str, embedding: np.ndarray
    ) -> None:
        """
        Save a face embedding to the database.

        Args:
            name (str): Name of the person associated with the embedding
            organization (str): Organization the person belongs to
            embedding (np.ndarray): Face embedding vector to save

        Raises:
            ValueError: If organization doesn't exist
            RuntimeError: If saving the embedding fails
        """
        try:
            # Check if collection exists
            if not self.database_exists(organization):
                raise ValueError(
                    f"Database '{organization}' does not exist. Create it first."
                )

            document = {
                "name": name,
                "embedding": embedding.tolist(),
                "created_at": datetime.now(),
            }

            db = self._get_organization_db(organization)
            db["embeddings"].insert_one(document)
        except Exception as e:
            raise RuntimeError(f"Failed to save embedding: {str(e)}")

    def vector_search(
        self, embedding: np.ndarray, threshold: float, organization: str
    ) -> VectorSearchResult:
        """
        Search for the closest match to the provided embedding.

        Args:
            embedding (np.ndarray): Query face embedding vector
            threshold (float): Similarity threshold for matching
            organization (str): Organization to search within

        Returns:
            VectorSearchResult: Result containing the name of the matched person and similarity score

        Raises:
            ValueError: If organization or vector index doesn't exist
            RuntimeError: If search operation fails
        """
        try:
            # Check if collection exists
            if not self.database_exists(organization):
                raise ValueError(
                    f"Database '{organization}' does not exist. Create it first."
                )

            # Check if index exists
            index_name = f"face_embbedings"
            if not self.vector_index_exists(organization, index_name):
                raise ValueError(
                    f"Vector index '{index_name}' does not exist for '{organization}'. Create it first."
                )

            pipeline = [
                {
                    "$vectorSearch": {
                        "index": f"face_embbedings",
                        "exact": False,
                        "numCandidates": 20,
                        "path": "embedding",
                        "queryVector": embedding.tolist(),
                        "limit": 1,
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "name": 1,
                        "score": {"$meta": "vectorSearchScore"},
                    }
                },
            ]

            results = list(
                self._get_organization_db(organization)["embeddings"].aggregate(
                    pipeline
                )
            )

            if not results:  # Check if no results
                return VectorSearchResult(name="unknown", distance=None)

            best_match = results[0]  # Get the first (and only) result
            if best_match["score"] < threshold:
                return VectorSearchResult(name="unknown", distance=best_match["score"])

            return VectorSearchResult(
                name=best_match["name"], distance=best_match["score"]
            )

        except Exception as e:
            raise RuntimeError(f"Failed to search similar embeddings: {str(e)}")

    def get_organizations(self) -> list:
        """
        Get a list of all organizations (databases) in MongoDB,
        filtering out system databases.

        Returns:
            list: List of organization names

        Raises:
            RuntimeError: If getting organizations fails
        """
        try:
            all_dbs = self.client.list_database_names()

            system_dbs = ["admin", "local", "config"]
            organizations = [db for db in all_dbs if db not in system_dbs]

            return organizations
        except Exception as e:
            logger.error(f"Failed to get organizations: {e}")
            raise RuntimeError(f"Failed to get organizations: {str(e)}")
