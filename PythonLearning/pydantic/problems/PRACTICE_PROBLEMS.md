# Pydantic Practice Problems

This file contains practice exercises to help you master Pydantic. Solutions are provided in the `solutions` folder.

---

## Beginner Level

### Problem 1: Basic User Model

Create a `User` model with the following fields:

- `id`: integer (must be positive)
- `username`: string (3-20 characters, alphanumeric + underscore only)
- `email`: valid email
- `age`: integer (0-150)
- `is_active`: boolean (default: True)

Test with valid and invalid data.

---

### Problem 2: Product with Validation

Create a `Product` model with:

- `name`: string (1-100 characters)
- `price`: float (must be positive)
- `quantity`: integer (non-negative)
- `description`: optional string (max 500 characters)

Add a custom validator that:

- Capitalizes the product name
- Ensures price has maximum 2 decimal places

---

### Problem 3: Address Model

Create an `Address` model with:

- `street`: string
- `city`: string
- `state`: string (2 characters, uppercase)
- `zip_code`: string (format: XXXXX or XXXXX-XXXX)
- `country`: string (default: "USA")

Implement validators to:

- Convert state to uppercase
- Validate zip code format

---

### Problem 4: Date Range Validation

Create a `DateRange` model with:

- `start_date`: date
- `end_date`: date

Add a model validator to ensure `end_date` is after `start_date`.

---

### Problem 5: Simple JSON Parsing

Create a `Book` model with:

- `title`: string
- `author`: string
- `year`: integer
- `isbn`: string

Parse the following JSON and create Book instances:

```json
[
  {
    "title": "1984",
    "author": "George Orwell",
    "year": 1949,
    "isbn": "978-0451524935"
  },
  {
    "title": "To Kill a Mockingbird",
    "author": "Harper Lee",
    "year": 1960,
    "isbn": "978-0061120084"
  }
]
```

---

## Intermediate Level

### Problem 6: Nested Models

Create models for a blog system:

- `Author` model: id, name, email
- `Comment` model: id, author (Author), content, created_at
- `Post` model: id, title, content, author (Author), comments (list of Comment), published_at

Create sample data with nested structures.

---

### Problem 7: Password Validation

Create a `UserRegistration` model with:

- `username`: string (3-20 characters)
- `email`: valid email
- `password`: string (min 8 characters)
- `password_confirm`: string

Implement validators for password that check:

- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character
- Passwords match

---

### Problem 8: Order System

Create models for an order system:

- `OrderItem`: product_id (int), quantity (int, 1-100), unit_price (float)
- `Order`: order_id (int), items (list of OrderItem, min 1 item), customer_email

Add computed fields:

- `OrderItem.subtotal`: quantity × unit_price
- `Order.total_amount`: sum of all item subtotals
- `Order.total_items`: sum of all quantities

---

### Problem 9: Configuration from .env

Create a `Settings` model using `pydantic-settings` that reads:

- `APP_NAME`: string (default: "MyApp")
- `DEBUG`: boolean (default: False)
- `DATABASE_URL`: string (required)
- `SECRET_KEY`: string (required, min 32 characters)
- `MAX_CONNECTIONS`: integer (1-100, default: 10)

Create a sample `.env` file and load settings.

---

### Problem 10: Discriminated Unions

Create models for different payment methods:

- `CreditCard`: type="credit_card", card_number, expiry, cvv
- `PayPal`: type="paypal", email
- `BankTransfer`: type="bank_transfer", account_number, routing_number

Create a `Payment` model that uses discriminated unions based on `type`.

---

## Advanced Level

### Problem 11: E-commerce System

Build a complete e-commerce system with:

Models:

- `User`: id, username, email, role (customer/seller/admin)
- `Product`: id, name, price, seller_id, category, stock_quantity
- `CartItem`: product_id, quantity
- `Cart`: user_id, items (list of CartItem)
- `Order`: id, user_id, items, total, status, created_at

Requirements:

- Validate that products have sufficient stock
- Calculate cart total with applied discounts
- Generate order from cart
- Track order status (pending, processing, shipped, delivered)

---

### Problem 12: API Response Models

Create generic response models:

- `PaginationMeta`: page, page_size, total_items, total_pages
- `ApiResponse[T]`: success, data (generic type T), message, timestamp
- `ErrorResponse`: success (False), errors (list of error details), message

Implement for:

- List users with pagination
- Single user response
- Error response with multiple validation errors

---

### Problem 13: Tree Structure

Create a `TreeNode` model for hierarchical data:

- `id`: integer
- `name`: string
- `value`: optional float
- `children`: list of TreeNode (self-referencing)

Implement methods:

- `find_node(id)`: Find node by ID
- `total_value`: Calculate sum of node value + all descendants
- `depth`: Calculate depth of tree
- `is_leaf`: Check if node has no children

Create a tree structure representing a company organization chart.

---

### Problem 14: Data Validation Pipeline

Create models for an ETL pipeline that validates CSV data:

Input: CSV with columns: name, email, age, salary, department
Create:

