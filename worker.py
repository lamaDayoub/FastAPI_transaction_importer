
    
    
    
import asyncio
import json
from datetime import datetime, timedelta
from redis_client import redis_client
from database import collection
from pymongo import UpdateOne

async def run_worker():
    """
    Consumes raw transactions from the Redis queue and aggregates them 
    into 'hot' stats in Redis hashes.
    """
    print(" Worker: Consuming transactions...")
    while True:
        try:
            # brpop: 'B' stands for 'Blocking'. It waits for data to appear in the list.
            # It returns a tuple: (queue_name, data)
            result = await redis_client.brpop("transaction_queue", timeout=1)
            
            if result:
                _, data = result
                tx = json.loads(data)
                
                # Extract date (YYYY-MM-DD) from timestamp for the key name
                day = tx['timestamp'][:10]
                # Create a unique key for this day and transaction type (e.g., stats:2026-02-09:income)
                hash_key = f"stats:{day}:{tx['type']}"
                
                # Increment the specific payment method (field) by the amount
                # Redis handles this math instantly in memory.
                await redis_client.hincrbyfloat(hash_key, tx['payment_method'], tx['amount'])
                
        except Exception as e:
            print(f"Worker Error: {e}")
            # Wait a bit before retrying if there is a connection error
            await asyncio.sleep(1)

async def sync_to_mongodb():
    """
    Periodically scans Redis for 'hot' stats, converts values to numbers,
    and performs a high-speed Bulk Write to MongoDB.
    """
    print(" Archiver: Syncing to MongoDB...")
    while True:
        try:
            # Wait 10 seconds between sync cycles to allow data to accumulate
            await asyncio.sleep(10)
            
            keys = []
            cursor = 0
            # SCAN: Iteratively finds keys matching the pattern without freezing Redis
            while True:
                cursor, found_keys = await redis_client.scan(cursor, match="stats:*", count=100)
                keys.extend(found_keys)
                if cursor == 0: # Cursor 0 means we have finished scanning all keys
                    break

            if not keys:
                continue

            today = datetime.now().date()
            threshold_date = today - timedelta(days=7)
            
            bulk_ops = []
            keys_to_delete = []

            for key in keys:
                # Get all payment methods and totals for this specific key
                data = await redis_client.hgetall(key)
                if not data:
                    continue
                
                # --- THE CONVERSION STEP ---
                # Redis returns strings: {"visa": "100.50"}. 
                # We convert to: {"visa": 100.50} so MongoDB sees them as numbers.
                numeric_totals = {method: float(amount) for method, amount in data.items()}
                
                # Extract the date from the key name for the 'date' field
                date_str = key.split(":")[1]
                
                # Prepare the 'Upsert' operation: Update if exists, Create if not.
                bulk_ops.append(
                    UpdateOne(
                        {"_id": key}, 
                        {"$set": {"totals": numeric_totals, "date": date_str}},
                        upsert=True
                    )
                )

                # If the data is older than 7 days, mark it for removal from Redis
                key_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if key_date < threshold_date:
                    keys_to_delete.append(key)

            # Perform all MongoDB updates in a single network request
            if bulk_ops:
                result = await collection.bulk_write(bulk_ops)
                print(f" MongoDB Sync: Upserted {result.upserted_count}, Modified {result.modified_count}")
            # Bulk delete expired keys from Redis to save memory
            if keys_to_delete:
                await redis_client.delete(*keys_to_delete)
                print(f" Cleanup: Removed {len(keys_to_delete)} old keys from Redis.")

        except Exception as e:
            print(f"Sync Error: {e}")

async def main():
    """
    Runs both the Worker and the Archiver concurrently.
    """
    # asyncio.gather runs multiple tasks in the same event loop
    await asyncio.gather(run_worker(), sync_to_mongodb())

if __name__ == "__main__":
    # Start the asyncio event loop
    asyncio.run(main())