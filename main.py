from fastapi import FastAPI
from models import Transaction
from importer import load_and_verify_csv

app = FastAPI()

@app.on_event("startup")
def startup_event():
    print("Checking CSV data...")
    load_and_verify_csv("sample_transactions.csv")

@app.get("/")
def home():
    return {"message": "Transaction Importer is running"}