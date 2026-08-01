from fastapi import FastAPI

app = FastAPI(title="GetScry API")

@app.get("/")
def home():
    return {"message": "GetScry API chal rahi hai"}