from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def get_connection():
    engine = create_engine('sqlite:///my_database.db', echo=True)
    session = sessionmaker(bind=engine)
    return session()