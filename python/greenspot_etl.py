"""
Greenspot Grocer ETL Script
===========================

This script transforms the flat CSV dataset into a normalized relational database.
It handles data cleaning, validation, and loading into MySQL.

Author: Data Engineer
Date: November 2025
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional
import os
from decimal import Decimal
from config import DATABASE_CONFIG, CSV_FILE_PATH

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_log.txt'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GreenspotETL:
    """ETL class for processing Greenspot Grocer data"""
    
    def __init__(self, db_config: Dict[str, str]):
        """Initialize ETL with database configuration"""
        self.db_config = db_config
        self.connection = None
        self.cursor = None
        
        # Data containers
        self.vendors = {}
        self.products = {}
        self.customers = set()
        self.categories = {}
        self.purchases = []
        self.sales = []
        self.inventory = {}
    
    def connect_database(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            self.cursor = self.connection.cursor()
            logger.info("Database connection established")
            return True
        except Error as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def disconnect_database(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Database connection closed")
    
    def clean_vendor_data(self, vendor_string: str) -> Dict[str, str]:
        """Parse and clean vendor information"""
        if pd.isna(vendor_string) or vendor_string.strip() == '':
            return None
            
        # Parse vendor string format: "Name, Address, City, State Zip"
        parts = vendor_string.split(', ')
        
        vendor_data = {
            'vendor_name': parts[0].strip() if len(parts) > 0 else 'Unknown Vendor',
            'address': parts[1].strip() if len(parts) > 1 else '',
            'city': '',
            'state': '',
            'zip_code': ''
        }
        
        # Parse city, state, zip from last part
        if len(parts) > 2:
            location = parts[2].strip()
            # Match pattern: "City, State Zip"
            match = re.match(r'([^,]+),?\s+([A-Z]{2})\s+(\d{5})', location)
            if match:
                vendor_data['city'] = match.group(1).strip()
                vendor_data['state'] = match.group(2).strip()
                vendor_data['zip_code'] = match.group(3).strip()
        
        return vendor_data
    
    def normalize_unit(self, unit: str) -> str:
        """Standardize unit of measure"""
        if pd.isna(unit):
            return 'each'
        
        unit = unit.lower().strip()
        
        # Standardize common variations
        unit_mappings = {
            '12 ounce can': '12 oz can',
            '12-oz can': '12 oz can',
            '36 oz can': '36 oz can',
            'bunch': 'bunch',
            'dozen': 'dozen'
        }
        
        return unit_mappings.get(unit, unit)
    
    def normalize_location(self, location: str) -> str:
        """Standardize location codes"""
        if pd.isna(location):
            return 'GENERAL'
        
        return location.upper().strip()
    
    def parse_csv_data(self, csv_file: str):
        """Parse and clean CSV data"""
        logger.info(f"Reading CSV file: {csv_file}")
        
        try:
            df = pd.read_csv(csv_file)
            logger.info(f"Loaded {len(df)} rows from CSV")
            
            # Remove empty rows
            df = df.dropna(how='all')
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            # Process each row
            for index, row in df.iterrows():
                if pd.isna(row['Item num']):
                    continue
                
                self.process_row(row)
                
        except Exception as e:
            logger.error(f"Error parsing CSV: {e}")
            raise
    
    def process_row(self, row):
        """Process a single row of data"""
        item_num = int(row['Item num'])
        
        # Extract product information
        if item_num not in self.products:
            category_name = row['item type'].strip() if pd.notna(row['item type']) else 'General'
            
            self.products[item_num] = {
                'product_id': item_num,
                'product_name': row['description'].strip() if pd.notna(row['description']) else f'Product {item_num}',
                'category': category_name,
                'unit_of_measure': self.normalize_unit(row['Unit']),
                'location_code': self.normalize_location(row['Location'])
            }
            
            # Track categories
            if category_name not in self.categories:
                self.categories[category_name] = len(self.categories) + 1
        
        # Process vendor information (for purchases)
        if pd.notna(row['vendor']) and pd.notna(row['cost']):
            vendor_data = self.clean_vendor_data(row['vendor'])
            if vendor_data:
                vendor_key = vendor_data['vendor_name']
                if vendor_key not in self.vendors:
                    self.vendors[vendor_key] = {
                        'vendor_id': len(self.vendors) + 1,
                        **vendor_data
                    }
                
                # Record purchase
                self.purchases.append({
                    'product_id': item_num,
                    'vendor_id': self.vendors[vendor_key]['vendor_id'],
                    'quantity_ordered': int(row['Quantity']) if pd.notna(row['Quantity']) else 0,
                    'unit_cost': float(row['cost']),
                    'purchase_date': self.parse_date(row['purchase date'])
                })
                
                # Update inventory
                if item_num not in self.inventory:
                    self.inventory[item_num] = int(row['quantity on-hand']) if pd.notna(row['quantity on-hand']) else 0
        
        # Process sales information
        if pd.notna(row['price']) and pd.notna(row['date sold']):
            customer_id = None
            if pd.notna(row['cust']) and str(row['cust']).strip():
                customer_id = int(row['cust'])
                self.customers.add(customer_id)
            
            self.sales.append({
                'product_id': item_num,
                'customer_id': customer_id,
                'quantity_sold': int(row['Quantity']) if pd.notna(row['Quantity']) else 0,
                'unit_price': float(row['price']),
                'sale_date': self.parse_date(row['date sold'])
            })
    
    def parse_date(self, date_str) -> Optional[str]:
        """Parse date string into MySQL format"""
        if pd.isna(date_str):
            return None
        
        try:
            # Handle MM/DD/YYYY format
            date_obj = datetime.strptime(str(date_str).strip(), '%m/%d/%Y')
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            logger.warning(f"Could not parse date: {date_str}")
            return None
    
    def load_categories(self):
        """Load product categories into database"""
        logger.info("Loading product categories...")
        
        for category_name, category_id in self.categories.items():
            try:
                query = """
                INSERT IGNORE INTO product_categories (category_id, category_name, description)
                VALUES (%s, %s, %s)
                """
                self.cursor.execute(query, (category_id, category_name, f"{category_name} products"))
                
            except Error as e:
                logger.error(f"Error loading category {category_name}: {e}")
        
        self.connection.commit()
        logger.info(f"Loaded {len(self.categories)} categories")
    
    def load_vendors(self):
        """Load vendors into database"""
        logger.info("Loading vendors...")
        
        for vendor_data in self.vendors.values():
            try:
                query = """
                INSERT IGNORE INTO vendors 
                (vendor_id, vendor_name, address, city, state, zip_code)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                self.cursor.execute(query, (
                    vendor_data['vendor_id'],
                    vendor_data['vendor_name'],
                    vendor_data['address'],
                    vendor_data['city'],
                    vendor_data['state'],
                    vendor_data['zip_code']
                ))
                
            except Error as e:
                logger.error(f"Error loading vendor {vendor_data['vendor_name']}: {e}")
        
        self.connection.commit()
        logger.info(f"Loaded {len(self.vendors)} vendors")
    
    def load_products(self):
        """Load products into database"""
        logger.info("Loading products...")
        
        for product in self.products.values():
            try:
                # Find primary vendor (first vendor that supplies this product)
                primary_vendor_id = None
                for purchase in self.purchases:
                    if purchase['product_id'] == product['product_id']:
                        primary_vendor_id = purchase['vendor_id']
                        break
                
                query = """
                INSERT IGNORE INTO products 
                (product_id, product_name, category_id, unit_of_measure, location_code, primary_vendor_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                self.cursor.execute(query, (
                    product['product_id'],
                    product['product_name'],
                    self.categories[product['category']],
                    product['unit_of_measure'],
                    product['location_code'],
                    primary_vendor_id
                ))
                
            except Error as e:
                logger.error(f"Error loading product {product['product_name']}: {e}")
        
        self.connection.commit()
        logger.info(f"Loaded {len(self.products)} products")
    
    def load_customers(self):
        """Load customers into database"""
        logger.info("Loading customers...")
        
        for customer_id in self.customers:
            try:
                query = """
                INSERT IGNORE INTO customers (customer_id, first_name, last_name)
                VALUES (%s, %s, %s)
                """
                self.cursor.execute(query, (customer_id, f"Customer", f"{customer_id}"))
                
            except Error as e:
                logger.error(f"Error loading customer {customer_id}: {e}")
        
        self.connection.commit()
        logger.info(f"Loaded {len(self.customers)} customers")
    
    def load_inventory(self):
        """Load inventory into database"""
        logger.info("Loading inventory...")
        
        for product_id, quantity in self.inventory.items():
            try:
                query = """
                INSERT IGNORE INTO inventory (product_id, quantity_on_hand)
                VALUES (%s, %s)
                """
                self.cursor.execute(query, (product_id, quantity))
                
            except Error as e:
                logger.error(f"Error loading inventory for product {product_id}: {e}")
        
        self.connection.commit()
        logger.info(f"Loaded inventory for {len(self.inventory)} products")
    
    def load_purchases(self):
        """Load purchase orders into database"""
        logger.info("Loading purchase orders...")
        
        for purchase in self.purchases:
            try:
                query = """
                INSERT INTO purchase_orders 
                (product_id, vendor_id, quantity_ordered, unit_cost, purchase_date, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                self.cursor.execute(query, (
                    purchase['product_id'],
                    purchase['vendor_id'],
                    purchase['quantity_ordered'],
                    purchase['unit_cost'],
                    purchase['purchase_date'],
                    'received'
                ))
                
            except Error as e:
                logger.error(f"Error loading purchase: {e}")
        
        self.connection.commit()
        logger.info(f"Loaded {len(self.purchases)} purchase orders")
    
    def load_sales(self):
        """Load sales transactions into database"""
        logger.info("Loading sales transactions...")
        
        for sale in self.sales:
            try:
                query = """
                INSERT INTO sales_transactions 
                (product_id, customer_id, quantity_sold, unit_price, sale_date)
                VALUES (%s, %s, %s, %s, %s)
                """
                self.cursor.execute(query, (
                    sale['product_id'],
                    sale['customer_id'],
                    sale['quantity_sold'],
                    sale['unit_price'],
                    sale['sale_date']
                ))
                
            except Error as e:
                logger.error(f"Error loading sale: {e}")
        
        self.connection.commit()
        logger.info(f"Loaded {len(self.sales)} sales transactions")
    
    def run_etl(self, csv_file: str):
        """Run complete ETL process"""
        logger.info("Starting Greenspot Grocer ETL process...")
        
        try:
            # Connect to database
            if not self.connect_database():
                return False
            
            # Parse CSV data
            self.parse_csv_data(csv_file)
            
            # Load data in proper order (respecting foreign keys)
            self.load_categories()
            self.load_vendors()
            self.load_products()
            self.load_customers()
            self.load_inventory()
            self.load_purchases()
            self.load_sales()
            
            logger.info("ETL process completed successfully!")
            
            # Print summary
            self.print_summary()
            
            return True
            
        except Exception as e:
            logger.error(f"ETL process failed: {e}")
            if self.connection:
                self.connection.rollback()
            return False
            
        finally:
            self.disconnect_database()
    
    def print_summary(self):
        """Print ETL summary statistics"""
        print("\n" + "="*50)
        print("ETL SUMMARY")
        print("="*50)
        print(f"Categories loaded: {len(self.categories)}")
        print(f"Vendors loaded: {len(self.vendors)}")
        print(f"Products loaded: {len(self.products)}")
        print(f"Customers loaded: {len(self.customers)}")
        print(f"Inventory records: {len(self.inventory)}")
        print(f"Purchase orders: {len(self.purchases)}")
        print(f"Sales transactions: {len(self.sales)}")
        print("="*50)

def main():
    """Main execution function"""
    
    # Use configuration from config.py
    db_config = DATABASE_CONFIG
    csv_file = CSV_FILE_PATH
    
    # Check if CSV file exists
    if not os.path.exists(csv_file):
        logger.error(f"CSV file not found: {csv_file}")
        return
    
    # Run ETL process
    etl = GreenspotETL(db_config)
    success = etl.run_etl(csv_file)
    
    if success:
        print("\nETL process completed successfully!")
        print("You can now run validation queries to verify the data.")
    else:
        print("\nETL process failed. Check logs for details.")

if __name__ == "__main__":
    main()