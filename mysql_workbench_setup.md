# MySQL Workbench Setup Guide for Greenspot Grocer

## 🚀 Quick Setup with MySQL Workbench

### Step 1: Create Database in MySQL Workbench

1. **Open MySQL Workbench**
2. **Connect to your MySQL server** (usually localhost)
3. **Create the database** by running this query:

```sql
CREATE DATABASE IF NOT EXISTS greenspot_grocer;
USE greenspot_grocer;
```

### Step 2: Run the Schema Creation Script

1. **Open the schema file**: `sql/create_schema.sql`
2. **Copy the entire contents** of the file
3. **Paste into MySQL Workbench** query editor
4. **Execute the script** (Ctrl+Shift+Enter or click the lightning bolt)

### Step 3: Configure Python Connection

1. **Edit** `python/config.py`
2. **Update your credentials**:
   ```python
   DATABASE_CONFIG = {
       'host': 'localhost',
       'port': 3306,
       'database': 'greenspot_grocer',
       'user': 'your_username',    # Your MySQL username
       'password': 'your_password' # Your MySQL password
   }
   ```

### Step 4: Run the ETL Process

```bash
cd python
python greenspot_etl.py
```

### Step 5: Validate in MySQL Workbench

Run these queries to verify the data loaded correctly:

```sql
-- Check table counts
SELECT 'product_categories' as table_name, COUNT(*) as records FROM product_categories
UNION ALL
SELECT 'vendors', COUNT(*) FROM vendors
UNION ALL  
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'customers', COUNT(*) FROM customers
UNION ALL
SELECT 'inventory', COUNT(*) FROM inventory
UNION ALL
SELECT 'purchase_orders', COUNT(*) FROM purchase_orders
UNION ALL
SELECT 'sales_transactions', COUNT(*) FROM sales_transactions;

-- View sample data
SELECT * FROM v_product_inventory LIMIT 10;
```

### Step 6: Explore with Analytics Queries

1. **Open** `sql/analytics_queries.sql`
2. **Run sections** of the analytics queries in MySQL Workbench
3. **Explore the results** to see business insights

## 🔧 Troubleshooting

### Connection Issues:
- Verify MySQL server is running
- Check username/password in config.py
- Ensure port 3306 is accessible
- Try connecting in MySQL Workbench first

### Schema Issues:
- Make sure database `greenspot_grocer` exists
- Run schema creation in correct order
- Check for any error messages in Workbench

### ETL Issues:
- Verify CSV file path in config.py
- Check Python dependencies are installed
- Review etl_log.txt for detailed errors

## ✅ Success Indicators

You'll know it worked when:
- ✅ 7 tables created in MySQL Workbench
- ✅ ETL script runs without errors
- ✅ Data appears in all tables
- ✅ Sample queries return results
- ✅ Analytics queries show business insights

**Ready to transform your grocery data! 🛒📊**