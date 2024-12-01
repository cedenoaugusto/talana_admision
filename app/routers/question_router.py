import json
import sys
from fastapi import HTTPException, status
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent)) # para importar modulos de la app
from models import QuestionPydantic, QuestionAlchemy, AnswerAlchemy
import database

from fastapi import APIRouter
router = APIRouter()

ITEM_NO_ENCONTRADO = "Pregunta no encontrada."

def logging(ex):
    print(__file__, type(ex), ex)
    raise ex

def add_question(question: QuestionPydantic):
    conexion = None
    try:
        pregunta = QuestionAlchemy(
            pregunta = question.pregunta,
            puntaje = question.puntaje,
            dificultad = question.dificultad,
            categoria = question.categoria,
            estado = 'activo' if question.estado is None else question.estado,
        )
        conexion = database.get_connection()
        conexion.add(pregunta)
        conexion.commit()
        pregunta_id = pregunta.id

        for respuesta_pyd in question.respuestas:
            respuesta = AnswerAlchemy(
                respuesta = respuesta_pyd.respuesta,
                es_correcta = respuesta_pyd.es_correcta,
                estado = respuesta_pyd.estado,
                pregunta_id = pregunta_id
            )
            conexion.add(respuesta)

        conexion.commit()
        return pregunta.id
    except Exception as ex:
        if conexion and hasattr(conexion, 'rollback'):
            conexion.rollback()
        logging(ex)
    finally:
        if conexion:
            conexion.close()

@router.post("/questions/", status_code=status.HTTP_201_CREATED, tags=["questions"])
async def create_question(question: QuestionPydantic):
    """Crear una pregunta"""
    item_id = add_question(question)
    return {"message": "Item creado.", "id": item_id}

@router.get("/questions/", response_model=list[QuestionPydantic], tags=["questions"])
async def read_questions() -> list[QuestionPydantic]:
    """Leer todas las preguntas"""
    try:
        conexion = database.get_connection()
        sqlalchemy_questions = conexion.query(QuestionAlchemy).filter(QuestionAlchemy.estado != "eliminado").all()
        pydantic_questions = [QuestionPydantic.from_orm(question) for question in sqlalchemy_questions]
        return pydantic_questions
    except Exception as ex:
        logging(ex)
    finally:
        conexion.close()

@router.get("/questions/{question_id}", response_model=QuestionPydantic, tags=["questions"])
async def read_question(question_id) -> QuestionPydantic:
    """Lee una pregunta"""
    try:
        conexion = database.get_connection()
        sqlalchemy_question = conexion.query(QuestionAlchemy).filter_by(id = question_id).first()
        if sqlalchemy_question:
            pydantic_question = QuestionPydantic.from_orm(sqlalchemy_question)
            return json.loads(pydantic_question.json())
    except Exception as ex:
        logging(ex)
    finally:
        conexion.close()

    raise HTTPException(status_code=404, detail=ITEM_NO_ENCONTRADO)

@router.put("/questions/{question_id}", status_code=status.HTTP_200_OK, tags=["questions"])
async def update_question(question_id: int, question_object: QuestionPydantic):
    """Actualizar pregunta"""
    try:
        conexion = database.get_connection()
        pregunta = conexion.query(QuestionAlchemy).filter_by(id = question_id).first()
        if not pregunta:
            raise HTTPException(status_code=404, detail=ITEM_NO_ENCONTRADO)
        
        pregunta.pregunta = question_object.pregunta
        pregunta.puntaje = question_object.puntaje
        pregunta.categoria = question_object.categoria
        pregunta.dificultad = question_object.dificultad
        pregunta.estado = question_object.estado

        i_preguntas_correctas = 0
        for respuesta_pydantic in question_object.respuestas:
            if respuesta_pydantic.es_correcta == True:
                i_preguntas_correctas += 1
                if i_preguntas_correctas > 1:
                    raise HTTPException(status_code=400, detail="Solo puede exitir una respuesta correcta.")
            
            respuesta = conexion.query(AnswerAlchemy).filter_by(id = respuesta_pydantic.id).first()
            if respuesta:
                respuesta.respuesta = respuesta_pydantic.respuesta
                respuesta.es_correcta = respuesta_pydantic.es_correcta
                respuesta.estado = respuesta_pydantic.estado

        conexion.commit()
        return {"message": "Item actualizado."}
        
    except Exception as ex:
        if conexion and hasattr(conexion, 'rollback'):
            conexion.rollback()

        logging(ex)
    finally:
        conexion.close()
    
@router.delete("/questions/{question_id}", status_code=status.HTTP_200_OK, tags=["questions"])
async def delete_question(question_id: int):
    """Eliminar una pregunta"""
    try:
        conexion = database.get_connection()
        pregunta = conexion.query(QuestionAlchemy).filter_by(id = question_id).first()
        if not pregunta:
            raise HTTPException(status_code=404, detail=ITEM_NO_ENCONTRADO)
        
        pregunta.estado = "eliminado"
        conexion.commit()
        return {"message": "Item eliminado."}
    except Exception as ex:
        logging(ex)
    finally:
        conexion.close()
