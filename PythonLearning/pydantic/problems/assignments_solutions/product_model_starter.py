from pydantic import BaseModel

# Create a product model with the following fields:
# id, name, price, and in_stock.

class Product(BaseModel):
    id: int
    name:str
    price:float
    in_stock: bool
    