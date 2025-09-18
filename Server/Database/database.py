from sqlalchemy import create_engine, text
from Server.Database.config import DB_ENGINE, DB_HOST, DB_NAME, DB_PORT, DB_USER, DB_PASSWORD
from sqlalchemy.orm import sessionmaker, Session
from Server.Database.models import Base

import bcrypt

DB_URL = f"{DB_ENGINE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DB_URL)


class Database:
    def __init__(self):
        self.engine = create_engine(DB_URL)
        self.main_session = sessionmaker(bind=self.engine)()
        self.session_pool: dict[str, Session] = {}
        self.create_tables()

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def drop_tables(self):
        Base.metadata.drop_all(self.engine)

    def create_user_session_into_pool(self, username) -> Session:
        user_session = sessionmaker(bind=self.engine)
        self.session_pool[username] = user_session()
        return user_session()

    def find_user_by_name(self, name):
        check_query = text("""
                            SELECT * FROM players WHERE name = :name
                        """)
        check_query_params = {
            'name': name,
        }
        print(f"here4: {name}")
        print(self.session_pool)
        print("here5")
        existing_user = self.main_session.execute(check_query, check_query_params).fetchone()
        return existing_user

    def find_user_for_login(self, name: str, password: str) -> str | None:
        existing_user = self.find_user_by_name(name)
        if not existing_user:
            print(f"Logging into account {name}: Account not found")
            return "Incorrect username or password"
        if not bcrypt.checkpw(password.encode(), existing_user.password_hash.encode()):
            print(f"Logging into account {name}: Incorrect password {password}")
            return "Incorrect username or password"
        print(f"Logging into account {name}: Successfully logged in")

    def insert_user(self, name: str, password: str) -> str | None:
        existing_user = self.find_user_by_name(name)
        if existing_user:
            return "User already exists"

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        print(f"password_hash: {hashed_password}")
        insert_query = text("""
            INSERT INTO players (name, password_hash, rating)
            VALUES (:name, :hashed_password, DEFAULT)
        """)
        insert_query_params = {
            "name": name,
            "hashed_password": hashed_password
        }
        self.main_session.execute(insert_query, insert_query_params)
        self.main_session.commit()
