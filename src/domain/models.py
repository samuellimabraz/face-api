from dataclasses import dataclass
from typing import List, Optional
import numpy as np
from datetime import datetime

@dataclass
class BoundingBox:
    x: int
    y: int
    w: int
    h: int

@dataclass
class DetectionResult:
    bounding_box: BoundingBox
    confidence: float
    face_image: np.ndarray

@dataclass
class DetectionResults:
    result: List[DetectionResult]
    inference_time: float

@dataclass
class VectorSearchResult:
    name: str
    distance: Optional[float]
    
@dataclass
class RecognizeResult:
    detections: DetectionResults
    searchs: List[VectorSearchResult]

@dataclass
class APIKey:
    key: str
    user: str
    api_key_name: str
    organization: str
    created_at: datetime
    last_used: Optional[datetime]
    is_active: bool