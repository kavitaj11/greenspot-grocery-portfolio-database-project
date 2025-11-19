"""
Greenspot Grocer Data Export Script
==================================

This script exports clean, normalized data from each database table to CSV files.
Perfect for portfolio demonstrations and data analysis.
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime
from config import DATABASE_CONFIG

class DataExporter:
    """Export database tables to CSV files"""
    
    def __init__(self, db_config, output_dir="../data"):
        self.db_config = db_config
        self.output_dir = output_dir
        self.connection = None
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def connect_database(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            print("✅ Connected to MySQL database")
            return True
        except Error as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def export_table_to_csv(self, table_name, query=None):
        """Export a single table to CSV"""
        if not query:
            query = f"SELECT * FROM {table_name}"
        
        try:
            # Read data into pandas DataFrame
            df = pd.read_sql(query, self.connection)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d")
            filename = f"{table_name}_{timestamp}.csv"
            filepath = os.path.join(self.output_dir, filename)
            
            # Export to CSV
            df.to_csv(filepath, index=False)
            
            print(f"✅ Exported {len(df)} records from {table_name} to {filename}")
            return filepath, len(df)
            
        except Exception as e:
            print(f"❌ Error exporting {table_name}: {e}")
            return None, 0
    
    def export_all_tables(self):
        """Export all tables to CSV files"""
        print("🚀 Starting Data Export Process...")
        print("=" * 50)
        
        if not self.connect_database():
            return False
        
        # Define tables and their export queries
        tables_to_export = {
            "product_categories": {
                "query": """
                SELECT 
                    category_id,
                    category_name,
                    description,
                    created_at
                FROM product_categories
                ORDER BY category_id
                """,
                "description": "Product categories (Dairy, Produce, Canned)"
            },
            
            "vendors": {
                "query": """
                SELECT 
                    vendor_id,
                    vendor_name,
                    address,
                    city,
                    state,
                    zip_code,
                    created_at
                FROM vendors
                ORDER BY vendor_id
                """,
                "description": "Vendor information and addresses"
            },
            
            "products": {
                "query": """
                SELECT 
                    p.product_id,
                    p.product_name,
                    pc.category_name,
                    p.unit_of_measure,
                    p.location_code,
                    v.vendor_name as primary_vendor,
                    p.created_at
                FROM products p
                LEFT JOIN product_categories pc ON p.category_id = pc.category_id
                LEFT JOIN vendors v ON p.primary_vendor_id = v.vendor_id
                ORDER BY p.product_id
                """,
                "description": "Complete product catalog with categories and vendors"
            },
            
            "customers": {
                "query": """
                SELECT 
                    customer_id,
                    CONCAT(first_name, ' ', last_name) as customer_name,
                    first_name,
                    last_name,
                    email,
                    phone,
                    registration_date,
                    created_at
                FROM customers
                ORDER BY customer_id
                """,
                "description": "Customer registry and contact information"
            },
            
            "inventory": {
                "query": """
                SELECT 
                    i.inventory_id,
                    p.product_id,
                    p.product_name,
                    pc.category_name,
                    i.quantity_on_hand,
                    i.reorder_level,
                    i.max_stock_level,
                    CASE 
                        WHEN i.quantity_on_hand <= i.reorder_level THEN 'REORDER NEEDED'
                        WHEN i.quantity_on_hand <= (i.reorder_level * 1.5) THEN 'LOW STOCK'
                        ELSE 'ADEQUATE'
                    END as stock_status,
                    i.last_updated
                FROM inventory i
                JOIN products p ON i.product_id = p.product_id
                LEFT JOIN product_categories pc ON p.category_id = pc.category_id
                ORDER BY i.product_id
                """,
                "description": "Current inventory levels with stock status"
            },
            
            "purchase_orders": {
                "query": """
                SELECT 
                    po.purchase_id,
                    p.product_name,
                    v.vendor_name,
                    po.quantity_ordered,
                    po.unit_cost,
                    po.total_cost,
                    po.purchase_date,
                    po.received_date,
                    po.status,
                    po.created_at
                FROM purchase_orders po
                JOIN products p ON po.product_id = p.product_id
                JOIN vendors v ON po.vendor_id = v.vendor_id
                ORDER BY po.purchase_date DESC, po.purchase_id
                """,
                "description": "Purchase order history with vendor details"
            },
            
            "sales_transactions": {
                "query": """
                SELECT 
                    st.transaction_id,
                    p.product_name,
                    pc.category_name,
                    CONCAT(c.first_name, ' ', c.last_name) as customer_name,
                    st.quantity_sold,
                    st.unit_price,
                    st.total_amount,
                    st.sale_date,
                    st.transaction_time,
                    st.payment_method,
                    st.created_at
                FROM sales_transactions st
                JOIN products p ON st.product_id = p.product_id
                LEFT JOIN product_categories pc ON p.category_id = pc.category_id
                LEFT JOIN customers c ON st.customer_id = c.customer_id
                ORDER BY st.sale_date DESC, st.transaction_id
                """,
                "description": "Sales transaction history with customer and product details"
            }
        }
        
        # Export each table
        export_summary = []
        total_records = 0
        
        for table_name, config in tables_to_export.items():
            print(f"\n📊 Exporting {table_name}...")
            print(f"   Description: {config['description']}")
            
            filepath, record_count = self.export_table_to_csv(
                table_name, 
                config['query']
            )
            
            if filepath:
                export_summary.append({
                    'table': table_name,
                    'file': os.path.basename(filepath),
                    'records': record_count,
                    'description': config['description']
                })
                total_records += record_count
        
        # Export business views
        print(f"\n📈 Exporting Business Intelligence Views...")
        self.export_business_views()
        
        # Create export summary
        self.create_export_summary(export_summary, total_records)
        
        if self.connection:
            self.connection.close()
        
        print(f"\n🎉 Export Complete!")
        print(f"📁 All files saved to: {os.path.abspath(self.output_dir)}")
        
        return True
    
    def export_business_views(self):
        """Export pre-built business intelligence views"""
        business_views = {
            "product_inventory_view": {
                "query": """
                SELECT 
                    product_id,
                    product_name,
                    category_name,
                    unit_of_measure,
                    location_code,
                    quantity_on_hand,
                    reorder_level,
                    primary_vendor
                FROM v_product_inventory
                ORDER BY category_name, product_name
                """,
                "description": "Product inventory summary view"
            },
            
            "sales_summary_view": {
                "query": """
                SELECT 
                    product_id,
                    product_name,
                    category_name,
                    total_transactions,
                    total_quantity_sold,
                    total_revenue,
                    avg_price,
                    last_sale_date
                FROM v_sales_summary
                WHERE total_transactions > 0
                ORDER BY total_revenue DESC
                """,
                "description": "Sales performance summary by product"
            },
            
            "purchase_summary_view": {
                "query": """
                SELECT 
                    vendor_id,
                    vendor_name,
                    total_orders,
                    total_quantity_ordered,
                    total_spent,
                    avg_unit_cost,
                    last_order_date
                FROM v_purchase_summary
                WHERE total_orders > 0
                ORDER BY total_spent DESC
                """,
                "description": "Vendor performance and spending summary"
            }
        }
        
        for view_name, config in business_views.items():
            print(f"   📋 Exporting {view_name}...")
            self.export_table_to_csv(view_name, config['query'])
    
    def create_export_summary(self, export_summary, total_records):
        """Create a summary file of all exports"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        summary_content = f"""# Greenspot Grocer Data Export Summary
