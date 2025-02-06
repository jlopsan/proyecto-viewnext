from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from .agente import ejecutar_consulta

router = APIRouter()

# Modelo para validar la entrada
class PreguntaRequest(BaseModel):
    pregunta: str

# Endpoint para procesar consultas
@router.post("/", response_description="Consulta del usuario", status_code=status.HTTP_202_ACCEPTED)
def ejecutar(request: PreguntaRequest):
    try:
        # Ejecutar la consulta con la pregunta proporcionada
        respuesta_completa = ejecutar_consulta(request.pregunta)
        return {"respuesta": respuesta_completa}
    except Exception as e:
        # Manejo del error con detección de "Final Answer:"
        error_str = str(e)
        if "Final Answer:" in error_str:
            try:
                respuesta = ejecutar_consulta(error_str.split("Final Answer:")[1].strip())
                return {"respuesta": respuesta}
            except Exception as inner_e:
                print(f"Error al procesar el mensaje de error: {inner_e}")
        
        # Respuesta genérica para errores no manejados
        print(f"Error en la consulta: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lo siento, ocurrió un error al procesar tu consulta.",
        )


