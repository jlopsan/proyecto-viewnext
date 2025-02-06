from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel
from .agente import ejecutar_consulta
import random
import uuid

router = APIRouter()

# Modelo para validar la entrada
class PreguntaRequest(BaseModel):
    pregunta: str
    perfil: str = None  # La descripción del perfil también es opcional
    uuid: str = None  # UUID es opcional en la solicitud

# Endpoint para procesar consultas
@router.post("/", response_description="Consulta del usuario", status_code=status.HTTP_202_ACCEPTED)
async def ejecutar(request: Request, pregunta_request: PreguntaRequest):
    try:
        # Comprobar si se recibió un uuid desde el frontend
        if pregunta_request.uuid:
            current_uuid = pregunta_request.uuid  # Si se recibe, lo usamos
        else:
            # Si no existe, generar uno nuevo
            if not hasattr(request.state, 'uuid'):
                random_digits = ''.join(random.choices('0123456789', k=8))
                request.state.uuid = f"EscuelasViewnextIA-AsesorIA-{random_digits}"

            # Obtener el UUID actual
            current_uuid = request.state.uuid

        # Combinar la pregunta con la descripción del perfil si está disponible
        prompt_completo = pregunta_request.pregunta
        if pregunta_request.perfil:
            prompt_completo = f"{pregunta_request.perfil}\n\n{pregunta_request.pregunta}"

        # Console log para debug
        print(f"Prompt combinado: {prompt_completo}")

        # Ejecutar la consulta con el prompt combinado y pasar el UUID
        respuesta_completa = ejecutar_consulta(prompt_completo, current_uuid)

        return {"respuesta": respuesta_completa, "uuid": current_uuid}

    except Exception as e:
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
