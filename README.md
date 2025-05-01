# Facial Recognition API

A scalable and distributed facial recognition system built with **FastAPI**, **MongoDB Atlas Vector Search**, **Redis**, **DeepFace**, and **Docker**.

## Table of Contents

- [Overview](#overview)  
- [System Architecture](#system-architecture)  
- [Technologies Used](#technologies-used)  
- [Features](#features)  
- [API Routes](#api-routes)  
- [Installation](#installation)  
    - [Docker Compose](#docker-compose)  
    - [Manual Python](#manual-installation)
- [Distributed Systems Aspects](#distributed-systems-aspects)  
- [Performance Considerations](#performance-considerations)  
- [Security](#security)  

## Overview  

This facial recognition API was designed for distributed systems, offering high scalability and efficient vector similarity searches. The system supports a multi-tenant architecture with organization-based isolation, API key management, and real-time facial recognition using advanced deep learning models.    

## System Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Client Apps   │────▶│  FastAPI Server │────▶│  Redis Cache    │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                               │
                        ┌──────▼───────┐
                        │  DeepFace    │
                        │  Processing  │
                        └──────┬───────┘
                               │
                        ┌──────▼───────┐
                        │MongoDB Atlas │
                        │Vector Search │
                        └──────────────┘
```

## Technologies Used  

### Main Components  

- **FastAPI**: High-performance asynchronous web framework  
  - Selected for its asynchronous capabilities and excellent performance  
  - Built-in WebSocket support for real-time processing  
  - Automatic API documentation  

- **MongoDB Atlas**:  
  - Vector search capability using the HNSW algorithm  
  - Distributed database for scalability  
  - Multi-tenant support with separate databases  
  - Efficient similarity search using ANN (Approximate Nearest Neighbor)  

- **Redis**:  
  - Fast cache for API keys  
  - Reduces database load  

- **DeepFace**:  
  - State-of-the-art facial detection  
  - Support for multiple models for facial embedding generation  
  - High precision in facial detection and recognition tasks

### Key Features in Distributed Context

- Horizontal scalability via containerization  
- Asynchronous processing  
- WebSocket support for real-time operations  
- Multi-tenant isolation  
- Distributed cache  
- Vector similarity search  

## Features  

1. **Organization Management**  
   - Creation of isolated environments for different clients  
   - Separate vector search indexes by organization  
   - Data isolation and security  

2. **API Key Management**  
   - API key generation and revocation  
   - Organization-based authentication  
   - Key validation with Redis cache  

3. **Facial Registration**  
   - Support for multiple image formats (URL, path, base64)  
   - Automatic facial detection and embedding generation  
   - Vector storage in MongoDB Atlas  

4. **Facial Recognition**  
   - Real-time facial detection  
   - Vector similarity search using ANN  
   - Configurable similarity threshold  
   - WebSocket support for continuous recognition  

## API Routes  

### **Organization Management**
```http
POST /orgs
{
    "organization": "org_name"
}
```

### **API Key Management** 
```http
POST /orgs/{organization}/api-key
{
    "user": "username",
    "api_key_name": "key_name"
}

DELETE /orgs/{organization}/api-key
{
    "api_auth": {
        "user": "username",
        "api_key_name": "key_name"
    }
}
```

### **Facial Registration** 
```http
POST /register/{organization}
{
    "images": ["path/to/image", "http://url/to/image", "base64_string"],
    "name": "person_name",
    "api_auth": {
        "user": "username",
        "api_key_name": "key_name"
    }
}
```

### **Facial Recognition**
```http
POST /recognize/{organization}
{
    "image": "path/to/image",
    "threshold": 0.5,
    "api_auth": {
        "user": "username",
        "api_key_name": "key_name"
    }
}

WebSocket: ws://host/ws/recognize?token={api_key}&organization={org}&user={user}&api_key_name={api_key_name}
{
    "image": "path/to/image",
    "threshold": 0.5,
    "organization": "org_name"
}
```

## Installation 

First, clone the repository:  
```bash
git clone https://github.com/samuellimabraz/face-api.git
```  

### Docker Compose  

1. Create a `.env` file with the necessary configurations:  
```env
MONGODB_URI=<your_mongodb_atlas_uri>
REDIS_HOST=localhost
DEEPFACE_DETECTOR_BACKEND=yolov8
DEEPFACE_EMBEDDER_MODEL=Facenet512
```  

2. Run the system with Docker Compose:  
```bash
docker-compose up --build
```  

- [Dockerfile](./Dockerfile)
- [docker-compose.yml](./docker-compose.yml)

Currently, the image is configured to run in a CPU-only environment. GPU support will be added in the future.

### Manual Installation  

1. Install Python dependencies:  
```bash
pip install -r requirements.txt
```  

2. Configure environment variables  
3. Run the application:  
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```  

## Distributed Systems Aspects  

### Scalability  
- Horizontal scalability via containerization  
- Stateless API design  
- Distributed database with MongoDB Atlas  
- Redis cache layer  

### Performance  
- Vector search based on ANN for fast similarity matching  
- Asynchronous API design  
- Efficient caching strategy  
- WebSocket support for real-time processing  

### Security  
- Multi-tenant isolation  
- API key authentication  
- Organization-based data separation  
- Key validation with Redis cache  

## Performance Considerations  

### Vector Search Optimization  
- Uses MongoDB Atlas Vector Search with HNSW algorithm  
- Approximate Nearest Neighbor (ANN) for efficient similarity search  
- Configurable similarity thresholds  
- Optimized index creation by organization  

### Caching Strategy  
- API key caching in Redis  
- Reduction of database load  
- Faster authentication validation  
- Configurable cache expiration  

### Real-time Processing  
- WebSocket support for continuous recognition  
- Asynchronous request processing  
- Efficient Deep Learning models  
- Scalable architecture  

---

### User Interface (UI) Demo  

A demonstration interface was developed using **Vite**, **React**, and **TypeScript**, with the goal of exploring all the functionality of the created API. The UI provides real-time visualizations of the facial detection and recognition process, integrating the **Webcam** to capture and display results in real time.  

#### Main UI Features  

- **Real-time Facial Detection**: Use your webcam to capture images and visualize the facial detection process.  
- **Facial Recognition**: Explore similarity search and recognition of registered faces.  
- **Intuitive Interface**: Simple and interactive demonstration of the API's capabilities.  

#### How to Run the UI  

1. Navigate to the UI directory:  
   ```bash
   cd ui/
   ```  

2. Install dependencies:  
   ```bash
   npm install
   ```  

3. Start the development server:  
   ```bash
   npm run dev -- --port 2000
   ```  

4. Access the interface in your browser:  
   - Go to **http://localhost:2000** to view and interact with the demo.  

This interface is a useful tool for validating the API's integration with real applications, highlighting its potential for use in distributed facial recognition systems.