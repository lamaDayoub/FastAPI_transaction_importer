from pydantic import BaseModel
from datetime import datetime

class Transaction(BaseModel):
    timestamp :datetime 
    type : str
    payment_method : str
    amount : float 
    sleep_ms : int