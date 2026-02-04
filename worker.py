import asyncio
import json
from datetime import datetime, timedelta
from redis_client import redis_client
from database import collection

async def run_worker():
    await asyncio.sleep(0.1)
    print(" Worker: Consuming transactions...")
    while True:
        try:
            result = await redis_client.brpop("transaction_queue", timeout=1)
            if result:
                _, data = result
                tx = json.loads(data)
                # Format: YYYY-MM-DD
                day = tx['timestamp'][:10]
                tx_type = tx['type']
                method = tx['payment_method']
                amount = tx['amount']
                
                hash_key = f"stats:{day}:{tx_type}"
                await redis_client.hincrbyfloat(hash_key, method, amount)
        except Exception as e:
            print(f"Worker Error: {e}")
            await asyncio.sleep(1)

async def sync_to_mongodb():
    print(" Archiver: Syncing to MongoDB and cleaning old Redis keys...")
    while True:
        try:
            await asyncio.sleep(10)
            keys = await redis_client.keys("stats:*")
            if not keys:
                continue

            today = datetime.now().date()
            threshold_date = today - timedelta(days=7)
            dump_count = 0

            for key in keys:
                # Key format: stats:YYYY-MM-DD:type
                parts = key.split(":")
                date_str = parts[1]
                
                # 1. Persist to Mongo
                data = await redis_client.hgetall(key)
                if data:
                    await collection.update_one(
                        {"_id": key},
                        {"$set": {"totals": data, "date": date_str}},
                        upsert=True
                    )
                    dump_count += 1
                
                # 2. Cleanup Redis if older than 7 days
                key_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if key_date < threshold_date:
                    await redis_client.delete(key)
            
            print(f" MongoDB Sync: Persisted {dump_count} items. Cleanup complete.", flush=True)
            
        except Exception as e:
            print(f"Sync Error: {e}")

async def main():
    await asyncio.gather(run_worker(), sync_to_mongodb())

if __name__ == "__main__":
    asyncio.run(main())