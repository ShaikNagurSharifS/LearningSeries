"""
Advanced Pydantic Examples
This file contains practical examples demonstrating advanced Pydantic features.
"""

from pydantic import (
    BaseModel, 
    Field, 
    field_validator, 
    model_validator,
    ConfigDict,
    EmailStr,
    HttpUrl,
    computed_field
)
from typing import List, Optional, Dict, Union, Literal
from datetime import datetime, date
from enum import Enum
import json


# Example 1: E-commerce Product System
# =====================================

class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"


class ProductCategory(str, Enum):
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    BOOKS = "books"
    HOME = "home"


class Price(BaseModel):
    """Immutable price value object"""
    model_config = ConfigDict(frozen=True)
    
    amount: float = Field(gt=0, description="Price amount")
    currency: Currency = Currency.USD
    
    @computed_field
    @property
    def formatted(self) -> str:
        symbols = {"USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥"}
        symbol = symbols.get(self.currency.value, self.currency.value)
        return f"{symbol}{self.amount:.2f}"


class Product(BaseModel):
    """Product model with validation"""
    id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(max_length=1000)
    price: Price
    category: ProductCategory
    stock_quantity: int = Field(ge=0)
    tags: List[str] = Field(default_factory=list, max_length=10)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    
    @computed_field
    @property
    def in_stock(self) -> bool:
        return self.stock_quantity > 0
    
    @field_validator('name')
    @classmethod
    def clean_name(cls, v: str) -> str:
        return v.strip().title()
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        # Remove duplicates and clean tags
        return list(set(tag.strip().lower() for tag in v if tag.strip()))


class OrderItem(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=100)
    price_at_purchase: Price
    
    @computed_field
    @property
    def subtotal(self) -> float:
        return self.quantity * self.price_at_purchase.amount


class Order(BaseModel):
    order_id: int = Field(gt=0)
    customer_email: EmailStr
    items: List[OrderItem] = Field(min_length=1)
    order_date: datetime = Field(default_factory=datetime.now)
    status: Literal["pending", "processing", "shipped", "delivered", "cancelled"] = "pending"
    
    @computed_field
    @property
    def total_amount(self) -> float:
        return sum(item.subtotal for item in self.items)
    
    @computed_field
    @property
    def total_items(self) -> int:
        return sum(item.quantity for item in self.items)
    
    @field_validator('items')
    @classmethod
    def validate_items(cls, v: List[OrderItem]) -> List[OrderItem]:
        if len(v) > 50:
            raise ValueError('Order cannot contain more than 50 different items')
        return v


# Example 2: User Management System
# ===================================

class Address(BaseModel):
    street: str = Field(min_length=1, max_length=200)
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=2, max_length=50)
    zip_code: str = Field(pattern=r'^\d{5}(-\d{4})?$')
    country: str = Field(default="USA")
    
    def __str__(self):
        return f"{self.street}, {self.city}, {self.state} {self.zip_code}"


