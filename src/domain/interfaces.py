from abc import ABC, abstractmethod
from typing import List, Union
import numpy as np
from .models import DetectionResults, VectorSearchResult, APIKey

class FaceDetector(ABC):
    @abstractmethod
    def detect(self, image: Union[str, np.ndarray]) -> DetectionResults:
        pass

class FaceEmbedder(ABC):
    @abstractmethod
    def generate_embedding(self, face_image: np.ndarray) -> np.ndarray:
        pass

class FaceDatabase(ABC):
    @abstractmethod
    def create_organization(self, organization: str) -> bool:
        pass

    @abstractmethod
    def save_embedding(self, name: str, organization: str, embedding: np.ndarray) -> None:
        pass

    @abstractmethod
    def vector_search(self, embedding: np.ndarray, threshold: float, organization: str) -> VectorSearchResult:
        pass
    
    @abstractmethod
    def generate_api_key(self, user: str, api_key_name: str, organization: str) -> APIKey:
        pass
    @abstractmethod
    def revoke_api_key(self, api_key: str, user: str, api_key_name: str, organization: str) -> bool:
        pass
    
    @abstractmethod
    def validate_api_key(api_key: str, user: str, api_key_name: str, organization: str) -> bool:
        pass