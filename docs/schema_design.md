# Greenspot Grocer Database Schema Design

## Data Analysis

### Current CSV Structure Issues:
- **Denormalized data**: Item information repeated across multiple rows
- **Inconsistent formatting**: Units described differently (12 oz can, 12-oz can, 12 ounce can)
- **Mixed transaction types**: Purchase and sales data in same rows
- **Vendor information duplication**: Full vendor details repeated
- **Data quality issues**: Empty rows, inconsistent location codes (D12 vs d12)

### Identified Entities:

1. **Products**: Unique grocery items
   - Item Number (Primary Key)
   - Description
   - Item Type/Category
   - Unit of Measure
   - Current Location

2. **Vendors**: Suppliers of products
   - Vendor ID (Primary Key)
   - Vendor Name
   - Address

3. **Customers**: Grocery store customers
   - Customer ID (Primary Key)
   - Customer details (expandable for future)

4. **Inventory**: Current stock levels
   - Product ID (Foreign Key)
   - Quantity on Hand
   - Location

5. **Purchase Orders**: Product procurement
   - Purchase ID (Primary Key)
   - Product ID (Foreign Key)
   - Vendor ID (Foreign Key)
   - Quantity Ordered
   - Unit Cost
   - Purchase Date

6. **Sales Transactions**: Customer purchases
   - Transaction ID (Primary Key)
   - Product ID (Foreign Key)
   - Customer ID (Foreign Key)
   - Quantity Sold
   - Unit Price
   - Sale Date

## Normalized Schema Design

### Third Normal Form (3NF) Structure:

1. **No partial dependencies**: All non-key attributes depend on entire primary key
2. **No transitive dependencies**: Non-key attributes don't depend on other non-key attributes
3. **Atomic values**: Each column contains single values
4. **Referential integrity**: Foreign keys maintain data consistency

### Relationships:
- Products → Vendors (Many-to-One): Each product has one primary vendor
- Products → Inventory (One-to-One): Each product has current inventory
- Products → Purchases (One-to-Many): Products can have multiple purchase orders
- Products → Sales (One-to-Many): Products can have multiple sales
- Customers → Sales (One-to-Many): Customers can have multiple purchases
- Vendors → Purchases (One-to-Many): Vendors can supply multiple products

## Benefits of Normalized Design:

1. **Eliminates data redundancy**: Vendor info stored once
2. **Maintains data integrity**: Updates only needed in one place
3. **Scalable**: Easy to add new products, vendors, customers
4. **Supports analytics**: Proper structure for reporting and analysis
5. **Flexible**: Can accommodate future business requirements