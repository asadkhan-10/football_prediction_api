from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TeamOut(BaseModel):
    id: int
    external_id: int
    name: str
    short_name: Optional[str]
    tla: Optional[str]
    crest_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
        
        
class FixtureOut(BaseModel):
    id: int
    external_id: int
    home_team_id: int
    away_team_id: int
    matchday: Optional[int]
    match_date: Optional[datetime]
    status: Optional[str]
    home_score: Optional[int]
    away_score: Optional[int]
    winner: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True