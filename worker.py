import asyncio
import json
from redis_client import redis_client

async def run_worker():
    print(" Worker started: Waiting for transactions...")
    
    while True:
        # brpop "Blocks" until something is in the queue. 
        # It's very efficient—no wasted CPU power.
        result = await redis_client.brpop("transaction_queue")
        
        if result:
            # result is (list_name, data)
            _, data = result
            tx = json.loads(data)
            
            # Extract info for aggregation
            day = tx['timestamp'][:10]  # Get YYYY-MM-DD
            tx_type = tx['type']        # deposit or withdrawal
            method = tx['payment_method']
            amount = tx['amount']
            
            # Key design: stats:2026-01-01:deposit
            hash_key = f"stats:{day}:{tx_type}"
            
            # Increment the specific payment method total inside the hash
            await redis_client.hincrbyfloat(hash_key, method, amount)
            
            print(f" Aggregated: {hash_key} -> {method}: +{amount}")

if __name__ == "__main__":
    asyncio.run(run_worker())