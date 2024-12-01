import json
import sys
from sqlalchemy import desc
from collections import defaultdict
from fastapi import HTTPException, status

# modulos propios
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent)) # para importar modulos de la app
from models import TriviaPydantic, TriviaAlchemy, TriviaQuestionAlchemy, QuestionAlchemy, TriviaAnsweredAlchemy, TriviaAnsweredPydantic, UserAlchemy
import database

from fastapi import APIRouter
router = APIRouter()

ITEM_NO_ENCONTRADO = "Trivia no encontrada."

def logging(ex):
    print(__file__, type(ex), ex)
    raise ex

def add_trivia(trivia: TriviaPydantic):
    conexion = None
    try:
        trivia_item = TriviaAlchemy(
            nombre = trivia.nombre,
            descripcion = trivia.descripcion,
            estado = 'activo' if trivia.estado is None else trivia.estado,
        )
        conexion = database.get_connection()
        conexion.add(trivia_item)
        conexion.commit()
        return trivia_item.id
    except Exception as ex:
        if conexion and hasattr(conexion, 'rollback'):
            conexion.rollback()
        logging(ex)
    finally:
        if conexion:
            conexion.close()

@router.post("/trivias/", status_code=status.HTTP_201_CREATED, tags=["trivias"])
async def create_trivia(trivia: TriviaPydantic):
    """Crear una trivia"""
    item_id = add_trivia(trivia)
    return {"message": "Item creado.", "id": item_id}

@router.get("/trivias/", response_model=list[TriviaPydantic], tags=["trivias"])
async def read_trivias() -> list[TriviaPydantic]:
    """Leer todas las trivias"""
    try:
        conexion = database.get_connection()
        sqlalchemy_trivias = conexion.query(TriviaAlchemy).all()
        pydantic_trivias = [TriviaPydantic.from_orm(trivia) for trivia in sqlalchemy_trivias]
        return pydantic_trivias
    except Exception as ex:
        logging(ex)
    finally:
        conexion.close()

@router.get("/trivias/{trivia_id}", response_model=TriviaPydantic, tags=["trivias"])
async def read_trivia(trivia_id) -> TriviaPydantic:
    """Leer una trivia"""
    try:
        conexion = database.get_connection()
        sqlalchemy_trivia = conexion.query(TriviaAlchemy).filter_by(id=trivia_id).first()
        if sqlalchemy_trivia:
            pydantic_trivia = TriviaPydantic.from_orm(sqlalchemy_trivia)
            return json.loads(pydantic_trivia.json())
    except Exception as ex:
        logging(ex)
    finally:
        conexion.close()

    raise HTTPException(status_code=404, detail=ITEM_NO_ENCONTRADO)

@router.get("/trivias/{trivia_id}/details", tags=["trivias"])
async def read_trivia(trivia_id):
    """Leer una trivia"""
    try:
        conexion = database.get_connection()
        sqlalchemy_trivia = (
            conexion.query(TriviaAlchemy, TriviaQuestionAlchemy, QuestionAlchemy)
                .join(TriviaQuestionAlchemy, TriviaAlchemy.id==TriviaQuestionAlchemy.trivia_id) # uno con la tabla relacion
                .join(QuestionAlchemy, QuestionAlchemy.id==TriviaQuestionAlchemy.pregunta_id) # uno con las preguntas
                .filter(
                    TriviaAlchemy.id==trivia_id,
                    QuestionAlchemy.estado=='activo'
                )
                .all()
        )
        # return sqlalchemy_trivia # para revisar la data completa
        if sqlalchemy_trivia:
            trivia_response = {}
            if len(sqlalchemy_trivia) == 1:
                trivia, _, questions = sqlalchemy_trivia # desempaquetar objeto
                if "trivia" not in trivia_response:
                    trivia_response["trivia"] = trivia.to_dict()
                    trivia_response["preguntas"] = []
                trivia_response["preguntas"].append(questions.to_dict())
                return trivia_response  
            elif len(sqlalchemy_trivia) > 1:
                for trivia, _, questions in sqlalchemy_trivia:
                    if "trivia" not in trivia_response:
                        trivia_response["trivia"] = trivia.to_dict()
                        trivia_response["preguntas"] = []
                    trivia_response["preguntas"].append(questions.to_dict())
                return trivia_response        
    except Exception as ex:
        logging(ex)
    finally:
        conexion.close()

    raise HTTPException(status_code=404, detail=ITEM_NO_ENCONTRADO)

@router.put("/trivias/{trivia_id}", status_code=status.HTTP_200_OK, tags=["trivias"])
async def update_trivia(trivia_id: int, trivia_object: TriviaPydantic):
    """Actualizar trivia"""
    try:
        conexion = database.get_connection()
        sqlalchemy_trivia = conexion.query(TriviaAlchemy).filter_by(id = trivia_id).first()
        if sqlalchemy_trivia:
            sqlalchemy_trivia.nombre = trivia_object.nombre
            sqlalchemy_trivia.descripcion = trivia_object.descripcion
            sqlalchemy_trivia.estado = trivia_object.estado
            conexion.commit()
            return {"message": "Item actualizado."}
    except Exception as ex:
        if conexion and hasattr(conexion, 'rollback'):
            conexion.rollback()
        logging(ex)
    finally:
        conexion.close()
    
    raise HTTPException(status_code=404, detail=ITEM_NO_ENCONTRADO)

@router.delete("/trivias/{trivia_id}", status_code=status.HTTP_200_OK, tags=["trivias"])
async def delete_trivia(trivia_id: int):
    """Eliminar trivia"""
    try:
        conexion = database.get_connection()
        sqlalchemy_trivia = conexion.query(TriviaAlchemy).filter_by(id = trivia_id).first()
        if sqlalchemy_trivia:
            conexion.delete(sqlalchemy_trivia)
            conexion.commit()
            return {"message": "Item eliminado."}
    except Exception as ex:
        logging(ex)
    finally:
        conexion.close()
    
    raise HTTPException(status_code=404, detail=ITEM_NO_ENCONTRADO)

@router.get("/trivias/{trivia_id}/ranking", tags=["trivias"])
async def read_trivia(trivia_id):
    """Leer una trivia"""
    try:
        conexion = database.get_connection()
        ranking_alchemy = (
            conexion.query(TriviaAnsweredAlchemy, UserAlchemy, TriviaAlchemy)
                .join(TriviaAlchemy, TriviaAlchemy.id==TriviaAnsweredAlchemy.trivia_id)
                .join(UserAlchemy, UserAlchemy.id==TriviaAnsweredAlchemy.usuario_id)
                .filter(
                    TriviaAnsweredAlchemy.trivia_id==trivia_id,
                    TriviaAlchemy.estado=='activo'
                )
                .order_by(desc(TriviaAnsweredAlchemy.puntaje))
                .all()
        )

        # return sqlalchemy_trivia # para revisar la data completa
        if ranking_alchemy:
            puntajes_usuarios_list = defaultdict(list)

            for trivia_respuesta, usuario, trivia in ranking_alchemy:
                puntajes_usuarios_list[trivia.nombre].append({
                    "usuario": usuario.nombres,
                    "puntaje": trivia_respuesta.puntaje,
                })

            ranking_salida = [
                {
                    "trivia": trivia_name,
                    "users": users
                }
                for trivia_name, users in puntajes_usuarios_list.items()
            ]
            return ranking_salida
    except Exception as ex:
        logging(ex)
    finally:
        conexion.close()

    raise HTTPException(status_code=404, detail=ITEM_NO_ENCONTRADO)
