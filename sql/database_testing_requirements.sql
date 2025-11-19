-- ===================================================================
-- GREENSPOT GROCER DATABASE TESTING SCRIPT
-- Purpose: Demonstrate database testing requirements fulfillment
-- Created: November 2025
-- Author: Database Design Portfolio Project
-- ===================================================================

-- This script demonstrates:
-- 1. Table joining demonstrations (2, 3, and 4-table joins)
-- 2. Business question queries (purchase orders, customer analytics, inventory management)
-- 3. All tables in one query (complete 7-table join)

USE greenspot_grocer;

-- ===================================================================
-- SECTION 1: TABLE JOINING DEMONSTRATIONS
-- ===================================================================

-- ===================================================================
-- TEST 1: TWO-TABLE JOIN (Products + Categories)
-- Purpose: Demonstrate basic INNER JOIN functionality
-- Tables: products, product_categories
-- ===================================================================
SELECT '=== TEST 1: TWO-TABLE JOIN (Products + Categories) ===' as test_description;

SELECT 
    p.product_id,
    p.product_name,
    pc.category_name,
    p.unit_of_measure,
    p.location_code
FROM products p
INNER JOIN product_categories pc ON p.category_id = pc.category_id
ORDER BY pc.category_name, p.product_name;

-- Expected Results: 7 products with their categories
-- Validates: Basic JOIN operations and foreign key relationships

-- ===================================================================
-- TEST 2: THREE-TABLE JOIN (Products + Categories + Vendors)
-- Purpose: Demonstrate complex JOIN with multiple relationships
-- Tables: products, product_categories, vendors
-- ===================================================================
SELECT '=== TEST 2: THREE-TABLE JOIN (Products + Categories + Vendors) ===' as test_description;

SELECT 
    p.product_name,
    pc.category_name,
    v.vendor_name,
    v.city,
    v.state,
    p.unit_of_measure,
    p.location_code
FROM products p
INNER JOIN product_categories pc ON p.category_id = pc.category_id
INNER JOIN vendors v ON p.primary_vendor_id = v.vendor_id
ORDER BY pc.category_name, p.product_name;

-- Expected Results: 7 products with category and vendor information
-- Validates: Multi-table JOIN operations and referential integrity

-- ===================================================================
-- TEST 3: FOUR-TABLE JOIN (Sales Analysis)
-- Purpose: Demonstrate complex business analytics with multiple JOINs
-- Tables: sales_transactions, products, product_categories, customers
-- ===================================================================
SELECT '=== TEST 3: FOUR-TABLE JOIN (Sales Analysis) ===' as test_description;

SELECT 
    st.transaction_id,
    p.product_name,
    pc.category_name,
    CONCAT(c.first_name, ' ', c.last_name) as customer_name,
    st.quantity_sold,
    st.unit_price,
    st.total_amount,
    st.sale_date,
    st.payment_method
FROM sales_transactions st
INNER JOIN products p ON st.product_id = p.product_id
INNER JOIN product_categories pc ON p.category_id = pc.category_id
LEFT JOIN customers c ON st.customer_id = c.customer_id
ORDER BY st.sale_date DESC, st.transaction_id;

-- Expected Results: 13 sales transactions with complete context
-- Validates: LEFT JOIN handling and complex business queries

-- ===================================================================
-- SECTION 2: BUSINESS QUESTION QUERIES
-- ===================================================================

-- ===================================================================
-- BUSINESS QUERY 1: PURCHASE ORDER GENERATION
-- Question: "Can we produce a query that displays all data necessary to create a purchase order?"
-- Purpose: Demonstrates practical business application of database design
-- ===================================================================
SELECT '=== BUSINESS QUERY 1: PURCHASE ORDER GENERATION ===' as test_description;

SELECT 
    po.purchase_id as "PO_Number",
    po.purchase_date as "Order_Date",
    v.vendor_name as "Vendor",
    CONCAT(v.address, ', ', v.city, ', ', v.state, ' ', v.zip_code) as "Vendor_Full_Address",
    v.phone as "Vendor_Phone",
    v.email as "Vendor_Email",
    p.product_name as "Product",
    p.unit_of_measure as "Unit",
    po.quantity_ordered as "Qty_Ordered",
    CONCAT('$', FORMAT(po.unit_cost, 2)) as "Unit_Cost",
    CONCAT('$', FORMAT(po.total_cost, 2)) as "Total_Cost",
    po.status as "Status",
    CASE 
        WHEN po.received_date IS NULL THEN 'Pending Delivery'
        ELSE CONCAT('Received: ', po.received_date)
    END as "Delivery_Status"
FROM purchase_orders po
INNER JOIN vendors v ON po.vendor_id = v.vendor_id
INNER JOIN products p ON po.product_id = p.product_id
ORDER BY po.purchase_date DESC, po.purchase_id;

