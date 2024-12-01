
import json
import sys
from fastapi import HTTPException, status

from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent)) # para importar modulos de la app
from models import UserPydantic, UserAlchemy, TriviaAlchemy, QuestionAlchemy, TriviaUserAlchemy, TriviaQuestionAlchemy, \
    TriviaAnsweredPydantic, TriviaAnsweredAlchemy, AnswerAlchemy
import database

from fastapi import APIRouter
router = APIRouter()

ITEM_NO_ENCONTRADO = "Usuario no encontrado."

def logging(ex):
    print(__file__, type(ex), ex)
    raise ex

def add_user(user: UserPydantic):
    """Agrega el usuario"""
    conexion = None
    try:
        usuario = UserAlchemy(
            email = user.email,
            nombres = user.nombres,
            apellidos = user.apellidos,
            estado = 'activo' if user.estado is None else user.estado,
        )

        conexion = database.get_connection()
        sqlalchemy_user = conexion.query(UserAlchemy).filter_by(email = usuario.email).first()
        if sqlalchemy_user:
            raise HTTPException(status_code=400, detail="Ya existe un usuario con ese correo.")

        conexion.add(usuario)
        conexion.commit()
        return usuario.id
    
    except Exception as ex:
        if conexion and hasattr(conexion, 'rollback'):
            conexion.rollback()
        logging(ex)
    finally:
        if conexion:
            conexion.close()

@router.post("/users/", status_code=status.HTTP_201_CREATED, tags=["users"])
async def create_user(user: UserPydantic):
    """Crear un usuario"""
    item_id = add_user(user)
    return {"message": "Item creado.", "id": item_id}

@router.get("/users/", response_model=list[UserPydantic], tags=["users"])
async def read_users() -> list[UserPydantic]:
    """Leer todos los usuarios"""
    try:
        conexion = database.get_connection()
        sqlalchemy_users = conexion.query(UserAlchemy).all()
        pydantic_users = [UserPydantic.from_orm(user) for user in sqlalchemy_users]
        return pydantic_users
    finally:
        conexion.close()

@router.get("/users/{usuario_id}", response_model=UserPydantic, tags=["users"])
async def read_user(usuario_id: int) -> UserPydantic:
    """Lee un usuario"""
    try:
        conexion = database.get_connection()
        sqlalchemy_user = conexion.query(UserAlchemy).filter_by(id=usuario_id).first()
        if sqlalchemy_user:
            pydantic_user = UserPydantic.from_orm(sqlalchemy_user)
            return json.loads(pydantic_user.json())
    except Exception as ex:
        logging(ex)
    finally:
        conexion.close()

    raise HTTPException(status_code=404, detail=ITEM_NO_ENCONTRADO)

@router.put("/users/{usuario_id}", status_code=status.HTTP_200_OK, tags=["users"])
async def update_user(usuario_id: int, user_object: UserPydantic):
    """Actualizar usuario"""
    try:
        conexion = database.get_connection()
        usuario = conexion.query(UserAlchemy).filter_by(id = usuario_id).first()
        if usuario:
            usuario.nombres = user_object.nombres
            usuario.apellidos = user_object.apellidos
            usuario.email = user_object.email
            usuario.estado = user_object.estado
            conexion.commit()
            return {"message": "Item actualizado."}
    except Exception as ex:
        if conexion and hasattr(conexion, 'rollback'):
            conexion.rollback()
        print(__file__, type(ex), ex)
        raise ex
    finally:
        conexion.close()
    
    raise HTTPException(status_code=404, detail=ITEM_NO_ENCONTRADO)

@router.delete("/users/{usuario_id}", status_code=status.HTTP_200_OK, tags=["users"])
async def delete_user(usuario_id: int):
    """Eliminar usuario"""
    try:
        conexion = database.get_connection()
        sqlalchemy_user = conexion.query(UserAlchemy).filter_by(id = usuario_id).first()
        if sqlalchemy_user:
            conexion.delete(sqlalchemy_user)
            conexion.commit()
            return {"message": "Item eliminado."}
    except Exception as ex:
        logging(ex)
    finally:
        conexion.close()
    
    raise HTTPException(status_code=404, detail=ITEM_NO_ENCONTRADO)

@router.get("/users/{usuario_id}/trivia", response_model=UserPydantic, tags=["users"])
async def read_user(usuario_id: int) -> UserPydantic:
    """Obtiene la trivia del usuario"""
    try:
        conexion = database.get_connection()
        sqlalchemy_user = conexion.query(UserAlchemy).filter_by(id = usuario_id).first()
        if sqlalchemy_user:
            pydantic_user = UserPydantic.from_orm(sqlalchemy_user)
            return json.loads(pydantic_user.json())
    except Exception as ex:
        logging(ex)
    finally:
        conexion.close()

    raise HTTPException(status_code=404, detail=ITEM_NO_ENCONTRADO)

