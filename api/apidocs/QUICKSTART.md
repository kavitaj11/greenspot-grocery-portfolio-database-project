# 🚀 Greenspot Grocer REST API - Complete Implementation

## 🎯 Overview
This REST API provides comprehensive analytics endpoints for the Greenspot Grocer database, featuring JWT authentication, interactive documentation, and Docker deployment capabilities.

## 📋 Features
- ✅ JWT Authentication with Bearer tokens
- ✅ **Encrypted Database Password** for enhanced security
- ✅ Environment-based configuration
- ✅ Executive Summary Analytics
- ✅ Product Performance Metrics
- ✅ Customer Insights
- ✅ Inventory Status Monitoring
- ✅ Interactive API Documentation (Swagger UI)
- ✅ CORS Support for web applications
- ✅ Docker deployment ready
- ✅ Comprehensive error handling

## 🛠️ Quick Start

### 1. Start the API Server
```bash
cd api
python main.py
```

The server will start on `http://localhost:8000`

### 2. Test the API
Open a new terminal and run:
```bash
cd api
python tests/final_test.py
```

### 3. Interactive Documentation
Visit `http://localhost:8000/docs` in your browser for the interactive Swagger UI documentation.

## 🔐 Security & Authentication

### Database Security
- **Database password is encrypted** using Fernet symmetric encryption
- Master key can be customized via environment variable `GREENSPOT_MASTER_KEY`
- Password stored encrypted in `secure_config.py`

### API Authentication
- **Username:** `admin`
- **Password:** `admin123`
- **Token expires:** 30 minutes

### Password Management
```bash
# Encrypt a new password
python utils/password_manager.py encrypt

# Change database password
python utils/password_manage.py change-db

# Test encryption/decryption
python utils/password_manage.py test
```

## 📊 API Endpoints

### System Endpoints
- `GET /` - Root endpoint with API information
- `GET /health` - Health check and database status
- `POST /login` - User authentication

### Analytics Endpoints (Require Authentication)
- `GET /executive-summary` - Business overview metrics
- `GET /product-performance?limit=10` - Top performing products
- `GET /customer-insights?limit=10` - Customer spending analysis  
- `GET /inventory-status` - Current stock levels and reorder alerts

## 🗄️ Database Schema
The API works with the following tables:
- `sales_transactions` - Transaction records
- `products` - Product catalog
- `customers` - Customer information
- `product_categories` - Product categorization
- `inventory` - Stock levels and reorder points

## 📝 Usage Examples

### 1. Get Authentication Token
```python
import requests

login_data = {"username": "admin", "password": "admin123"}
response = requests.post("http://localhost:8000/login", json=login_data)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
```

### 2. Get Executive Summary
```python
response = requests.get("http://localhost:8000/executive-summary", headers=headers)
summary = response.json()
print(f"Total Revenue: ${summary['total_revenue']:,.2f}")
```

### 3. Get Top Products
```python
response = requests.get("http://localhost:8000/product-performance?limit=5", headers=headers)
products = response.json()
for product in products:
    print(f"{product['product_name']}: ${product['total_revenue']:,.2f}")
```

## 🐳 Docker Deployment
```bash
# Build the image
docker build -t greenspot-api .

# Run with docker-compose
docker-compose up -d
```

## 📁 Project Structure
```
api/
├── main.py                    # Main API application (RECOMMENDED)
├── config/                    # 📁 Configuration files
│   ├── __init__.py           # 🔐 Encrypted configuration
│   ├── .env.template         # Environment variables template
│   └── legacy_config.py      # Backward compatibility
├── utils/                     # 📁 Utility functions
│   ├── __init__.py           # Utils package
│   ├── encryption_utils.py   # 🔐 Encryption utilities
│   └── password_manager_updated.py # 🔐 Password management tool
├── main_fixed.py              # Alternative version with schema fixes
├── simple_api.py              # Simplified version for testing
├── final_test.py              # Comprehensive test suite
├── models.py                  # Pydantic data models
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose setup
├── README.md                  # API documentation
└── test_api.py               # Basic test script
```

## 🔧 Configuration

### Default Settings
Database settings are securely configured:
- **Host:** localhost
- **User:** root
- **Password:** encrypted (`devpwd` by default)
- **Database:** greenspot_grocer
- **Port:** 3306

### Environment Variables
Copy `config/.env.template` to `config/.env` and customize:
```bash
cp config/.env.template config/.env
```

### Security Files
- `config/__init__.py` - Encrypted configuration
- `utils/encryption_utils.py` - Encryption/decryption utilities
- `utils/password_manager_updated.py` - Password management tool
- `config/legacy_config.py` - Backward compatibility

## 🎯 Next Steps
1. **Start the API:** Run `python main.py`
2. **Test endpoints:** Run `python final_test.py`
3. **Explore docs:** Visit `http://localhost:8000/docs`
4. **Integrate:** Use the API endpoints in your applications

## 🚨 Troubleshooting
- **Port conflicts:** Change `API_PORT` in `config/.env` or `config/__init__.py`
- **Database errors:** Verify MySQL is running and credentials are correct
- **Import errors:** Ensure all requirements are installed: `pip install -r requirements.txt`
- **Encryption errors:** Verify `cryptography` package is installed
- **Password issues:** Use `python utils/password_manager_updated.py change-db` to update password
- **Config errors:** Check `config/__init__.py` and ensure encrypted password is valid
- **Path issues:** Ensure you're running commands from the `api/` directory

## 📈 Sample Response - Executive Summary
```json
{
  "total_transactions": 13,
  "total_revenue": 217.94,
  "average_transaction_value": 16.76,
  "unique_customers": 6
}
```

---
**🎉 Your Greenspot Grocer REST API is ready to serve analytics data to any application!**
