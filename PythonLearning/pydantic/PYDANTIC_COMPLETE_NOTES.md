# Complete Pydantic Notes

## Table of Contents

1. [Introduction to Pydantic](#introduction)
2. [Installation](#installation)
3. [Basic Models](#basic-models)
4. [Field Types](#field-types)
5. [Field Validation](#field-validation)
6. [Custom Validators](#custom-validators)
7. [Model Configuration](#model-configuration)
8. [Field Customization](#field-customization)
9. [Nested Models](#nested-models)
10. [Data Parsing](#data-parsing)
11. [JSON Schema](#json-schema)
12. [Settings Management](#settings-management)
13. [Advanced Features](#advanced-features)
14. [Best Practices](#best-practices)
15. [Common Use Cases](#common-use-cases)

---

## Introduction to Pydantic

### What is Pydantic?

Pydantic is a data validation library for Python that uses Python type annotations to validate data and manage settings. It enforces type hints at runtime and provides user-friendly errors when data is invalid.

### Key Features

- **Runtime type validation** - Validates data types at runtime
- **Data parsing** - Converts input data to the correct types
- **JSON Schema generation** - Automatically generates JSON schemas
- **Fast** - Core validation logic written in Rust (Pydantic V2)
- **IDE support** - Works seamlessly with IDEs for autocomplete
- **Settings management** - Easy configuration management
- **Immutability support** - Can create immutable models

### When to Use Pydantic?

- API request/response validation (FastAPI uses Pydantic)
- Configuration management
- Data parsing from external sources
- ETL pipelines
- Command-line applications
- Database ORM models validation

---

## Installation

```bash
# Basic installation
pip install pydantic

# With email validation
pip install pydantic[email]

# With dotenv support for settings
pip install pydantic-settings

# Latest version (V2)
pip install "pydantic>=2.0"
```

### Version Differences

- **Pydantic V1** (< 2.0): Original implementation in pure Python
- **Pydantic V2** (>= 2.0): Rewritten with Rust core (`pydantic-core`), 5-50x faster

---

## Basic Models

### Creating a Simple Model

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str
    age: int
    is_active: bool = True  # Default value
```

### Creating Model Instances

```python
# Valid data
user = User(id=1, name="John Doe", email="john@example.com", age=30)
print(user)
# Output: id=1 name='John Doe' email='john@example.com' age=30 is_active=True

# From dictionary
data = {"id": 2, "name": "Jane", "email": "jane@example.com", "age": 25}
user2 = User(**data)

# From JSON
import json
json_data = '{"id": 3, "name": "Bob", "email": "bob@example.com", "age": 35}'
user3 = User(**json.loads(json_data))

# Using model_validate (V2)
user4 = User.model_validate(data)

# From JSON string directly (V2)
user5 = User.model_validate_json(json_data)
```

### Accessing Data

```python
user = User(id=1, name="John", email="john@example.com", age=30)

# Access attributes
print(user.id)        # 1
print(user.name)      # John
print(user.is_active) # True

# Convert to dictionary
print(user.model_dump())
# {'id': 1, 'name': 'John', 'email': 'john@example.com', 'age': 30, 'is_active': True}

# Convert to JSON
print(user.model_dump_json())
# '{"id":1,"name":"John","email":"john@example.com","age":30,"is_active":true}'

# Convert to JSON with indentation
print(user.model_dump_json(indent=2))
```

### Type Coercion

```python
# Pydantic automatically converts compatible types
user = User(id="123", name="John", email="john@example.com", age="30")
print(user.id)   # 123 (int)
print(user.age)  # 30 (int)

# Invalid conversion raises ValidationError
try:
    user = User(id="abc", name="John", email="john@example.com", age=30)
except ValidationError as e:
    print(e)
```

---

## Field Types

### Built-in Python Types

```python
from pydantic import BaseModel
from typing import List, Dict, Set, Tuple, Optional, Union, Any

class DataTypes(BaseModel):
    # Basic types
    integer: int
    floating: float
    string: str
    boolean: bool
    bytes_data: bytes

    # Collections
    list_of_ints: List[int]
    dict_data: Dict[str, int]
    set_of_strings: Set[str]
    tuple_data: Tuple[int, str, bool]

    # Optional and Union
    optional_field: Optional[str] = None  # Can be str or None
    union_field: Union[int, str]          # Can be int or str

    # Any type (no validation)
    any_field: Any
```

### Pydantic Specific Types

```python
from pydantic import (
    BaseModel,
    EmailStr,
    HttpUrl,
    FilePath,
    DirectoryPath,
    UUID4,
    PositiveInt,
    NegativeInt,
    PositiveFloat,
    conint,
    constr,
    confloat,
    conlist,
    Field
)
from datetime import datetime, date, time
from decimal import Decimal

class AdvancedTypes(BaseModel):
    # String types
    email: EmailStr                    # Validates email format
    url: HttpUrl                       # Validates URL format

    # Numeric constraints
    positive_num: PositiveInt          # Must be > 0
    negative_num: NegativeInt          # Must be < 0
    constrained_int: conint(ge=0, le=100)  # Between 0 and 100
    constrained_float: confloat(gt=0.0, lt=1.0)  # Between 0 and 1

    # String constraints
    limited_string: constr(min_length=3, max_length=50)
    pattern_string: constr(pattern=r'^[a-z]+$')  # Only lowercase letters

    # List constraints
    limited_list: conlist(int, min_length=1, max_length=10)

    # Date and time
    datetime_field: datetime
    date_field: date
    time_field: time

    # UUID
    uuid_field: UUID4

    # Decimal (for precise calculations)
    price: Decimal

    # File paths
    file_path: FilePath        # Must exist and be a file
    dir_path: DirectoryPath    # Must exist and be a directory
```

### Custom Types

```python
from pydantic import BaseModel, field_validator
from typing import NewType

# Create custom type
UserId = NewType('UserId', int)

class CustomTypes(BaseModel):
    user_id: UserId

    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v):
        if v <= 0:
            raise ValueError('User ID must be positive')
        return v
```

---

## Field Validation

### Automatic Validation

```python
from pydantic import BaseModel, ValidationError

class Product(BaseModel):
    name: str
    price: float
    quantity: int

# Valid data
product = Product(name="Laptop", price=999.99, quantity=5)

# Invalid data - raises ValidationError
try:
    product = Product(name="Laptop", price="invalid", quantity=5)
except ValidationError as e:
    print(e.json(indent=2))
```

### Field Constraints with Field()

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    price: float = Field(gt=0, description="Price must be positive")
    quantity: int = Field(ge=0, le=1000)
    discount: float = Field(default=0, ge=0, le=100)
    tags: list[str] = Field(default_factory=list, max_length=10)

# Field parameters:
# ... = required field (no default)
# default = default value
# default_factory = function to generate default
# gt = greater than
# ge = greater than or equal
# lt = less than
# le = less than or equal
# min_length = minimum length
# max_length = maximum length
# pattern = regex pattern
# description = field description (for JSON schema)
# alias = alternative name for field
# title = field title (for JSON schema)
# examples = example values
```

### Multiple Validation Errors

```python
from pydantic import BaseModel, Field, ValidationError

class User(BaseModel):
    name: str = Field(min_length=2)
    age: int = Field(ge=0, le=150)
    email: str

try:
    user = User(name="A", age=-5, email="invalid")
except ValidationError as e:
    print(e.error_count())  # Number of errors
    for error in e.errors():
        print(f"Field: {error['loc']}, Error: {error['msg']}")
```

---

## Custom Validators

### Field Validators (V2)

```python
from pydantic import BaseModel, field_validator, ValidationError

class User(BaseModel):
    name: str
    email: str
    age: int

    @field_validator('name')
    @classmethod
    def name_must_contain_space(cls, v):
        if ' ' not in v:
            raise ValueError('Name must contain a space')
        return v.title()  # Capitalize each word

    @field_validator('email')
    @classmethod
    def email_must_be_valid(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email')
        return v.lower()

    @field_validator('age')
    @classmethod
    def age_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Age must be positive')
        if v > 150:
            raise ValueError('Age must be realistic')
        return v

# Usage
user = User(name="john doe", email="JOHN@EXAMPLE.COM", age=30)
print(user.name)   # "John Doe"
print(user.email)  # "john@example.com"
```

### Validating Multiple Fields

```python
from pydantic import BaseModel, field_validator

class User(BaseModel):
    username: str
    email: str

    @field_validator('username', 'email')
    @classmethod
    def check_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()
```

### Model Validators (Validate Multiple Fields Together)

```python
from pydantic import BaseModel, model_validator

class User(BaseModel):
    password: str
    password_confirm: str

    @model_validator(mode='after')
    def check_passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError('Passwords do not match')
        return self

# Another example
class DateRange(BaseModel):
    start_date: datetime
    end_date: datetime

    @model_validator(mode='after')
    def check_dates(self):
        if self.end_date < self.start_date:
            raise ValueError('End date must be after start date')
        return self
```

### Before and After Validators

```python
from pydantic import BaseModel, field_validator

class User(BaseModel):
    name: str

    # 'before' mode: runs before Pydantic's validation
    @field_validator('name', mode='before')
    @classmethod
    def convert_to_string(cls, v):
        # Convert any input to string
        return str(v) if v is not None else ''

    # 'after' mode (default): runs after Pydantic's validation
    @field_validator('name')
    @classmethod
    def clean_name(cls, v):
        return v.strip().title()
```

### Reusing Validators

```python
from pydantic import BaseModel, field_validator

def check_not_empty(v):
    if not v or not v.strip():
        raise ValueError('Cannot be empty')
    return v.strip()

class User(BaseModel):
    username: str
    email: str

    _validate_username = field_validator('username')(check_not_empty)
    _validate_email = field_validator('email')(check_not_empty)
```

---

## Model Configuration

### ConfigDict (V2)

```python
from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    model_config = ConfigDict(
        # Validation settings
        validate_assignment=True,      # Validate on attribute assignment
        validate_default=True,         # Validate default values
        strict=False,                  # Allow type coercion

        # Extra fields handling
        extra='forbid',                # 'allow', 'ignore', or 'forbid'

        # Field settings
        frozen=False,                  # Make model immutable
        from_attributes=True,          # Allow ORM mode
        populate_by_name=True,         # Allow population by field name and alias

        # String handling
        str_strip_whitespace=True,     # Strip whitespace from strings
        str_to_lower=False,            # Convert strings to lowercase
        str_to_upper=False,            # Convert strings to uppercase
        str_min_length=0,              # Minimum string length
        str_max_length=None,           # Maximum string length

        # JSON schema
        json_schema_extra={            # Add extra info to JSON schema
            "examples": [
                {"id": 1, "name": "John"}
            ]
        },

        # Serialization
        use_enum_values=False,         # Use enum values instead of enum objects
        arbitrary_types_allowed=False, # Allow arbitrary types
    )

    id: int
    name: str
```

### Extra Fields Handling

```python
from pydantic import BaseModel, ConfigDict

# Forbid extra fields (raises error)
class StrictModel(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str

# Allow extra fields (stored in __pydantic_extra__)
class FlexibleModel(BaseModel):
    model_config = ConfigDict(extra='allow')
    name: str

# Ignore extra fields (silently discarded)
class IgnoreModel(BaseModel):
    model_config = ConfigDict(extra='ignore')
    name: str

# Examples
try:
    StrictModel(name="John", age=30)  # Raises error
except ValidationError as e:
    print("Extra field not allowed")

flexible = FlexibleModel(name="John", age=30)
print(flexible.__pydantic_extra__)  # {'age': 30}

ignore = IgnoreModel(name="John", age=30)
print(ignore.model_dump())  # {'name': 'John'}
```

### Immutable Models

```python
from pydantic import BaseModel, ConfigDict

class ImmutableUser(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    name: str

user = ImmutableUser(id=1, name="John")
# user.name = "Jane"  # Raises ValidationError
```

### Validate on Assignment

```python
from pydantic import BaseModel, ConfigDict, Field

class User(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    age: int = Field(ge=0, le=150)

user = User(age=30)
# user.age = 200  # Raises ValidationError
# user.age = "invalid"  # Raises ValidationError
user.age = 25  # OK
```

---

## Field Customization

### Field Aliases

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    id: int
    name: str = Field(alias='userName')
    email: str = Field(alias='email_address')

# Input uses aliases
data = {'id': 1, 'userName': 'John', 'email_address': 'john@example.com'}
user = User(**data)

print(user.name)  # John
print(user.model_dump())  # Uses actual field names
# {'id': 1, 'name': 'John', 'email': 'john@example.com'}

print(user.model_dump(by_alias=True))  # Uses aliases
# {'id': 1, 'userName': 'John', 'email_address': 'john@example.com'}
```

### Computed Fields

```python
from pydantic import BaseModel, computed_field

class User(BaseModel):
    first_name: str
    last_name: str

    @computed_field
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

user = User(first_name="John", last_name="Doe")
print(user.full_name)  # "John Doe"
print(user.model_dump())
# {'first_name': 'John', 'last_name': 'Doe', 'full_name': 'John Doe'}
```

### Field Serialization

```python
from pydantic import BaseModel, Field, field_serializer

class Product(BaseModel):
    name: str
    price: float

    @field_serializer('price')
    def serialize_price(self, value: float) -> str:
        return f"${value:.2f}"

product = Product(name="Laptop", price=999.999)
print(product.price)  # 999.999 (internal value)
print(product.model_dump())
# {'name': 'Laptop', 'price': '$1000.00'}
```

### Exclude Fields from Serialization

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    username: str
    password: str = Field(exclude=True)
    email: str

user = User(username="john", password="secret123", email="john@example.com")
print(user.model_dump())
# {'username': 'john', 'email': 'john@example.com'}
# password is excluded

# Include it explicitly
print(user.model_dump(exclude=None))
# {'username': 'john', 'password': 'secret123', 'email': 'john@example.com'}
```

### Dynamic Field Exclusion

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    username: str
    password: str
    email: str
    is_admin: bool

user = User(id=1, username="john", password="secret", email="john@example.com", is_admin=True)

# Exclude specific fields
print(user.model_dump(exclude={'password'}))

# Exclude multiple fields
print(user.model_dump(exclude={'password', 'is_admin'}))

# Include only specific fields
print(user.model_dump(include={'id', 'username'}))
```

---

## Nested Models

### Basic Nested Models

```python
from pydantic import BaseModel
from typing import List

class Address(BaseModel):
    street: str
    city: str
    country: str
    zip_code: str

class User(BaseModel):
    id: int
    name: str
    address: Address

# Create instance
data = {
    'id': 1,
    'name': 'John Doe',
    'address': {
        'street': '123 Main St',
        'city': 'New York',
        'country': 'USA',
        'zip_code': '10001'
    }
}

user = User(**data)
print(user.address.city)  # New York
```

### Lists of Nested Models

```python
from pydantic import BaseModel
from typing import List

class Order(BaseModel):
    product_id: int
    quantity: int
    price: float

class Customer(BaseModel):
    name: str
    orders: List[Order]

data = {
    'name': 'John',
    'orders': [
        {'product_id': 1, 'quantity': 2, 'price': 10.99},
        {'product_id': 2, 'quantity': 1, 'price': 25.50}
    ]
}

customer = Customer(**data)
print(customer.orders[0].product_id)  # 1
```

### Self-Referencing Models

```python
from pydantic import BaseModel
from typing import List, Optional

class Category(BaseModel):
    id: int
    name: str
    subcategories: Optional[List['Category']] = None

# Tree structure
data = {
    'id': 1,
    'name': 'Electronics',
    'subcategories': [
        {
            'id': 2,
            'name': 'Computers',
            'subcategories': [
                {'id': 3, 'name': 'Laptops'},
                {'id': 4, 'name': 'Desktops'}
            ]
        },
        {'id': 5, 'name': 'Phones'}
    ]
}

category = Category(**data)
print(category.subcategories[0].name)  # Computers
```

### Circular References

```python
from pydantic import BaseModel
from typing import Optional, List

class User(BaseModel):
    id: int
    name: str
    posts: List['Post'] = []

class Post(BaseModel):
    id: int
    title: str
    author: Optional[User] = None

# Update forward references
User.model_rebuild()
Post.model_rebuild()
```

---

## Data Parsing

### From JSON

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str

# Parse JSON string
json_data = '{"id": 1, "name": "John"}'
user = User.model_validate_json(json_data)

# Parse JSON bytes
json_bytes = b'{"id": 1, "name": "John"}'
user = User.model_validate_json(json_bytes)
```

### From Dictionary

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str

data = {"id": 1, "name": "John"}
user = User.model_validate(data)
# or
user = User(**data)
```

### From ORM Objects

```python
from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str

# Example with SQLAlchemy-like object
class ORMUser:
    def __init__(self):
        self.id = 1
        self.name = "John"

orm_user = ORMUser()
user = User.model_validate(orm_user)
print(user)  # id=1 name='John'
```

### Batch Parsing

```python
from pydantic import BaseModel, ValidationError
from typing import List

class User(BaseModel):
    id: int
    name: str

users_data = [
    {"id": 1, "name": "John"},
    {"id": 2, "name": "Jane"},
    {"id": 3, "name": "Bob"}
]

# Parse multiple records
users = [User(**data) for data in users_data]

# With error handling
users = []
for data in users_data:
    try:
        users.append(User(**data))
    except ValidationError as e:
        print(f"Error parsing {data}: {e}")
```

### Export Data

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str

user = User(id=1, name="John", email="john@example.com")

# To dictionary
user_dict = user.model_dump()

# To JSON string
user_json = user.model_dump_json()

# To JSON with indentation
user_json = user.model_dump_json(indent=2)

# Exclude fields
user_dict = user.model_dump(exclude={'email'})

# Include only specific fields
user_dict = user.model_dump(include={'id', 'name'})

# Exclude unset fields
class UserWithDefaults(BaseModel):
    id: int
    name: str
    is_active: bool = True

user = UserWithDefaults(id=1, name="John")
print(user.model_dump(exclude_unset=True))
# {'id': 1, 'name': 'John'}  # is_active excluded

# Exclude defaults
print(user.model_dump(exclude_defaults=True))
# {'id': 1, 'name': 'John'}

# Exclude None values
class UserOptional(BaseModel):
    id: int
    name: str
    email: Optional[str] = None

user = UserOptional(id=1, name="John")
print(user.model_dump(exclude_none=True))
# {'id': 1, 'name': 'John'}
```

---

## JSON Schema

### Generate JSON Schema

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    id: int = Field(description="User ID")
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    age: int = Field(ge=0, le=150, description="User age")

# Get JSON schema
schema = User.model_json_schema()
import json
print(json.dumps(schema, indent=2))
```

### Custom JSON Schema

```python
from pydantic import BaseModel, ConfigDict, Field

class User(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "title": "User Model",
            "description": "A user in the system",
            "examples": [
                {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john@example.com"
                }
            ]
        }
    )

    id: int
    name: str
    email: str
```

### Field-Level Schema Customization

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(
        title="Product Name",
        description="The name of the product",
        examples=["Laptop", "Phone"]
    )
    price: float = Field(
        gt=0,
        title="Price",
        description="Product price in USD",
        examples=[999.99, 1299.00]
    )
```

---

## Settings Management

### Basic Settings

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "MyApp"
    admin_email: str
    items_per_page: int = 50
    debug: bool = False

# Loads from environment variables
# APP_NAME, ADMIN_EMAIL, ITEMS_PER_PAGE, DEBUG
settings = Settings()
```

### Settings from .env File

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False
    )

    database_url: str
    secret_key: str
    debug: bool = False

# .env file:
# DATABASE_URL=postgresql://localhost/mydb
# SECRET_KEY=mysecretkey
# DEBUG=true

settings = Settings()
print(settings.database_url)
```

### Nested Settings

```python
from pydantic import BaseModel
from pydantic_settings import BaseSettings

class DatabaseSettings(BaseModel):
    host: str = "localhost"
    port: int = 5432
    username: str
    password: str
    database: str

class Settings(BaseSettings):
    app_name: str
    database: DatabaseSettings

# Environment variables:
# APP_NAME=MyApp
# DATABASE__HOST=localhost
# DATABASE__PORT=5432
# DATABASE__USERNAME=user
# DATABASE__PASSWORD=pass
# DATABASE__DATABASE=mydb

settings = Settings()
```

### Multiple .env Files

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=['.env', '.env.local'],
        env_file_encoding='utf-8'
    )

    api_key: str
    debug: bool = False

# Loads from .env first, then .env.local
# Values in .env.local override .env
settings = Settings()
```

### Settings Priority

Priority order (highest to lowest):

1. Arguments passed to `Settings()`
2. Environment variables
3. .env file variables
4. Default values in field definitions

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "DefaultApp"

# 1. Default value
settings = Settings()  # app_name = "DefaultApp"

# 2. .env file (if exists with APP_NAME=EnvApp)
# app_name = "EnvApp"

# 3. Environment variable (if APP_NAME=EnvVarApp is set)
# app_name = "EnvVarApp"

# 4. Explicit argument (highest priority)
settings = Settings(app_name="ExplicitApp")  # app_name = "ExplicitApp"
```

---

## Advanced Features

### Generic Models

```python
from pydantic import BaseModel
from typing import TypeVar, Generic, List

T = TypeVar('T')

class Response(BaseModel, Generic[T]):
    data: T
    message: str
    success: bool

class User(BaseModel):
    id: int
    name: str

# Typed responses
user_response = Response[User](
    data=User(id=1, name="John"),
    message="User retrieved",
    success=True
)

list_response = Response[List[User]](
    data=[User(id=1, name="John"), User(id=2, name="Jane")],
    message="Users retrieved",
    success=True
)
```

### Discriminated Unions

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

# Automatically determines which model to use
cat_data = {'animal': {'pet_type': 'cat', 'meow': 'loud'}}
dog_data = {'animal': {'pet_type': 'dog', 'bark': 'quiet'}}

pet1 = Pet(**cat_data)  # animal is Cat
pet2 = Pet(**dog_data)  # animal is Dog
```

### Custom Root Types

```python
from pydantic import BaseModel, RootModel
from typing import List, Dict

# List as root
class UserList(RootModel[List[User]]):
    root: List[User]

users = UserList([
    User(id=1, name="John"),
    User(id=2, name="Jane")
])

# Access via root
print(users.root[0].name)

# Dictionary as root
class UserDict(RootModel[Dict[str, User]]):
    root: Dict[str, User]

users_dict = UserDict({
    'user1': User(id=1, name="John"),
    'user2': User(id=2, name="Jane")
})
```

### Deferred Annotation

```python
from __future__ import annotations
from pydantic import BaseModel
from typing import Optional

class Node(BaseModel):
    value: int
    left: Optional[Node] = None
    right: Optional[Node] = None

# Create binary tree
tree = Node(
    value=1,
    left=Node(value=2),
    right=Node(value=3, left=Node(value=4))
)
```

### Private Attributes

```python
from pydantic import BaseModel, PrivateAttr

class User(BaseModel):
    id: int
    name: str
    _password: str = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._password = data.get('password', '')

    def check_password(self, password: str) -> bool:
        return self._password == password

user = User(id=1, name="John", password="secret")
print(user.model_dump())  # {'id': 1, 'name': 'John'}
# _password not included
print(user.check_password("secret"))  # True
```

### Model Inheritance

```python
from pydantic import BaseModel
from datetime import datetime

class BaseEntity(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

class User(BaseEntity):
    username: str
    email: str

class Product(BaseEntity):
    name: str
    price: float

# User has: id, created_at, updated_at, username, email
# Product has: id, created_at, updated_at, name, price
```

### Model Copy and Update

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str

user = User(id=1, name="John", email="john@example.com")

# Create copy with updates
updated_user = user.model_copy(update={'email': 'newemail@example.com'})
print(updated_user.email)  # newemail@example.com

# Deep copy
copied_user = user.model_copy(deep=True)
```

### Serialization Customization

```python
from pydantic import BaseModel, field_serializer, model_serializer
from datetime import datetime

class Event(BaseModel):
    name: str
    timestamp: datetime

    @field_serializer('timestamp')
    def serialize_timestamp(self, value: datetime, _info):
        return value.isoformat()

    @model_serializer
    def serialize_model(self) -> dict:
        # Custom serialization logic
        return {
            'event_name': self.name,
            'event_time': self.timestamp.isoformat()
        }
```

---

## Best Practices

### 1. Use Type Hints Properly

```python
# Good
from typing import Optional, List

class User(BaseModel):
    name: str
    age: Optional[int] = None
    tags: List[str] = []

# Avoid
class User(BaseModel):
    name: str
    age: int = None  # Should use Optional
    tags: list = []  # Should use List[str]
```

### 2. Validate Business Logic

```python
from pydantic import BaseModel, field_validator

class Order(BaseModel):
    quantity: int
    price: float

    @field_validator('quantity')
    @classmethod
    def quantity_positive(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v

    @property
    def total(self) -> float:
        return self.quantity * self.price
```

### 3. Use Immutable Models for Value Objects

```python
from pydantic import BaseModel, ConfigDict

class Money(BaseModel):
    model_config = ConfigDict(frozen=True)

    amount: float
    currency: str
```

### 4. Separate Input/Output Models

```python
# Input model (for API requests)
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

# Output model (for API responses)
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Internal model (database)
class User(BaseModel):
    id: int
    username: str
    email: str
    password_hash: str
    created_at: datetime
```

### 5. Use Settings for Configuration

```python
from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
    app_name: str = "MyApp"
    debug: bool = False
    database_url: str
    secret_key: str

    model_config = SettingsConfigDict(env_file='.env')

# Single instance pattern
settings = AppSettings()
```

### 6. Document Your Models

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    """
    User model representing a system user.

    Attributes:
        id: Unique user identifier
        username: User's login name
        email: User's email address
    """
    id: int = Field(description="Unique user identifier")
    username: str = Field(min_length=3, max_length=50, description="User's login name")
    email: str = Field(description="User's email address")
```

### 7. Handle Errors Gracefully

```python
from pydantic import BaseModel, ValidationError

def create_user(data: dict) -> User:
    try:
        return User(**data)
    except ValidationError as e:
        # Log errors
        logger.error(f"Validation error: {e.json()}")
        # Return user-friendly error
        raise ValueError("Invalid user data provided")
```

### 8. Use Aliases for External Data

```python
from pydantic import BaseModel, Field, ConfigDict

class User(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: int = Field(alias='userId')
    user_name: str = Field(alias='userName')

    # Can accept both camelCase (API) and snake_case (Python)
```

---

## Common Use Cases

### 1. FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List

app = FastAPI()

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str
    age: int = Field(ge=0, le=150)

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    age: int

@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate):
    # Automatic validation and serialization
    return UserResponse(id=1, **user.model_dump())

@app.get("/users/", response_model=List[UserResponse])
def list_users():
    return [
        UserResponse(id=1, username="john", email="john@example.com", age=30),
        UserResponse(id=2, username="jane", email="jane@example.com", age=25)
    ]
```

### 2. Configuration Management

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )

    # Application
    app_name: str = "MyApp"
    debug: bool = False

    # Database
    database_url: str
    db_pool_size: int = 10

    # Security
    secret_key: str
    access_token_expire_minutes: int = 30

    # External APIs
    api_key: str
    api_url: str

@lru_cache()
def get_settings() -> Settings:
    return Settings()

# Usage
settings = get_settings()
```

### 3. Data Validation for ETL

```python
from pydantic import BaseModel, Field, field_validator
from typing import List
from datetime import datetime

class RawDataRecord(BaseModel):
    timestamp: str
    value: float
    status: str

    @field_validator('timestamp')
    @classmethod
    def parse_timestamp(cls, v):
        return datetime.fromisoformat(v)

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v not in ['active', 'inactive', 'pending']:
            raise ValueError('Invalid status')
        return v

def process_data(raw_data: List[dict]) -> List[RawDataRecord]:
    validated_records = []
    errors = []

    for idx, record in enumerate(raw_data):
        try:
            validated_records.append(RawDataRecord(**record))
        except ValidationError as e:
            errors.append({'index': idx, 'errors': e.errors()})

    return validated_records, errors
```

### 4. API Request/Response Models

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Pagination
class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

# Generic response wrapper
class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# Search request
class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    filters: Optional[dict] = None
    pagination: PaginationParams = PaginationParams()

# List response with metadata
class ListResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    page_size: int
    has_more: bool
```

### 5. Database ORM Integration

```python
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# SQLAlchemy model
class UserDB(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)

# Pydantic model with ORM mode
class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str

# Convert ORM object to Pydantic
def get_user(user_id: int) -> UserSchema:
    db_user = session.query(UserDB).filter(UserDB.id == user_id).first()
    return UserSchema.model_validate(db_user)
```

### 6. Form Data Validation

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional

class RegistrationForm(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: str
    password: str = Field(min_length=8)
    password_confirm: str
    age: int = Field(ge=18)
    terms_accepted: bool
    newsletter: bool = False

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if '@' not in v or '.' not in v:
            raise ValueError('Invalid email format')
        return v.lower()

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v

    @model_validator(mode='after')
    def check_passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError('Passwords do not match')
        return self

    @field_validator('terms_accepted')
    @classmethod
    def terms_must_be_accepted(cls, v):
        if not v:
            raise ValueError('You must accept terms and conditions')
        return v
```

### 7. CLI Application with Pydantic

```python
import click
from pydantic import BaseModel, ValidationError

class CommandArgs(BaseModel):
    input_file: str
    output_file: str
    verbose: bool = False
    workers: int = 4

@click.command()
@click.option('--input-file', required=True)
@click.option('--output-file', required=True)
@click.option('--verbose', is_flag=True)
@click.option('--workers', default=4, type=int)
def process(input_file, output_file, verbose, workers):
    try:
        args = CommandArgs(
            input_file=input_file,
            output_file=output_file,
            verbose=verbose,
            workers=workers
        )
        # Process with validated args
        print(f"Processing {args.input_file} with {args.workers} workers")
    except ValidationError as e:
        click.echo(f"Invalid arguments: {e}", err=True)
        raise click.Abort()
```

### 8. JSON Configuration Files

```python
from pydantic import BaseModel
from typing import List
import json

class ServerConfig(BaseModel):
    host: str = "localhost"
    port: int
    workers: int = 4

class DatabaseConfig(BaseModel):
    url: str
    pool_size: int = 10

class AppConfig(BaseModel):
    app_name: str
    server: ServerConfig
    database: DatabaseConfig
    allowed_hosts: List[str]

# Load from JSON file
def load_config(config_path: str) -> AppConfig:
    with open(config_path) as f:
        config_data = json.load(f)
    return AppConfig(**config_data)

# config.json:
# {
#   "app_name": "MyApp",
#   "server": {"host": "0.0.0.0", "port": 8000},
#   "database": {"url": "postgresql://..."},
#   "allowed_hosts": ["example.com", "*.example.com"]
# }

config = load_config('config.json')
```

---

## Additional Tips and Tricks

### Working with Dates and Times

```python
from pydantic import BaseModel, field_validator
from datetime import datetime, date, time

class Event(BaseModel):
    name: str
    event_date: date
    event_time: time
    created_at: datetime = Field(default_factory=datetime.now)

    @field_validator('event_date')
    @classmethod
    def date_not_in_past(cls, v):
        if v < date.today():
            raise ValueError('Event date cannot be in the past')
        return v
```

### Working with Enums

```python
from pydantic import BaseModel
from enum import Enum

class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

class User(BaseModel):
    name: str
    status: Status

user = User(name="John", status="active")
print(user.status)  # Status.ACTIVE
print(user.status.value)  # "active"
```

### Working with Files

```python
from pydantic import BaseModel, FilePath, DirectoryPath
from pathlib import Path

class FileConfig(BaseModel):
    input_file: FilePath  # Must exist and be a file
    output_dir: DirectoryPath  # Must exist and be a directory

config = FileConfig(
    input_file="data.csv",
    output_dir="output"
)
```

### Custom Error Messages

```python
from pydantic import BaseModel, Field, field_validator

class User(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=20,
        pattern=r'^[a-zA-Z0-9_]+$'
    )

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').isalnum():
            raise ValueError(
                'Username must contain only letters, numbers, and underscores'
            )
        return v
```

### Performance Optimization

```python
from pydantic import BaseModel, ConfigDict

class FastModel(BaseModel):
    model_config = ConfigDict(
        # Skip validation for better performance
        validate_assignment=False,
        # Use slots for memory efficiency
        # (Pydantic V2 uses slots by default)
    )

    id: int
    name: str
```

---

## Summary

Pydantic is a powerful library for:

- ✅ Data validation using Python type hints
- ✅ Parsing and serialization (JSON, dict, ORM objects)
- ✅ Settings and configuration management
- ✅ Generating JSON schemas
- ✅ Creating type-safe APIs
- ✅ ETL data validation
- ✅ Form validation

**Key Concepts:**

1. **BaseModel** - Base class for all models
2. **Type hints** - Define expected data types
3. **Validators** - Custom validation logic
4. **Field** - Customize field behavior
5. **ConfigDict** - Model configuration
6. **Nested models** - Complex data structures
7. **Serialization** - Export to dict/JSON
8. **Settings** - Environment configuration

**Version Note:**

- Use **Pydantic V2** (2.0+) for new projects (faster, better features)
- Migration guide available for V1 to V2 upgrades

For more information, visit: https://docs.pydantic.dev/
