from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.routers import teams
from .. import models, schemas
from ..database import get_db
from ..external.football_client import get_premier_league_fixtures
from app.services.cache import delete_cached

router = APIRouter(prefix="/fixtures", tags=["Fixtures"])


@router.get("/", response_model=list[schemas.FixtureOut])
def get_fixtures(db: Session = Depends(get_db)):
    fixtures = db.query(models.Fixture).all()
    return fixtures


@router.post("/sync", status_code=202)
def sync_fixtures(db: Session = Depends(get_db)):
    data = get_premier_league_fixtures()
    matches = data.get("matches", [])

    for match in matches:
        existing = db.query(models.Fixture).filter(
            models.Fixture.external_id == match["id"]
        ).first()

        score = match.get("score", {})
        full_time = score.get("fullTime", {})

        home_team = db.query(models.Team).filter(
            models.Team.external_id == match["homeTeam"]["id"]
        ).first()

        away_team = db.query(models.Team).filter(
            models.Team.external_id == match["awayTeam"]["id"]
        ).first()

        if not home_team or not away_team:
            continue

        if existing:
            existing.status = match["status"]
            existing.home_score = full_time.get("home")
            existing.away_score = full_time.get("away")
            existing.winner = score.get("winner")
        else:
            new_fixture = models.Fixture(
                external_id=match["id"],
                home_team_id=home_team.id,
                away_team_id=away_team.id,
                matchday=match.get("matchday"),
                match_date=match.get("utcDate"),
                status=match["status"],
                home_score=full_time.get("home"),
                away_score=full_time.get("away"),
                winner=score.get("winner")
            )
            db.add(new_fixture)

    db.commit()
    teams = db.query(models.Team).all()
    for team in teams:
        delete_cached(f"team_form:{team.id}:5")
    return {"message": f"Synced {len(matches)} fixtures"}