-- Business Value: Complete purchase order information for procurement decisions
-- Validates: Complex business logic and data formatting

-- ===================================================================
-- BUSINESS QUERY 2: CUSTOMER ANALYTICS DASHBOARD
-- Question: "What are the purchasing patterns of our customers?"
-- Purpose: Customer relationship management and marketing insights
-- ===================================================================
SELECT '=== BUSINESS QUERY 2: CUSTOMER ANALYTICS DASHBOARD ===' as test_description;

SELECT 
    c.customer_id,
    CONCAT(c.first_name, ' ', c.last_name) as "Customer_Name",
    c.email as "Email",
    c.city as "City",
    COUNT(st.transaction_id) as "Total_Orders",
    SUM(st.quantity_sold) as "Items_Purchased",
    CONCAT('$', FORMAT(SUM(st.total_amount), 2)) as "Total_Spent",
    CONCAT('$', FORMAT(AVG(st.total_amount), 2)) as "Avg_Order_Value",
    MIN(st.sale_date) as "First_Purchase",
    MAX(st.sale_date) as "Last_Purchase",
    DATEDIFF(MAX(st.sale_date), MIN(st.sale_date)) as "Customer_Lifespan_Days"
FROM customers c
INNER JOIN sales_transactions st ON c.customer_id = st.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.email, c.city
HAVING COUNT(st.transaction_id) >= 1
ORDER BY SUM(st.total_amount) DESC;

-- Business Value: Customer lifetime value and purchasing behavior analysis
-- Validates: Aggregate functions and business intelligence capabilities

-- ===================================================================
-- BUSINESS QUERY 3: INVENTORY REORDER MANAGEMENT
-- Question: "Which products need to be reordered and from which vendors?"
-- Purpose: Automated inventory management and procurement planning
-- ===================================================================
SELECT '=== BUSINESS QUERY 3: INVENTORY REORDER MANAGEMENT ===' as test_description;

SELECT 
    p.product_id,
    p.product_name,
    pc.category_name,
    i.quantity_on_hand as "Current_Stock",
    i.reorder_level as "Reorder_Level",
    (i.reorder_level - i.quantity_on_hand) as "Qty_Needed",
    CASE 
        WHEN i.quantity_on_hand <= i.reorder_level THEN 'REORDER_NEEDED'
        WHEN i.quantity_on_hand <= (i.reorder_level * 1.5) THEN 'LOW_STOCK'
        ELSE 'ADEQUATE'
    END as "Stock_Status",
    v.vendor_name as "Primary_Vendor",
    v.phone as "Vendor_Phone",
    v.email as "Vendor_Email",
    COALESCE(avg_cost.avg_unit_cost, 0) as "Avg_Unit_Cost",
    CONCAT('$', FORMAT((i.reorder_level - i.quantity_on_hand) * COALESCE(avg_cost.avg_unit_cost, 0), 2)) as "Est_Order_Value"
FROM products p
INNER JOIN inventory i ON p.product_id = i.product_id
INNER JOIN product_categories pc ON p.category_id = pc.category_id
LEFT JOIN vendors v ON p.primary_vendor_id = v.vendor_id
LEFT JOIN (
    SELECT 
        product_id, 
        AVG(unit_cost) as avg_unit_cost
    FROM purchase_orders 
    GROUP BY product_id
) avg_cost ON p.product_id = avg_cost.product_id
ORDER BY 
    CASE 
        WHEN i.quantity_on_hand <= i.reorder_level THEN 1
        WHEN i.quantity_on_hand <= (i.reorder_level * 1.5) THEN 2
        ELSE 3
    END,
    (i.reorder_level - i.quantity_on_hand) DESC;

-- Business Value: Actionable inventory reorder information with cost estimates
-- Validates: Subqueries, CASE statements, and complex business logic

-- ===================================================================
-- BUSINESS QUERY 4: PRODUCT PROFITABILITY ANALYSIS
-- Question: "Which products are most profitable and which categories perform best?"
-- Purpose: Financial analysis and product mix optimization
-- ===================================================================
SELECT '=== BUSINESS QUERY 4: PRODUCT PROFITABILITY ANALYSIS ===' as test_description;

