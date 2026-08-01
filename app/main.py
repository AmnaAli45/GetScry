from fastapi import FastAPI
from app.database import engine, Base
from app.models import db_models
from app.routers import track

Base.metadata.create_all(bind=engine)

app = FastAPI(title="GetScry API")

app.include_router(track.router)   # ye naya line add karein

@app.get("/")
def home():
    return {"message": "GetScry API chal rahi hai"}