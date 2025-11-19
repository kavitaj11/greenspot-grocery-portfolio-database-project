-- =====================================================
-- Greenspot Grocer Database Validation Queries
-- =====================================================

USE greenspot_grocer;

-- =====================================================
-- 1. DATA INTEGRITY VALIDATION
-- =====================================================

-- Check for referential integrity
SELECT 'Checking referential integrity...' as validation_step;

-- Products without categories
SELECT 'Products without categories:' as check_type, COUNT(*) as count
FROM products p 
LEFT JOIN product_categories pc ON p.category_id = pc.category_id 
WHERE pc.category_id IS NULL;

-- Products without inventory
SELECT 'Products without inventory:' as check_type, COUNT(*) as count
FROM products p 
LEFT JOIN inventory i ON p.product_id = i.product_id 
WHERE i.product_id IS NULL;

-- Sales with invalid product references
SELECT 'Sales with invalid products:' as check_type, COUNT(*) as count
FROM sales_transactions st 
LEFT JOIN products p ON st.product_id = p.product_id 
WHERE p.product_id IS NULL;

-- Purchases with invalid vendor references
SELECT 'Purchases with invalid vendors:' as check_type, COUNT(*) as count
FROM purchase_orders po 
LEFT JOIN vendors v ON po.vendor_id = v.vendor_id 
WHERE v.vendor_id IS NULL;

-- =====================================================
-- 2. DATA COMPLETENESS VALIDATION
-- =====================================================

SELECT 'Data completeness summary...' as validation_step;

-- Count records in each table
SELECT 'product_categories' as table_name, COUNT(*) as record_count FROM product_categories
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
SELECT 'sales_transactions', COUNT(*) FROM sales_transactions
ORDER BY table_name;

-- =====================================================
-- 3. BUSINESS LOGIC VALIDATION
-- =====================================================

-- Products with negative inventory (potential data quality issue)
SELECT 'Products with negative inventory:' as validation_check;
SELECT p.product_id, p.product_name, i.quantity_on_hand
FROM products p
JOIN inventory i ON p.product_id = i.product_id
WHERE i.quantity_on_hand < 0;

-- Sales with zero or negative quantities (data quality issue)
SELECT 'Sales with invalid quantities:' as validation_check;
SELECT transaction_id, product_id, quantity_sold, sale_date
FROM sales_transactions
WHERE quantity_sold <= 0;

-- Purchases with zero or negative costs (data quality issue)
SELECT 'Purchases with invalid costs:' as validation_check;
SELECT purchase_id, product_id, unit_cost, purchase_date
FROM purchase_orders
WHERE unit_cost <= 0;

-- =====================================================
-- 4. RELATIONSHIP VALIDATION THROUGH JOINS
-- =====================================================

-- Complete product information with all relationships
SELECT 'Complete product catalog with relationships:' as query_description;
SELECT 
    p.product_id,
    p.product_name,
    pc.category_name,
    p.unit_of_measure,
    p.location_code,
    i.quantity_on_hand,
    v.vendor_name as primary_vendor,
    COUNT(DISTINCT po.purchase_id) as total_purchases,
    COUNT(DISTINCT st.transaction_id) as total_sales
FROM products p
LEFT JOIN product_categories pc ON p.category_id = pc.category_id
LEFT JOIN inventory i ON p.product_id = i.product_id
LEFT JOIN vendors v ON p.primary_vendor_id = v.vendor_id
LEFT JOIN purchase_orders po ON p.product_id = po.product_id
LEFT JOIN sales_transactions st ON p.product_id = st.product_id
GROUP BY p.product_id, p.product_name, pc.category_name, 
         p.unit_of_measure, p.location_code, i.quantity_on_hand, v.vendor_name
ORDER BY p.product_id;

-- Customer transaction history
SELECT 'Customer transaction summary:' as query_description;
SELECT 
    c.customer_id,
    CONCAT(c.first_name, ' ', c.last_name) as customer_name,
    COUNT(st.transaction_id) as total_transactions,
    SUM(st.quantity_sold) as total_items_purchased,
    SUM(st.total_amount) as total_spent,
    MIN(st.sale_date) as first_purchase,
    MAX(st.sale_date) as last_purchase
FROM customers c
LEFT JOIN sales_transactions st ON c.customer_id = st.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name
HAVING COUNT(st.transaction_id) > 0
ORDER BY total_spent DESC;

-- Vendor performance analysis
SELECT 'Vendor performance summary:' as query_description;
SELECT 
    v.vendor_id,
    v.vendor_name,
    v.city,
    v.state,
    COUNT(DISTINCT po.product_id) as products_supplied,
    COUNT(po.purchase_id) as total_orders,
    SUM(po.quantity_ordered) as total_quantity_supplied,
    SUM(po.total_cost) as total_business_value,
    AVG(po.unit_cost) as avg_unit_cost,
    MIN(po.purchase_date) as first_order,
    MAX(po.purchase_date) as last_order
FROM vendors v
LEFT JOIN purchase_orders po ON v.vendor_id = po.vendor_id
GROUP BY v.vendor_id, v.vendor_name, v.city, v.state
HAVING COUNT(po.purchase_id) > 0
ORDER BY total_business_value DESC;

-- =====================================================
-- 5. FINANCIAL VALIDATION
-- =====================================================

