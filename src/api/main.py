from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials

import os
from dotenv import load_dotenv
from typing import List
import numpy as np
from pydantic import BaseModel
from dataclasses import asdict

from src.services.face_recognition_service import FaceRecognitionService
from src.infrastructure.ml.detect.deepface_detector import DeepFaceDetector
from src.infrastructure.ml.embedd.deepface_embedder import DeepFaceEmbedder
from src.infrastructure.database.mongodb import MongoDBFaceDatabase
from src.utils.posprocessing import remove_face_image
from src.api.middleware.auth import APIKeyAuth

load_dotenv()

app = FastAPI(title="Face Recognition API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
db = MongoDBFaceDatabase(
    connection_string=os.getenv("MONGODB_URI"),
)

face_service = FaceRecognitionService(
    detector=DeepFaceDetector(os.getenv("DEEPFACE_DETECTOR_BACKEND")),
    embedder=DeepFaceEmbedder(os.getenv("DEEPFACE_EMBEDDER_MODEL")),
    database=db
)

# Initialize auth middleware
auth_handler = APIKeyAuth(face_service)

# Requests types
class APIKeyRequest(BaseModel):
    user: str
    api_key_name: str
    
class RevokeAPIKeyRequest(BaseModel):
    api_auth: APIKeyRequest
    
class OrganizationRequest(BaseModel):
    organization: str
    
class RegisterRequest(BaseModel):
    images: List[str]
    name: str
    api_auth: APIKeyRequest

class RecognizeRequest(BaseModel):
    image: str
    threshold: float
    api_auth: APIKeyRequest

class DetectionRequest(BaseModel):
    image: str
    api_auth: APIKeyRequest

## Config routes
@app.post("/orgs")
async def create_organization(
    request: OrganizationRequest,
):
    success = face_service.create_organization(request.organization)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to create organization")
    return {"message": "Organization created successfully"}

@app.post("/orgs/{organization}/api-key")
async def create_api_key(
    organization: str,
    request: APIKeyRequest
):
    """Create a new API key for an organization"""
    api_key = face_service.generate_api_key(request.user, request.api_key_name, organization)
    if api_key is None:
        raise HTTPException(status_code=400, detail="Failed to create API key")
    
    return asdict(api_key)
    
@app.delete("/orgs/{organization}/api-key")
async def revoke_api_key(
    organization: str,
    request: RevokeAPIKeyRequest,
    credentials: HTTPAuthorizationCredentials = Depends(auth_handler)
):
    """Revoke an existing API key"""
    success = face_service.revoke_api_key(credentials.credentials, request.api_auth.user, request.api_auth.api_key_name, organization)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to revoke API key")
    return {"message": "API key revoked successfully"}

## Functionalites routes
@app.post("/register/{organization}")
async def register_person(
    organization: str,
    request: RegisterRequest,
    credentials: HTTPAuthorizationCredentials = Depends(auth_handler)
):
    success = face_service.register_person(request.images, request.name, organization)
    print(success)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to register person")
    return {"message": "Person registered successfully"}

@app.post("/recognize/{organization}")
async def recognize_person(
    organization: str,
    request: RecognizeRequest,
    credentials: HTTPAuthorizationCredentials = Depends(auth_handler)
):
    recognize_result = asdict(face_service.recognize_person(request.image, request.threshold, organization))
    cleaned_result = remove_face_image(recognize_result)
    return cleaned_result
 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)