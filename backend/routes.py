from fastapi import APIRouter, Body, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List
from .agente import ejecutar_consulta

router = APIRouter()

@router.post("/", response_description="Consulta del usuario", status_code=status.HTTP_202_ACCEPTED)
def ejecutar(pregunta:str = Body(...)):
    try:
        respuesta_completa = ejecutar_consulta(pregunta)
        return respuesta_completa
    except Exception as e:
        # Si hay un error de parsing, intentar extraer la respuesta útil del mensaje de error
        error_str = str(e)
        if "Final Answer:" in error_str:
            return ejecutar_consulta(error_str)
        print(f"Error en la consulta: {e}")
        return "Lo siento, ocurrió un error al procesar tu consulta."