-- Revenue and cost analysis
SELECT 'Financial summary:' as analysis_type;
SELECT 
    'Total Revenue' as metric,
    CONCAT('$', FORMAT(SUM(total_amount), 2)) as value
FROM sales_transactions
UNION ALL
SELECT 
    'Total Procurement Cost',
    CONCAT('$', FORMAT(SUM(total_cost), 2))
FROM purchase_orders
UNION ALL
SELECT 
    'Gross Margin (Revenue - Cost)',
    CONCAT('$', FORMAT(
        (SELECT SUM(total_amount) FROM sales_transactions) - 
        (SELECT SUM(total_cost) FROM purchase_orders), 2))
UNION ALL
SELECT 
    'Average Transaction Value',
    CONCAT('$', FORMAT(AVG(total_amount), 2))
FROM sales_transactions
UNION ALL
SELECT 
    'Total Transactions',
    FORMAT(COUNT(*), 0)
FROM sales_transactions;

-- Product profitability analysis
SELECT 'Product profitability analysis:' as analysis_type;
SELECT 
    p.product_id,
    p.product_name,
    pc.category_name,
    SUM(st.total_amount) as total_revenue,
    SUM(po.total_cost) as total_cost,
    SUM(st.total_amount) - SUM(po.total_cost) as gross_profit,
    ROUND(
        ((SUM(st.total_amount) - SUM(po.total_cost)) / SUM(st.total_amount)) * 100, 2
    ) as profit_margin_percent
FROM products p
JOIN product_categories pc ON p.category_id = pc.category_id
LEFT JOIN sales_transactions st ON p.product_id = st.product_id
LEFT JOIN purchase_orders po ON p.product_id = po.product_id
WHERE st.total_amount IS NOT NULL AND po.total_cost IS NOT NULL
GROUP BY p.product_id, p.product_name, pc.category_name
ORDER BY gross_profit DESC;

-- =====================================================
-- 6. INVENTORY VALIDATION
-- =====================================================

-- Low stock alerts
SELECT 'Inventory alerts:' as alert_type;
SELECT 
    p.product_id,
    p.product_name,
    pc.category_name,
    i.quantity_on_hand,
    i.reorder_level,
    CASE 
        WHEN i.quantity_on_hand <= i.reorder_level THEN 'REORDER NEEDED'
        WHEN i.quantity_on_hand <= (i.reorder_level * 1.5) THEN 'LOW STOCK'
        ELSE 'OK'
    END as stock_status
FROM products p
JOIN inventory i ON p.product_id = i.product_id
JOIN product_categories pc ON p.category_id = pc.category_id
WHERE i.quantity_on_hand <= (i.reorder_level * 1.5)
ORDER BY i.quantity_on_hand ASC;

-- Inventory turnover by category
SELECT 'Inventory turnover by category:' as analysis_type;
SELECT 
    pc.category_name,
    SUM(i.quantity_on_hand) as total_on_hand,
    SUM(st.quantity_sold) as total_sold,
    ROUND(
        SUM(st.quantity_sold) / NULLIF(SUM(i.quantity_on_hand), 0), 2
    ) as turnover_ratio
FROM product_categories pc
JOIN products p ON pc.category_id = p.category_id
LEFT JOIN inventory i ON p.product_id = i.product_id
LEFT JOIN sales_transactions st ON p.product_id = st.product_id
GROUP BY pc.category_name
ORDER BY turnover_ratio DESC;

-- =====================================================
-- 7. TIME-BASED ANALYSIS VALIDATION
-- =====================================================

-- Sales trends by date
SELECT 'Daily sales summary:' as trend_analysis;
SELECT 
    sale_date,
    COUNT(transaction_id) as transaction_count,
    SUM(quantity_sold) as total_items_sold,
    SUM(total_amount) as daily_revenue
FROM sales_transactions
WHERE sale_date IS NOT NULL
GROUP BY sale_date
ORDER BY sale_date;

-- Purchase trends by date
SELECT 'Daily purchase summary:' as trend_analysis;
SELECT 
    purchase_date,
    COUNT(purchase_id) as purchase_count,
    SUM(quantity_ordered) as total_items_ordered,
    SUM(total_cost) as daily_procurement_cost
FROM purchase_orders
WHERE purchase_date IS NOT NULL
GROUP BY purchase_date
ORDER BY purchase_date;

-- =====================================================
-- 8. DATA QUALITY SUMMARY REPORT
-- =====================================================

SELECT 'DATA QUALITY SUMMARY REPORT' as report_title;

-- Check for duplicate products
SELECT 'Duplicate product check:' as quality_check;
SELECT product_name, COUNT(*) as duplicate_count
FROM products
GROUP BY product_name
HAVING COUNT(*) > 1;

-- Check for products without sales or purchases
SELECT 'Products with no activity:' as quality_check;
SELECT 
    p.product_id,
    p.product_name,
    CASE 
        WHEN po.product_id IS NULL THEN 'No Purchases'
        WHEN st.product_id IS NULL THEN 'No Sales'
        ELSE 'Active'
    END as activity_status
FROM products p
LEFT JOIN purchase_orders po ON p.product_id = po.product_id
LEFT JOIN sales_transactions st ON p.product_id = st.product_id
WHERE po.product_id IS NULL OR st.product_id IS NULL;

-- =====================================================
-- VALIDATION COMPLETE
-- =====================================================
SELECT 'Database validation complete!' as status,
       NOW() as validation_timestamp;