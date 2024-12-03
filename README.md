# API de Reconhecimento Facial

Um sistema distribuído e escalável de reconhecimento facial construído com **FastAPI**, **MongoDB Atlas Vector Search**, **Redis** e **DeepFace** e **Docker**.

## Índice

- [Visão Geral](#visão-geral)  
- [Arquitetura do Sistema](#arquitetura-do-sistema)  
- [Tecnologias Utilizadas](#tecnologias-utilizadas)  
- [Funcionalidades](#funcionalidades)  
- [Rotas da API](#rotas-da-api)  
- [Instalação](#instalação)  
    - [Docker Compose](#docker-compose)  
    - [Python Manual](#instalação-manual)
- [Aspectos de Sistemas Distribuídos](#aspectos-de-sistemas-distribuídos)  
- [Considerações de Desempenho](#considerações-de-desempenho)  
- [Segurança](#segurança)  

## Visão Geral  

Esta API de reconhecimento facial foi projetada para sistemas distribuídos, oferecendo alta escalabilidade e buscas eficientes por similaridade de vetores. O sistema suporta uma arquitetura multi-tenant com isolamento por organizações, gerenciamento de chaves de API e reconhecimento facial em tempo real usando modelos avançados de deep learning.    

## Arquitetura do Sistema

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

## Tecnologias Utilizadas  

### Componentes Principais  

- **FastAPI**: Framework web assíncrono de alta performance  
  - Selecionado por suas capacidades assíncronas e excelente desempenho  
  - Suporte integrado a WebSocket para processamento em tempo real  
  - Documentação automática da API  

- **MongoDB Atlas**:  
  - Capacidade de busca vetorial usando o algoritmo HNSW  
  - Banco de dados distribuído para escalabilidade  
  - Suporte a multi-tenant com bancos de dados separados  
  - Busca eficiente por similaridade usando ANN (Approximate Nearest Neighbor)  

- **Redis**:  
  - Cache rápido para chaves de API  
  - Reduz a carga no banco de dados  

- **DeepFace**:  
  - Detecção facial de última geração  
  - Suporte a múltiplos modelos para geração de embeddings faciais  
  - Alta precisão em tarefas de detecção e reconhecimento facial

### Principais Funcionalidades no Contexto Distribuído

- Escalabilidade horizontal via containerização  
- Processamento assíncrono  
- Suporte a WebSocket para operações em tempo real  
- Isolamento multi-tenant  
- Cache distribuído  
- Busca por similaridade vetorial  

## Funcionalidades  

1. **Gerenciamento de Organizações**  
   - Criação de ambientes isolados para diferentes clientes  
   - Índices de busca vetorial separados por organização  
   - Isolamento e segurança dos dados  

2. **Gerenciamento de Chaves de API**  
   - Geração e revogação de chaves de API  
   - Autenticação por organização  
   - Validação de chaves com cache em Redis  

3. **Registro Facial**  
   - Suporte a múltiplos formatos de imagem (URL, caminho, base64)  
   - Detecção facial automática e geração de embeddings  
   - Armazenamento de vetores no MongoDB Atlas  

4. **Reconhecimento Facial**  
   - Detecção facial em tempo real  
   - Busca por similaridade vetorial usando ANN  
   - Configuração de limite de similaridade  
   - Suporte a WebSocket para reconhecimento contínuo  

## Rotas da API  

### **Gerenciamento de Organizações**
```http
POST /orgs
{
    "organization": "org_name"
}
```

### **Gerenciamento de Chaves de API** 
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

### **Registro Facial** 
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

### **Reconhecimento Facial**
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

## Instalação 

Primeiramente clone o repositório  
```bash
git clone https://github.com/samuellimabraz/face-api.git
```  

### Docker Compose  

1. Crie um arquivo `.env` com as configurações necessárias:  
```env
MONGODB_URI=<seu_uri_mongodb_atlas>
REDIS_HOST=localhost
DEEPFACE_DETECTOR_BACKEND=yolov8
DEEPFACE_EMBEDDER_MODEL=Facenet512
```  

2. Execute o sistema com Docker Compose:  
```bash
docker-compose up --build
```  

- [Dockerfile](./Dockerfile)
- [docker-compose.yml](./docker-compose.yml)

Atualmente a imagem está configura para rodar em ambiente com CPU somente. Futuramente será adicionado suporte para GPU.

### Instalação Manual  

1. Instale as dependências do Python:  
```bash
pip install -r requirements.txt
```  

2. Configure as variáveis de ambiente  
3. Execute a aplicação:  
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```  

## Aspectos de Sistemas Distribuídos  

### Escalabilidade  
- Escalabilidade horizontal via containerização  
- Design de API sem estado  
- Banco de dados distribuído com MongoDB Atlas  
- Camada de cache com Redis  

### Desempenho  
- Busca vetorial com base em ANN para rápida correspondência de similaridade  
- Design de API assíncrona  
- Estratégia de cache eficiente  
- Suporte a WebSocket para processamento em tempo real  

### Segurança  
- Isolamento multi-tenant  
- Autenticação via chave de API  
- Separação de dados por organização  
- Validação de chaves com cache em Redis  

## Considerações de Desempenho  

### Otimização de Busca Vetorial  
- Utiliza MongoDB Atlas Vector Search com o algoritmo HNSW  
- Approximate Nearest Neighbor (ANN) para busca eficiente por similaridade  
- Limiares de similaridade configuráveis  
- Criação otimizada de índices por organização  

### Estratégia de Cache  
- Cache de chaves de API no Redis  
- Redução de carga no banco de dados  
- Validação de autenticação mais rápida  
- Expiração configurável do cache  

### Processamento em Tempo Real  
- Suporte a WebSocket para reconhecimento contínuo  
- Processamento assíncrono de requisições  
- Modelos de Deep Learning eficientes  
- Arquitetura escalável  