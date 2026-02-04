import csv
import asyncio
from models import Transaction
from redis_client import redis_client 

is_running = False

async def start_import_logic(file_path: str):
    global is_running
    is_running = True
    
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            if not is_running:
                print(" Importer stopped manually.")
                break
            
            # 1. Validate the row using Pydantic
            transaction = Transaction(**row)
            
            # 2. PUSH to Redis List
            # We convert the object to a JSON string and put it in a list called 'transaction_queue'
            await redis_client.lpush("transaction_queue", transaction.model_dump_json())
            
            # 3. Updated Log
            print(f" Queued in Redis: {transaction.amount}")
            
            # 4. Respect the sleep_ms from the CSV
            wait_time = transaction.sleep_ms / 1000
            await asyncio.sleep(wait_time)

    is_running = False
    print(" Import finished.")
    
def stop_import_logic():
    global is_running
    is_running = False