- `RawRecord`: Parse raw CSV data
- `ValidatedRecord`: Validated and cleaned data
- `TransformationResult`: success/failure stats

Implement:

- Validators for each field
- Error collection (don't stop on first error)
- Statistics (total records, valid, invalid, errors)
- Export valid records to JSON

---

### Problem 15: Multi-Model Form

Create models for a job application form:

- `PersonalInfo`: name, email, phone, address
- `Education`: degree, school, graduation_year
- `Experience`: company, position, start_date, end_date, description
- `JobApplication`: personal_info, education (list), experience (list), resume_url, cover_letter

Requirements:

- Validate all nested models
- Ensure at least one education entry
- Validate date ranges for experience
- Export to JSON schema for frontend forms

---

### Problem 16: Settings with Nested Configuration

Create a comprehensive settings model:

```python
- AppSettings:
  - app_name: str
  - debug: bool
  - database: DatabaseSettings
    - host, port, username, password, database
    - pool_size, timeout
  - redis: RedisSettings
    - host, port, db, password
  - email: EmailSettings
    - smtp_host, smtp_port, username, password
    - from_email, from_name
  - security: SecuritySettings
    - secret_key, algorithm, token_expire_minutes
```

Load from `.env` file with nested prefixes (e.g., `DATABASE__HOST`).

---

### Problem 17: Polymorphic Models

Create models for different notification types:

Base: `Notification`

- id, user_id, created_at, is_read

Types:

- `EmailNotification`: subject, body, recipients
- `SMSNotification`: phone_number, message
- `PushNotification`: title, body, device_token, badge
- `InAppNotification`: title, message, action_url

Requirements:

- Use discriminated unions
- Serialize/deserialize from database
- Create factory method to build appropriate type

---

### Problem 18: Validation with External Data

Create models that validate against external data:

- `Product`: id, name, category_id
- Validate `category_id` exists in allowed categories (from external API/database)
- Validate `sku` is unique (check against database)
- Validate `price` is within category-specific min/max range

Implement async validators that check external systems.

---

### Problem 19: Complex Business Rules

Create models for a booking system:

- `TimeSlot`: start_time, end_time, capacity
- `Booking`: user_id, time_slot, number_of_people, status
- `BookingRules`: Validation rules

Implement validators for:

- No overlapping bookings for same user
- Capacity not exceeded
- Booking at least 24 hours in advance
- Maximum 7 days in advance
- Cancellation only if > 2 hours before start

---

### Problem 20: Performance Optimization

Given a large dataset (100k+ records), create an optimized validation pipeline:

Requirements:

- Validate CSV with 100,000+ rows
- Measure validation time
- Implement batch processing
- Collect all errors (don't stop on first error)
- Generate validation report
- Compare performance with/without `validate_assignment`

Create benchmarks for:

- Single record validation
- Batch validation (1000 records at a time)
- Full dataset validation

---

## Challenge Problems

### Challenge 1: Complete REST API

Build a complete REST API with FastAPI and Pydantic for a task management system:

Features:

- User authentication (register, login)
- CRUD operations for tasks
- Task categories and tags
- Task assignments
- Due dates and reminders
- File attachments
- Activity logs
- Search and filtering
- Pagination

Use proper request/response models, validation, and error handling.

---

### Challenge 2: Configuration Management System

Build a configuration management system:

Features:

- Multiple environments (dev, staging, prod)
- Environment-specific overrides
- Secrets management
- Configuration validation
- Hot reload
- Configuration versioning
- Audit logging

Use Pydantic for all configuration validation.

---

### Challenge 3: Data Migration Tool

Create a data migration tool that:

- Reads data from multiple sources (CSV, JSON, XML, databases)
- Validates using Pydantic models
- Transforms data (field mapping, type conversion)
- Validates business rules
- Generates migration report
- Rollback on errors
- Handles large datasets efficiently

---

## Testing Your Solutions

For each problem, ensure you:

1. ✅ Create appropriate models
2. ✅ Implement all validators
3. ✅ Test with valid data
4. ✅ Test with invalid data
5. ✅ Handle ValidationError properly
6. ✅ Export to JSON/dict as needed
7. ✅ Write clear documentation

---

## Tips for Success

1. **Read the Pydantic docs**: Always refer to official documentation
2. **Start simple**: Begin with basic models, add complexity gradually
3. **Test thoroughly**: Test both valid and invalid data
4. **Use type hints**: Proper type hints improve validation
5. **Custom validators**: Don't hesitate to write custom validators for complex rules
6. **Error handling**: Always handle ValidationError gracefully
7. **Performance**: Be mindful of validation performance with large datasets
8. **Documentation**: Document your models and validators
9. **Reusability**: Create reusable validators and base models
10. **Real-world scenarios**: Think about how your models would work in production

---

## Resources

- Official Pydantic Docs: https://docs.pydantic.dev/
- FastAPI + Pydantic: https://fastapi.tiangolo.com/
- Type Hints: https://docs.python.org/3/library/typing.html
- JSON Schema: https://json-schema.org/

---

Good luck with your practice! 🚀
