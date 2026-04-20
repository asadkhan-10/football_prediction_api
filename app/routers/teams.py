from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, schemas
from .. database import get_db
from ..external.football_client import get_premier_league_teams


router = APIRouter(prefix="/teams", tags=["Teams"])


@router.get("/", response_model=list[schemas.TeamOut])
def get_teams(db: Session = Depends(get_db)):
    teams = db.query(models.Team).all()
    return teams


@router.post("/sync", status_code=202)
def sync_teams(db: Session = Depends(get_db)):
    data = get_premier_league_teams()
    teams = data.get("teams", [])

    for team_data in teams:
        existing = db.query(models.Team).filter(
            models.Team.external_id == team_data["id"]
        ).first()

        if existing:
            existing.name = team_data["name"]
            existing.short_name = team_data.get("shortName")
            existing.tla = team_data.get("tla")
            existing.crest_url = team_data.get("crest")
        else:
            new_team = models.Team(
                external_id=team_data["id"],
                name=team_data["name"],
                short_name=team_data.get("shortName"),
                tla=team_data.get("tla"),
                crest_url=team_data.get("crest")
            )
            db.add(new_team)

    db.commit()
    return {"message": f"Synced {len(teams)} teams"}