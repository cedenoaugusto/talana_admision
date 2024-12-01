from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def get_connection():
    engine = create_engine('sqlite:///my_database.db', echo=True)
    session = sessionmaker(bind=engine)
    return session()

# def pydantic_to_sqlalchemy(pydantic_obj: TriviaUserPydantic) -> TriviaUserAlchemy:
#     # Convierte un objeto Pydantic a un dictionary 
#     return TriviaUserAlchemy(**pydantic_obj.dict())

# def add_item(trivia_user: TriviaUserPydantic):
#     conexion = None
#     try:
#         item = pydantic_to_sqlalchemy(trivia_user)
#         conexion = get_connection()
#         conexion.add(item)
#         conexion.commit()
#         conexion.commit()
#         return item.id
#     except Exception as ex:
#         if conexion and hasattr(conexion, 'rollback'):
#             conexion.rollback()
#         print(ex)
#     finally:
#         if conexion:
#             conexion.close()