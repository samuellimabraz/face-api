import numpy as np
from deepface import DeepFace
from src.domain.interfaces import FaceEmbedder
from src.utils.logging import logger

class DeepFaceEmbedder(FaceEmbedder):
    def __init__(self, model_name: str = "Facenet512"):
        self.model_name = model_name

    def generate_embedding(self, face_image: np.ndarray) -> np.ndarray:
        try:
            result = DeepFace.represent(
                img_path=face_image,
                model_name=self.model_name,
                detector_backend='skip',
                enforce_detection=False
            )
            return np.array(result[0]["embedding"])
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise