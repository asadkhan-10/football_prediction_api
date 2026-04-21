from alembic.util import status
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from .. database import get_db
from ..external.football_client import get_premier_league_teams
from app.services.form import get_team_form
from app.tasks import sync_teams_task
router = APIRouter(prefix="/teams", tags=["Teams"])


@router.get("/", response_model=list[schemas.TeamOut])
def get_teams(db: Session = Depends(get_db)):
    teams = db.query(models.Team).all()
    return teams


@router.post("/sync", status_code=202)
def sync_teams(db: Session = Depends(get_db)):
      task = sync_teams_task.delay()
      return {"message": "Team sync started", "task_id": task.id}



@router.get("/{id}/form")
def get_form(
    id: int,
    db: Session = Depends(get_db),
):
    team = db.query(models.Team).filter(models.Team.id == id).first()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with id {id} not found"
        )

    form = get_team_form(team_id=id, db=db)
    return form