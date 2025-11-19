"""
Show Database Schema Structure - Visual representation of the normalized tables
"""

def show_database_structure():
    print("🏗️ GREENSPOT GROCER DATABASE SCHEMA")
    print("="*60)
    
    print("\n📋 NORMALIZED TABLES (7 Tables):")
    print("-"*40)
    
    print("\n1. 📂 PRODUCT_CATEGORIES")
    print("   ├── category_id (PK) - Auto increment")
    print("   ├── category_name - Dairy, Produce, Canned")
    print("   ├── description - Category description")
    print("   └── created_at - Timestamp")
    
    print("\n2. 🏪 VENDORS")
    print("   ├── vendor_id (PK) - Auto increment")
    print("   ├── vendor_name - Bennet Farms, Freshness Inc")
    print("   ├── address - Street address")
    print("   ├── city, state, zip_code - Location details")
    print("   └── created_at - Timestamp")
    
    print("\n3. 📦 PRODUCTS")
    print("   ├── product_id (PK) - 1000, 1100, 2000, etc.")
    print("   ├── product_name - Bennet Farm free-range eggs")
    print("   ├── category_id (FK) → product_categories")
    print("   ├── unit_of_measure - dozen, 12 oz can, bunch")
    print("   ├── location_code - D12, A2, P12")
    print("   └── primary_vendor_id (FK) → vendors")
    
    print("\n4. 👥 CUSTOMERS")
    print("   ├── customer_id (PK) - 198765, 202900, etc.")
    print("   ├── first_name, last_name - Customer details")
    print("   ├── email, phone - Contact info")
    print("   └── registration_date - When joined")
    
    print("\n5. 📊 INVENTORY")
    print("   ├── inventory_id (PK) - Auto increment")
    print("   ├── product_id (FK) → products")
    print("   ├── quantity_on_hand - Current stock")
    print("   ├── reorder_level - When to reorder")
    print("   └── last_updated - Stock update time")
    
    print("\n6. 🛒 PURCHASE_ORDERS")
    print("   ├── purchase_id (PK) - Auto increment")
    print("   ├── product_id (FK) → products")
    print("   ├── vendor_id (FK) → vendors")
    print("   ├── quantity_ordered - How many ordered")
    print("   ├── unit_cost - Cost per unit")
    print("   ├── total_cost - (calculated field)")
    print("   └── purchase_date - When ordered")
    
    print("\n7. 💰 SALES_TRANSACTIONS")
    print("   ├── transaction_id (PK) - Auto increment")
    print("   ├── product_id (FK) → products")
    print("   ├── customer_id (FK) → customers")
    print("   ├── quantity_sold - How many sold")
    print("   ├── unit_price - Price per unit")
    print("   ├── total_amount - (calculated field)")
    print("   └── sale_date - When sold")
    
    print("\n🔗 RELATIONSHIPS:")
    print("-"*30)
    print("   Products ←→ Categories (Many-to-One)")
    print("   Products ←→ Vendors (Many-to-One)")
    print("   Products ←→ Inventory (One-to-One)")
    print("   Products ←→ Sales (One-to-Many)")
    print("   Products ←→ Purchases (One-to-Many)")
    print("   Customers ←→ Sales (One-to-Many)")
    
    print("\n📈 BUSINESS BENEFITS:")
    print("-"*30)
    print("   ✅ Eliminates data redundancy")
    print("   ✅ Maintains referential integrity")
    print("   ✅ Supports complex analytics")
    print("   ✅ Scalable for growth")
    print("   ✅ Enables inventory management")
    print("   ✅ Tracks customer patterns")
    print("   ✅ Vendor performance analysis")

if __name__ == "__main__":
    show_database_structure()