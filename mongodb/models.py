import uuid
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

#Clase Consulta para gestionar correctamente las consultas
class Consulta(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    usuario: str = Field(...)
    consulta: str = Field(...)
    fecha: datetime = Field(...)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "test": {
                "_id": "12345678-1234-5678-1234-567812345678",
                "usuario": "test_user",
                "consulta": "Consulta becas",
                "fecha": datetime(2024, 4, 4)
            }
        }

#Clase ConsultaUpdate para getionar las actualizaciones de las consultas
class ConsultaUpdate(BaseModel):
    usuario: Optional[str]
    consulta: Optional[str]
    fecha: Optional[datetime]

    class Config:
        json_schema_extra = {
            "test": {
                "usuario": "test_user",
                "consulta": "Consulta becas",
                "fecha": datetime(2022, 2, 2)
            }
        }
