from elasticsearch import Elasticsearch

# Conexión a Elasticsearch
ES_HOST = "http://localhost:9200"
es = Elasticsearch(ES_HOST)

# URL de la API que genera embeddings
EMBEDDING_API_URL = "x"

# Encabezados para la API
headers = {
        "user": "x",
        "origin": "EscuelasViewnextIA",
        "X-API-Key": "x"
    }

