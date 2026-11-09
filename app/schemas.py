from pydantic import BaseModel
from typing import List, Optional

class CartItem(BaseModel):
    product_id: int
    name: str
    price: float
    qty: int

class OrderCreate(BaseModel):
    full_name: str
    phone_number: str
    delivery_area: str
    street_address: str
    event_type: Optional[str] = "Standard Order"
    pickup_date: Optional[str] = ""
    pickup_time: Optional[str] = ""
    items: List[CartItem]
    total_amount: float