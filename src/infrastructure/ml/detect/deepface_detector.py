from typing import Union

import numpy as np
from deepface import DeepFace
import time

from src.domain.interfaces import FaceDetector
from src.domain.models import DetectionResult, DetectionResults, BoundingBox
from src.utils.logging import logger

class DeepFaceDetector(FaceDetector):
    def __init__(self, detector_backend: str = "yolov8"):
        self.detector_backend = detector_backend
        
    def detect(self, image: Union[str, np.ndarray]) -> DetectionResults:
        try:
            start_time = time.time()
            faces = DeepFace.extract_faces(
                img_path=image,
                detector_backend=self.detector_backend,
                enforce_detection=True,
                align=True
            )
            inference_time = time.time() - start_time
            results = [
                DetectionResult(
                    bounding_box=BoundingBox(
                        x=face["facial_area"]["x"],
                        y=face["facial_area"]["y"],
                        w=face["facial_area"]["w"],
                        h=face["facial_area"]["h"]
                    ),
                    confidence=face["confidence"],
                    face_image=face["face"]
                )
                for face in faces
                if face["confidence"] > 0.7
            ]

            return DetectionResults(result=results, inference_time=inference_time)
        except Exception as e:
            logger.error(f"Face detection failed: {e}")
            return DetectionResults(result=[], inference_time=0)