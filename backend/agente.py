import os
import sys
import requests
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.agents import Tool, initialize_agent
from langchain.agents.agent_types import AgentType

sys.path.append(os.path.join(os.path.dirname(__file__), '../elasticsearch'))

from Consulta_RAG import search 

# Cargar variables de entorno
load_dotenv()

# Clase personalizada para tu endpoint de IA
class CustomLLM(LLM):
    def _call(self, prompt, stop=None):
        # Datos para la solicitud
        data = {
            "model": "meta-llama/llama-3-1-70b-instruct",
            "uuid": "EscuelasViewnextIA-test-12343245",
            "message": {
                "role": "user",
                "content": prompt
            },
            "prompt": None,
            "temperature": 0,
            "plugin_id": None,
            "vectorization_model": None,
            "origin": "EscuelasViewnextIA",
            "origin_detail": "web",
            "language": "es",
            "user": os.getenv('USER_EMAIL')
        }

        headers = {
            "Content-Type": "application/json",
            "X-API-KEY": os.getenv('API_KEY')
        }

        try:
            response = requests.post(
                "https://api-nextai-challenge.codingbuddy-4282826dce7d155229a320302e775459-0000.eu-de.containers.appdomain.cloud/aigen/research/wx",
                json=data,
                headers=headers,
                timeout=500
            )
            response.raise_for_status()
            result = response.json()
            return result['content']
        except requests.exceptions.RequestException as e:
            print("Error al realizar la solicitud:", e)
            return "Lo siento, ocurrió un error al procesar tu solicitud."

    @property
    def _identifying_params(self):
        return {"name_of_model": "CustomLLM"}

    @property
    def _llm_type(self):
        return "custom"

# Función para realizar búsquedas en Tavily
def tavily_search(query):
    api_key = os.getenv("TAVILY_API_KEY")
    client = TavilyClient(api_key)
    response = client.search(query)
    return response['answer']

# Función para realizar búsquedas utilizando Elasticsearch (consulta_rag.py)
def elasticsearch_search(query):
    """Función para hacer una búsqueda utilizando el script consulta_rag.py"""
    try:
        # Llamamos a la función de búsqueda de consulta_rag.py
        search(query)  # Esta función imprimirá los resultados directamente
        return "Consulta completada. Verifica los resultados en la consola."
    except Exception as e:
        print(f"Error al realizar la búsqueda en Elasticsearch: {e}")
        return "Lo siento, ocurrió un error al realizar la búsqueda."

# Definir la herramienta de búsqueda en Tavily
tavily_tool = Tool(
    name="Tavily Search",
    func=tavily_search,
    description="Usa esta herramienta para buscar información en Tavily cuando no encuentres información sobre lo que buscas."
)

# Definir la herramienta de búsqueda en Elasticsearch
elasticsearch_tool = Tool(
    name="Elasticsearch Search",
    func=elasticsearch_search,
    description="Usa esta herramienta para buscar información en Elasticsearch usando búsqueda semántica. Úsalo como primera opción siempre"
)

# Crear una instancia de tu LLM personalizado
custom_llm = CustomLLM()

# Inicializar el agente con las herramientas y el LLM
agent = initialize_agent(
    tools=[tavily_tool, elasticsearch_tool],
    llm=custom_llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=False
)

def extraer_respuesta_final(texto):
    """Extrae la respuesta final del texto completo"""
    if "Final Answer:" in texto:
        partes = texto.split("Final Answer:")
        return partes[-1].strip()
    return texto.strip()

def ejecutar_consulta(pregunta):
    try:
        respuesta_completa = agent.run(pregunta)
        # Extraer la respuesta final
        respuesta_limpia = extraer_respuesta_final(respuesta_completa)
        return respuesta_limpia
    except Exception as e:
        # Si hay un error de parsing, intentar extraer la respuesta útil del mensaje de error
        error_str = str(e)
        if "Final Answer:" in error_str:
            return extraer_respuesta_final(error_str)
        print(f"Error en la consulta: {e}")
        return "Lo siento, ocurrió un error al procesar tu consulta."

# Ejecutar el agente con una pregunta de ejemplo
if __name__ == "__main__":
    pregunta = "Si tengo dos pagadores pero mi renta es inferior a 11.000 euros tengo que hacer la declaración de la renta?"
    print("\nConsultando información...")
    respuesta = ejecutar_consulta(pregunta)
    print("\nRespuesta:", respuesta)
