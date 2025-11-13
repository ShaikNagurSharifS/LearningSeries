# Pydantic Quick Reference Guide

A concise reference for common Pydantic patterns and syntax.

---

## Installation

```bash
pip install pydantic
pip install pydantic[email]        # With email validation
pip install pydantic-settings      # For settings management
```

---

## Basic Model

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str
    age: int
    is_active: bool = True  # With default

# Create instance
user = User(id=1, name="John", email="john@example.com", age=30)
```

---

## Common Field Types

```python
from typing import List, Dict, Set, Tuple, Optional, Union
from pydantic import EmailStr, HttpUrl, UUID4

class DataTypes(BaseModel):
    # Basic
    integer: int
    floating: float
    string: str
    boolean: bool

    # Collections
    list_field: List[int]
    dict_field: Dict[str, int]
    set_field: Set[str]
    tuple_field: Tuple[int, str]

    # Optional
    optional: Optional[str] = None
    union: Union[int, str]

    # Pydantic types
    email: EmailStr
    url: HttpUrl
    uuid: UUID4
```

---

## Field Constraints

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)  # gt: greater than
    quantity: int = Field(ge=0, le=1000)  # ge/le: greater/less or equal
    description: str = Field(default="", max_length=500)
    tags: List[str] = Field(default_factory=list)
```

### Available Constraints

- `gt` - greater than
- `ge` - greater than or equal
- `lt` - less than
- `le` - less than or equal
- `min_length` - minimum length
- `max_length` - maximum length
- `pattern` - regex pattern
- `default` - default value
- `default_factory` - function to generate default

---

## Field Validators

```python
from pydantic import BaseModel, field_validator

class User(BaseModel):
    name: str
    email: str

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip().title()

    # Multiple fields
    @field_validator('name', 'email')
    @classmethod
    def check_not_empty(cls, v):
        if not v:
            raise ValueError('Field cannot be empty')
        return v
```

---

## Model Validators

```python
from pydantic import BaseModel, model_validator

class PasswordModel(BaseModel):
    password: str
    password_confirm: str

    @model_validator(mode='after')
    def check_passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError('Passwords do not match')
        return self
```

---

## Computed Fields

```python
from pydantic import BaseModel, computed_field

class User(BaseModel):
    first_name: str
    last_name: str

    @computed_field
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
```

---

## Model Configuration

```python
from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,    # Validate on attribute assignment
        frozen=False,                 # Make immutable if True
        extra='forbid',              # 'allow', 'ignore', or 'forbid'
        str_strip_whitespace=True,   # Strip whitespace from strings
        from_attributes=True,        # Enable ORM mode
        populate_by_name=True,       # Allow field name and alias
    )

    id: int
    name: str
```

---

## Nested Models

```python
from pydantic import BaseModel
from typing import List

class Address(BaseModel):
    street: str
    city: str
    zip_code: str

class User(BaseModel):
    name: str
    address: Address

# Usage
user = User(
    name="John",
    address={"street": "123 Main", "city": "NYC", "zip_code": "10001"}
)
```

---

## Self-Referencing Models

```python
from pydantic import BaseModel
from typing import List, Optional

class Category(BaseModel):
    id: int
    name: str
    subcategories: Optional[List['Category']] = None

# Usage
category = Category(
    id=1,
    name="Electronics",
    subcategories=[
        Category(id=2, name="Computers"),
        Category(id=3, name="Phones")
    ]
)
```

---

## Parsing Data

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str

# From dict
data = {"id": 1, "name": "John"}
user = User(**data)
# or
user = User.model_validate(data)

# From JSON string
json_str = '{"id": 1, "name": "John"}'
user = User.model_validate_json(json_str)

# From ORM objects
class UserORM:
    def __init__(self):
        self.id = 1
        self.name = "John"

orm_user = UserORM()
user = User.model_validate(orm_user)  # Requires from_attributes=True
```

---

## Exporting Data

```python
user = User(id=1, name="John", email="john@example.com")

# To dict
user_dict = user.model_dump()

# To JSON string
user_json = user.model_dump_json()
user_json = user.model_dump_json(indent=2)  # With indentation

# Exclude fields
user_dict = user.model_dump(exclude={'email'})

# Include only specific fields
user_dict = user.model_dump(include={'id', 'name'})

# Exclude unset/default/None values
user_dict = user.model_dump(exclude_unset=True)
user_dict = user.model_dump(exclude_defaults=True)
user_dict = user.model_dump(exclude_none=True)
```

---

## Aliases

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    id: int
    name: str = Field(alias='userName')

# Input uses alias
data = {'id': 1, 'userName': 'John'}
user = User(**data)

# Output with alias
user_dict = user.model_dump(by_alias=True)
# {'id': 1, 'userName': 'John'}
```

---

## Settings Management

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )

    app_name: str = "MyApp"
    debug: bool = False
    database_url: str
    secret_key: str

