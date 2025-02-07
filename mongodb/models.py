import uuid
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

# Clase Consulta para gestionar correctamente las consultas
class Consulta(BaseModel):
    uuid: str
    consulta: str = Field(...)
    respuesta: str = Field(...)
    fecha: datetime = Field(...)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "test": {
                "uuid": "EscuelasViewnextIA-JLS-12345678",
                "consulta": "Consulta becas",
                "respuesta": "Para solicitar una beca...",
                "fecha": datetime(2024, 4, 4)
            }
        }

# Clase ConsultaUpdate para getionar las actualizaciones de las consultas
class ConsultaUpdate(BaseModel):
    consulta: Optional[str]
    respuesta: Optional[str]
    fecha: Optional[datetime]

    class Config:
        json_schema_extra = {
            "test": {
                "consulta": "Consulta becas",
                "respuesta": "Para solicitar una beca...",
                "fecha": datetime(2022, 2, 2)
            }
        }
