from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel
from .agente import ejecutar_consulta
import random
import uuid

router = APIRouter()

# Modelo para validar la entrada
class PreguntaRequest(BaseModel):
    pregunta: str
    perfil: str = None
    uuid: str = None 

# Endpoint para procesar consultas
@router.post("/", response_description="Consulta del usuario", status_code=status.HTTP_202_ACCEPTED)
async def ejecutar(request: Request, pregunta_request: PreguntaRequest):
    try:
        # Comprobar si se recibió un uuid desde el frontend
        if pregunta_request.uuid:
            current_uuid = pregunta_request.uuid 
        else:
            # Generar un nuevo UUID si no se recibió
            if not hasattr(request.state, 'uuid'):
                random_digits = ''.join(random.choices('0123456789', k=8))
                request.state.uuid = f"EscuelasViewnextIA-DemoAsesorIA-{random_digits}"

            current_uuid = request.state.uuid

        # Combinar la pregunta con el perfil si está disponible
        prompt_completo = pregunta_request.pregunta
        if pregunta_request.perfil:
            prompt_completo = f"{pregunta_request.perfil}\n\n{pregunta_request.pregunta}"

        respuesta_completa = ejecutar_consulta(prompt_completo, current_uuid)

        return {"respuesta": respuesta_completa, "uuid": current_uuid}

    except Exception as e:
        # Manejo de errores al procesar la consulta
        error_str = str(e)
        if "Final Answer:" in error_str:
            try:
                respuesta = ejecutar_consulta(error_str.split("Final Answer:")[1].strip())
                return {"respuesta": respuesta}
            except Exception as inner_e:
                print(f"Error al procesar el mensaje de error: {inner_e}")

        print(f"Error en la consulta: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lo siento, ocurrió un error al procesar tu consulta.",
        )
