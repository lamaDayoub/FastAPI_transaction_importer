from fastapi import FastAPI
from models import Transaction

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Transaction Importer is running"}