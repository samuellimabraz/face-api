from typing import List, Union
import numpy as np
from src.domain.interfaces import FaceDetector, FaceEmbedder, FaceDatabase
from src.domain.models import (
    DetectionResults, 
    VectorSearchResult, 
    RecognizeResult,
    APIKey
)
from src.utils.logging import logger

class FaceRecognitionService:
    def __init__(self, detector: FaceDetector, embedder: FaceEmbedder, database: FaceDatabase):
        self.face_detector = detector
        self.face_embedder = embedder
        self.face_database = database

    def create_organization(self, organization: str) -> bool:
        try:
            result = self.face_database.create_organization(organization)
        except Exception as e:
            print(e)
            return False
        
        return result
    
    def generate_api_key(self, user: str, api_key_name: str, organization: str) -> APIKey | None:
        try:
            return self.face_database.generate_api_key(user, api_key_name, organization)
        except Exception as e:
            logger.error(f"Failed to generate API key: {e}")
            return None

    def revoke_api_key(self, api_key: str, user: str, api_key_name: str, organization: str) -> bool:
        try:
            return self.face_database.revoke_api_key(api_key, user, api_key_name, organization)
        except Exception as e:
            logger.error(f"Failed to revoke API key: {e}")
            return False
    
    def validate_api_key(self, api_key: str, user: str, api_key_name: str, organization: str) -> bool:
        try:
            return self.face_database.validate_api_key(api_key, user, api_key_name, organization)
        except Exception as e:
            logger.error(f"Failed to validate API key: {e}")
            return False
    
    def register_person(self, images: List[Union[str, np.ndarray]], name: str, organization: str) -> bool:
        embeddings = []
        
        for i, image in enumerate(images, 1):
            try:
                print(f"Processing image {i}/{len(images)}")
                detection_results = self.face_detector.detect(image)
                
                if detection_results.result:
                    for detection in detection_results.result:
                        embedding = self.face_embedder.generate_embedding(detection.face_image)
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
        return self.face_detector.detect(image)

    def recognize_person(self, image: Union[str, np.ndarray], threshold: float, organization: str) -> RecognizeResult:
        detection_results = self.face_detector.detect(image)
        
        search_results = []
        for detection in detection_results.result:
            embedding = self.face_embedder.generate_embedding(detection.face_image)
            search_results.append(self.face_database.vector_search(embedding, threshold, organization))
        
        return RecognizeResult(detections=detection_results, searchs=search_results)