# 🛒 Greenspot Grocer Analytics API

> **Professional REST API with encrypted security and organized structure**

## 🎯 Overview

The Greenspot Grocer Analytics API is a comprehensive, production-ready REST API that provides secure access to business analytics data. Built with FastAPI, featuring JWT authentication, encrypted database passwords, and a professionally organized codebase.

## 🚀 Quick Start

```bash
# Start the API
python main.py

# Run comprehensive tests
python tests/run_all_tests.py

# Access interactive documentation
# Visit: http://localhost:8000/docs
```

## 📁 Project Structure

```
api/
├── 🚀 main.py                     # Main API application
├── 📁 config/                     # Configuration management
│   ├── __init__.py               # 🔐 Encrypted configuration
│   ├── .env.template             # Environment variables
│   └── legacy_config.py          # Backward compatibility
├── 📁 utils/                      # Utility functions
│   ├── encryption_utils.py       # 🔐 Encryption tools
│   └── password_manager_updated.py # 🔐 Password management
├── 📁 tests/                      # Testing suite
│   ├── run_all_tests.py          # 🧪 Comprehensive test runner
│   ├── final_test.py             # Complete API tests
│   ├── db_test.py                # Database tests
│   └── [other test files]
├── 📁 apidocs/                    # Documentation
│   ├── index.md                  # 📚 Documentation index
│   ├── QUICKSTART.md             # Quick start guide
│   ├── SECURITY.md               # Security documentation
│   └── [other docs]
└── 📄 [other API files]
```

## 🔐 Security Features

- **Encrypted Database Passwords** using Fernet symmetric encryption
- **JWT Authentication** with configurable expiration
- **Environment-based Configuration** for production deployment
- **Professional Security Practices** following industry standards

## 📊 API Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/` | GET | API information | No |
| `/health` | GET | Health check | No |
| `/login` | POST | Authentication | No |
| `/executive-summary` | GET | Business metrics | Yes |
| `/product-performance` | GET | Product analytics | Yes |
| `/customer-insights` | GET | Customer analytics | Yes |
| `/inventory-status` | GET | Inventory status | Yes |

## 🛠️ Management Tools

### Password Management
```bash
# Encrypt new password
python utils/password_manager_updated.py encrypt

# Change database password
python utils/password_manager_updated.py change-db

# Test encryption
python utils/password_manager_updated.py test
```

### Testing
```bash
# Run all tests
python tests/run_all_tests.py

# Run specific test
python tests/final_test.py
```

### Configuration
```bash
# Copy environment template
cp config/.env.template config/.env

# Edit configuration
# Modify config/.env as needed
```

## 📚 Documentation

- **[📖 Full Documentation](apidocs/index.md)** - Complete documentation index
- **[🚀 Quick Start Guide](apidocs/QUICKSTART.md)** - Get started quickly
- **[🔐 Authentication Guide](apidocs/AUTHENTICATION.md)** - JWT authentication and security
- **[🛡️ Security Guide](apidocs/SECURITY.md)** - Security features and setup
- **[📁 Organization Guide](apidocs/REORGANIZATION.md)** - Project structure details

## 🧪 Testing

The API includes a comprehensive testing suite:

```bash
# Run all tests with detailed output
cd tests
python run_all_tests.py
```

Test categories:
- **Database Tests** - Connection and schema validation
- **API Tests** - Endpoint functionality and responses
- **Security Tests** - Authentication and encryption
- **Integration Tests** - Complete workflow testing

## ⚙️ Configuration

### Environment Variables
Copy `config/.env.template` to `config/.env` and customize:

```bash
# Database
DB_HOST=localhost
DB_USER=root
DB_NAME=greenspot_grocer

# API
API_HOST=127.0.0.1
API_PORT=8000

# Security
JWT_SECRET_KEY=your_secret_key
GREENSPOT_MASTER_KEY=your_encryption_key
```

### Database Requirements
- MySQL 5.7+ or 8.0+
- Database: `greenspot_grocer`
- Tables: `sales_transactions`, `products`, `customers`, `product_categories`, `inventory`

## 🚢 Deployment

### Local Development
```bash
python main.py
```

### Docker (if configured)
```bash
docker-compose up -d
```

### Production
1. Set environment variables securely
2. Use strong passwords and encryption keys
3. Configure proper CORS origins
4. Enable HTTPS/SSL
5. Set up monitoring and logging

## 🔧 Requirements

```bash
pip install -r requirements.txt
```

Key dependencies:
- FastAPI 0.104+
- uvicorn[standard] 0.24+
- mysql-connector-python 8.2+
- cryptography 3.4+
- PyJWT 2.8+

## 📈 Performance

The API is designed for production use with:
- **Async request handling** via FastAPI
- **Connection pooling** for database efficiency
- **JWT caching** for authentication performance
- **Optimized queries** for analytics endpoints

## 🤝 Contributing

1. Follow the organized project structure
2. Add tests for new features
3. Update documentation
4. Use the provided utility tools
5. Maintain security standards

## 📄 License

This project is part of the Greenspot Grocer portfolio project.

---

## 🎉 Ready to Go!

Your professionally organized Greenspot Grocer API is ready for development and production use!

- **Secure** - Encrypted passwords and JWT authentication
- **Professional** - Organized structure with proper separation of concerns
- **Tested** - Comprehensive testing suite included
- **Documented** - Complete documentation and guides
- **Production-Ready** - Environment configuration and deployment support

**Start exploring:** `python main.py` and visit `http://localhost:8000/docs`