SELECT 
    p.product_id,
    p.product_name,
    pc.category_name,
    COALESCE(SUM(st.quantity_sold), 0) as "Units_Sold",
    CONCAT('$', FORMAT(COALESCE(SUM(st.total_amount), 0), 2)) as "Total_Revenue",
    COALESCE(SUM(po.quantity_ordered), 0) as "Units_Purchased",
    CONCAT('$', FORMAT(COALESCE(SUM(po.total_cost), 0), 2)) as "Total_Cost",
    CONCAT('$', FORMAT(COALESCE(SUM(st.total_amount), 0) - COALESCE(SUM(po.total_cost), 0), 2)) as "Profit_Margin",
    CASE 
        WHEN COALESCE(SUM(po.total_cost), 0) > 0 THEN 
            CONCAT(FORMAT(((COALESCE(SUM(st.total_amount), 0) - COALESCE(SUM(po.total_cost), 0)) / COALESCE(SUM(po.total_cost), 0)) * 100, 1), '%')
        ELSE 'N/A'
    END as "ROI_Percentage",
    COUNT(DISTINCT st.transaction_id) as "Sales_Count",
    COUNT(DISTINCT po.purchase_id) as "Purchase_Count"
FROM products p
LEFT JOIN product_categories pc ON p.category_id = pc.category_id
LEFT JOIN sales_transactions st ON p.product_id = st.product_id
LEFT JOIN purchase_orders po ON p.product_id = po.product_id
GROUP BY p.product_id, p.product_name, pc.category_name
ORDER BY (COALESCE(SUM(st.total_amount), 0) - COALESCE(SUM(po.total_cost), 0)) DESC;

-- Business Value: Complete product profitability analysis with ROI calculations
-- Validates: Advanced aggregations and financial calculations

-- ===================================================================
-- SECTION 3: ULTIMATE TEST - ALL TABLES IN ONE QUERY
-- ===================================================================

-- ===================================================================
-- ULTIMATE TEST: COMPLETE DATABASE QUERY (ALL 7 TABLES)
-- Purpose: Prove that data can be retrieved from all tables in one query
-- Tables: All 7 tables (sales_transactions, products, product_categories, 
--          customers, vendors, inventory, purchase_orders)
-- ===================================================================
SELECT '=== ULTIMATE TEST: ALL 7 TABLES IN ONE QUERY ===' as test_description;

SELECT 
    -- Sales Transaction Info (Table 1: sales_transactions)
    st.transaction_id as "Transaction_ID",
    st.sale_date as "Sale_Date",
    st.payment_method as "Payment_Method",
    
    -- Product Information (Table 2: products)
    p.product_id as "Product_ID",
    p.product_name as "Product_Name",
    p.unit_of_measure as "Unit",
    p.location_code as "Location",
    
    -- Category Information (Table 3: product_categories)
    pc.category_name as "Category",
    
    -- Customer Information (Table 4: customers)
    COALESCE(CONCAT(c.first_name, ' ', c.last_name), 'Walk-in Customer') as "Customer",
    c.email as "Customer_Email",
    c.city as "Customer_City",
    
    -- Vendor Information (Table 5: vendors)
    v.vendor_name as "Primary_Vendor",
    v.city as "Vendor_City",
    v.state as "Vendor_State",
    
    -- Inventory Information (Table 6: inventory)
    i.quantity_on_hand as "Stock_Level",
    i.reorder_level as "Reorder_Level",
    
    -- Purchase Order Information (Table 7: purchase_orders - Latest)
    latest_po.purchase_date as "Last_Restocked",
    CONCAT('$', FORMAT(latest_po.unit_cost, 2)) as "Last_Purchase_Cost",
    
    -- Sales Transaction Details
    st.quantity_sold as "Qty_Sold",
    CONCAT('$', FORMAT(st.unit_price, 2)) as "Unit_Price",
    CONCAT('$', FORMAT(st.total_amount, 2)) as "Total_Sale",
    
    -- Calculated Business Metrics
    CONCAT('$', FORMAT(st.unit_price - COALESCE(latest_po.unit_cost, 0), 2)) as "Profit_Per_Unit",
    CONCAT('$', FORMAT((st.unit_price - COALESCE(latest_po.unit_cost, 0)) * st.quantity_sold, 2)) as "Transaction_Profit"

FROM sales_transactions st                    -- TABLE 1: Sales Transactions
INNER JOIN products p ON st.product_id = p.product_id              -- TABLE 2: Products
INNER JOIN product_categories pc ON p.category_id = pc.category_id -- TABLE 3: Product Categories  
LEFT JOIN customers c ON st.customer_id = c.customer_id            -- TABLE 4: Customers
LEFT JOIN vendors v ON p.primary_vendor_id = v.vendor_id           -- TABLE 5: Vendors
INNER JOIN inventory i ON p.product_id = i.product_id              -- TABLE 6: Inventory
LEFT JOIN (                                                        -- TABLE 7: Purchase Orders (Latest)
    SELECT 
        po1.product_id,
        po1.purchase_date,
        po1.unit_cost
    FROM purchase_orders po1
    INNER JOIN (
        SELECT product_id, MAX(purchase_date) as max_date
        FROM purchase_orders
        GROUP BY product_id
    ) po2 ON po1.product_id = po2.product_id AND po1.purchase_date = po2.max_date
) latest_po ON p.product_id = latest_po.product_id

