from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class UserPydantic(BaseModel):
    id: int | None
    nombres: str
    apellidos: str
    email: EmailStr
    estado: str | None
    class Config:
        orm_mode = True

class UserAlchemy(Base):
    __tablename__ = 'tbl_usuarios'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    nombres = Column(String, nullable=False)
    apellidos = Column(String, nullable=False)
    email = Column(String, nullable=False)
    estado = Column(String, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "email": self.email,
            "estado": self.estado,
        }


class AnswerPydantic(BaseModel):
    id: int | None
    respuesta: str
    es_correcta: bool
    estado: str | None
    pregunta_id: int | None
    class Config:
        orm_mode = True

class AnswerAlchemy(Base):
    __tablename__ = 'tbl_respuestas'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    respuesta = Column(String, nullable=False)
    es_correcta = Column(Boolean, nullable=False)
    estado = Column(String, nullable=False)
    pregunta_id = Column(Integer, ForeignKey('tbl_preguntas.id'), nullable=False)
    
    pregunta = relationship('QuestionAlchemy', back_populates='respuestas')


class QuestionPydantic(BaseModel):
    id: int | None
    pregunta: str
    dificultad: str
    categoria: str
    puntaje: int
    estado: str | None
    respuestas: list[AnswerPydantic]
    class Config:
        orm_mode = True

class QuestionAlchemy(Base):
    __tablename__ = 'tbl_preguntas'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    pregunta = Column(String, nullable=False)
    categoria = Column(String, nullable=False)
    puntaje = Column(Integer, nullable=False)
    dificultad = Column(String, nullable=False)
    estado = Column(String, nullable=False)

    respuestas = relationship('AnswerAlchemy', back_populates='pregunta')

    def to_dict(self):
        return {
            "id": self.id,
            "pregunta": self.pregunta,
            "categoria": self.categoria,
            "puntaje": self.puntaje,
            "dificultad": self.dificultad,
            "estado": self.estado,
        }


class TriviaPydantic(BaseModel):
    id: int | None
    nombre: str
    descripcion: str
    estado: str | None
    # preguntas: list[UserPydantic]
    # usuarios: list[QuestionPydantic]
    class Config:
        orm_mode = True

class TriviaAlchemy(Base):
    __tablename__ = 'tbl_trivias'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String)
    estado = Column(String, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "estado": self.estado,
        }


class TriviaQuestionPydantic(BaseModel):
    id: int | None 
    trivia_id: int
    # preguntas: list[int] = Field(alias="pregunta_id")
    pregunta_id: int
    class Config:
        orm_mode = True
        allow_population_by_field_name = True

class TriviaQuestionAlchemy(Base):
    __tablename__ = 'tbl_trivias_preguntas'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    trivia_id = Column(Integer, nullable=False)
    pregunta_id = Column(Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "trivia_id": self.trivia_id,
            "pregunta_id": self.pregunta_id,
        }


class TriviaUserPydantic(BaseModel):
    id: int | None
    trivia_id: int
    # usuarios: list[int] = Field(alias="usuario_id")
    usuario_id: int
    class Config:
        orm_mode = True
        allow_population_by_field_name = True

class TriviaUserAlchemy(Base):
    __tablename__ = 'tbl_trivias_usuarios'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    trivia_id = Column(Integer, nullable=False)
    usuario_id = Column(Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "trivia_id": self.trivia_id,
            "usuario_id": self.usuario_id,
        }


class TriviaAnsweredPydantic(BaseModel):
    id: int | None
    trivia_id: int
    usuario_id: int
    pregunta_id: int
    respuesta_id: int
    puntaje: int | None
    class Config:
        orm_mode = True

class TriviaAnsweredAlchemy(Base):
    __tablename__ = 'tbl_trivias_respondidas'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    trivia_id = Column(Integer, nullable=False)
    usuario_id = Column(Integer, nullable=False)
    pregunta_id = Column(Integer, nullable=False)
    respuesta_id = Column(Integer, nullable=False)
    puntaje = Column(Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "trivia_id": self.trivia_id,
            "usuario_id": self.usuario_id,
            "pregunta_id": self.pregunta_id,
            "respuesta_id": self.respuesta_id,
            "puntaje": self.puntaje,
        }