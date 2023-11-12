import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

user = os.getenv('POSTGRES_USER')
passw = os.getenv('POSTGRES_PASSWORD')
server = os.getenv('POSTGRES_SERVER')
port = os.getenv('POSTGRES_PORT')
dbs = os.getenv('POSTGRES_DB')

engine = create_engine(url=f"postgresql+psycopg2://{user}:{passw}@{server}:{port}/{dbs}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base = declarative_base()
