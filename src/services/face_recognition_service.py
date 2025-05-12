from typing import List, Union
import numpy as np
from src.domain.interfaces import FaceDetector, FaceEmbedder, FaceDatabase
from src.domain.models import (
    DetectionResults,
    RecognizeResult,
    APIKey,
)
from src.utils.logging import logger


class FaceRecognitionService:
    """
    Service class that coordinates face detection, embedding generation, and database operations.

    This service acts as a facade over the detection, embedding, and database components,
    providing a simplified API for face recognition operations.
    """

    def __init__(
        self, detector: FaceDetector, embedder: FaceEmbedder, database: FaceDatabase
    ):
        """
        Initialize the face recognition service with required components.

        Args:
            detector (FaceDetector): Component responsible for detecting faces in images
            embedder (FaceEmbedder): Component responsible for generating face embeddings
            database (FaceDatabase): Component responsible for storing and retrieving face data
        """
        self.face_detector = detector
        self.face_embedder = embedder
        self.face_database = database

    def create_organization(self, organization: str) -> bool:
        """
        Create a new organization in the database.

        Args:
            organization (str): Name of the organization to create

        Returns:
            bool: True if creation was successful, False otherwise
        """
        try:
            result = self.face_database.create_organization(organization)
        except Exception as e:
            print(e)
            return False

        return result

    def generate_api_key(
        self, user: str, api_key_name: str, organization: str
    ) -> APIKey | None:
        """
        Generate a new API key for a user in an organization.

        Args:
            user (str): Username requesting the API key
            api_key_name (str): Name/identifier for the API key
            organization (str): Organization the key is associated with

        Returns:
            APIKey | None: Generated API key information or None if operation fails
        """
        try:
            return self.face_database.generate_api_key(user, api_key_name, organization)
        except Exception as e:
            logger.error(f"Failed to generate API key: {e}")
            return None

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
        try:
            return self.face_database.revoke_api_key(
                api_key, user, api_key_name, organization
            )
        except Exception as e:
            logger.error(f"Failed to revoke API key: {e}")
            return False

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
        try:
            return self.face_database.validate_api_key(
                api_key, user, api_key_name, organization
            )
        except Exception as e:
            logger.error(f"Failed to validate API key: {e}")
            return False

    def register_person(
        self, images: List[Union[str, np.ndarray]], name: str, organization: str
    ) -> bool:
        """
        Register a person in the face recognition system.

        Processes multiple images of a person, detects faces in each,
        generates embeddings, and stores them in the database.

        Args:
            images (List[Union[str, np.ndarray]]): List of images containing the person's face
            name (str): Name of the person to register
            organization (str): Organization the person belongs to

        Returns:
            bool: True if at least one face was successfully registered, False otherwise
        """
        embeddings = []

        for i, image in enumerate(images, 1):
            try:
                print(f"Processing image {i}/{len(images)}")
                detection_results = self.face_detector.detect(image)

                if detection_results.result:
                    for detection in detection_results.result:
                        embedding = self.face_embedder.generate_embedding(
                            detection.face_image
                        )
                        embeddings.append(embedding)
                else:
                    print(f"No faces detected in image {i}")
            except Exception as e:
                print(f"Error processing image {i}: {e}")
                continue

        if embeddings:
            print(f"Saving {len(embeddings)} embeddings for {name}")
            for embedding in embeddings:
                self.face_database.save_embedding(name, organization, embedding)
            return True

        print("No faces detected in any image")
        return False

    def detect_faces(self, image: Union[str, np.ndarray]) -> DetectionResults:
        """
        Detect faces in the provided image.

        Args:
            image (Union[str, np.ndarray]): Image to analyze, either as a file path or numpy array

        Returns:
            DetectionResults: Container object with detection results including face coordinates,
                              confidence scores, and cropped face images
        """
        return self.face_detector.detect(image)

    def recognize_person(
        self, image: Union[str, np.ndarray], threshold: float, organization: str
    ) -> RecognizeResult:
        """
        Recognize people in an image by comparing detected faces against the database.

        Args:
            image (Union[str, np.ndarray]): Image to analyze, either as a file path or numpy array
            threshold (float): Similarity threshold for matching (higher values require closer matches)
            organization (str): Organization to search within

        Returns:
            RecognizeResult: Result containing both detection information and recognition results
        """
        detection_results = self.face_detector.detect(image)

        search_results = []
        for detection in detection_results.result:
            embedding = self.face_embedder.generate_embedding(detection.face_image)
            search_results.append(
                self.face_database.vector_search(embedding, threshold, organization)
            )

        return RecognizeResult(detections=detection_results, searchs=search_results)

    def get_organizations(self) -> List[str]:
        """
        Get a list of all registered organizations.

        Returns:
            List[str]: A list of organization names
        """
        try:
            return self.face_database.get_organizations()
        except Exception as e:
            logger.error(f"Failed to get organizations: {e}")
            return []