ORDER BY st.sale_date DESC, st.transaction_id;

-- VALIDATION: This query successfully joins all 7 tables
-- Expected Results: 13 sales transactions with complete business context
-- Demonstrates: Complete database integration and complex JOIN operations

-- ===================================================================
-- SECTION 4: DATABASE STATISTICS AND VALIDATION
-- ===================================================================

-- ===================================================================
-- DATABASE STATISTICS SUMMARY
-- Purpose: Validate data migration and database integrity
-- ===================================================================
SELECT '=== DATABASE STATISTICS AND VALIDATION ===' as test_description;

-- Table record counts
SELECT 'product_categories' as table_name, COUNT(*) as record_count FROM product_categories
UNION ALL
SELECT 'vendors' as table_name, COUNT(*) as record_count FROM vendors
UNION ALL
SELECT 'products' as table_name, COUNT(*) as record_count FROM products
UNION ALL
SELECT 'customers' as table_name, COUNT(*) as record_count FROM customers
UNION ALL
SELECT 'inventory' as table_name, COUNT(*) as record_count FROM inventory
UNION ALL
SELECT 'purchase_orders' as table_name, COUNT(*) as record_count FROM purchase_orders
UNION ALL
SELECT 'sales_transactions' as table_name, COUNT(*) as record_count FROM sales_transactions
ORDER BY table_name;

-- ===================================================================
-- FOREIGN KEY INTEGRITY VALIDATION
-- Purpose: Ensure all foreign key relationships are properly maintained
-- ===================================================================
SELECT '=== FOREIGN KEY INTEGRITY CHECK ===' as test_description;

-- Check for orphaned records (should return 0 for all)
SELECT 
    'products with invalid category_id' as check_description,
    COUNT(*) as orphaned_records
FROM products p
LEFT JOIN product_categories pc ON p.category_id = pc.category_id
WHERE p.category_id IS NOT NULL AND pc.category_id IS NULL

UNION ALL

SELECT 
    'products with invalid primary_vendor_id' as check_description,
    COUNT(*) as orphaned_records
FROM products p
LEFT JOIN vendors v ON p.primary_vendor_id = v.vendor_id
WHERE p.primary_vendor_id IS NOT NULL AND v.vendor_id IS NULL

UNION ALL

SELECT 
    'inventory with invalid product_id' as check_description,
    COUNT(*) as orphaned_records
FROM inventory i
LEFT JOIN products p ON i.product_id = p.product_id
WHERE i.product_id IS NOT NULL AND p.product_id IS NULL

UNION ALL

SELECT 
    'purchase_orders with invalid product_id' as check_description,
    COUNT(*) as orphaned_records
FROM purchase_orders po
LEFT JOIN products p ON po.product_id = p.product_id
WHERE po.product_id IS NOT NULL AND p.product_id IS NULL

UNION ALL

SELECT 
    'purchase_orders with invalid vendor_id' as check_description,
    COUNT(*) as orphaned_records
FROM purchase_orders po
LEFT JOIN vendors v ON po.vendor_id = v.vendor_id
WHERE po.vendor_id IS NOT NULL AND v.vendor_id IS NULL

UNION ALL

SELECT 
    'sales_transactions with invalid product_id' as check_description,
    COUNT(*) as orphaned_records
FROM sales_transactions st
LEFT JOIN products p ON st.product_id = p.product_id
WHERE st.product_id IS NOT NULL AND p.product_id IS NULL

UNION ALL

SELECT 
    'sales_transactions with invalid customer_id' as check_description,
    COUNT(*) as orphaned_records
FROM sales_transactions st
LEFT JOIN customers c ON st.customer_id = c.customer_id
WHERE st.customer_id IS NOT NULL AND c.customer_id IS NULL;

-- Expected Results: All orphaned_records counts should be 0
-- Validates: Complete referential integrity

-- ===================================================================
-- TESTING SCRIPT COMPLETION SUMMARY
-- ===================================================================
SELECT '=== TESTING SCRIPT COMPLETION SUMMARY ===' as summary;
SELECT 'Database Testing Requirements Fulfillment:' as status;
SELECT '✓ Table joining demonstrations (2, 3, and 4-table joins) - COMPLETED' as requirement_1;
SELECT '✓ Business question queries (purchase orders, customer analytics, inventory) - COMPLETED' as requirement_2;
SELECT '✓ All tables in one query (complete 7-table join) - COMPLETED' as requirement_3;
SELECT '✓ Data integrity validation - COMPLETED' as requirement_4;
SELECT 'Portfolio Project Status: READY FOR PRESENTATION' as final_status;

-- ===================================================================
-- END OF TESTING SCRIPT
-- ===================================================================