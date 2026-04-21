from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Float
from sqlalchemy.sql.expression import text
from .database import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, nullable=False)
    external_id = Column(Integer, unique=True, nullable=False)
    name = Column(String, nullable=False)
    short_name = Column(String)
    tla = Column(String)
    crest_url = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))


class Fixture(Base):
    __tablename__ = "fixtures"

    id = Column(Integer, primary_key=True, nullable=False)
    external_id = Column(Integer, unique=True, nullable=False)
    home_team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    away_team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    matchday = Column(Integer)
    match_date = Column(TIMESTAMP(timezone=True))
    status = Column(String)
    home_score = Column(Integer)
    away_score = Column(Integer)
    winner = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))



class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, nullable=False)
    fixture_id = Column(Integer, ForeignKey("fixtures.id", ondelete="CASCADE"), nullable=False)
    predicted_winner = Column(String, nullable=False)
    home_win_prob = Column(Float, nullable=False)
    away_win_prob = Column(Float, nullable=False)
    draw_prob = Column(Float, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))