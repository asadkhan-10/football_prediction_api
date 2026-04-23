

from fastapi import APIRouter, Depends, HTTPException
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


@router.get("/{id}", response_model=schemas.FixtureOut)
def get_fixture(id: int, db: Session = Depends(get_db)):
    fixture = db.query(models.Fixture).filter(models.Fixture.id == id).first()
    if not fixture:
        raise HTTPException(status_code=404, detail=f"Fixture with id {id} not found")
    return fixture


@router.post("/sync", status_code=202)
def sync_fixtures(db: Session = Depends(get_db)):
    task = sync_fixtures_task.delay()
    return {"message": "Fixture sync started", "task_id": task.id}
