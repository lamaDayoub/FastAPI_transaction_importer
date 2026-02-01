from fastapi import FastAPI
from fastapi import FastAPI, BackgroundTasks
from importer import start_import_logic, stop_import_logic

app = FastAPI()


@app.post("/start")
async def start(background_tasks: BackgroundTasks):
    # This sends the function to the background
    background_tasks.add_task(start_import_logic, "sample_transactions.csv")
    return {"message": "Importer started in the background"}

@app.post("/stop")
async def stop():
    stop_import_logic()
    return {"message": "Stop signal sent"}

@app.get("/")
def home():
    return {"message": "Transaction Importer is running"}