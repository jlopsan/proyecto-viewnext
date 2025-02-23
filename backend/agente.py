import os
import re
import requests
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.agents import Tool, initialize_agent
from langchain.agents.agent_types import AgentType
from .correo import enviar_correo
from Elasticsearch.Consulta_RAG import search 

# Cargar variables de entorno
load_dotenv()

# Para utilizar el endpoint de ViewNext
class CustomLLM(LLM):
    def _call(self, prompt, uuid):
        data = {
            "model": "meta-llama/llama-3-1-70b-instruct",
            "uuid": uuid, 
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
            return self.extract_final_answer(result['content'])
        except requests.exceptions.RequestException as e:
            print("Error al realizar la solicitud:", e)
            return "Lo siento, ocurrió un error al procesar tu solicitud."
        
    # Extrae la respuesta final del texto devuelto por el modelo.
    def extract_final_answer(self, text):
        
        if "Final Answer:" in text:
            final_answer = text.split("Final Answer:")[-1].strip()
            # Limpia marcadores adicionales en la respuesta
            final_answer = re.sub(r'Thought:|Action:|Action Input:|Observation:', '', final_answer)
            return final_answer.strip()
        return text.strip()

    @property
    def _identifying_params(self):
        return {"name_of_model": "CustomLLM"}

    @property
    def _llm_type(self):
        return "custom"

# Realiza una búsqueda en la API de Tavily.
def tavily_search(query):
    api_key = os.getenv("TAVILY_API_KEY")
    client = TavilyClient(api_key)
    response = client.search(query)
    return response['answer']

# Realiza una búsqueda utilizando Elasticsearch.
def elasticsearch_search(query):
    try:
        search(query)
        return "Consulta completada."
    except Exception as e:
        print(f"Error al realizar la búsqueda en Elasticsearch: {e}")
        return "Lo siento, ocurrió un error al realizar la búsqueda."
    
# Procesa el envío de correos basado en la consulta del usuario.
def tool_enviar_correo(query):
    try:
        correo_extraido = extraer_correo(query)
        if not correo_extraido:
            return "No se detectó un correo. ¿Podrías proporcionarlo?"

        consulta_limpia = re.sub(r"(envíamelo|mándalo|envía la respuesta) (a \S+@\S+\.\S+|por correo|a mi correo|a mi email)", "", query, flags=re.IGNORECASE).strip()
        respuesta = ejecutar_consulta(consulta_limpia)

        if not respuesta.strip():
            respuesta = "Lo siento, no pude encontrar una respuesta a tu consulta."

        enviar_correo(correo_extraido, consulta_limpia, respuesta)
        return respuesta
    except Exception as e:
        return f"Error al procesar la solicitud: {e}"

tavily_tool = Tool(
    name="Tavily Search",
    func=tavily_search,
    description="Usa esta herramienta para buscar información en Tavily cuando no encuentres información sobre lo que buscas."
)

elasticsearch_tool = Tool(
    name="Elasticsearch Search",
    func=elasticsearch_search,
    description="Usa esta herramienta para buscar información en Elasticsearch usando búsqueda semántica. Úsalo como primera opción siempre."
)

enviar_correo_tool = Tool(
    name="Enviar Correo",
    func=tool_enviar_correo,
    description="Usa esta herramienta solo cuando el usuario pida que le envíes un correo con la consulta. Busca la respuesta en las otras también."
)

# Extrae la dirección del correo.
def extraer_correo(query):
    patron_correo = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    coincidencias = re.findall(patron_correo, query)
    return coincidencias[0] if coincidencias else None

# Procesa la consulta del usuario
def ejecutar_consulta(pregunta, uuid):
    custom_llm = CustomLLM()
    correo_extraido = extraer_correo(pregunta)

    if correo_extraido:
        pregunta = 'NO menciones nada sobre el correo (Aunque no puedas enviarlo). Eres un asistente virtual especializado en trámites burocráticos en España. ' + pregunta
        pregunta_limpia = re.sub(r"(envíamelo|mándalo|envía la respuesta) (a \S+@\S+\.\S+|por correo|a mi correo|a mi email)", "", pregunta, flags=re.IGNORECASE).strip()
        respuesta = custom_llm._call(pregunta_limpia, uuid)

        try:
            pregunta_limpia = pregunta_limpia.replace('NO menciones nada sobre el correo (Aunque no puedas enviarlo). Eres un asistente virtual especializado en trámites burocráticos en España. ', '')
            enviar_correo(correo_extraido, pregunta_limpia, respuesta)
            return respuesta
        except Exception as e:
            return f"Error al procesar la solicitud: {e}"
    else:
        pregunta = 'Eres un asistente virtual especializado en trámites burocráticos en España. ' + pregunta
        return custom_llm._call(pregunta, uuid)

# Para testeo
if __name__ == "__main__":
    pregunta = "Como se llama la beca de fp? Envia un correo con la información a juanloperasanchez@gmail.com"
    print("\nConsultando información...")
    respuesta = ejecutar_consulta(pregunta, uuid="12345")
    print("\nRespuesta:", respuesta)