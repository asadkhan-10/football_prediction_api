# Football Prediction API

A REST API that predicts Premier League match outcomes based on recent team form. Built with FastAPI, PostgreSQL, Redis, and Celery.

LIVE at: https://football-api.duckdns.org/docs

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL + SQLAlchemy 2.0 + Alembic
- **Caching**: Redis
- **Task Queue**: Celery + Celery Beat
- **External API**: football-data.org
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions

## Features

- Sync Premier League teams and fixtures from football-data.org
- Calculate team form based on last 5 matches (wins, draws, losses, goal difference)
- Predict match outcomes with home/away win and draw probabilities
- Redis caching on form calculations to reduce database load
- Background task processing with Celery for non-blocking sync endpoints
- Automated daily fixture sync and weekly team sync via Celery Beat

## Project Structure

```
football_api/
├── app/
│   ├── routers/
│   │   ├── teams.py          # Team endpoints + form
│   │   ├── fixtures.py       # Fixture endpoints
│   │   └── predictions.py    # Prediction endpoints + task status
│   ├── services/
│   │   ├── form.py           # Form calculation logic
│   │   ├── prediction.py     # Prediction algorithm
│   │   └── cache.py          # Redis cache helpers
│   ├── external/
│   │   └── football_client.py  # football-data.org API client
│   ├── celery_app.py         # Celery + Beat configuration
│   ├── tasks.py              # Background sync tasks
│   ├── models.py             # SQLAlchemy models
│   ├── schemas.py            # Pydantic schemas
│   ├── database.py           # DB connection + session
│   ├── config.py             # Environment settings
│   └── main.py               # FastAPI app entry point
├── tests/
│   ├── conftest.py           # Test fixtures + DB setup
│   ├── test_teams.py
│   ├── test_fixtures.py
│   └── test_predictions.py
├── Dockerfile
├── docker-compose-dev.yml
├── docker-compose-prod.yml
└── requirements.txt
```

## API Endpoints

### Teams
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/teams/` | List all teams |
| GET | `/teams/{id}` | Get team by ID |
| GET | `/teams/{id}/form` | Get team's recent form (last 5 matches) |
| POST | `/teams/sync` | Trigger background team sync from API |

### Fixtures
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/fixtures/` | List all fixtures |
| GET | `/fixtures/{id}` | Get fixture by ID |
| POST | `/fixtures/sync` | Trigger background fixture sync from API |

### Predictions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/predictions/{fixture_id}` | Generate and save prediction for a fixture |
| GET | `/predictions/{fixture_id}` | Get prediction for a fixture |
| GET | `/predictions/` | List all predictions |
| GET | `/predictions/task/{task_id}` | Check background task status |

## Prediction Algorithm

The prediction engine calculates a score for each team based on:
- **Points** from last 5 matches (3 per win, 1 per draw)
- **Goal difference** from last 5 matches
- **Home advantage** bonus (+3 points for the home team)

Probabilities are derived from each team's share of the total score, with a fixed 25% baseline for draws. Results are returned as `home_win`, `away_win`, or `Draw` with the actual team names.

## Getting Started

### Prerequisites

- Docker and Docker Compose
- A [football-data.org](https://www.football-data.org/) API key (free tier available)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/asadkhan-10/football_prediction_api.git
cd football_prediction_api
```

2. Create a `.env` file in the root directory:
```env
database_hostname=localhost
database_port=5432
database_username=postgres
database_password=yourpassword
database_name=football_api
secret_key=your-secret-key
algorithm=HS256
access_token_expire_minutes=30
football_api_key=your-football-data-api-key
redis_url=redis://localhost:6379/0
```

3. Start all services with Docker Compose:
```bash
docker compose -f docker-compose-dev.yml up --build
```

This starts 4 services:
- **api** — FastAPI app on port 8000
- **postgres** — PostgreSQL on port 5433
- **redis** — Redis on port 6379
- **celery_worker** — Background task processor
- **celery_beat** — Scheduled task runner

4. Run Alembic migrations:
```bash
docker compose -f docker-compose-dev.yml exec api alembic upgrade head
```

5. Sync initial data:
```bash
# Sync teams first (fixtures depend on teams)
curl -X POST http://localhost:8000/teams/sync

# Then sync fixtures
curl -X POST http://localhost:8000/fixtures/sync
```

6. Access the API docs at `http://localhost:8000/docs`

### Running Tests

```bash
pytest -v
```

## Background Tasks

Sync endpoints return immediately with a `task_id`:

```json
{"message": "Fixture sync started", "task_id": "abc-123"}
```

Check task status:
```
GET /predictions/task/abc-123
```

### Automated Scheduling (Celery Beat)

| Task | Schedule |
|------|----------|
| Fixture sync | Daily at 3:00 AM |
| Team sync | Every Monday at 3:00 AM |

## CI/CD

GitHub Actions pipeline runs on every push to `main`:

1. **Test job** — spins up PostgreSQL and Redis services, runs pytest
2. **Docker job** — builds and pushes image to Docker Hub (only on `main` branch, after tests pass)
