import requests
from config import es, EMBEDDING_API_URL, headers

def get_query_embedding(query):
    """Obtiene el embedding del texto utilizando la API de NextAI."""
    body = {
        "texts": [query],
        "model": "LaBSE"
    }
    response = requests.post(EMBEDDING_API_URL, headers=headers, json=body)

    if response.status_code == 200:
        return response.json().get("vectors")[0]
    else:
        print(f"Error al obtener embedding: {response.text}")
        return None

def search(query, index_name="documents", top_k=3):
    """Realiza una búsqueda en Elasticsearch usando búsqueda semántica"""
    query_vector = get_query_embedding(query)
    
    if query_vector is None:
        print("No se pudo obtener embedding de la consulta")
        return

    # Consulta de Elasticsearch con búsqueda de similitud (cosine similarity)
    search_query = {
        "size": top_k,
        "query": {
            "script_score": {
                "query": {"match_all": {}}, 
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'vector') + 1.0",
                    "params": {"query_vector": query_vector}
                }
            }
        }
    }

    results = es.search(index=index_name, body=search_query)

    print("\n Resultados de la búsqueda:")
    for hit in results["hits"]["hits"]:
        print(f"Documento: {hit['_source']['filename']} (Score: {hit['_score']:.4f})")
        print(f"Extracto: {hit['_source']['content'][:300]}...\n")

if __name__ == "__main__":
    query = "becas universitarias"
    search(query)
