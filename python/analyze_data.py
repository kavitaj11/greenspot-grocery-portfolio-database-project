"""
Greenspot Grocer Data Analysis Script
====================================

Quick analysis and visualization of the exported CSV data.
Perfect for portfolio demonstrations.
"""

import pandas as pd
import os
from datetime import datetime

def analyze_exported_data():
    """Analyze the exported CSV files"""
    print("📊 Greenspot Grocer Data Analysis")
    print("=" * 50)
    
    data_dir = "../data"
    
    # Load key datasets
    try:
        products = pd.read_csv(f"{data_dir}/products_20251118.csv")
        sales_summary = pd.read_csv(f"{data_dir}/sales_summary_view_20251118.csv")
        inventory = pd.read_csv(f"{data_dir}/inventory_20251118.csv")
        vendors = pd.read_csv(f"{data_dir}/vendors_20251118.csv")
        
        print("✅ Successfully loaded all data files")
        
    except FileNotFoundError as e:
        print(f"❌ Error loading data files: {e}")
        return
    
    # Data Analysis
    print("\n🔍 DATA ANALYSIS RESULTS:")
    print("-" * 30)
    
    # Product Analysis
    print(f"\n📦 PRODUCT ANALYSIS:")
    print(f"   Total Products: {len(products)}")
    print(f"   Categories: {products['category_name'].nunique()}")
    print(f"   Category Breakdown:")
    category_counts = products['category_name'].value_counts()
    for category, count in category_counts.items():
        print(f"     • {category}: {count} products")
    
    # Sales Analysis  
    print(f"\n💰 SALES ANALYSIS:")
    total_revenue = sales_summary['total_revenue'].sum()
    total_transactions = sales_summary['total_transactions'].sum()
    total_items_sold = sales_summary['total_quantity_sold'].sum()
    avg_transaction_value = total_revenue / total_transactions if total_transactions > 0 else 0
    
    print(f"   Total Revenue: ${total_revenue:.2f}")
    print(f"   Total Transactions: {int(total_transactions)}")
    print(f"   Total Items Sold: {int(total_items_sold)}")
    print(f"   Average Transaction Value: ${avg_transaction_value:.2f}")
    
    # Top Products
    print(f"\n🏆 TOP PRODUCTS BY REVENUE:")
    top_products = sales_summary.nlargest(5, 'total_revenue')
    for idx, product in top_products.iterrows():
        print(f"   {idx+1}. {product['product_name']}: ${product['total_revenue']:.2f}")
    
    # Inventory Analysis
    print(f"\n📊 INVENTORY ANALYSIS:")
    total_stock = inventory['quantity_on_hand'].sum()
    low_stock_items = len(inventory[inventory['stock_status'] == 'REORDER NEEDED'])
    
    print(f"   Total Items in Stock: {int(total_stock)}")
    print(f"   Items Needing Reorder: {low_stock_items}")
    
    if low_stock_items > 0:
        print(f"   ⚠️  Low Stock Alert:")
        low_stock = inventory[inventory['stock_status'] == 'REORDER NEEDED']
        for idx, item in low_stock.iterrows():
            print(f"      • {item['product_name']}: {item['quantity_on_hand']} units")
    
    # Vendor Analysis
    print(f"\n🏪 VENDOR ANALYSIS:")
    print(f"   Total Vendors: {len(vendors)}")
    print(f"   Vendor Locations:")
    for idx, vendor in vendors.iterrows():
        print(f"     • {vendor['vendor_name']}: {vendor['city']}, {vendor['state']}")
    
    # Generate insights
    print(f"\n💡 KEY INSIGHTS:")
    print("-" * 15)
    
    # Best performing category
    category_revenue = sales_summary.groupby('category_name')['total_revenue'].sum().sort_values(ascending=False)
    best_category = category_revenue.index[0]
    best_category_revenue = category_revenue.iloc[0]
    
    print(f"   📈 Best Performing Category: {best_category} (${best_category_revenue:.2f})")
    
    # Most popular product
    most_sold = sales_summary.loc[sales_summary['total_quantity_sold'].idxmax()]
    print(f"   🔥 Most Popular Product: {most_sold['product_name']} ({int(most_sold['total_quantity_sold'])} units sold)")
    
    # Average order size
    avg_order_size = total_items_sold / total_transactions if total_transactions > 0 else 0
    print(f"   📦 Average Order Size: {avg_order_size:.1f} items per transaction")
    
    print(f"\n✅ Analysis Complete!")
    print(f"📁 All data available in CSV format for further analysis")

def create_data_dictionary():
    """Create a data dictionary for the CSV files"""
    dictionary = {
        "Table": [],
        "File": [],
        "Description": [],
        "Key Fields": [],
        "Use Cases": []
    }
    
    tables_info = [
        {
            "table": "Products",
            "file": "products_20251118.csv",
            "description": "Master product catalog with categories and vendor information",
            "key_fields": "product_id, product_name, category_name, unit_of_measure, location_code",
            "use_cases": "Product management, catalog analysis, inventory planning"
        },
        {
            "table": "Sales Summary",
            "file": "sales_summary_view_20251118.csv", 
            "description": "Aggregated sales performance metrics by product",
            "key_fields": "product_name, total_revenue, total_transactions, avg_price",
            "use_cases": "Sales analysis, product performance, revenue reporting"
        },
        {
            "table": "Inventory",
            "file": "inventory_20251118.csv",
            "description": "Current stock levels with reorder status",
            "key_fields": "product_name, quantity_on_hand, reorder_level, stock_status",
            "use_cases": "Inventory management, reorder planning, stock optimization"
        },
        {
            "table": "Vendors",
            "file": "vendors_20251118.csv",
            "description": "Supplier contact information and addresses",
            "key_fields": "vendor_name, address, city, state, zip_code",
            "use_cases": "Vendor management, supplier analysis, procurement planning"
        },
        {
            "table": "Sales Transactions",
            "file": "sales_transactions_20251118.csv",
            "description": "Individual customer purchase records",
            "key_fields": "product_name, customer_name, quantity_sold, sale_date, total_amount",
            "use_cases": "Customer analysis, transaction tracking, sales trends"
        }
    ]
    
    for info in tables_info:
        dictionary["Table"].append(info["table"])
        dictionary["File"].append(info["file"])
        dictionary["Description"].append(info["description"])
        dictionary["Key Fields"].append(info["key_fields"])
        dictionary["Use Cases"].append(info["use_cases"])
    
    df = pd.DataFrame(dictionary)
    df.to_csv("../data/data_dictionary.csv", index=False)
    print("✅ Created data dictionary: data_dictionary.csv")

if __name__ == "__main__":
    analyze_exported_data()
    create_data_dictionary()
    
    print(f"\n🎯 PORTFOLIO READY!")
    print("=" * 20)
    print("Your Greenspot Grocer project now includes:")
    print("✅ Normalized MySQL database")
    print("✅ Clean CSV exports for each table")
    print("✅ Business intelligence views")
    print("✅ Data analysis and insights")
    print("✅ Complete documentation")
    print("\n📊 Perfect for data science portfolios!")