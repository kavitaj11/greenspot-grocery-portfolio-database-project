"""
SQLite Alternative for Greenspot Grocer
=======================================

If MySQL connection issues persist, this creates a SQLite version
that works locally without server setup.
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime

def create_sqlite_database():
    """Create SQLite version of Greenspot database"""
    print("🗃️ Creating SQLite Database Alternative...")
    
    # Create SQLite database
    db_path = "greenspot_grocer.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables (simplified SQLite syntax)
    schema_sql = """
    -- Product Categories
    CREATE TABLE IF NOT EXISTS product_categories (
        category_id INTEGER PRIMARY KEY,
        category_name TEXT UNIQUE NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Vendors
    CREATE TABLE IF NOT EXISTS vendors (
        vendor_id INTEGER PRIMARY KEY,
        vendor_name TEXT NOT NULL,
        address TEXT,
        city TEXT,
        state TEXT,
        zip_code TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Products
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT NOT NULL,
        category_id INTEGER,
        unit_of_measure TEXT,
        location_code TEXT,
        primary_vendor_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES product_categories(category_id),
        FOREIGN KEY (primary_vendor_id) REFERENCES vendors(vendor_id)
    );
    
    -- Customers
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Inventory
    CREATE TABLE IF NOT EXISTS inventory (
        inventory_id INTEGER PRIMARY KEY,
        product_id INTEGER UNIQUE NOT NULL,
        quantity_on_hand INTEGER DEFAULT 0,
        reorder_level INTEGER DEFAULT 10,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );
    
    -- Purchase Orders
    CREATE TABLE IF NOT EXISTS purchase_orders (
        purchase_id INTEGER PRIMARY KEY,
        product_id INTEGER NOT NULL,
        vendor_id INTEGER NOT NULL,
        quantity_ordered INTEGER NOT NULL,
        unit_cost REAL NOT NULL,
        total_cost REAL,
        purchase_date DATE NOT NULL,
        status TEXT DEFAULT 'received',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(product_id),
        FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
    );
    
    -- Sales Transactions
    CREATE TABLE IF NOT EXISTS sales_transactions (
        transaction_id INTEGER PRIMARY KEY,
        product_id INTEGER NOT NULL,
        customer_id INTEGER,
        quantity_sold INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        total_amount REAL,
        sale_date DATE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(product_id),
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );
    """
    
    # Execute schema
    cursor.executescript(schema_sql)
    conn.commit()
    
    print(f"✅ SQLite database created: {db_path}")
    
    # Load sample data
    load_sample_data(conn)
    
    conn.close()
    return db_path

def load_sample_data(conn):
    """Load data from CSV into SQLite"""
    cursor = conn.cursor()
    
    # Insert categories
    categories = [
        (1, 'Dairy', 'Milk, eggs, cheese products'),
        (2, 'Produce', 'Fresh fruits and vegetables'),
        (3, 'Canned', 'Canned and preserved goods')
    ]
    cursor.executemany("INSERT OR IGNORE INTO product_categories (category_id, category_name, description) VALUES (?, ?, ?)", categories)
    
    # Insert vendors
    vendors = [
        (1, 'Bennet Farms', 'Rt. 17', 'Evansville', 'IL', '55446'),
        (2, 'Freshness Inc', '202 E. Maple St.', 'St. Joseph', 'MO', '45678'),
        (3, 'Ruby Redd Produce LLC', '1212 Milam St.', 'Kenosha', 'AL', '34567')
    ]
    cursor.executemany("INSERT OR IGNORE INTO vendors (vendor_id, vendor_name, address, city, state, zip_code) VALUES (?, ?, ?, ?, ?, ?)", vendors)
    
    # Insert products
    products = [
        (1000, 'Bennet Farm free-range eggs', 1, 'dozen', 'D12', 1),
        (1100, 'Freshness White beans', 3, '12 oz can', 'A2', 2),
        (1222, 'Freshness Green beans', 3, '12 oz can', 'A3', 2),
        (1223, 'Freshness Green beans', 3, '36 oz can', 'A7', 2),
        (1224, 'Freshness Wax beans', 3, '12 oz can', 'A3', 2),
        (2000, 'Ruby\'s Kale', 2, 'bunch', 'P12', 3),
        (2001, 'Ruby\'s Organic Kale', 2, 'bunch', 'PO2', 3)
    ]
    cursor.executemany("INSERT OR IGNORE INTO products (product_id, product_name, category_id, unit_of_measure, location_code, primary_vendor_id) VALUES (?, ?, ?, ?, ?, ?)", products)
    
    # Add more sample data...
    conn.commit()
    print("✅ Sample data loaded")

def run_sample_queries(db_path):
    """Run sample queries on SQLite database"""
    conn = sqlite3.connect(db_path)
    
    print("\n📊 Sample Query Results:")
    print("=" * 40)
    
    # Products with categories
    query = """
    SELECT p.product_name, pc.category_name, p.unit_of_measure
    FROM products p
    JOIN product_categories pc ON p.category_id = pc.category_id
    LIMIT 5
    """
    
    df = pd.read_sql_query(query, conn)
    print("\n🛒 Products by Category:")
    print(df.to_string(index=False))
    
    conn.close()

if __name__ == "__main__":
    print("🛒 Greenspot Grocer - SQLite Alternative")
    print("=" * 50)
    
    db_path = create_sqlite_database()
    run_sample_queries(db_path)
    
    print(f"\n✅ Database ready: {db_path}")
    print("You can open this with DB Browser for SQLite or any SQLite tool")
    input("\nPress Enter to exit...")