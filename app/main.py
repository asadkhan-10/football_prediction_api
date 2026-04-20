from fastapi import FastAPI
from .routers import teams, fixtures

app = FastAPI()

app.include_router(teams.router)
app.include_router(fixtures.router)
@app.get("/")
def root():
    return {"message": "Football Predict API is running"}