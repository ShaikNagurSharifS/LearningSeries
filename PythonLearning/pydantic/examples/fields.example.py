from pydantic import BaseModel
from typing import Optional, List, Dict

class Cart(BaseModel):
    user_id:int
    items: List[str]
    total_price: float
    quantities: Dict[str, int]
    discount_code: Optional[str] = None
    
class BlogPost(BaseModel):
    title: str
    content: str
    image_url: Optional[str] = None