class UserRole(str, Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    GUEST = "guest"


class User(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    id: int = Field(gt=0)
    username: str = Field(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$')
    email: EmailStr
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    role: UserRole = UserRole.USER
    address: Optional[Address] = None
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$')
    birth_date: Optional[date] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    
    @computed_field
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    @computed_field
    @property
    def age(self) -> Optional[int]:
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None
    
    @field_validator('birth_date')
    @classmethod
    def validate_birth_date(cls, v: Optional[date]) -> Optional[date]:
        if v and v >= date.today():
            raise ValueError('Birth date must be in the past')
        if v and date.today().year - v.year > 150:
            raise ValueError('Birth date is too far in the past')
        return v
    
    @field_validator('username')
    @classmethod
    def username_lowercase(cls, v: str) -> str:
        return v.lower()


class UserRegistration(BaseModel):
    """Separate model for user registration"""
    username: str = Field(min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    password_confirm: str
    first_name: str
    last_name: str
    terms_accepted: bool
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
            raise ValueError('Password must contain at least one special character')
        return v
    
    @model_validator(mode='after')
    def check_passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError('Passwords do not match')
        return self
    
    @field_validator('terms_accepted')
    @classmethod
    def terms_must_be_accepted(cls, v: bool) -> bool:
        if not v:
            raise ValueError('You must accept the terms and conditions')
        return v


# Example 3: API Response Models
# ================================

class PaginationMeta(BaseModel):
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total_items: int = Field(ge=0)
    total_pages: int = Field(ge=0)
    has_next: bool
    has_previous: bool


class ApiError(BaseModel):
    code: str
    message: str
    field: Optional[str] = None
    details: Optional[Dict] = None


class ApiResponse(BaseModel):
    """Generic API response wrapper"""
    success: bool
    data: Optional[Dict] = None
    errors: Optional[List[ApiError]] = None
    meta: Optional[PaginationMeta] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    @model_validator(mode='after')
    def check_success_consistency(self):
        if self.success and self.errors:
            raise ValueError('Successful response should not contain errors')
        if not self.success and not self.errors:
            raise ValueError('Failed response must contain errors')
        return self


# Example 4: Configuration Models
# =================================

class DatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = Field(ge=1, le=65535, default=5432)
    database: str
    username: str
    password: str
    pool_size: int = Field(ge=1, le=100, default=10)
    ssl_enabled: bool = False
    
    @computed_field
    @property
    def connection_url(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


class RedisConfig(BaseModel):
    host: str = "localhost"
    port: int = Field(ge=1, le=65535, default=6379)
    db: int = Field(ge=0, le=15, default=0)
    password: Optional[str] = None
    ssl: bool = False


class AppConfig(BaseModel):
    app_name: str
    debug: bool = False
    secret_key: str = Field(min_length=32)
    database: DatabaseConfig
    redis: RedisConfig
    allowed_hosts: List[str] = Field(default_factory=list)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    
    @field_validator('secret_key')
    @classmethod
    def secret_key_strong(cls, v: str) -> str:
        if len(set(v)) < 20:
            raise ValueError('Secret key must have at least 20 unique characters')
        return v


# Example 5: Discriminated Unions for Polymorphism
# ==================================================

class EmailNotification(BaseModel):
    type: Literal["email"] = "email"
    recipient: EmailStr
    subject: str
    body: str
    cc: Optional[List[EmailStr]] = None


class SMSNotification(BaseModel):
    type: Literal["sms"] = "sms"
    phone_number: str = Field(pattern=r'^\+?1?\d{9,15}$')
    message: str = Field(max_length=160)


class PushNotification(BaseModel):
    type: Literal["push"] = "push"
    device_token: str
    title: str
    body: str
    badge: Optional[int] = None


class NotificationRequest(BaseModel):
    notification: Union[EmailNotification, SMSNotification, PushNotification] = Field(
        discriminator='type'
    )
    priority: Literal["low", "normal", "high"] = "normal"
    scheduled_at: Optional[datetime] = None


# Example 6: Tree Structures
# ============================

class TreeNode(BaseModel):
    """Self-referencing model for tree structures"""
    id: int
    name: str
    value: Optional[float] = None
    children: List['TreeNode'] = Field(default_factory=list)
    
    @computed_field
    @property
    def is_leaf(self) -> bool:
        return len(self.children) == 0
    
    @computed_field
    @property
    def total_value(self) -> float:
        """Calculate total value including all descendants"""
        total = self.value or 0
        for child in self.children:
            total += child.total_value
        return total
    
    def find_node(self, node_id: int) -> Optional['TreeNode']:
        """Find a node by ID in the tree"""
        if self.id == node_id:
            return self
        for child in self.children:
            result = child.find_node(node_id)
            if result:
                return result
        return None


# Demonstration Functions
# ========================

def demo_product_system():
    """Demo e-commerce system"""
    print("\n=== E-commerce Product System ===\n")
    
    # Create a product
    product = Product(
        id=1,
        name="wireless headphones",
        description="High-quality wireless headphones with noise cancellation",
        price=Price(amount=199.99, currency=Currency.USD),
        category=ProductCategory.ELECTRONICS,
        stock_quantity=50,
        tags=["audio", "wireless", "electronics", "audio"]  # duplicate will be removed
    )
    
    print(f"Product: {product.name}")
    print(f"Price: {product.price.formatted}")
    print(f"In Stock: {product.in_stock}")
    print(f"Tags: {product.tags}")
    
    # Create an order
    order = Order(
        order_id=1001,
        customer_email="customer@example.com",
        items=[
            OrderItem(
                product_id=1,
                quantity=2,
                price_at_purchase=Price(amount=199.99, currency=Currency.USD)
            ),
            OrderItem(
                product_id=2,
                quantity=1,
                price_at_purchase=Price(amount=49.99, currency=Currency.USD)
            )
        ]
    )
    
    print(f"\nOrder ID: {order.order_id}")
    print(f"Total Items: {order.total_items}")
    print(f"Total Amount: ${order.total_amount:.2f}")
    print(f"Status: {order.status}")


def demo_user_system():
    """Demo user management system"""
    print("\n=== User Management System ===\n")
    
    # Create a user
    user = User(
        id=1,
        username="johndoe",
        email="john.doe@example.com",
        first_name="John",
        last_name="Doe",
        role=UserRole.USER,
        address=Address(
            street="123 Main St",
            city="New York",
            state="NY",
            zip_code="10001"
        ),
        birth_date=date(1990, 5, 15),
        phone="+11234567890"
    )
    
    print(f"User: {user.username}")
    print(f"Full Name: {user.full_name}")
    print(f"Email: {user.email}")
    print(f"Age: {user.age}")
    print(f"Address: {user.address}")
    print(f"Role: {user.role.value}")


def demo_api_response():
    """Demo API response models"""
    print("\n=== API Response Models ===\n")
    
    # Success response
    success_response = ApiResponse(
        success=True,
        data={"user_id": 1, "username": "johndoe"},
        meta=PaginationMeta(
            page=1,
            page_size=20,
            total_items=100,
            total_pages=5,
            has_next=True,
            has_previous=False
        )
    )
    
    print("Success Response:")
    print(success_response.model_dump_json(indent=2))
    
    # Error response
    error_response = ApiResponse(
        success=False,
        errors=[
            ApiError(
                code="VALIDATION_ERROR",
                message="Invalid email format",
                field="email"
            )
        ]
    )
    
    print("\nError Response:")
    print(error_response.model_dump_json(indent=2))


def demo_notifications():
    """Demo discriminated unions"""
    print("\n=== Notification System ===\n")
    
    notifications = [
        NotificationRequest(
            notification=EmailNotification(
                recipient="user@example.com",
                subject="Welcome!",
                body="Welcome to our platform"
            ),
            priority="high"
        ),
        NotificationRequest(
            notification=SMSNotification(
                phone_number="+11234567890",
                message="Your verification code is 123456"
            ),
            priority="high"
        ),
        NotificationRequest(
            notification=PushNotification(
                device_token="abc123",
                title="New Message",
                body="You have a new message"
            ),
            priority="normal"
        )
    ]
    
    for idx, notif in enumerate(notifications, 1):
        print(f"\nNotification {idx}:")
        print(f"Type: {notif.notification.type}")
        print(f"Priority: {notif.priority}")
        print(f"Details: {notif.notification.model_dump()}")


def demo_tree_structure():
    """Demo tree structures"""
    print("\n=== Tree Structure ===\n")
    
    # Create a tree
    tree = TreeNode(
        id=1,
        name="Root",
        value=100,
        children=[
            TreeNode(
                id=2,
                name="Child 1",
                value=50,
                children=[
                    TreeNode(id=4, name="Grandchild 1", value=25),
                    TreeNode(id=5, name="Grandchild 2", value=25)
                ]
            ),
            TreeNode(
                id=3,
                name="Child 2",
                value=50,
                children=[
                    TreeNode(id=6, name="Grandchild 3", value=30)
                ]
            )
        ]
    )
    
    print(f"Root: {tree.name}")
    print(f"Is Leaf: {tree.is_leaf}")
    print(f"Total Value: {tree.total_value}")
    
    # Find a node
    found_node = tree.find_node(5)
    if found_node:
        print(f"\nFound Node: {found_node.name}")
        print(f"Value: {found_node.value}")
        print(f"Is Leaf: {found_node.is_leaf}")


if __name__ == "__main__":
    """Run all demonstrations"""
    demo_product_system()
    demo_user_system()
    demo_api_response()
    demo_notifications()
    demo_tree_structure()
    
    print("\n" + "="*50)
    print("All demonstrations completed successfully!")
    print("="*50 + "\n")
