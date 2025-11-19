# 🚀 Greenspot Grocer REST API

## Complete RESTful API for Business Analytics

### 🎯 **Quick Start**

1. **Install Dependencies**
   ```bash
   cd api
   pip install -r requirements.txt
   ```

2. **Start the API Server**
   ```bash
   python main.py
   # OR
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Access Interactive Documentation**
   - **Swagger UI**: http://localhost:8000/docs
   - **ReDoc**: http://localhost:8000/redoc
   - **API Root**: http://localhost:8000/

### 🔐 **Authentication**

#### **Get Access Token**
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "greenspot2025"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### **Use Token in Requests**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  "http://localhost:8000/api/v1/executive-summary"
```

---

## 📊 **API Endpoints**

### **🏢 Executive Summary**
`GET /api/v1/executive-summary`

**Returns:** Key business metrics and KPIs
```json
{
  "total_revenue": 217.94,
  "total_customers": 6,
  "total_transactions": 13,
  "average_order_value": 16.76,
  "top_product": "Ruby's Organic Kale",
  "top_category": "Produce"
}
```

### **📈 Product Performance**
`GET /api/v1/products/performance?limit=10`

**Parameters:**
- `limit`: Number of products to return (1-100)

**Returns:** Top performing products by revenue
```json
[
  {
    "product_id": 1,
    "product_name": "Ruby's Organic Kale",
    "total_revenue": 90.87,
    "units_sold": 13,
    "average_price": 6.99,
    "category": "Produce"
  }
]
```

### **👥 Customer Insights**
`GET /api/v1/customers/insights?limit=10`

**Returns:** Customer analytics with segmentation
```json
[
  {
    "customer_id": 1,
    "customer_name": "John Doe",
    "total_spent": 125.50,
    "transaction_count": 5,
    "average_order_value": 25.10,
    "customer_segment": "VIP"
  }
]
```

### **📦 Inventory Status**
`GET /api/v1/inventory/status`

**Returns:** Current inventory levels and reorder alerts
```json
[
  {
    "product_id": 1,
    "product_name": "Ruby's Organic Kale",
    "current_stock": 45,
    "reorder_level": 10,
    "needs_reorder": false,
    "vendor_name": "Ruby's Organic Farm"
  }
]
```

---

## 🛠️ **Development**

### **Project Structure**
```
api/
├── main.py              # FastAPI application
├── models.py            # Pydantic data models
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── README.md           # API documentation
├── Dockerfile          # Docker container
├── docker-compose.yml  # Multi-container setup
└── tests/              # API tests
    ├── test_auth.py
    ├── test_analytics.py
    └── test_endpoints.py
```

### **Environment Variables**
Create `.env` file:
```env
# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=Bigdata@1234
DB_NAME=greenspot_grocer
DB_PORT=3306

# JWT Configuration
SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False
```

### **Running Tests**
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest tests/

# Run with coverage
pytest --cov=. tests/
```

---

## 🐳 **Docker Deployment**

### **Build and Run**
```bash
# Build Docker image
docker build -t greenspot-api .

# Run container
docker run -p 8000:8000 greenspot-api

# OR use docker-compose
docker-compose up -d
```

### **Docker Compose Stack**
- **API Server**: FastAPI application
- **MySQL Database**: Database server
- **Nginx**: Reverse proxy and load balancer
- **Redis**: Caching layer (optional)

---

## 📚 **Integration Examples**

### **Python Client**
```python
import requests

# Authenticate
auth_response = requests.post(
    "http://localhost:8000/auth/login",
    json={"username": "admin", "password": "greenspot2025"}
)
token = auth_response.json()["access_token"]

# Get executive summary
headers = {"Authorization": f"Bearer {token}"}
summary = requests.get(
    "http://localhost:8000/api/v1/executive-summary",
    headers=headers
).json()

print(f"Total Revenue: ${summary['total_revenue']}")
```

### **JavaScript/Node.js**
```javascript
const axios = require('axios');

async function getAnalytics() {
  // Authenticate
  const auth = await axios.post('http://localhost:8000/auth/login', {
    username: 'admin',
    password: 'greenspot2025'
  });
  
  const token = auth.data.access_token;
  
  // Get product performance
  const products = await axios.get(
    'http://localhost:8000/api/v1/products/performance',
    { headers: { Authorization: `Bearer ${token}` } }
  );
  
  console.log('Top Products:', products.data);
}
```

### **Curl Examples**
```bash
# Health check (no auth required)
curl http://localhost:8000/health

# Get executive summary
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/executive-summary

# Get top 5 products
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/products/performance?limit=5"

# Get customer insights
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/customers/insights
```

---

## 🔧 **Configuration**

### **Database Settings**
Configure MySQL connection in `config.py`:
```python
DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',
    'database': 'greenspot_grocer',
    'port': 3306
}
```

### **CORS Configuration**
Allow specific origins in production:
```python
CORS_ORIGINS = [
    "https://yourdomain.com",
    "https://app.yourdomain.com",
    "http://localhost:3000"  # React dev server
]
```

### **JWT Security**
- Change default secret key in production
- Set appropriate token expiration time
- Consider refresh token implementation

---

## 📈 **Performance & Monitoring**

### **Metrics Endpoints**
- `/health` - Health check and database status
- `/metrics` - Prometheus metrics (if enabled)
- Performance monitoring with request/response times

### **Caching Strategy**
- Database query caching with Redis
- Response caching for frequently accessed data
- Connection pooling for improved performance

### **Rate Limiting**
- Implement rate limiting for production use
- API key-based quotas
- User-based request limits

---

## 🚀 **Production Deployment**

### **Recommended Stack**
- **Load Balancer**: Nginx or AWS ALB
- **Application Server**: Gunicorn + Uvicorn workers
- **Database**: MySQL 8.0+ with read replicas
- **Caching**: Redis for session and query caching
- **Monitoring**: Prometheus + Grafana
- **Logging**: Structured logging with ELK stack

### **Security Checklist**
- [ ] Change default credentials
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS with SSL certificates
- [ ] Implement proper CORS policies
- [ ] Add rate limiting and request validation
- [ ] Set up API key management
- [ ] Enable audit logging
- [ ] Regular security updates

---

## 🎯 **Use Cases**

### **Business Intelligence**
- Executive dashboards
- Automated reporting
- KPI monitoring
- Trend analysis

### **Application Integration**
- Mobile app backend
- Web application API
- Third-party integrations
- Microservices architecture

### **Data Analytics**
- Custom analytics tools
- Data visualization platforms
- Business intelligence software
- Reporting systems

---

## 📞 **Support**

### **Documentation**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **GitHub**: Repository with examples and issues

### **API Status**
- **Health Check**: `/health`
- **Version Info**: `/`
- **OpenAPI Spec**: `/openapi.json`

---

**🛒 Greenspot Grocer REST API - Powering modern business intelligence through RESTful data access!**