"""
Greenspot Grocer REST API - Final Working Version
"""

from fastapi import FastAPI, HTTPException, Depends, Security, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import jwt
import mysql.connector
from typing import Optional, List
import uvicorn
from pydantic import BaseModel, Field
from config import get_database_config, get_jwt_config, get_api_config, get_admin_credentials

# Load secure configuration
DATABASE_CONFIG = get_database_config()
JWT_CONFIG = get_jwt_config()
API_CONFIG = get_api_config()
ADMIN_CREDS = get_admin_credentials()

# JWT Configuration
SECRET_KEY = JWT_CONFIG['secret_key']
ALGORITHM = JWT_CONFIG['algorithm']
ACCESS_TOKEN_EXPIRE_MINUTES = JWT_CONFIG['access_token_expire_minutes']

# Pydantic Models
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class UserLogin(BaseModel):
    username: str
    password: str

class ExecutiveSummary(BaseModel):
    total_transactions: int
    total_revenue: float
    average_transaction_value: float
    unique_customers: int

class ProductPerformance(BaseModel):
    product_id: int
    product_name: str
    category_name: str
    transaction_count: int
    total_quantity_sold: int
    total_revenue: float
    average_unit_price: float

class CustomerInsight(BaseModel):
    customer_id: int
    customer_name: str
    total_spent: float
    transaction_count: int
    average_order_value: float

class InventoryStatus(BaseModel):
    product_id: int
    product_name: str
    category_name: str
    unit_price: float
    stock_quantity: int
    reorder_level: int
    stock_status: str

# FastAPI app
app = FastAPI(
    title=API_CONFIG['title'],
    description=API_CONFIG['description'],
    version=API_CONFIG['version'],
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=API_CONFIG['cors_origins'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Database functions
def get_db_connection():
    """Get database connection"""
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        return conn
    except mysql.connector.Error as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Database connection failed: {str(e)}"
        )

# Authentication functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        return username
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

# Routes
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Greenspot Grocer Analytics API",
        "version": API_CONFIG['version'],
        "status": "active",
        "security": "encrypted",
        "docs": "/docs",
        "health": "/health",
        "login": "/login"
    }

@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": f"disconnected: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }

@app.post("/login", response_model=Token, tags=["Authentication"])
async def login(user_credentials: UserLogin):
    """User login endpoint"""
    # Authentication using secure config (in production, use proper password hashing)
    if (user_credentials.username == ADMIN_CREDS['username'] and 
        user_credentials.password == ADMIN_CREDS['password']):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_credentials.username},
            expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

@app.get("/executive-summary", response_model=ExecutiveSummary, tags=["Analytics"])
async def get_executive_summary(current_user: str = Depends(verify_token)):
    """Get executive summary analytics"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT 
            COUNT(DISTINCT st.transaction_id) as total_transactions,
            ROUND(COALESCE(SUM(st.total_amount), 0), 2) as total_revenue,
            ROUND(COALESCE(AVG(st.total_amount), 0), 2) as average_transaction_value,
            COUNT(DISTINCT st.customer_id) as unique_customers
        FROM sales_transactions st
        """
        
        cursor.execute(query)
        result = cursor.fetchone()
        
        if result:
            return ExecutiveSummary(
                total_transactions=result[0] or 0,
                total_revenue=float(result[1]) if result[1] else 0.0,
                average_transaction_value=float(result[2]) if result[2] else 0.0,
                unique_customers=result[3] or 0
            )
        else:
            return ExecutiveSummary(
                total_transactions=0,
                total_revenue=0.0,
                average_transaction_value=0.0,
                unique_customers=0
            )
            
    except mysql.connector.Error as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Database query failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Unexpected error: {str(e)}"
        )
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

