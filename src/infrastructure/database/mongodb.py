from datetime import datetime
from typing import Optional

import numpy as np
import time
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.operations import SearchIndexModel
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError
import bcrypt
import secrets

from src.domain.interfaces import FaceDatabase
from src.domain.models import VectorSearchResult, APIKey
from src.utils.logging import logger

class MongoDBFaceDatabase(FaceDatabase):
    vector_search_index_definition = {
        "fields":[
            {
                "type": "vector",
                "path": "embedding",
                "similarity": "cosine",
                "numDimensions": 512,
            },
        ]
    }
    
    def __init__(self, connection_string: str):
        self.client = MongoClient(connection_string, server_api=ServerApi('1'))
        self._verify_connection()

    def _verify_connection(self) -> None:
        try:
            self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise
    
    def _get_organization_db(self, organization: str) -> Database:
        return self.client[organization]
    
    def database_exists(self, database_name: str) -> bool:
        return database_name in self.client.list_database_names()
    
    def vector_index_exists(self, organization: str, index_name: str) -> bool:
        """Verifica se o índice vetorial existe para a coleção."""
        try:
            indexes = self.client[organization].get_collection("embeddings").list_search_indexes()
            return any(index["name"] == index_name for index in indexes)
        except Exception as e:
            raise RuntimeError(f"Failed to verify vector index: {str(e)}")
    
    def create_organization(self, organization: str) -> bool:
        if self.database_exists(organization):
            print(f"Organization '{organization}' already exists.")
            return True
        
        db = self._get_organization_db(organization)

        # Cria coleção `api_keys` com índices
        if "api_keys" not in db.list_collection_names():
            db.create_collection("api_keys")
            db["api_keys"].create_index(
                [("user", 1), ("api_key_name", 1), ("organization", 1)],
                unique=True
            )

        # Cria coleção `embeddings`
        if "embeddings" not in db.list_collection_names():
            db.create_collection("embeddings")
            if not self.vector_index_exists(organization, f"face_embbedings"):
                print(f"Creating vector index for '{organization}'")
                db["embeddings"].create_search_index(
                    SearchIndexModel(
                        definition=self.vector_search_index_definition,
                        name="face_embbedings",
                        type="vectorSearch",
                    )
                )
                time.sleep(2)  # Aguardar a criação do índice
                
        return True

    def generate_api_key(self, user: str, api_key_name: str, organization: str) -> APIKey:
        api_key = secrets.token_urlsafe(32)
        hashed_key = bcrypt.hashpw(api_key.encode(), bcrypt.gensalt())

        if not self.database_exists(organization):
            raise ValueError(f"Database '{organization}' does not exist. Create it first.")
            
        db = self._get_organization_db(organization)
        api_keys_collection = db["api_keys"]

        # Verificação manual para evitar duplicados
        existing_key = api_keys_collection.find_one({
            "user": user,
            "api_key_name": api_key_name,
            "organization": organization
        })

        if existing_key:
            raise ValueError(f"API key for '{user}' with name '{api_key_name}' already exists in '{organization}'.")

        api_key_doc = {
            "user": user,
            "api_key_name": api_key_name,
            "organization": organization,
            "created_at": datetime.now(),
            "last_used": None,
            "is_active": True,
        }
        try:
            api_keys_collection.insert_one({**api_key_doc, 'key': str(hashed_key.decode())})
            print(f"API key generated for '{user}' in organization '{organization}'")
        except Exception as e:
            raise RuntimeError(f"Failed to create API key: {str(e)}")

        return APIKey(**api_key_doc, key=api_key)

    def validate_api_key(self, api_key: str, user: str, api_key_name: str, organization: str) -> bool:
        if not self.database_exists(organization):
            raise ValueError(f"Database '{organization}' does not exist.")
        
        db = self._get_organization_db(organization)
        
        key_doc = db['api_keys'].find_one({
            'user': user,
            'api_key_name': api_key_name,
            'is_active': True
        })
        
        logger.info(f"Validating {api_key} API key for '{user}' in organization '{organization}'")
        print(f"Validating {api_key} API key for '{user}' in organization '{organization}'")
        
        if not key_doc:
            print(f"No {api_key} API key found for user '{user}' in organization '{organization}'")
            return False
        
        is_valid = bcrypt.checkpw(api_key.encode("utf-8"), key_doc['key'].encode("utf-8"))
        if is_valid:
            db['api_keys'].update_one(
                {'_id': key_doc['_id']},
                {'$set': {'last_used': datetime.now()}}
            )
        else:
            print(f"Hash mismatch for API key: {api_key}")
        
        print(f"API key validated for {user} in org:'{organization}'")
            
        return is_valid

    def revoke_api_key(self, api_key: str, user: str, api_key_name: str, organization: str) -> bool:
        if not self.validate_api_key(api_key, user, api_key_name, organization):
            return False
        
        logger.info(f"Revoking API key for {user} in organization '{organization}'")
        print(f"Revoking API key for {user} in organization '{organization}'")
        
        db = self._get_organization_db(organization)   
        db['api_keys'].delete_one({
            'user': user,
            'api_key_name': api_key_name
        })
        
        return True

    def save_embedding(self, name: str, organization: str, embedding: np.ndarray) -> None:
        try:
            # Verificar se a coleção existe
            if not self.database_exists(organization):
                raise ValueError(f"Database '{organization}' does not exist. Create it first.")

            document = {
                "name": name,
                "embedding": embedding.tolist(),
                "created_at": datetime.now()
            }
            
            db = self._get_organization_db(organization)
            db["embeddings"].insert_one(document)
        except Exception as e:
            raise RuntimeError(f"Failed to save embedding: {str(e)}")
    
    def vector_search(self, embedding: np.ndarray,  threshold: float, organization: str) -> VectorSearchResult:
        try:
            # Verificar se a coleção existe
            if not self.database_exists(organization):
                raise ValueError(f"Database '{organization}' does not exist. Create it first.")

            # Verificar se o índice existe
            index_name = f"face_embbedings"
            if not self.vector_index_exists(organization, index_name):
                raise ValueError(f"Vector index '{index_name}' does not exist for '{organization}'. Create it first.")

            pipeline = [
                {
                '$vectorSearch': {
                    'index': f"face_embbedings" ,
                    'exact': False,
                    'numCandidates': 20,
                    'path': 'embedding',
                    'queryVector': embedding.tolist(),
                    'limit': 1
                }
                },
                {
                '$project': {
                    '_id': 0,
                    'name': 1,
                    'score': { '$meta': 'vectorSearchScore' }
                    }
                }
            ]
            
            results = list(self._get_organization_db(organization)["embeddings"].aggregate(pipeline))
            
            if not results:  # Verificar se não há resultados
                return VectorSearchResult(name='unknown', distance=None)
            
            best_match = results[0]  # Pegar o primeiro (e único) resultado
            if best_match['score'] < threshold:
                return VectorSearchResult(name='unknown', distance=best_match['score'])

            return VectorSearchResult(name=best_match['name'], distance=best_match['score'])
        
        except Exception as e:
            raise RuntimeError(f"Failed to search similar embeddings: {str(e)}")