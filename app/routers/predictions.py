
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services.prediction import predict_match
from celery.result import AsyncResult
from app.celery_app import celery_app
router = APIRouter(prefix="/predictions", tags=["Predictions"])




def build_response(prediction: models.Prediction, fixture: models.Fixture, db: Session) -> dict:
    home_team = db.query(models.Team).filter(models.Team.id == fixture.home_team_id).first()
    away_team = db.query(models.Team).filter(models.Team.id == fixture.away_team_id).first()

    # Map "home_win"/"away_win"/"draw" to actual team name
    if prediction.predicted_winner == "home_win": #type: ignore
        winner_name = home_team.name
    elif prediction.predicted_winner == "away_win":#type: ignore
        winner_name = away_team.name
    else:
        winner_name = "Draw"

    return {
        "id": prediction.id,
        "fixture_id": prediction.fixture_id,
        "home_team": home_team.name,
        "away_team": away_team.name,
        "predicted_winner": winner_name,
        "home_win_prob": prediction.home_win_prob,
        "away_win_prob": prediction.away_win_prob,
        "draw_prob": prediction.draw_prob,
        "created_at": prediction.created_at,
    }


@router.post("/{fixture_id}", status_code=status.HTTP_201_CREATED, response_model=schemas.PredictionOut)
def create_prediction(fixture_id: int, db: Session = Depends(get_db)):
    fixture = db.query(models.Fixture).filter(models.Fixture.id == fixture_id).first()
    if not fixture:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Fixture with id {fixture_id} not found")

    existing = db.query(models.Prediction).filter(models.Prediction.fixture_id == fixture_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Prediction for fixture {fixture_id} already exists")

    result = predict_match(home_team_id=fixture.home_team_id, away_team_id=fixture.away_team_id, db=db) #type: ignore

    prediction = models.Prediction(
        fixture_id=fixture_id,
        predicted_winner=result["predicted_outcome"],
        home_win_prob=result["home_win_probability"],
        away_win_prob=result["away_win_probability"],
        draw_prob=result["draw_probability"],
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return build_response(prediction, fixture, db)


@router.get("/{fixture_id}", response_model=schemas.PredictionOut)
def get_prediction(fixture_id: int, db: Session = Depends(get_db)):
    prediction = db.query(models.Prediction).filter(models.Prediction.fixture_id == fixture_id).first()
    if not prediction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No prediction found for fixture {fixture_id}")

    fixture = db.query(models.Fixture).filter(models.Fixture.id == fixture_id).first()
    return build_response(prediction, fixture, db)


@router.get("/", response_model=list[schemas.PredictionOut])
def get_all_predictions(db: Session = Depends(get_db)):
    predictions = db.query(models.Prediction).order_by(models.Prediction.created_at.desc()).all()

    results = []
    for prediction in predictions:
        fixture = db.query(models.Fixture).filter(models.Fixture.id == prediction.fixture_id).first()
        results.append(build_response(prediction, fixture, db))

    return results

@router.get("/task/{task_id}")
def get_task_status(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
    }