# app/tasks.py
from app.celery_app import celery_app
from app.database import SessionLocal
from app.external.football_client import get_premier_league_teams, get_premier_league_fixtures
from app import models
from app.services.cache import delete_cached


@celery_app.task
def sync_teams_task():
    db = SessionLocal()
    try:
        data = get_premier_league_teams()
        teams = data["teams"]
        for team_data in teams:
            existing = db.query(models.Team).filter(
                models.Team.external_id == team_data["id"]
            ).first()
            if existing:
                existing.name = team_data["name"]
                existing.short_name = team_data["shortName"]
                existing.tla = team_data["tla"]
                existing.crest_url = team_data["crest"]
            else:
                new_team = models.Team(
                    external_id=team_data["id"],
                    name=team_data["name"],
                    short_name=team_data["shortName"],
                    tla=team_data["tla"],
                    crest_url=team_data["crest"],
                )
                db.add(new_team)
        db.commit()
        return {"status": "success", "teams_synced": len(teams)}
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


@celery_app.task
def sync_fixtures_task():
    db = SessionLocal()
    try:
        data = get_premier_league_fixtures()
        fixtures = data["matches"]
        synced = 0
        for fixture_data in fixtures:
            home_team = db.query(models.Team).filter(
                models.Team.external_id == fixture_data["homeTeam"]["id"]
            ).first()
            away_team = db.query(models.Team).filter(
                models.Team.external_id == fixture_data["awayTeam"]["id"]
            ).first()

            if not home_team or not away_team:
                continue

            home_score = fixture_data["score"]["fullTime"].get("home")
            away_score = fixture_data["score"]["fullTime"].get("away")

            existing = db.query(models.Fixture).filter(
                models.Fixture.external_id == fixture_data["id"]
            ).first()

            if existing:
                existing.home_score = home_score
                existing.away_score = away_score
            else:
                new_fixture = models.Fixture(
                    external_id=fixture_data["id"],
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    match_date=fixture_data["utcDate"],
                    home_score=home_score,
                    away_score=away_score,
                    status=fixture_data["status"],
                )
                db.add(new_fixture)
            synced += 1

        db.commit()

        # Invalidate form cache for all teams
        teams = db.query(models.Team).all()
        for team in teams:
            delete_cached(f"team_form:{team.id}:5")

        return {"status": "success", "fixtures_synced": synced}
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()