# Loads from environment variables and .env file
settings = Settings()
```

---

## Enums

```python
from enum import Enum
from pydantic import BaseModel

class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class User(BaseModel):
    name: str
    status: Status

user = User(name="John", status="active")
print(user.status)        # Status.ACTIVE
print(user.status.value)  # "active"
```

---

## Generic Models

```python
from pydantic import BaseModel
from typing import TypeVar, Generic, List

T = TypeVar('T')

class Response(BaseModel, Generic[T]):
    data: T
    success: bool
    message: str

# Usage
user_response = Response[User](
    data=User(id=1, name="John"),
    success=True,
    message="Success"
)
```

---

## Discriminated Unions

```python
from pydantic import BaseModel, Field
from typing import Union, Literal

class Cat(BaseModel):
    pet_type: Literal['cat']
    meow: str

class Dog(BaseModel):
    pet_type: Literal['dog']
    bark: str

class Pet(BaseModel):
    animal: Union[Cat, Dog] = Field(discriminator='pet_type')

# Automatically picks correct model based on pet_type
cat = Pet(animal={'pet_type': 'cat', 'meow': 'loud'})
```

---

## Error Handling

```python
from pydantic import BaseModel, ValidationError

class User(BaseModel):
    id: int
    name: str

try:
    user = User(id="invalid", name="John")
except ValidationError as e:
    # Error count
    print(e.error_count())

    # Iterate errors
    for error in e.errors():
        print(f"Field: {error['loc']}")
        print(f"Message: {error['msg']}")
        print(f"Type: {error['type']}")

    # JSON format
    print(e.json())
```

---

## JSON Schema

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    id: int = Field(description="User ID")
    name: str = Field(min_length=1, max_length=100)

# Generate JSON schema
schema = User.model_json_schema()
print(schema)
```

---

## FastAPI Integration

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

@app.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate):
    # Automatic validation and serialization
    return UserResponse(id=1, **user.model_dump())
```

---

## Common Patterns

### Pattern 1: Optional fields with validation

```python
class User(BaseModel):
    name: str
    email: Optional[EmailStr] = None

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if v is not None and not '@company.com' in v:
            raise ValueError('Must be company email')
        return v
```

### Pattern 2: Immutable value objects

```python
class Money(BaseModel):
    model_config = ConfigDict(frozen=True)

    amount: float
    currency: str
```

### Pattern 3: Separate input/output models

```python
class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime
```

### Pattern 4: Reusable validators

```python
def not_empty(v: str) -> str:
    if not v.strip():
        raise ValueError('Cannot be empty')
    return v.strip()

class User(BaseModel):
    name: str
    email: str

    _validate_name = field_validator('name')(not_empty)
    _validate_email = field_validator('email')(not_empty)
```

---

## Performance Tips

1. **Disable validation** when not needed:

```python
user = User.model_construct(id=1, name="John")  # No validation
```

2. **Batch validation** for large datasets:

```python
users = [User(**data) for data in batch]
```

3. **Use strict mode** for better performance:

```python
class User(BaseModel):
    model_config = ConfigDict(strict=True)
    id: int
```

---

## Common Validations Cheat Sheet

```python
# String validations
name: str = Field(min_length=1, max_length=100, pattern=r'^[A-Za-z\s]+$')

# Numeric validations
age: int = Field(ge=0, le=150)
price: float = Field(gt=0, decimal_places=2)

# Email
email: EmailStr

# URL
website: HttpUrl

# Date/time
from datetime import datetime, date
created: datetime
birth_date: date

# UUID
from pydantic import UUID4
id: UUID4

# File paths
from pydantic import FilePath, DirectoryPath
config_file: FilePath
data_dir: DirectoryPath

# List with constraints
tags: List[str] = Field(min_length=1, max_length=10)

# Regex pattern
phone: str = Field(pattern=r'^\+?1?\d{9,15}$')
```

---

## Debugging Tips

```python
# Print model schema
print(User.model_json_schema())

# Print model fields
print(User.model_fields)

# Check if value is valid without raising exception
from pydantic import ValidationError
try:
    User.model_validate(data)
    print("Valid")
except ValidationError:
    print("Invalid")
```

---

## Version Compatibility

### Pydantic V2 (Recommended)

```python
from pydantic import BaseModel, ConfigDict, field_validator

class User(BaseModel):
    model_config = ConfigDict(...)

    @field_validator('field')
    @classmethod
    def validate(cls, v):
        return v
```

### Pydantic V1 (Legacy)

```python
from pydantic import BaseModel, validator

class User(BaseModel):
    class Config:
        ...

    @validator('field')
    def validate(cls, v):
        return v
```

---

## Links

- **Documentation**: https://docs.pydantic.dev/
- **GitHub**: https://github.com/pydantic/pydantic
- **FastAPI**: https://fastapi.tiangolo.com/
- **Type Hints**: https://docs.python.org/3/library/typing.html

---

**Pro Tip**: Keep this reference handy while coding! 📚
