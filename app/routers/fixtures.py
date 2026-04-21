from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.routers import teams
from .. import models, schemas
from ..database import get_db
from ..external.football_client import get_premier_league_fixtures
from app.services.cache import delete_cached
from app.tasks import sync_fixtures_task
router = APIRouter(prefix="/fixtures", tags=["Fixtures"])


@router.get("/", response_model=list[schemas.FixtureOut])
def get_fixtures(db: Session = Depends(get_db)):
    fixtures = db.query(models.Fixture).all()
    return fixtures


@router.post("/sync", status_code=202)
def sync_fixtures(db: Session = Depends(get_db)):
    task = sync_fixtures_task.delay()
    return {"message": "Fixture sync started", "task_id": task.id}