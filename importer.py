import csv
import asyncio
from models import Transaction

# This global variable acts like a light switch
is_running = False

async def start_import_logic(file_path: str):
    global is_running
    is_running = True
    
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            # Check if someone flipped the switch to False
            if not is_running:
                print("🛑 Importer stopped manually.")
                break
            
            # 1. Validate using your Pydantic model
            transaction = Transaction(**row)
            
            # 2. Log it
            print(f"📥 Processing: {transaction.amount}...")
            
            # 3. Async Sleep: pauses this loop but lets FastAPI handle other requests
            wait_time = transaction.sleep_ms / 1000
            await asyncio.sleep(wait_time)

    is_running = False
    print("🏁 Import finished.")

def stop_import_logic():
    global is_running
    is_running = False