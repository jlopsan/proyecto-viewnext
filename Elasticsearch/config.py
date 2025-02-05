from elasticsearch import Elasticsearch

# Conexión a Elasticsearch
ES_HOST = "http://localhost:9200"
es = Elasticsearch(ES_HOST)

# URL de la API que genera embeddings
EMBEDDING_API_URL = "https://api-nextai-challenge.codingbuddy-4282826dce7d155229a320302e775459-0000.eu-de.containers.appdomain.cloud/aigen/vector/research"

# Encabezados para la API
headers = {
        "user": "juanloperasanchez@escuelaviewnext.com",
        "origin": "EscuelasViewnextIA",
        "X-API-Key": "jls-dev-Rjy9c1aPacqHLMrzOz607NEB5ifLB14f"
    }

