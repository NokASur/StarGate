from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

# RECONFIGURE

DATABASE_URL = "postgresql://username:password@localhost:5432/mydatabase"

engine = create_engine(DATABASE_URL)

Base = declarative_base()


class Players(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    password = Column(String)

class Games(Base):
    pass


class Maps(Base):
    pass


class PlayerGames(Base):
    pass
