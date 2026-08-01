from fastapi import FastAPI
from app.database import engine, Base
from app.models import db_models

# Ye line file/tables ko actually create karti hai
Base.metadata.create_all(bind=engine)

app = FastAPI(title="GetScry API")

@app.get("/")
def home():
    return {"message": "GetScry API chal rahi hai"}