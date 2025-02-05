import os
import re
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
from correo import enviar_correo

# Cargar variables de entorno
load_dotenv()

# Clase personalizada para tu endpoint de IA
class CustomLLM(LLM):
    def _call(self, prompt, stop=None):
        # Datos para la solicitud
        data = {
            "model": "meta-llama/llama-3-1-70b-instruct",
            "uuid": "EscuelasViewnextIA-test-12343299",
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
    
def tool_enviar_correo(query):
    """Herramienta que envía la respuesta por correo."""
    try:
        # Extraer el correo electrónico de la consulta
        correo_extraido = extraer_correo(query)
        
        if not correo_extraido:
            return "No se detectó un correo. ¿Podrías proporcionarlo?"

        # Limpiar la consulta para que no incluya la parte del correo
        consulta_limpia = re.sub(r"(envíamelo|mándalo|envía la respuesta) (a \S+@\S+\.\S+|por correo|a mi correo|a mi email)", "", query, flags=re.IGNORECASE).strip()

        # Ejecutar la consulta sin la parte del correo
        respuesta = ejecutar_consulta(consulta_limpia)

        # Enviar el correo con la respuesta
        resultado_envio = enviar_correo(correo_extraido, consulta_limpia, respuesta)
        return f"Respuesta enviada a {correo_extraido}. {resultado_envio}"
    except Exception as e:
        return f"Error al procesar la solicitud de correo: {e}"

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

# Definir la herramienta de enviar correo
enviar_correo_tool = Tool(
    name="Enviar Correo",
    func=tool_enviar_correo,
    description="Usa esta herramienta cuando el usuario pida que le envíes un correo con la consulta. Si no se detecta ningún correo, se proporcionará un mensaje de aviso.Esta es la acción final y no se deben realizar más acciones después de enviar el correo."
)

# Crear una instancia de tu LLM personalizado
custom_llm = CustomLLM()

# Inicializar el agente con las herramientas y el LLM
agent = initialize_agent(
    tools=[tavily_tool, elasticsearch_tool,enviar_correo_tool],
    llm=custom_llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)

def extraer_respuesta_final(texto):
    """Extrae la respuesta final del texto completo"""
    if "Final Answer:" in texto:
        partes = texto.split("Final Answer:")
        return partes[-1].strip()
    return texto.strip()

import re

def extraer_correo(query):
    """Extrae una dirección de correo electrónico de la consulta."""
    # Expresión regular mejorada para detectar correos electrónicos
    patron_correo = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    coincidencias = re.findall(patron_correo, query)
    return coincidencias[0] if coincidencias else None

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
    pregunta = "que requisitos hacen falta para obtener una beca en estudios de FP? Mándame la respuesta por correo a raulcasta23@gmail.com."
    print("\nConsultando información...")
    respuesta = ejecutar_consulta(pregunta)
    print("\nRespuesta:", respuesta)
