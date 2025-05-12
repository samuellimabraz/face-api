from fastapi import Request, HTTPException, WebSocket, WebSocketException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import json
import os
from src.services.face_recognition_service import FaceRecognitionService
import redis


class APIKeyAuth(HTTPBearer):
    """
    API Key authentication middleware for FastAPI.
    
    This class extends FastAPI's HTTPBearer to implement custom API key authentication
    with Redis caching for performance. It validates API keys against the face recognition
    service and caches valid keys to reduce database lookups.
    
    The middleware supports both HTTP REST endpoints and WebSocket connections.
    """
    def __init__(
        self,
        service: FaceRecognitionService,
        cache_host: str = os.getenv("REDIS_HOST", "localhost"),
        cache_port: int = os.getenv("REDIS_PORT", 6379),
        cache_password: str = os.getenv("REDIS_PASSWORD", ""),
    ):
        """
        Initialize the API Key authentication middleware.
        
        Args:
            service (FaceRecognitionService): Service instance for API key validation
            cache_host (str, optional): Redis host address. Defaults to environment variable or "localhost".
            cache_port (int, optional): Redis port. Defaults to environment variable or 6379.
            cache_password (str, optional): Redis password. Defaults to environment variable or empty string.
        """
        super(APIKeyAuth, self).__init__(auto_error=True)
        self.service = service
        self.cache = redis.Redis(
            host=cache_host,
            port=cache_port,
            password=cache_password,
            decode_responses=True,
        )

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        """
        FastAPI dependency injection entry point.
        
        This method is called automatically by FastAPI when the middleware is used
        as a dependency in a route.
        
        Args:
            request (Request): The incoming HTTP request
            
        Returns:
            HTTPAuthorizationCredentials: The validated credentials
            
        Raises:
            HTTPException: If authentication fails
        """
        return await self.authenticate_request(request)

    async def authenticate_request(
        self, request: Request
    ) -> HTTPAuthorizationCredentials:
        """
        Authenticate an HTTP request using the Bearer token.
        
        The method extracts the API key from the Authorization header, looks up organization,
        user, and API key name from the request, and validates the key. It uses Redis
        to cache valid keys for better performance.
        
        Args:
            request (Request): The incoming HTTP request
            
        Returns:
            HTTPAuthorizationCredentials: The validated credentials
            
        Raises:
            HTTPException: If authentication fails, with appropriate status codes:
                - 403: For invalid/missing credentials or invalid API key
                - 400: For missing organization, request body, user, or API key name
        """
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)

        if not credentials or not credentials.scheme == "Bearer":
            raise HTTPException(
                status_code=403, detail="Invalid or missing authorization credentials."
            )

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
            raise HTTPException(
                status_code=400, detail="User or API key name not specified."
            )

        cache_key = f"{organization}:{user}:{api_key_name}:{credentials.credentials}"
        if self.cache.exists(cache_key):
            print("Cache hit")
            return credentials

        # Validate with the service if not in cache
        if not self.service.validate_api_key(
            credentials.credentials, user, api_key_name, organization
        ):
            raise HTTPException(status_code=403, detail="Invalid or expired API key.")

        # Store in cache
        self.cache.set(cache_key, "valid", ex=3600)  # Cache for 1 hour

        return credentials

    async def authenticate_websocket(self, websocket: WebSocket) -> str:
        """
        Authenticate a WebSocket connection using query parameters.
        
        This method extracts the API key (token) and required parameters from
        WebSocket query parameters and validates the key. It uses Redis to
        cache valid keys for better performance.
        
        Args:
            websocket (WebSocket): The incoming WebSocket connection
            
        Returns:
            str: The validated API key token
            
        Raises:
            WebSocketException: If authentication fails, with appropriate status codes:
                - 403: For missing token or invalid API key
                - 400: For missing organization, user, or API key name
        """
        token = websocket.query_params.get("token")
        if not token:
            raise WebSocketException(code=403, detail="Missing authorization token")

        # Extract organization, user, and api_key_name from the token or other means
        # For simplicity, assume they are passed as query parameters
        organization = websocket.query_params.get("organization")
        user = websocket.query_params.get("user")
        api_key_name = websocket.query_params.get("api_key_name")

        if not organization or not user or not api_key_name:
            raise WebSocketException(
                code=400, reason="Missing organization, user, or api_key_name"
            )

        cache_key = f"{organization}:{user}:{api_key_name}:{token}"
        if self.cache.exists(cache_key):
            print("Cache hit")
            return token

        if not self.service.validate_api_key(token, user, api_key_name, organization):
            raise WebSocketException(code=403, reason="Invalid or expired API key")

        self.cache.set(cache_key, "valid", ex=3600)  # Cache for 1 hour
        return token
