"""
Pydantic with FastAPI Integration Examples
Real-world examples of using Pydantic with FastAPI
"""

from fastapi import FastAPI, HTTPException, Query, Path, Body, status
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import List, Optional
from datetime import datetime
from enum import Enum


# Initialize FastAPI app
app = FastAPI(
    title="E-commerce API",
    description="Example API using Pydantic models",
    version="1.0.0"
)


# Enums
# ======

class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class UserRole(str, Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"
    SELLER = "seller"


# Request Models (Input)
# ========================

class UserCreate(BaseModel):
    """Model for creating a new user"""
    username: str = Field(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$')
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    full_name: str = Field(min_length=1, max_length=100)
    role: UserRole = UserRole.CUSTOMER
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "johndoe",
                    "email": "john@example.com",
                    "password": "SecurePass123",
                    "full_name": "John Doe",
                    "role": "customer"
                }
            ]
        }
    }


class UserUpdate(BaseModel):
    """Model for updating user information"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "full_name": "John Smith",
                    "email": "john.smith@example.com"
                }
            ]
        }
    }


class UserLogin(BaseModel):
    """Model for user login"""
    username: str
    password: str
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "johndoe",
                    "password": "SecurePass123"
                }
            ]
        }
    }


class ProductCreate(BaseModel):
    """Model for creating a product"""
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(max_length=2000)
    price: float = Field(gt=0, description="Price must be positive")
    stock_quantity: int = Field(ge=0)
    category: str = Field(min_length=1)
    tags: List[str] = Field(default_factory=list, max_length=10)
    is_active: bool = True
    
    @field_validator('tags')
    @classmethod
    def clean_tags(cls, v):
        return [tag.strip().lower() for tag in v if tag.strip()]
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Wireless Headphones",
                    "description": "High-quality wireless headphones",
                    "price": 99.99,
                    "stock_quantity": 100,
                    "category": "Electronics",
                    "tags": ["audio", "wireless", "headphones"]
                }
            ]
        }
    }


class ProductUpdate(BaseModel):
    """Model for updating a product"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    price: Optional[float] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


class OrderItemCreate(BaseModel):
    """Model for order items"""
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=100)


class OrderCreate(BaseModel):
    """Model for creating an order"""
    items: List[OrderItemCreate] = Field(min_length=1)
    shipping_address: str = Field(min_length=10, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "items": [
                        {"product_id": 1, "quantity": 2},
                        {"product_id": 3, "quantity": 1}
                    ],
                    "shipping_address": "123 Main St, New York, NY 10001",
                    "notes": "Please ring doorbell"
                }
            ]
        }
    }


# Response Models (Output)
# ==========================

class UserResponse(BaseModel):
    """Model for user responses"""
    id: int
    username: str
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "username": "johndoe",
                    "email": "john@example.com",
                    "full_name": "John Doe",
                    "role": "customer",
                    "is_active": True,
                    "created_at": "2024-01-01T00:00:00"
                }
            ]
        }
    }


class ProductResponse(BaseModel):
    """Model for product responses"""
    id: int
    name: str
    description: str
    price: float
    stock_quantity: int
    category: str
    tags: List[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "from_attributes": True
    }


class OrderItemResponse(BaseModel):
    """Model for order item responses"""
    id: int
    product_id: int
    product_name: str
    quantity: int
    price_at_purchase: float
    subtotal: float
    
    model_config = {
        "from_attributes": True
    }


class OrderResponse(BaseModel):
    """Model for order responses"""
    id: int
    user_id: int
    items: List[OrderItemResponse]
    status: OrderStatus
    total_amount: float
    shipping_address: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "from_attributes": True
    }


# Generic Response Wrappers
# ===========================

class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total_items: int = Field(ge=0)
    total_pages: int


class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool = True
    message: str
    data: Optional[dict] = None


class ErrorDetail(BaseModel):
    """Error detail model"""
    field: Optional[str] = None
    message: str
    code: str


class ErrorResponse(BaseModel):
    """Generic error response"""
    success: bool = False
    message: str
    errors: List[ErrorDetail]


class PaginatedResponse(BaseModel):
    """Generic paginated response"""
    items: List[dict]
    meta: PaginationMeta


# API Endpoints
# ==============

@app.post(
    "/users/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Users"],
    summary="Register a new user",
    description="Create a new user account with the provided information"
)
async def register_user(user: UserCreate):
    """
    Register a new user:
    - **username**: Unique username (3-20 characters, alphanumeric and underscore)
    - **email**: Valid email address
    - **password**: Strong password (min 8 characters, must include uppercase, lowercase, and digit)
    - **full_name**: User's full name
    - **role**: User role (default: customer)
    """
    # In real app, save to database
    return UserResponse(
        id=1,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=True,
        created_at=datetime.now()
    )


@app.post(
    "/users/login",
    response_model=SuccessResponse,
    tags=["Users"],
    summary="User login"
)
async def login_user(credentials: UserLogin):
    """
    Authenticate a user:
    - **username**: User's username
    - **password**: User's password
    """
    # In real app, verify credentials
    return SuccessResponse(
        success=True,
        message="Login successful",
        data={"token": "dummy_token_12345"}
    )


@app.get(
    "/users/{user_id}",
    response_model=UserResponse,
    tags=["Users"],
    summary="Get user by ID"
)
async def get_user(
    user_id: int = Path(gt=0, description="The ID of the user to retrieve")
):
    """Get a user by their ID"""
    # In real app, fetch from database
    return UserResponse(
        id=user_id,
        username="johndoe",
        email="john@example.com",
        full_name="John Doe",
        role=UserRole.CUSTOMER,
        is_active=True,
        created_at=datetime.now()
    )


