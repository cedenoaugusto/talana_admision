import sys
from fastapi import HTTPException, status
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent)) # para importar modulos de la app
from models import TriviaUserPydantic, TriviaUserAlchemy
from database import get_connection#, add_item

from fastapi import APIRouter
router = APIRouter()

ITEM_NO_ENCONTRADO = "Usuario no encontrado."

def logging(ex):
    print(__file__, type(ex), ex)
    raise ex

def add_item(trivia_user_list: list[TriviaUserPydantic]):
    conexion = None
    try:
        conexion = get_connection()
        for item in trivia_user_list:
            trivia_usuario = TriviaUserAlchemy(
                trivia_id = item.trivia_id,
                usuario_id = item.usuario_id
            )
            registro = conexion.query(TriviaUserAlchemy).filter(
                TriviaUserAlchemy.trivia_id==trivia_usuario.trivia_id, 
                TriviaUserAlchemy.usuario_id==trivia_usuario.usuario_id
            ).first()
            if registro is None:
                conexion.add(trivia_usuario)
        conexion.commit()
    except Exception as ex:
        if conexion and hasattr(conexion, 'rollback'):
            conexion.rollback()
        logging(ex)
    finally:
        if conexion:
            conexion.close()

@router.post("/trivias/{trivia_id}/users/", status_code=status.HTTP_201_CREATED, tags=["trivias"])
async def create_trivia_user(trivia_user: list[TriviaUserPydantic]):
    """Crear un usuario de trivia"""
    if len(trivia_user) == 0:
        raise HTTPException(status_code=400, detail="Ingrese valores.")
    add_item(trivia_user)
    m = "Item creado." if len(trivia_user) == 1 else "Items creados."
    return {"message": m}

@router.get("/trivias/{trivia_id}/users/", response_model=list[TriviaUserPydantic], tags=["trivias"])
async def read_trivia_users(trivia_id) -> list[TriviaUserPydantic]:
    """Leer todos los usuarios de trivia"""
    try:
        conexion = get_connection()
        sqlalchemy_trivia_users = conexion.query(TriviaUserAlchemy).filter_by(trivia_id = trivia_id).all()
        pydantic_trivia_users = [TriviaUserPydantic.from_orm(user) for user in sqlalchemy_trivia_users]
        return pydantic_trivia_users
    except Exception as ex:
        logging(ex)
    finally:
        conexion.close()
    
@router.delete("/trivias/{trivia_id}/users/{user_id}", status_code=status.HTTP_200_OK, tags=["trivias"])
async def delete_trivia_user(trivia_id: int, user_id: int):
    """Eliminar un usuario de trivia"""
    try:
        conexion = get_connection()
        registro = conexion.query(TriviaUserAlchemy).filter(
            TriviaUserAlchemy.trivia_id==trivia_id, 
            TriviaUserAlchemy.usuario_id==user_id
        ).first()
        if not registro:
            raise HTTPException(status_code=404, detail=ITEM_NO_ENCONTRADO)
        
        conexion.delete(registro)
        conexion.commit()
        return {"message": "Item eliminado."}
    except Exception as ex:
        logging(ex)
    finally:
        conexion.close()