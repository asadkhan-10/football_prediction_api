from fastapi import FastAPI
from .routers import teams, fixtures, predictions

app = FastAPI()

app.include_router(teams.router)
app.include_router(fixtures.router)
app.include_router(predictions.router)

@app.get("/")
def root():
    return {"message": "Football Predict API is running"}