@app.get("/product-performance", response_model=List[ProductPerformance], tags=["Analytics"])
async def get_product_performance(
    limit: int = Query(10, ge=1, le=100, description="Number of products to return"),
    current_user: str = Depends(verify_token)
):
    """Get product performance analytics"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT 
            p.product_id,
            p.product_name,
            COALESCE(pc.category_name, 'Unknown') as category_name,
            COUNT(st.transaction_id) as transaction_count,
            COALESCE(SUM(st.quantity_sold), 0) as total_quantity_sold,
            ROUND(COALESCE(SUM(st.total_amount), 0), 2) as total_revenue,
            ROUND(COALESCE(AVG(st.unit_price), 0), 2) as average_unit_price
        FROM products p
        LEFT JOIN product_categories pc ON p.category_id = pc.category_id
        LEFT JOIN sales_transactions st ON p.product_id = st.product_id
        GROUP BY p.product_id, p.product_name, pc.category_name
        HAVING transaction_count > 0
        ORDER BY total_revenue DESC
        LIMIT %s
        """
        
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        
        products = []
        for row in results:
            products.append(ProductPerformance(
                product_id=row[0],
                product_name=row[1],
                category_name=row[2],
                transaction_count=row[3] or 0,
                total_quantity_sold=row[4] or 0,
                total_revenue=float(row[5]) if row[5] else 0.0,
                average_unit_price=float(row[6]) if row[6] else 0.0
            ))
        
        return products
        
    except mysql.connector.Error as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Database query failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Unexpected error: {str(e)}"
        )
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

@app.get("/customer-insights", response_model=List[CustomerInsight], tags=["Analytics"])
async def get_customer_insights(
    limit: int = Query(10, ge=1, le=100, description="Number of customers to return"),
    current_user: str = Depends(verify_token)
):
    """Get customer insights analytics"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT 
            c.customer_id,
            CONCAT(c.first_name, ' ', c.last_name) as customer_name,
            ROUND(COALESCE(SUM(st.total_amount), 0), 2) as total_spent,
            COUNT(DISTINCT st.transaction_id) as transaction_count,
            ROUND(COALESCE(AVG(st.total_amount), 0), 2) as average_order_value
        FROM customers c
        LEFT JOIN sales_transactions st ON c.customer_id = st.customer_id
        GROUP BY c.customer_id, c.first_name, c.last_name
        HAVING transaction_count > 0
        ORDER BY total_spent DESC
        LIMIT %s
        """
        
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        
        customers = []
        for row in results:
            customers.append(CustomerInsight(
                customer_id=row[0],
                customer_name=row[1],
                total_spent=float(row[2]) if row[2] else 0.0,
                transaction_count=row[3] or 0,
                average_order_value=float(row[4]) if row[4] else 0.0
            ))
        
        return customers
        
    except mysql.connector.Error as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Database query failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Unexpected error: {str(e)}"
        )
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

@app.get("/inventory-status", response_model=List[InventoryStatus], tags=["Analytics"])
async def get_inventory_status(current_user: str = Depends(verify_token)):
    """Get inventory status analytics"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT 
            p.product_id,
            p.product_name,
            COALESCE(pc.category_name, 'Unknown') as category_name,
            p.unit_price,
            COALESCE(i.quantity_available, 0) as stock_quantity,
            COALESCE(i.reorder_level, 0) as reorder_level,
            CASE 
                WHEN COALESCE(i.quantity_available, 0) <= COALESCE(i.reorder_level, 0) THEN 'Low Stock'
                WHEN COALESCE(i.quantity_available, 0) <= COALESCE(i.reorder_level, 0) * 2 THEN 'Medium Stock'
                ELSE 'High Stock'
            END as stock_status
        FROM products p
        LEFT JOIN product_categories pc ON p.category_id = pc.category_id
        LEFT JOIN inventory i ON p.product_id = i.product_id
        ORDER BY p.product_name
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        inventory = []
        for row in results:
            inventory.append(InventoryStatus(
                product_id=row[0],
                product_name=row[1],
                category_name=row[2],
                unit_price=float(row[3]) if row[3] else 0.0,
                stock_quantity=row[4] or 0,
                reorder_level=row[5] or 0,
                stock_status=row[6]
            ))
        
        return inventory
        
    except mysql.connector.Error as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Database query failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Unexpected error: {str(e)}"
        )
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    print("Starting Greenspot Grocer Analytics API (Secure)")
    print(f"Navigate to http://{API_CONFIG['host']}:{API_CONFIG['port']}/docs for interactive documentation")
    print("Database password encrypted for security")
    uvicorn.run(
        app, 
        host=API_CONFIG['host'], 
        port=API_CONFIG['port'], 
        log_level="info",
        reload=False
    )