@router.get("/users/{usuario_id}/trivias", tags=["users"])
async def read_user(usuario_id) -> dict:
    """Lee un usuario"""
    try:
        conexion = database.get_connection()

        # Obtener los usuarios y las trivias asociadas a este
        datos = (
            conexion.query(UserAlchemy, TriviaAlchemy, QuestionAlchemy)
                .join(TriviaUserAlchemy, UserAlchemy.id == TriviaUserAlchemy.usuario_id)
                .join(TriviaAlchemy, TriviaAlchemy.id == TriviaUserAlchemy.trivia_id)
                .join(TriviaQuestionAlchemy, TriviaAlchemy.id == TriviaQuestionAlchemy.trivia_id)
                .join(QuestionAlchemy, QuestionAlchemy.id == TriviaQuestionAlchemy.pregunta_id)
                .filter(UserAlchemy.id == usuario_id)
            .all()
        )

        if datos:
            datos_anidados = {}
            for usuario, trivia, preguntas in datos:
                if "usuario" not in datos_anidados:
                    datos_anidados["usuario"] = usuario.to_dict()
                    datos_anidados["usuario"]["trivia"] = trivia.to_dict()
                    datos_anidados["usuario"]["trivia"]["pregunta"] = []

                datos_anidados["usuario"]["trivia"]["pregunta"].append(preguntas.to_dict())
            return datos_anidados
    except Exception as ex:
        logging(ex)
    finally:
        conexion.close()

    raise HTTPException(status_code=404, detail="Usuario no tiene trivias asignadas. Por favor contacta a RRHH.")

def add_answer(rpta_usuario: TriviaAnsweredPydantic):
    """Agrega la respuesta"""
    conexion = None
    try:
        conexion = database.get_connection()

        respuesta_alchemy = TriviaAnsweredAlchemy(
            trivia_id=rpta_usuario.trivia_id,
            usuario_id=rpta_usuario.usuario_id,
            pregunta_id=rpta_usuario.pregunta_id,
            respuesta_id=rpta_usuario.respuesta_id,
            puntaje=rpta_usuario.puntaje,
        )
        
        trivia_existe = conexion.query(TriviaAlchemy).filter_by(id=rpta_usuario.trivia_id).first()
        if trivia_existe is None:
            raise HTTPException(status_code=400, detail="La trivia no existe.")

        usuario_existe = conexion.query(UserAlchemy).filter_by(id=rpta_usuario.usuario_id).first()
        if usuario_existe is None:
            raise HTTPException(status_code=400, detail="Usuario no existe.")
        
        respuesta_existe = conexion.query(AnswerAlchemy).filter_by(id=rpta_usuario.respuesta_id).first()
        if respuesta_existe is None:
            raise HTTPException(status_code=400, detail="La respuesta no existe.")
        
        pregunta_existe = conexion.query(QuestionAlchemy).filter_by(id=rpta_usuario.pregunta_id).first()
        if pregunta_existe is None:
            raise HTTPException(status_code=400, detail="La pregunta no existe.")

        respuesta_enviada = conexion.query(TriviaAnsweredAlchemy).filter_by(
            trivia_id=rpta_usuario.trivia_id,
            usuario_id=rpta_usuario.usuario_id,
            pregunta_id=rpta_usuario.pregunta_id
        ).first()
        if respuesta_enviada:
            raise HTTPException(status_code=400, detail="La respuesta ya ha sido enviada.")
        
        puntaje = 0
        if respuesta_existe.es_correcta:
            puntaje = pregunta_existe.puntaje

        puntaje_usuario = conexion.query(TriviaAnsweredAlchemy).filter_by(
            trivia_id=rpta_usuario.trivia_id,
            usuario_id=rpta_usuario.usuario_id
        ).first()

        if puntaje_usuario:
            for item in puntaje_usuario:
                puntaje += item.puntaje

        respuesta_alchemy.puntaje = puntaje
        conexion.add(respuesta_alchemy)
        conexion.commit()
        return respuesta_alchemy.id, puntaje
    
    except Exception as ex:
        if conexion and hasattr(conexion, 'rollback'):
            conexion.rollback()
        logging(ex)
    finally:
        if conexion:
            conexion.close()

@router.post("/users/{usuario_id}/trivias", status_code=status.HTTP_201_CREATED, tags=["users"])
async def create_user(trivia: TriviaAnsweredPydantic):
    """Registra una respuesta de la trivia"""
    item_id, puntaje_total = add_answer(trivia)
    return {"message": "Respuesta guardarda.", "id": item_id, "puntaje": puntaje_total}