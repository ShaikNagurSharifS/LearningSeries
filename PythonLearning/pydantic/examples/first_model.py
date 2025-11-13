from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    is_active: bool = True
    
# Example usage

input_data = {
    'id': 123,
    'name': 'John Doe',
    'is_active': False
}

user = User(**input_data)
print(user)