from fastapi import FastAPI, BackgroundTasks, Query, HTTPException
from importer import start_import_logic, stop_import_logic
from redis_client import redis_client
from database import collection
from datetime import datetime, timedelta


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

@app.get("/stats")
async def get_stats(
    from_date: str = Query(..., regex=r"^\d{4}-\d{2}-\d{2}$"),
    to_date: str = Query(..., regex=r"^\d{4}-\d{2}-\d{2}$")
):
    try:
        start_dt = datetime.strptime(from_date, "%Y-%m-%d").date()
        end_dt = datetime.strptime(to_date, "%Y-%m-%d").date()
        
        # Calculate the 7-day boundary for the "Source of Truth"
        today = datetime.now().date()
        threshold_date = today - timedelta(days=7)
        
        final_data = {}
        
        # Loop through every single day in the requested range
        current_day = start_dt
        while current_day <= end_dt:
            day_str = current_day.strftime("%Y-%m-%d")
            
            # Initialize empty structure for this day (Handles the "Gap" requirement)
            day_results = {"deposits": {}, "withdrawals": {}}
            
            # TIED LOGIC: Decide where to look based on the 7-day rule
            if current_day >= threshold_date:
                # RECENT: Look in Redis
                for t_type in ["deposit", "withdrawal"]:
                    key = f"stats:{day_str}:{t_type}"
                    r_data = await redis_client.hgetall(key)
                    if r_data:
                        # Convert Redis strings back to floats for JSON
                        day_results[f"{t_type}s"] = {m: float(v) for m, v in r_data.items()}
            else:
                # HISTORICAL: Look in MongoDB
                # We search by the 'date' field we added in the worker sync
                cursor = collection.find({"date": day_str})
                async for doc in cursor:
                    # id format is stats:YYYY-MM-DD:type, so we split to get the type
                    t_type = doc["_id"].split(":")[-1]
                    day_results[f"{t_type}s"] = {m: float(v) for m, v in doc["totals"].items()}

            # Add this day's data (even if empty) to the final response
            final_data[day_str] = day_results
            current_day += timedelta(days=1)

        return {"data": final_data}

    except Exception as e:
        print(f"API Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/")
def home():
    return {"message": "Transaction Importer API Active"}