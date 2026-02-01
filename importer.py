import csv
from models import Transaction



def load_and_verify_csv(file_path: str):
    count = 0
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            # The **row trick works because the dictionary keys 
            # match our Pydantic field names!
            transaction = Transaction(**row)
            
            print(f"✅ Success: {transaction.timestamp} | {transaction.amount}")
            count += 1
            
    print(f"\nFinished! Validated {count} transactions.")