# Face Recognition API

A scalable Face Recognition API built with FastAPI, DeepFace, and MongoDB Atlas Vector Search.

## Features

- Face detection using YOLOv8
- Face embedding generation using FaceNet512
- Vector similarity search using MongoDB Atlas
- Organization-based data isolation
- Real-time face recognition
- Configurable similarity threshold
- Comprehensive logging and timing metrics

## Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and update with your MongoDB credentials
6. Run the application: `uvicorn src.api.main:app --reload`

## API Endpoints

- `POST /organizations/{organization}`: Create a new organization
- `POST /register/{organization}/{name}`: Register a person with face images
- `POST /recognize/{organization}`: Recognize a person from an image

## Project Structure

```
src/
├── api/            # FastAPI application and routes
├── domain/         # Core domain models and interfaces
├── infrastructure/ # Implementation of interfaces
│   ├── database/   # MongoDB implementation
│   └── ml/         # DeepFace implementations
├── services/       # Business logic
└── utils/          # Utility functions
```

## Configuration

The application can be configured using environment variables:
- `MONGODB_URI`: MongoDB Atlas connection string
- `MONGODB_DB_NAME`: Database name for face recognition

## Error Handling

The API includes comprehensive error handling for:
- Database connection issues
- Face detection failures
- Invalid image formats
- Missing organizations
- Failed registrations