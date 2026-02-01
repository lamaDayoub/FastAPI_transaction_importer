import csv
import asyncio
from models import Transaction
from database import collection  # <--- IMPORT THIS

is_running = False

async def start_import_logic(file_path: str):
    global is_running
    is_running = True
    
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            if not is_running:
                print("🛑 Importer stopped manually.")
                break
            
            # 1. Validate using Pydantic
            transaction = Transaction(**row)
            
            # 2. THE MISSING PIECE: Save to MongoDB
            # Convert Pydantic model to a dictionary for Mongo
            await collection.insert_one(transaction.model_dump()) 
            
            # 3. Log it
            print(f"✅ Saved to DB: {transaction.amount}")
            
            # 4. Async Sleep
            wait_time = transaction.sleep_ms / 1000
            await asyncio.sleep(wait_time)

    is_running = False
    print("🏁 Import finished.")
    
def stop_import_logic():
    global is_running
    is_running = False