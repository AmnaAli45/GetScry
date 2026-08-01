from fastapi import FastAPI
from app.database import engine, Base
from app.models import db_models   # ye line zaroori hai

Base.metadata.create_all(bind=engine)

app = FastAPI(title="GetScry API")

@app.get("/")
def home():
    return {"message": "GetScry API chal rahi hai"}