@app.put(
    "/users/{user_id}",
    response_model=UserResponse,
    tags=["Users"],
    summary="Update user"
)
async def update_user(
    user_id: int = Path(gt=0),
    user_update: UserUpdate = Body(...)
):
    """Update user information"""
    # In real app, update in database
    return UserResponse(
        id=user_id,
        username="johndoe",
        email=user_update.email or "john@example.com",
        full_name=user_update.full_name or "John Doe",
        role=UserRole.CUSTOMER,
        is_active=True,
        created_at=datetime.now()
    )


@app.post(
    "/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Products"],
    summary="Create a new product"
)
async def create_product(product: ProductCreate):
    """
    Create a new product:
    - **name**: Product name
    - **description**: Detailed description
    - **price**: Price (must be positive)
    - **stock_quantity**: Available quantity
    - **category**: Product category
    - **tags**: List of tags for searching
    """
    # In real app, save to database
    return ProductResponse(
        id=1,
        name=product.name,
        description=product.description,
        price=product.price,
        stock_quantity=product.stock_quantity,
        category=product.category,
        tags=product.tags,
        is_active=product.is_active,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


@app.get(
    "/products",
    response_model=List[ProductResponse],
    tags=["Products"],
    summary="List all products"
)
async def list_products(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    in_stock: bool = Query(True, description="Show only in-stock items")
):
    """
    List products with optional filters:
    - **skip**: Pagination offset
    - **limit**: Number of items per page
    - **category**: Filter by category
    - **min_price**: Minimum price filter
    - **max_price**: Maximum price filter
    - **in_stock**: Show only items in stock
    """
    # In real app, query database with filters
    return [
        ProductResponse(
            id=1,
            name="Wireless Headphones",
            description="High-quality wireless headphones",
            price=99.99,
            stock_quantity=50,
            category="Electronics",
            tags=["audio", "wireless"],
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    ]


@app.get(
    "/products/{product_id}",
    response_model=ProductResponse,
    tags=["Products"],
    summary="Get product by ID"
)
async def get_product(
    product_id: int = Path(gt=0, description="The ID of the product")
):
    """Get a specific product by ID"""
    # In real app, fetch from database
    if product_id == 999:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return ProductResponse(
        id=product_id,
        name="Wireless Headphones",
        description="High-quality wireless headphones",
        price=99.99,
        stock_quantity=50,
        category="Electronics",
        tags=["audio", "wireless"],
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


@app.post(
    "/orders",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Orders"],
    summary="Create a new order"
)
async def create_order(order: OrderCreate):
    """
    Create a new order:
    - **items**: List of products and quantities
    - **shipping_address**: Delivery address
    - **notes**: Optional order notes
    """
    # In real app, validate products, calculate total, save to database
    return OrderResponse(
        id=1,
        user_id=1,
        items=[
            OrderItemResponse(
                id=1,
                product_id=item.product_id,
                product_name=f"Product {item.product_id}",
                quantity=item.quantity,
                price_at_purchase=99.99,
                subtotal=99.99 * item.quantity
            )
            for item in order.items
        ],
        status=OrderStatus.PENDING,
        total_amount=sum(99.99 * item.quantity for item in order.items),
        shipping_address=order.shipping_address,
        notes=order.notes,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


@app.get(
    "/orders/{order_id}",
    response_model=OrderResponse,
    tags=["Orders"],
    summary="Get order by ID"
)
async def get_order(
    order_id: int = Path(gt=0, description="The ID of the order")
):
    """Get order details by ID"""
    # In real app, fetch from database
    return OrderResponse(
        id=order_id,
        user_id=1,
        items=[
            OrderItemResponse(
                id=1,
                product_id=1,
                product_name="Wireless Headphones",
                quantity=2,
                price_at_purchase=99.99,
                subtotal=199.98
            )
        ],
        status=OrderStatus.PROCESSING,
        total_amount=199.98,
        shipping_address="123 Main St, New York, NY 10001",
        notes="Please ring doorbell",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


@app.get(
    "/orders",
    response_model=List[OrderResponse],
    tags=["Orders"],
    summary="List user orders"
)
async def list_orders(
    status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """
    List orders with optional filters:
    - **status**: Filter by order status
    - **skip**: Pagination offset
    - **limit**: Number of items per page
    """
    # In real app, query database
    return []


# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}


# Documentation
if __name__ == "__main__":
    import uvicorn
    
    print("""
    ╔══════════════════════════════════════════════════════╗
    ║  FastAPI + Pydantic Example Application             ║
    ╚══════════════════════════════════════════════════════╝
    
    To run this application:
    1. Install dependencies: pip install fastapi uvicorn
    2. Run: uvicorn fastapi_examples:app --reload
    3. Open browser: http://localhost:8000/docs
    
    Interactive API documentation will be available at:
    - Swagger UI: http://localhost:8000/docs
    - ReDoc: http://localhost:8000/redoc
    
    Available endpoints:
    - POST /users/register - Register new user
    - POST /users/login - User login
    - GET /users/{user_id} - Get user by ID
    - PUT /users/{user_id} - Update user
    - POST /products - Create product
    - GET /products - List products (with filters)
    - GET /products/{product_id} - Get product by ID
    - POST /orders - Create order
    - GET /orders/{order_id} - Get order by ID
    - GET /orders - List orders
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
