# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.config import settings

# Test database URL
TEST_DATABASE_URL = (
    f"postgresql://{settings.database_username}:"
    f"{settings.database_password}@"
    f"{settings.database_hostname}:"
    f"{settings.database_port}/"
    f"{settings.database_name}_test"
)

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def sample_team(db):
    from app import models
    team = models.Team(
        external_id=9999,
        name="Test FC",
        short_name="Test",
        tla="TST",
        # crest="https://test.com/crest.png"
    )
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


@pytest.fixture()
def sample_fixture(db, sample_team):
    from app import models
    away_team = models.Team(
        external_id=8888,
        name="Away FC",
        short_name="Away",
        tla="AWY",
        # crest="https://test.com/crest2.png"
    )
    db.add(away_team)
    db.commit()
    db.refresh(away_team)

    fixture = models.Fixture(
        external_id=7777,
        home_team_id=sample_team.id,
        away_team_id=away_team.id,
        match_date="2024-01-01T15:00:00Z",
        home_score=2,
        away_score=1,
        status="FINISHED"
    )
    db.add(fixture)
    db.commit()
    db.refresh(fixture)
    return fixture