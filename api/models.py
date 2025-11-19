"""
Pydantic models for Greenspot Grocer REST API
Data models for request/response validation and serialization
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum

# Authentication Models
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None

class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=6, description="Password")

class User(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

# Analytics Response Models
class ExecutiveSummary(BaseModel):
    total_revenue: float = Field(..., description="Total revenue in dollars", example=1234.56)
    total_customers: int = Field(..., description="Total number of customers", example=45)
    total_transactions: int = Field(..., description="Total number of transactions", example=123)
    average_order_value: float = Field(..., description="Average order value", example=27.89)
    top_product: str = Field(..., description="Best selling product by revenue", example="Ruby's Organic Kale")
    top_category: str = Field(..., description="Best performing category", example="Produce")

class ProductPerformance(BaseModel):
    product_id: int = Field(..., description="Product ID", example=1)
    product_name: str = Field(..., description="Product name", example="Ruby's Organic Kale")
    total_revenue: float = Field(..., description="Total revenue from this product", example=567.89)
    units_sold: int = Field(..., description="Total units sold", example=34)
    average_price: float = Field(..., description="Average selling price", example=16.70)
    category: str = Field(..., description="Product category", example="Produce")

class CustomerSegment(str, Enum):
    VIP = "VIP"
    REGULAR = "Regular" 
    OCCASIONAL = "Occasional"
    NEW = "New"

class CustomerInsight(BaseModel):
    customer_id: int = Field(..., description="Customer ID", example=1)
    customer_name: str = Field(..., description="Customer full name", example="John Doe")
    total_spent: float = Field(..., description="Total amount spent", example=234.56)
    transaction_count: int = Field(..., description="Number of transactions", example=8)
    average_order_value: float = Field(..., description="Average order value", example=29.32)
    customer_segment: CustomerSegment = Field(..., description="Customer segment classification")

class SalesMetrics(BaseModel):
    date: str = Field(..., description="Date in YYYY-MM-DD format", example="2025-11-18")
    daily_revenue: float = Field(..., description="Revenue for the day", example=123.45)
    transaction_count: int = Field(..., description="Number of transactions", example=5)
    units_sold: int = Field(..., description="Total units sold", example=23)

class InventoryStatus(BaseModel):
    product_id: int = Field(..., description="Product ID", example=1)
    product_name: str = Field(..., description="Product name", example="Ruby's Organic Kale")
    current_stock: int = Field(..., description="Current stock quantity", example=15)
    reorder_level: int = Field(..., description="Reorder threshold", example=10)
    needs_reorder: bool = Field(..., description="Whether product needs reordering", example=False)
    vendor_name: str = Field(..., description="Vendor name", example="Ruby's Organic Farm")

# Detailed Models
class VendorInfo(BaseModel):
    name: str = Field(..., description="Vendor name")
    contact: Optional[str] = Field(None, description="Contact information")

class SalesStats(BaseModel):
    total_sold: int = Field(..., description="Total units sold")
    total_revenue: float = Field(..., description="Total revenue generated")

class ProductDetails(BaseModel):
    product_id: int
    product_name: str
    category: str
    price: float
    stock_quantity: int
    reorder_level: int
    vendor: VendorInfo
    sales_stats: SalesStats

class CategoryPerformance(BaseModel):
    category_name: str = Field(..., description="Category name", example="Produce")
    product_count: int = Field(..., description="Number of products in category", example=5)
    total_revenue: float = Field(..., description="Total revenue from category", example=456.78)
    units_sold: int = Field(..., description="Total units sold in category", example=67)
    average_price: float = Field(..., description="Average price in category", example=6.81)

# Request Models
class DateRange(BaseModel):
    start_date: date = Field(..., description="Start date for analysis")
    end_date: date = Field(..., description="End date for analysis")

class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=100, description="Items per page")

# Response Models
class APIResponse(BaseModel):
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

class PaginatedResponse(BaseModel):
    items: List[Any] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")

# Error Models
class ErrorDetail(BaseModel):
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    field: Optional[str] = Field(None, description="Field that caused the error")

class ErrorResponse(BaseModel):
    error: bool = Field(True, description="Indicates an error occurred")
    message: str = Field(..., description="Error message")
    details: Optional[List[ErrorDetail]] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")

# Health Check Models
class HealthStatus(BaseModel):
    status: str = Field(..., description="Overall health status", example="healthy")
    database: str = Field(..., description="Database connection status", example="connected")
    timestamp: datetime = Field(..., description="Health check timestamp")
    version: str = Field(..., description="API version", example="1.0.0")

# Analytics Filter Models
class ProductFilter(BaseModel):
    category_id: Optional[int] = Field(None, description="Filter by category ID")
    vendor_id: Optional[int] = Field(None, description="Filter by vendor ID")
    min_price: Optional[float] = Field(None, ge=0, description="Minimum price filter")
    max_price: Optional[float] = Field(None, ge=0, description="Maximum price filter")
    in_stock_only: bool = Field(False, description="Show only products in stock")

class CustomerFilter(BaseModel):
    segment: Optional[CustomerSegment] = Field(None, description="Filter by customer segment")
    min_spent: Optional[float] = Field(None, ge=0, description="Minimum amount spent")
    min_transactions: Optional[int] = Field(None, ge=1, description="Minimum number of transactions")

class SalesFilter(BaseModel):
    start_date: Optional[date] = Field(None, description="Start date for sales data")
    end_date: Optional[date] = Field(None, description="End date for sales data")
    category_id: Optional[int] = Field(None, description="Filter by product category")
    customer_id: Optional[int] = Field(None, description="Filter by customer")

# Configuration Models
class APIConfig(BaseModel):
    title: str = "Greenspot Grocer Analytics API"
    description: str = "REST API for Greenspot Grocer business analytics"
    version: str = "1.0.0"
    debug: bool = False
    cors_origins: List[str] = ["*"]
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30

class DatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = 3306
    username: str
    password: str
    database: str
    charset: str = "utf8mb4"