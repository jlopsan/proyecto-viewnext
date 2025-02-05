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

    extracted_results = []  # Lista para almacenar los extractos encontrados

    print("\n Resultados de la búsqueda:")
    for hit in results["hits"]["hits"]:
        print(f"Documento: {hit['_source']['filename']} (Score: {hit['_score']:.4f})")
        filename = hit['_source']['filename']
        content = hit['_source']['content']
        
        start_idx = content.lower().find(query.lower())  # Encuentra la posición de la consulta en el contenido
        if start_idx != -1:
            # Define el contexto de la coincidencia (por ejemplo, 100 caracteres antes y después)
            context_start = max(0, start_idx - 100)
            context_end = min(len(content), start_idx + len(query) + 100)
            extract = content[context_start:context_end]

            # Almacena el extracto en la lista
            extracted_results.append({
                "filename": filename,
                "extract": extract,
                "score": hit['_score']
            })
        else:
            print("No se encontró el texto en el contenido.\n")

    return extracted_results  # Devuelve los resultados como una lista

if __name__ == "__main__":
    query = "becas universitarias"
    search(query)
