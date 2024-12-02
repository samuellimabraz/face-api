from fastapi import Request, HTTPException, WebSocket, WebSocketException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import json
import os
from src.services.face_recognition_service import FaceRecognitionService
import redis

class APIKeyAuth(HTTPBearer):
    def __init__(self, 
        service: FaceRecognitionService, 
        cache_host: str = os.getenv("REDIS_HOST", "localhost"), 
        cache_port: int = 6379
    ):
        super(APIKeyAuth, self).__init__(auto_error=True)
        self.service = service
        self.cache = redis.Redis(host=cache_host, port=cache_port, decode_responses=True)
    
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        return await self.authenticate_request(request)

    async def authenticate_request(self, request: Request) -> HTTPAuthorizationCredentials:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)

        if not credentials or not credentials.scheme == "Bearer":
            raise HTTPException(status_code=403, detail="Invalid or missing authorization credentials.")
        
        organization = request.path_params.get("organization")
        if not organization:
            raise HTTPException(status_code=400, detail="Organization not specified.")

        request_body = await request.body()
        if not request_body:
            raise HTTPException(status_code=400, detail="Missing request body.")

        request_data = json.loads(request_body.decode("utf-8"))
        user = request_data.get("api_auth", {}).get("user")
        api_key_name = request_data.get("api_auth", {}).get("api_key_name")

        if not user or not api_key_name:
            raise HTTPException(status_code=400, detail="User or API key name not specified.")

        cache_key = f"{organization}:{user}:{api_key_name}:{credentials.credentials}"
        if self.cache.exists(cache_key):
            print("Cache hit")
            return credentials

        # Validate with the service if not in cache
        if not self.service.validate_api_key(credentials.credentials, user, api_key_name, organization):
            raise HTTPException(status_code=403, detail="Invalid or expired API key.")

        # Store in cache
        self.cache.set(cache_key, "valid", ex=3600)  # Cache for 1 hour

        return 
    
    async def authenticate_websocket(self, websocket: WebSocket) -> str:
        token = websocket.query_params.get("token")
        if not token:
            raise WebSocketException(code=403, detail="Missing authorization token")

        # Extract organization, user, and api_key_name from the token or other means
        # For simplicity, assume they are passed as query parameters
        organization = websocket.query_params.get("organization")
        user = websocket.query_params.get("user")
        api_key_name = websocket.query_params.get("api_key_name")

        if not organization or not user or not api_key_name:
            raise WebSocketException(code=400, reason="Missing organization, user, or api_key_name")

        cache_key = f"{organization}:{user}:{api_key_name}:{token}"
        if self.cache.exists(cache_key):
            print("Cache hit")
            return token

        if not self.service.validate_api_key(token, user, api_key_name, organization):
            raise WebSocketException(code=403, reason="Invalid or expired API key")

        self.cache.set(cache_key, "valid", ex=3600)  # Cache for 1 hour
        return token