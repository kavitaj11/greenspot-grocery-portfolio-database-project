# 🛒 Greenspot Grocer Database Project

## Project Overview

**Greenspot Grocer** is a comprehensive database transformation project that converts a flat CSV dataset into a fully normalized, scalable relational database system. This project demonstrates advanced database design principles, ETL automation, and data analytics capabilities.

### 🎯 Project Objectives

This project transforms Greenspot Grocer's legacy spreadsheet data into:
- **Fully normalized relational database** (3rd Normal Form)
- **Scalable MySQL schema** with proper constraints and relationships  
- **Automated Python ETL pipeline** for data transformation and loading
- **Comprehensive validation and analytics** queries
- **Production-ready database structure** supporting inventory, sales, and vendor management

---

## 🏗️ Database Architecture

### Normalized Schema Design

The database follows **Third Normal Form (3NF)** principles to eliminate redundancy and ensure data integrity:

#### Core Tables:
1. **`product_categories`** - Product classification system
2. **`vendors`** - Supplier information and contacts
3. **`products`** - Master product catalog with specifications
4. **`customers`** - Customer registry (expandable)
5. **`inventory`** - Real-time stock levels and reorder points
6. **`purchase_orders`** - Procurement transactions from vendors
7. **`sales_transactions`** - Customer purchase history

#### Key Relationships:
- **Products ↔ Categories**: Many-to-One (products belong to categories)
- **Products ↔ Vendors**: Many-to-One (products have primary vendors)
- **Products ↔ Inventory**: One-to-One (each product has current stock)
- **Products ↔ Sales**: One-to-Many (products can have multiple sales)
- **Products ↔ Purchases**: One-to-Many (products can have multiple purchase orders)
- **Customers ↔ Sales**: One-to-Many (customers can make multiple purchases)

### Benefits of Normalized Design:
✅ **Eliminates data redundancy** - Vendor information stored once  
✅ **Maintains referential integrity** - Foreign key constraints prevent orphaned records  
✅ **Supports scalability** - Easy addition of new products, vendors, customers  
✅ **Enables advanced analytics** - Proper structure for complex reporting  
✅ **Improves data quality** - Validation rules and constraints  

---

## 📁 Project Structure

```
Greenspot-Grocery-Portfolio-Project/
├── 📄 GreenspotDataset.csv          # Original dataset
├── 📁 sql/                          # Database scripts
│   ├── create_schema.sql           # Complete database schema
│   ├── validation_queries.sql      # Data integrity validation
│   └── analytics_queries.sql       # Business analytics queries
├── 📁 python/                       # ETL automation
│   ├── greenspot_etl.py           # Main ETL script
│   ├── config.py                  # Configuration settings
│   └── requirements.txt           # Python dependencies
├── 📁 docs/                        # Documentation
│   └── schema_design.md           # Detailed schema documentation
└── 📄 README.md                    # This file
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **MySQL Server 8.0+** or MariaDB 10.3+
- **Python 3.8+** 
- **Git** (for cloning repository)

### 1. Database Setup

```sql
-- Connect to MySQL as root or privileged user
mysql -u root -p

-- Create database and user (optional)
CREATE DATABASE greenspot_grocer;
CREATE USER 'greenspot_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON greenspot_grocer.* TO 'greenspot_user'@'localhost';
FLUSH PRIVILEGES;
```

### 2. Schema Creation

```bash
# Run the schema creation script
mysql -u root -p greenspot_grocer < sql/create_schema.sql
```

### 3. Python Environment Setup

```bash
# Navigate to python directory
cd python

# Create virtual environment (recommended)
python -m venv greenspot_env
source greenspot_env/bin/activate  # On Windows: greenspot_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Database Connection

Edit `python/config.py` with your database credentials:

```python
DATABASE_CONFIG = {
    'host': 'localhost',
    'database': 'greenspot_grocer',
    'user': 'your_username',      # Update this
    'password': 'your_password',  # Update this
    'charset': 'utf8mb4',
    'use_unicode': True,
    'autocommit': False
}
```

### 5. Run ETL Process

```bash
# Execute the ETL script
python greenspot_etl.py
```

### 6. Validate Results

```bash
# Run validation queries
mysql -u root -p greenspot_grocer < ../sql/validation_queries.sql

# Run analytics queries  
mysql -u root -p greenspot_grocer < ../sql/analytics_queries.sql
```

---

## 📊 Data Transformation Details

### Original CSV Issues Addressed:

| Issue | Solution |
|-------|----------|
| **Denormalized structure** | Separated into 7 normalized tables |
| **Duplicate vendor info** | Extracted to dedicated `vendors` table |
| **Mixed transaction types** | Split into `purchase_orders` and `sales_transactions` |
| **Inconsistent units** | Standardized in `products.unit_of_measure` |
| **Data quality issues** | Validation rules and data cleaning |
| **No referential integrity** | Foreign key constraints implemented |

### ETL Process Flow:

1. **Extract**: Read CSV with pandas, handle missing values
2. **Transform**: 
   - Parse and normalize vendor addresses
   - Standardize product units and location codes  
   - Separate purchase vs. sales transactions
   - Generate surrogate keys where needed
3. **Load**: Insert data maintaining referential integrity order
4. **Validate**: Run integrity checks and business rule validation

---

## 🔍 Key Features

### Advanced Database Features:
- **Generated columns** for calculated fields (total_cost, total_amount)
- **Comprehensive indexes** for query performance
- **Views** for common business queries
- **Constraints** for data integrity
- **Triggers** ready for audit trails (expandable)

