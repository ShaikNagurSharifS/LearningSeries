"""
Pydantic Validation Examples
Comprehensive examples of different validation techniques in Pydantic
"""

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
    ValidationError,
    EmailStr,
    HttpUrl,
    conint,
    constr,
    confloat,
    conlist
)
from typing import List, Optional, Dict
from datetime import datetime, date
import re


# Example 1: Basic Field Validation
# ==================================

class BasicValidation(BaseModel):
    """Examples of basic field validation"""
    
    # String constraints
    name: str = Field(min_length=1, max_length=100)
    username: str = Field(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$')
    
    # Numeric constraints
    age: int = Field(ge=0, le=150)  # Greater than or equal, Less than or equal
    score: float = Field(gt=0, lt=100)  # Greater than, Less than
    
    # List constraints
    tags: List[str] = Field(min_length=1, max_length=10)
    
    # Email and URL
    email: EmailStr
    website: Optional[HttpUrl] = None


def demo_basic_validation():
    """Demonstrate basic field validation"""
    print("\n=== Basic Field Validation ===\n")
    
    try:
        # Valid data
        user = BasicValidation(
            name="John Doe",
            username="john_doe",
            age=30,
            score=85.5,
            tags=["python", "pydantic"],
            email="john@example.com",
            website="https://example.com"
        )
        print(f"✓ Valid user created: {user.username}")
    except ValidationError as e:
        print(f"✗ Validation failed: {e}")
    
    # Invalid data examples
    invalid_cases = [
        {"name": "", "username": "jd", "age": 30, "score": 50, "tags": ["tag"], "email": "test@test.com"},
        {"name": "John", "username": "john doe", "age": 30, "score": 50, "tags": ["tag"], "email": "test@test.com"},
        {"name": "John", "username": "john", "age": -5, "score": 50, "tags": ["tag"], "email": "test@test.com"},
        {"name": "John", "username": "john", "age": 30, "score": 150, "tags": ["tag"], "email": "test@test.com"},
        {"name": "John", "username": "john", "age": 30, "score": 50, "tags": [], "email": "test@test.com"},
        {"name": "John", "username": "john", "age": 30, "score": 50, "tags": ["tag"], "email": "invalid-email"},
    ]
    
    for idx, data in enumerate(invalid_cases, 1):
        try:
            BasicValidation(**data)
            print(f"✗ Case {idx} should have failed")
        except ValidationError as e:
            print(f"✓ Case {idx} correctly failed: {e.error_count()} error(s)")


# Example 2: Custom Field Validators
# ====================================

class CustomValidation(BaseModel):
    """Examples of custom field validators"""
    
    password: str
    confirm_password: str
    phone_number: str
    credit_card: str
    postal_code: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Strong password validation"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain special character')
        return v
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate and format phone number"""
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', v)
        
        if len(digits) != 10:
            raise ValueError('Phone number must have 10 digits')
        
        # Format as (XXX) XXX-XXXX
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    
    @field_validator('credit_card')
    @classmethod
    def validate_credit_card(cls, v: str) -> str:
        """Validate credit card using Luhn algorithm"""
        # Remove spaces and dashes
        card = re.sub(r'[\s-]', '', v)
        
        if not card.isdigit():
            raise ValueError('Credit card must contain only digits')
        
        if len(card) not in [13, 14, 15, 16, 19]:
            raise ValueError('Invalid credit card length')
        
        # Luhn algorithm
        def luhn_checksum(card_number):
            def digits_of(n):
                return [int(d) for d in str(n)]
            digits = digits_of(card_number)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d*2))
            return checksum % 10
        
        if luhn_checksum(card) != 0:
            raise ValueError('Invalid credit card number')
        
        return card
    
    @field_validator('postal_code')
    @classmethod
    def validate_postal_code(cls, v: str) -> str:
        """Validate US postal code"""
        # Match XXXXX or XXXXX-XXXX format
        if not re.match(r'^\d{5}(-\d{4})?$', v):
            raise ValueError('Invalid postal code format')
        return v


def demo_custom_validation():
    """Demonstrate custom validators"""
    print("\n=== Custom Field Validation ===\n")
    
    try:
        data = CustomValidation(
            password="SecurePass123!",
            confirm_password="SecurePass123!",
            phone_number="1234567890",
            credit_card="4532015112830366",  # Valid test card
            postal_code="12345"
        )
        print(f"✓ Valid data: Phone formatted as {data.phone_number}")
    except ValidationError as e:
        print(f"✗ Validation failed:\n{e}")


# Example 3: Model-Level Validation
# ===================================

class DateRangeModel(BaseModel):
    """Validate relationships between fields"""
    
    start_date: date
    end_date: date
    
    @model_validator(mode='after')
    def check_dates(self):
        if self.end_date < self.start_date:
            raise ValueError('End date must be after start date')
        return self


class PasswordConfirmation(BaseModel):
    """Password confirmation validation"""
    
    password: str = Field(min_length=8)
    password_confirm: str
    
    @model_validator(mode='after')
    def passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError('Passwords do not match')
        return self


class PriceRangeFilter(BaseModel):
    """Price range filter validation"""
    
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    
    @model_validator(mode='after')
    def check_price_range(self):
        if self.min_price is not None and self.max_price is not None:
            if self.min_price > self.max_price:
                raise ValueError('min_price cannot be greater than max_price')
        return self


def demo_model_validation():
    """Demonstrate model-level validation"""
    print("\n=== Model-Level Validation ===\n")
    
    # Date range validation
    try:
        valid_range = DateRangeModel(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31)
        )
        print(f"✓ Valid date range: {valid_range.start_date} to {valid_range.end_date}")
    except ValidationError as e:
        print(f"✗ Failed: {e}")
    
    try:
        invalid_range = DateRangeModel(
            start_date=date(2024, 12, 31),
            end_date=date(2024, 1, 1)
        )
    except ValidationError as e:
        print(f"✓ Correctly rejected invalid range: {e.error_count()} error(s)")
    
    # Password confirmation
    try:
        valid_password = PasswordConfirmation(
            password="SecurePass123",
            password_confirm="SecurePass123"
        )
        print(f"✓ Passwords match")
    except ValidationError as e:
        print(f"✗ Failed: {e}")
    
    try:
        invalid_password = PasswordConfirmation(
            password="SecurePass123",
            password_confirm="DifferentPass456"
        )
    except ValidationError as e:
        print(f"✓ Correctly rejected mismatched passwords")


# Example 4: Conditional Validation
# ===================================

class ConditionalValidation(BaseModel):
    """Validation that depends on other field values"""
    
    shipping_method: str
    tracking_number: Optional[str] = None
    estimated_delivery: Optional[date] = None
    
    @model_validator(mode='after')
    def validate_shipping_details(self):
        if self.shipping_method in ['express', 'standard']:
            if not self.tracking_number:
                raise ValueError(f'{self.shipping_method} shipping requires tracking number')
            if not self.estimated_delivery:
                raise ValueError(f'{self.shipping_method} shipping requires estimated delivery')
        return self


class ConditionalFieldsModel(BaseModel):
    """Different validation rules based on user type"""
    
    user_type: str
    business_name: Optional[str] = None
    tax_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    @model_validator(mode='after')
    def validate_user_type_fields(self):
        if self.user_type == 'business':
            if not self.business_name:
                raise ValueError('Business users must provide business_name')
            if not self.tax_id:
                raise ValueError('Business users must provide tax_id')
        elif self.user_type == 'individual':
            if not self.first_name:
                raise ValueError('Individual users must provide first_name')
            if not self.last_name:
                raise ValueError('Individual users must provide last_name')
        return self


def demo_conditional_validation():
    """Demonstrate conditional validation"""
    print("\n=== Conditional Validation ===\n")
    
    # Shipping validation
    try:
        valid_shipping = ConditionalValidation(
            shipping_method='express',
            tracking_number='TRACK123',
            estimated_delivery=date.today()
        )
        print(f"✓ Valid express shipping with tracking")
    except ValidationError as e:
        print(f"✗ Failed: {e}")
    
    try:
        invalid_shipping = ConditionalValidation(
            shipping_method='express',
            tracking_number=None
        )
    except ValidationError as e:
        print(f"✓ Correctly rejected express without tracking")


# Example 5: Collection Validation
# ==================================

class CollectionValidation(BaseModel):
    """Validate collections with custom rules"""
    
    email_list: List[EmailStr] = Field(min_length=1, max_length=10)
    score_dict: Dict[str, int]
    unique_ids: List[int]
    
    @field_validator('unique_ids')
    @classmethod
    def check_unique(cls, v: List[int]) -> List[int]:
        if len(v) != len(set(v)):
            raise ValueError('IDs must be unique')
        return v
    
    @field_validator('score_dict')
    @classmethod
    def validate_scores(cls, v: Dict[str, int]) -> Dict[str, int]:
        for key, score in v.items():
            if not 0 <= score <= 100:
                raise ValueError(f'Score for {key} must be between 0 and 100')
        return v


def demo_collection_validation():
    """Demonstrate collection validation"""
    print("\n=== Collection Validation ===\n")
    
    try:
        valid_data = CollectionValidation(
            email_list=["user1@example.com", "user2@example.com"],
            score_dict={"math": 95, "english": 88, "science": 92},
            unique_ids=[1, 2, 3, 4, 5]
        )
        print(f"✓ Valid collection data")
    except ValidationError as e:
        print(f"✗ Failed: {e}")
    
    try:
        invalid_data = CollectionValidation(
            email_list=["user1@example.com"],
            score_dict={"math": 95},
            unique_ids=[1, 2, 2, 3]  # Duplicate
        )
    except ValidationError as e:
        print(f"✓ Correctly rejected duplicate IDs")


# Example 6: Constrained Types
# ==============================

class ConstrainedTypes(BaseModel):
    """Using Pydantic's constrained types"""
    
    # Constrained integers
    percentage: conint(ge=0, le=100)
    positive_int: conint(gt=0)
    
    # Constrained floats
    rating: confloat(ge=0.0, le=5.0)
    temperature: confloat(ge=-273.15)  # Absolute zero
    
    # Constrained strings
    username: constr(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$')
    hex_color: constr(pattern=r'^#[0-9A-Fa-f]{6}$')
    
    # Constrained lists
    top_5: conlist(str, min_length=1, max_length=5)


def demo_constrained_types():
    """Demonstrate constrained types"""
    print("\n=== Constrained Types ===\n")
    
    try:
        valid = ConstrainedTypes(
            percentage=75,
            positive_int=100,
            rating=4.5,
            temperature=25.0,
            username="john_doe",
            hex_color="#FF5733",
            top_5=["first", "second", "third"]
        )
        print(f"✓ Valid constrained data")
    except ValidationError as e:
        print(f"✗ Failed: {e}")


# Example 7: Error Handling
# ==========================

def demo_error_handling():
    """Demonstrate error handling"""
    print("\n=== Error Handling ===\n")
    
    class User(BaseModel):
        username: str = Field(min_length=3)
        email: EmailStr
        age: int = Field(ge=0, le=150)
    
    invalid_data = {
        "username": "ab",  # Too short
        "email": "invalid",  # Invalid email
        "age": 200  # Too high
    }
    
    try:
        User(**invalid_data)
    except ValidationError as e:
        print(f"Total errors: {e.error_count()}\n")
        
        # Iterate through errors
        for error in e.errors():
            print(f"Field: {error['loc']}")
            print(f"Type: {error['type']}")
            print(f"Message: {error['msg']}")
            print(f"Input: {error['input']}")
            print()
        
        # Get JSON format
        print("JSON format:")
        print(e.json(indent=2))


# Example 8: Reusable Validators
# ================================

def not_empty_string(v: str) -> str:
    """Reusable validator for non-empty strings"""
    if not v or not v.strip():
        raise ValueError('String cannot be empty')
    return v.strip()


def positive_number(v: float) -> float:
    """Reusable validator for positive numbers"""
    if v <= 0:
        raise ValueError('Must be positive')
    return v


class ReusableValidators(BaseModel):
    """Using reusable validators"""
    
    name: str
    description: str
    price: float
    quantity: float
    
    # Apply reusable validators
    _validate_name = field_validator('name')(not_empty_string)
    _validate_description = field_validator('description')(not_empty_string)
    _validate_price = field_validator('price')(positive_number)
    _validate_quantity = field_validator('quantity')(positive_number)


def demo_reusable_validators():
    """Demonstrate reusable validators"""
    print("\n=== Reusable Validators ===\n")
    
    try:
        product = ReusableValidators(
            name="Laptop",
            description="High-performance laptop",
            price=999.99,
            quantity=10
        )
        print(f"✓ Valid product: {product.name}")
    except ValidationError as e:
        print(f"✗ Failed: {e}")


# Main demonstration
# ===================

if __name__ == "__main__":
    """Run all validation demonstrations"""
    
    print("="*60)
    print("PYDANTIC VALIDATION EXAMPLES")
    print("="*60)
    
    demo_basic_validation()
    demo_custom_validation()
    demo_model_validation()
    demo_conditional_validation()
    demo_collection_validation()
    demo_constrained_types()
    demo_error_handling()
    demo_reusable_validators()
    
    print("\n" + "="*60)
    print("All validation demonstrations completed!")
    print("="*60 + "\n")
