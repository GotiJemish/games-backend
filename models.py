import uuid
from typing import List, Optional, Dict
from sqlalchemy import Column, JSON
from sqlmodel import Field, Relationship, SQLModel

class Game(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8], primary_key=True)
    game_type: str = Field(default="ludo")  # ludo, snake-ladder
    status: str = Field(default="waiting")  # waiting, playing, finished
    current_turn: Optional[str] = Field(default=None)  # RED, GREEN, YELLOW, BLUE
    last_roll: Optional[int] = Field(default=None)
    has_rolled: bool = Field(default=False)
    winner: Optional[str] = Field(default=None)
    board_state: dict = Field(default_factory=dict, sa_column=Column(JSON))
    
    players: List["Player"] = Relationship(back_populates="game", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

class Player(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    game_id: str = Field(foreign_key="game.id")
    username: str
    color: str  # RED, GREEN, YELLOW, BLUE
    
    game: Optional[Game] = Relationship(back_populates="players")

class GameConfig(SQLModel, table=True):
    id: str = Field(primary_key=True)  # ludo, monopoly, snake-ladder, etc.
    is_public: bool = Field(default=True)
    modes_enabled: List[str] = Field(default_factory=list, sa_column=Column(JSON))