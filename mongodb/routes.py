from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

from .models import Consulta, ConsultaUpdate

router = APIRouter()

#Endpoint para crear una consulta nueva en la base de datos
@router.post("/", response_description="Nueva consulta de usuario", status_code=status.HTTP_201_CREATED, response_model=Consulta)
def create_consulta(request: Request, consulta: Consulta = Body(...)):
    consulta = jsonable_encoder(consulta)
    new_consulta = request.app.database["consultas"].insert_one(consulta)
    created_consulta = request.app.database["consultas"].find_one(
        {"_id": new_consulta.inserted_id}
    )

    return created_consulta

#Endpoint para obtener todas las consultas
@router.get("/", response_description="Lista todas las consultas", response_model=List[Consulta])
def list_consulta(request: Request):
    consultas = list(request.app.database["consultas"].find(limit=100))
    return consultas

#Endpoint para obtener una consulta específica por su ID
@router.get("/{id}", response_description="Busca una consulta por su ID", response_model=Consulta)
def find_consulta(id: str, request: Request):
    if (consulta := request.app.database["consultas"].find_one({"_id": id})) is not None:
        return consulta
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"La consulta con el ID {id} no se ha encontrado")

#Endpoint para modificar una consulta específica
@router.put("/{id}", response_description="Actualiza una consulta", response_model=Consulta)
def update_consulta(id: str, request: Request, consulta: ConsultaUpdate = Body(...)):
    consulta = {k: v for k, v in consulta.dict().items() if v is not None}
    if len(consulta) >= 1:
        update_result = request.app.database["consultas"].update_one(
            {"_id": id}, {"$set": consulta}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"La consulta con el ID {id} no se ha encontrado")

    if (
        consulta_existente := request.app.database["consultas"].find_one({"_id": id})
    ) is not None:
        return consulta_existente

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"La consulta con el ID {id} no se ha encontrado")

#Endpoint para borrar una consulta por su ID
@router.delete("/{id}", response_description="Elimina una consulta")
def delete_consulta(id: str, request: Request, response: Response):
    delete_result = request.app.database["consultas"].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"La consulta con el ID {id} no se ha encontrado")

