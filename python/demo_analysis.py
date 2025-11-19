"""
Demo script to show Greenspot Grocer data analysis without database
"""

import pandas as pd
import os
from datetime import datetime
import re

def analyze_csv():
    """Analyze the CSV file and show transformation results"""
    
    print("🛒 Greenspot Grocer Data Analysis Demo")
    print("="*50)
    
    # Read CSV
    csv_path = "../GreenspotDataset.csv"
    if not os.path.exists(csv_path):
        print("❌ CSV file not found!")
        return
    
    df = pd.read_csv(csv_path)
    print(f"✅ Loaded {len(df)} rows from CSV")
    
    # Remove empty rows
    df_clean = df.dropna(how='all')
    print(f"✅ After cleaning: {len(df_clean)} rows")
    
    # Show sample data
    print("\n📊 Sample Raw Data:")
    print(df_clean.head(3).to_string())
    
    # Analyze unique products
    products = df_clean.dropna(subset=['Item num'])['Item num'].unique()
    print(f"\n📦 Unique Products: {len(products)}")
    print(f"Product IDs: {sorted(products)}")
    
    # Analyze categories
    categories = df_clean.dropna(subset=['item type'])['item type'].unique()
    print(f"\n📂 Product Categories: {len(categories)}")
    print(f"Categories: {list(categories)}")
    
    # Analyze vendors
    vendors = df_clean.dropna(subset=['vendor'])['vendor'].unique()
    print(f"\n🏪 Unique Vendors: {len(vendors)}")
    for i, vendor in enumerate(vendors, 1):
        print(f"  {i}. {vendor}")
    
    # Sales vs Purchases
    sales = df_clean.dropna(subset=['price'])
    purchases = df_clean.dropna(subset=['cost'])
    
    print(f"\n💰 Transactions:")
    print(f"  Sales transactions: {len(sales)}")
    print(f"  Purchase orders: {len(purchases)}")
    
    # Show normalized data preview
    print("\n🔄 Normalized Data Preview:")
    print("="*30)
    
    # Products table preview
    print("\n📦 PRODUCTS TABLE:")
    products_data = []
    for _, row in df_clean.dropna(subset=['Item num']).iterrows():
        if int(row['Item num']) not in [p['id'] for p in products_data]:
            products_data.append({
                'id': int(row['Item num']),
                'name': row['description'].strip() if pd.notna(row['description']) else f"Product {int(row['Item num'])}",
                'category': row['item type'].strip() if pd.notna(row['item type']) else 'General',
                'unit': row['Unit'].lower().strip() if pd.notna(row['Unit']) else 'each'
            })
    
    for product in products_data[:3]:
        print(f"  ID: {product['id']} | Name: {product['name']} | Category: {product['category']}")
    
    # Vendors table preview
    print(f"\n🏪 VENDORS TABLE:")
    vendor_data = []
    for vendor_string in vendors:
        if pd.notna(vendor_string):
            parts = vendor_string.split(', ')
            vendor_info = {
                'name': parts[0].strip(),
                'address': parts[1].strip() if len(parts) > 1 else '',
                'location': parts[2].strip() if len(parts) > 2 else ''
            }
            vendor_data.append(vendor_info)
    
    for i, vendor in enumerate(vendor_data, 1):
        print(f"  {i}. {vendor['name']} - {vendor['location']}")
    
    # Sales summary
    print(f"\n💵 SALES SUMMARY:")
    total_revenue = sales['price'].sum()
    avg_transaction = sales['price'].mean()
    print(f"  Total Revenue: ${total_revenue:.2f}")
    print(f"  Average Transaction: ${avg_transaction:.2f}")
    print(f"  Items Sold: {sales['Quantity'].sum()}")
    
    print(f"\n✅ Data analysis complete!")
    print(f"📋 This data would be loaded into 7 normalized tables:")
    print(f"   1. product_categories ({len(categories)} records)")
    print(f"   2. vendors ({len(vendors)} records)")  
    print(f"   3. products ({len(products)} records)")
    print(f"   4. customers ({len(sales.dropna(subset=['cust']))} records)")
    print(f"   5. inventory ({len(products)} records)")
    print(f"   6. purchase_orders ({len(purchases)} records)")
    print(f"   7. sales_transactions ({len(sales)} records)")

if __name__ == "__main__":
    analyze_csv()