### ETL Features:
- **Robust error handling** with detailed logging
- **Data validation** and cleaning
- **Flexible configuration** via config files  
- **Batch processing** for large datasets
- **Rollback capability** on failures

### Analytics Capabilities:
- **Sales performance** tracking by product/category
- **Inventory management** with reorder alerts  
- **Vendor performance** analysis
- **Financial reporting** with profit margins
- **Customer analytics** and purchase patterns
- **Trend analysis** and growth metrics

---

## 📈 Sample Queries & Use Cases

### Inventory Management
```sql
-- Low stock alert
SELECT p.product_name, i.quantity_on_hand, i.reorder_level
FROM products p
JOIN inventory i ON p.product_id = i.product_id
WHERE i.quantity_on_hand <= i.reorder_level;
```

### Sales Analytics  
```sql
-- Top selling products by revenue
SELECT p.product_name, SUM(st.total_amount) as revenue
FROM products p
JOIN sales_transactions st ON p.product_id = st.product_id
GROUP BY p.product_id, p.product_name
ORDER BY revenue DESC
LIMIT 10;
```

### Vendor Performance
```sql
-- Vendor business value analysis
SELECT v.vendor_name, COUNT(po.purchase_id) as orders, 
       SUM(po.total_cost) as total_business
FROM vendors v
JOIN purchase_orders po ON v.vendor_id = po.vendor_id
GROUP BY v.vendor_id, v.vendor_name
ORDER BY total_business DESC;
```

---

## 🛠️ Customization & Extensions

### Adding New Products:
```sql
INSERT INTO products (product_id, product_name, category_id, unit_of_measure, location_code)
VALUES (3000, 'Organic Spinach', 2, 'bunch', 'P15');

INSERT INTO inventory (product_id, quantity_on_hand, reorder_level)  
VALUES (3000, 50, 10);
```

### Adding New Categories:
```sql
INSERT INTO product_categories (category_name, description)
VALUES ('Organic', 'Certified organic products');
```

### Extending Customer Information:
```sql
-- Add columns to customers table
ALTER TABLE customers 
ADD COLUMN email VARCHAR(100),
ADD COLUMN phone VARCHAR(20),
ADD COLUMN loyalty_points INT DEFAULT 0;
```

---

## 🧪 Testing & Validation

### Data Integrity Tests:
- **Referential integrity**: All foreign keys have matching primary keys
- **Business rules**: No negative quantities or prices  
- **Data completeness**: Required fields populated
- **Consistency**: Standardized formats and values

### Performance Tests:
- **Query optimization**: Indexes on frequently queried columns
- **Join performance**: Efficient relationships between tables
- **Scalability**: Structure supports growth to millions of records

### Validation Reports Available:
1. **Data Quality Summary** - Completeness and accuracy metrics
2. **Financial Validation** - Revenue, costs, and profit calculations  
3. **Inventory Analysis** - Stock levels and turnover rates
4. **Relationship Validation** - Foreign key integrity checks

---

## 📚 Technical Documentation

### Database Schema Details:
- **Primary Keys**: Auto-incrementing integers or business keys
- **Foreign Keys**: Enforced referential integrity
- **Indexes**: Optimized for common query patterns
- **Data Types**: Appropriate precision for business needs
- **Constraints**: Business rules enforced at database level

### ETL Script Architecture:
- **Modular design**: Separate functions for each transformation
- **Error handling**: Comprehensive exception management  
- **Logging**: Detailed audit trail of all operations
- **Configuration**: External settings for flexibility
- **Validation**: Data quality checks throughout process

---

## 🤝 Contributing

### Enhancement Ideas:
- **Real-time inventory updates** with triggers
- **Customer loyalty program** integration
- **Advanced analytics** with stored procedures  
- **Data warehouse** for historical reporting
- **API layer** for application integration

### Code Standards:
- Follow PEP 8 for Python code
- Use descriptive variable and function names
- Include comprehensive error handling
- Add unit tests for new functionality
- Document all database schema changes

---

## 📋 Troubleshooting

### Common Issues:

**Connection Errors:**
- Verify MySQL service is running
- Check username/password in config.py
- Ensure database exists and user has permissions

**ETL Failures:**  
- Check CSV file path in config.py
- Review etl_log.txt for detailed error messages
- Verify data formats match expected patterns

**Query Performance:**
- Run `ANALYZE TABLE` on large tables
- Check execution plans with `EXPLAIN`
- Ensure proper indexes are created

**Data Quality Issues:**
- Run validation_queries.sql for integrity checks
- Review original CSV for data inconsistencies  
- Check ETL transformation logic

---

## 📞 Support & Resources

### Project Resources:
- **Schema Documentation**: `/docs/schema_design.md`
- **ETL Logs**: `/python/etl_log.txt`  
- **Sample Queries**: `/sql/analytics_queries.sql`
- **Validation Scripts**: `/sql/validation_queries.sql`

### Learning Resources:
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Database Normalization Guide](https://en.wikipedia.org/wiki/Database_normalization)

---

## 🏆 Project Achievements

✅ **Complete normalization** from flat file to 3NF database  
✅ **Automated ETL pipeline** with error handling and logging  
✅ **Comprehensive validation** suite ensuring data integrity  
✅ **Rich analytics queries** supporting business intelligence  
✅ **Scalable architecture** ready for production deployment  
✅ **Documentation** for maintenance and extensions  
✅ **Best practices** implementation for enterprise standards  

---

**Author**: Database Engineer  
**Project**: Greenspot Grocer Portfolio Project  
**Date**: November 2025  
**Version**: 1.0  

*This project demonstrates advanced database design, ETL development, and data analytics skills suitable for enterprise-level applications.*