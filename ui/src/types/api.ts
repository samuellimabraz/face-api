export interface APIKeyRequest {
  user: string;
  api_key_name: string;
}

export interface APIKeyResponse {
  key: string;
  user: string;
  api_key_name: string;
  organization: string;
}

export interface OrganizationRequest {
  organization: string;
}

export interface RegisterRequest {
  images: string[];
  name: string;
  api_auth: APIKeyRequest;
}

export interface RecognizeRequest {
  image: string;
  threshold: number;
  api_auth: APIKeyRequest;
}

export interface BoundingBox {
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface DetectionResult {
  bounding_box: BoundingBox;
  confidence: number;
  face_image: number[];
}

export interface DetectionResults {
  result: DetectionResult[];
  inference_time: number;
}

export interface VectorSearchResult {
  name: string;
  distance?: number;
}

export interface RecognitionResult {
  detections: DetectionResults;
  searchs: VectorSearchResult[];
}