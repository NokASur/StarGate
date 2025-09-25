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

    def create_lobby_from_user(self, user: str):
        insert_query = text("""
            WITH new_game as(
                INSERT INTO games DEFAULT VALUES
                RETURNING id
            ),
            player as(
                SELECT id FROM players WHERE name = :user
            )
            INSERT INTO player_games (game_id, player_id)
            SELECT new_game.id, player.id
            FROM new_game, player
        """)
        params = {"user": user}
        self.main_session.execute(insert_query, params)
        self.main_session.commit()

    def get_lobbies(self):
        select_query = text("""
            SELECT * FROM games WHERE state = 'Lobby'
        """)
        lobbies = self.main_session.execute(select_query).fetchall()
        return lobbies

    def bind_user_to_lobby(self, username: str, lobby_id: int):
        insert_query = text("""
            INSERT INTO player_games (game_id, player_id)
            SELECT :lobby_id, id
            FROM players 
            WHERE name = :username
        """)
        params = {"username": username, "lobby_id": lobby_id}
        self.main_session.execute(insert_query, params)
        self.main_session.commit()

    def kick_user_from_lobbies(self, username: str):
        delete_query = text("""
            DELETE FROM player_games 
            WHERE player_id = (SELECT id FROM players WHERE name = :username)
        """)
        params = {"username": username}
        self.main_session.execute(delete_query, params)
        self.main_session.commit()

    def abandon_empty_lobbies(self) -> int:
        update_query = text("""
            UPDATE games
            SET state = :state
            WHERE id NOT IN (
                SELECT game_id FROM player_games
            ) AND games.state = 'Lobby'
            RETURNING id
        """)
        params = {"state": "Aborted"}
        updated_count = len(self.main_session.execute(update_query, params).fetchall())
        self.main_session.commit()
        return updated_count

    def save_message_to_current_user_lobby(self, username: str, message: str):
        insert_query = text("""
            INSERT INTO game_chats (game_id, player_id, message, timestamp)
            SELECT player_games.game_id, p.id, :message, CURRENT_TIMESTAMP
            FROM (SELECT id FROM players WHERE name = :username) as p
            LEFT JOIN player_games ON p.id = player_games.player_id
        """)
        params = {"username": username, "message": message}
        self.main_session.execute(insert_query, params)
        self.main_session.commit()

    def get_player_names_in_lobby_with(self, username: str):
        select_query = text("""
            SELECT DISTINCT p2.name
            FROM players p1
            JOIN player_games pg1 ON p1.id = pg1.player_id
            JOIN player_games pg2 ON pg1.game_id = pg2.game_id
            JOIN players p2 ON pg2.player_id = p2.id
            WHERE p1.name = :username
        """)
        params = {"username": username}
        names = self.main_session.execute(select_query, params).fetchall()
        self.main_session.commit()
        return [name[0] for name in names]
