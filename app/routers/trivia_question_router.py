import sys
from fastapi import HTTPException, status, APIRouter

from app.models import TriviaQuestionPydantic, TriviaQuestionAlchemy, QuestionAlchemy
from app.database import get_connection

router = APIRouter()

ITEM_NO_ENCONTRADO = "Pregunta no encontrada."

def logging(ex):
    print(__file__, type(ex), ex)
    raise ex

def add_trivia_question(trivia_user_list: list[TriviaQuestionPydantic]):
    conexion = None
    try:
        conexion = get_connection()
        for item in trivia_user_list:
            trivia_pregunta = TriviaQuestionAlchemy(
                trivia_id = item.trivia_id,
                pregunta_id = item.pregunta_id
            )

            existe_pregunta = conexion.query(QuestionAlchemy).filter_by(id=item.pregunta_id).first()
            if existe_pregunta is None:
                raise HTTPException(status_code=400, detail=f"La pregunta no existe: {item.pregunta_id}.")


            registro = conexion.query(TriviaQuestionAlchemy).filter(
                TriviaQuestionAlchemy.trivia_id==trivia_pregunta.trivia_id, 
                TriviaQuestionAlchemy.pregunta_id==trivia_pregunta.pregunta_id
            ).first()
            if registro is None:
                conexion.add(trivia_pregunta)
        conexion.commit()
    except Exception as ex:
        if conexion and hasattr(conexion, 'rollback'):
            conexion.rollback()
        logging(ex)
    finally:
        if conexion:
            conexion.close()

@router.post("/trivias/{trivia_id}/questions/", status_code=status.HTTP_201_CREATED, tags=["trivias"])
async def create_trivia_question(trivia_question: list[TriviaQuestionPydantic]):
    """Crear una preguntas en una trivia"""
    if len(trivia_question) == 0:
        raise HTTPException(status_code=400, detail="Ingrese valores.")
    add_trivia_question(trivia_question)
    m = "Item creado." if len(trivia_question) == 1 else "Items creados."
    return {"message": m}

@router.get("/trivias/{trivia_id}/questions/", response_model=list[TriviaQuestionPydantic], tags=["trivias"])
async def read_trivia_questions(trivia_id) -> list[TriviaQuestionPydantic]:
    """Leer todas las preguntas de trivia"""
    try:
        print('hello')
        conexion = get_connection()
        sqlalchemy_trivia_questions = conexion.query(TriviaQuestionAlchemy).filter_by(trivia_id = trivia_id).all()
        pydantic_trivia_questions = [TriviaQuestionPydantic.from_orm(question) for question in sqlalchemy_trivia_questions]
        if len(pydantic_trivia_questions) > 0:
            return pydantic_trivia_questions
        else:
            raise HTTPException(status_code=404, detail=ITEM_NO_ENCONTRADO)
    except Exception as ex:
        logging(ex)
    finally:
        conexion.close()

@router.delete("/trivias/{trivia_id}/questions/{question_id}", status_code=status.HTTP_200_OK, tags=["trivias"])
async def delete_trivia_user(trivia_id: int, question_id: int):
    """Eliminar un usuario de trivia"""
    try:
        conexion = get_connection()
        registro = conexion.query(TriviaQuestionAlchemy).filter(
            TriviaQuestionAlchemy.trivia_id==trivia_id, 
            TriviaQuestionAlchemy.pregunta_id==question_id
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

