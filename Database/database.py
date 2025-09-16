from sqlalchemy import create_engine
from Database.config import DB_ENGINE, DB_HOST, DB_NAME, DB_PORT, DB_USER, DB_PASSWORD
from sqlalchemy.orm import sessionmaker, Session
from Database.models import Base

print(DB_ENGINE, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)

DB_URL = f"{DB_ENGINE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DB_URL)


class Database:
    def __init__(self):
        self.engine = create_engine(DB_URL)
        self.main_session = sessionmaker(bind=self.engine)
        self.create_tables()
        self.session_pool = {}

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def drop_tables(self):
        Base.metadata.drop_all(self.engine)

    def create_user_session_into_pool(self, username) -> Session:
        user_session = sessionmaker(bind=self.engine)
        self.session_pool[username] = user_session
        return user_session()

    def find_user(self, name: str, password: str):
        pass
