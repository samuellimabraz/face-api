from abc import ABC, abstractmethod
from typing import List, Union
import numpy as np
from .models import DetectionResults, VectorSearchResult, APIKey


class FaceDetector(ABC):
    """
    Abstract interface for face detection functionality.

    Classes implementing this interface should provide functionality
    to detect faces in various image formats.
    """

    @abstractmethod
    def detect(self, image: Union[str, np.ndarray]) -> DetectionResults:
        """
        Detect faces in the provided image.

        Args:
            image (Union[str, np.ndarray]): Image to analyze, either as a file path or numpy array

        Returns:
            DetectionResults: Container object with detection results including face coordinates,
                              confidence scores, and cropped face images
        """
        pass


class FaceEmbedder(ABC):
    """
    Abstract interface for face embedding generation.

    Classes implementing this interface should convert face images
    into vector embeddings suitable for face recognition.
    """

    @abstractmethod
    def generate_embedding(self, face_image: np.ndarray) -> np.ndarray:
        """
        Generate a numerical embedding vector for a face image.

        Args:
            face_image (np.ndarray): Cropped and aligned face image as numpy array

        Returns:
            np.ndarray: Face embedding vector representing facial features
        """
        pass


class FaceDatabase(ABC):
    """
    Abstract interface for face database operations.

    Classes implementing this interface should provide storage and
    retrieval functionality for face embeddings and related operations.
    """

    @abstractmethod
    def create_organization(self, organization: str) -> bool:
        """
        Create a new organization in the database.

        Args:
            organization (str): Name of the organization to create

        Returns:
            bool: True if creation was successful, False otherwise
        """
        pass

    @abstractmethod
    def save_embedding(
        self, name: str, organization: str, embedding: np.ndarray
    ) -> None:
        """
        Save a face embedding to the database.

        Args:
            name (str): Name of the person associated with the embedding
            organization (str): Organization the person belongs to
            embedding (np.ndarray): Face embedding vector to save

        Returns:
            None
        """
        pass

    @abstractmethod
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
        """
        pass

    @abstractmethod
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
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        """
        pass
