from fastapi import APIRouter, Body, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List
from .agente import agent, extraer_respuesta_final

router = APIRouter()

@router.post("/", response_description="Consulta del usuario", status_code=status.HTTP_202_ACCEPTED)
def ejecutar_consulta(pregunta:str = Body(...)):
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

