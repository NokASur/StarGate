from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

game_type_enum = ENUM("Test", name="game_type_enum")
game_state_enum = ENUM("Lobby", "Playing", "Finished", name="game_state_enum")


class Players(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    password = Column(String)
    rating = Column(Float)
    registration_date = Column(DateTime)
    last_online = Column(DateTime)


class Games(Base):
    __tablename__ = 'games'
    id = Column(Integer, primary_key=True)
    map_id = Column(Integer, ForeignKey('maps.id'))
    type = Column(game_type_enum, default="Test")
    state = Column(game_state_enum, default="Lobby")
    start_time = Column(DateTime)
    end_time = Column(DateTime)


class Maps(Base):
    __tablename__ = 'maps'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    creation_date = Column(DateTime)
    map_tiles = Column(String)


class PlayerGames(Base):
    __tablename__ = 'player_games'
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'))
    player_id = Column(Integer, ForeignKey('players.id'))
