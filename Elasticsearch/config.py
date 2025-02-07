from elasticsearch import Elasticsearch
import os

# Conexión a Elasticsearch
ES_HOST = "http://localhost:9200"
es = Elasticsearch(ES_HOST)

# URL de la API que genera embeddings
EMBEDDING_API_URL = "https://api-nextai-challenge.codingbuddy-4282826dce7d155229a320302e775459-0000.eu-de.containers.appdomain.cloud/aigen/vector/research"

# Encabezados para la API
headers = {
        "user": os.getenv('USER_EMAIL'),
        "origin": "EscuelasViewnextIA",
        "X-API-Key": os.getenv('API_KEY'),
    }