Generated: {timestamp}
Total Records Exported: {total_records:,}

## Exported Tables:

"""
        
        for item in export_summary:
            summary_content += f"""### {item['table'].upper()}
- **File**: {item['file']}
- **Records**: {item['records']:,}
- **Description**: {item['description']}

"""
        
        summary_content += """## File Descriptions:

### Core Tables:
- **product_categories**: Master list of product categories
- **vendors**: Supplier information and contact details  
- **products**: Complete product catalog with specifications
- **customers**: Customer registry and profiles
- **inventory**: Real-time stock levels and reorder points
- **purchase_orders**: Procurement history and vendor transactions
- **sales_transactions**: Customer purchase history and revenue data

### Business Intelligence Views:
- **product_inventory_view**: Consolidated inventory status
- **sales_summary_view**: Product performance metrics
- **purchase_summary_view**: Vendor performance analysis

## Usage:
These CSV files can be used for:
- Data analysis in Excel, Python, or R
- Business intelligence dashboards
- Portfolio demonstrations
- Further data processing and modeling

---
*Generated by Greenspot Grocer ETL System*
"""
        
        summary_path = os.path.join(self.output_dir, "export_summary.md")
        with open(summary_path, 'w') as f:
            f.write(summary_content)
        
        print(f"✅ Created export summary: export_summary.md")

def main():
    """Main execution function"""
    print("🛒 Greenspot Grocer Data Export Tool")
    print("=" * 50)
    
    exporter = DataExporter(DATABASE_CONFIG)
    success = exporter.export_all_tables()
    
    if success:
        print("\n✅ All data exported successfully!")
        print("📊 Ready for analysis and portfolio presentation!")
    else:
        print("\n❌ Export failed. Check database connection.")

if __name__ == "__main__":
    main()