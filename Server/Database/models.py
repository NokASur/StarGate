from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import text

Base = declarative_base()

game_type_enum = ENUM("Test", name="game_type_enum")
game_state_enum = ENUM("Lobby", "Playing", "Finished", "Aborted", name="game_state_enum")


class Players(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    password_hash = Column(String)
    rating = Column(Float, server_default="800")
    registration_date = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    last_online = Column(DateTime, server_default=None)


class Games(Base):
    __tablename__ = 'games'
    id = Column(Integer, primary_key=True)
    map_id = Column(Integer, ForeignKey('maps.id'), server_default=None)
    type = Column(game_type_enum, server_default="Test")
    state = Column(game_state_enum, server_default="Lobby")
    password_hash = Column(String, server_default=None)
    start_time = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    end_time = Column(DateTime, server_default=None)
    open = Column(Boolean, server_default='false')


class Maps(Base):
    __tablename__ = 'maps'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    creation_date = Column(DateTime)
    map_tiles = Column(String)
    player_count = Column(Integer)


class PlayerGames(Base):
    __tablename__ = 'player_games'
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'))
    player_id = Column(Integer, ForeignKey('players.id'))


class GameChats(Base):
    __tablename__ = 'game_chats'
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'))
    player_id = Column(Integer, ForeignKey('players.id'))
    message = Column(String)
    timestamp = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
