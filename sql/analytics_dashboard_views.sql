-- ===================================================================
-- GREENSPOT GROCER ANALYTICS DASHBOARD
-- Purpose: Business Intelligence Views and Analytics Queries
-- Created: November 2025
-- Author: Database Design Portfolio Project
-- ===================================================================

-- This script creates comprehensive analytics views for business intelligence
-- dashboard, including sales performance, inventory analytics, customer insights,
-- vendor performance, and financial metrics.

USE greenspot_grocer;

-- ===================================================================
-- SECTION 1: SALES ANALYTICS VIEWS
-- ===================================================================

-- ===================================================================
-- VIEW 1: DAILY SALES SUMMARY
-- Purpose: Track daily sales performance and trends
-- ===================================================================
CREATE OR REPLACE VIEW daily_sales_summary AS
SELECT 
    sale_date,
    COUNT(transaction_id) as total_transactions,
    SUM(quantity_sold) as total_items_sold,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_transaction_value,
    MIN(total_amount) as min_transaction,
    MAX(total_amount) as max_transaction,
    COUNT(DISTINCT customer_id) as unique_customers,
    COUNT(DISTINCT product_id) as unique_products_sold
FROM sales_transactions
GROUP BY sale_date
ORDER BY sale_date DESC;

-- ===================================================================
-- VIEW 2: PRODUCT SALES PERFORMANCE
-- Purpose: Analyze product-level sales performance
-- ===================================================================
CREATE OR REPLACE VIEW product_sales_performance AS
SELECT 
    p.product_id,
    p.product_name,
    pc.category_name,
    COUNT(st.transaction_id) as sales_count,
    SUM(st.quantity_sold) as total_units_sold,
    SUM(st.total_amount) as total_revenue,
    AVG(st.unit_price) as avg_selling_price,
    MIN(st.sale_date) as first_sale_date,
    MAX(st.sale_date) as last_sale_date,
    DATEDIFF(MAX(st.sale_date), MIN(st.sale_date)) as sales_period_days
FROM products p
LEFT JOIN sales_transactions st ON p.product_id = st.product_id
LEFT JOIN product_categories pc ON p.category_id = pc.category_id
GROUP BY p.product_id, p.product_name, pc.category_name
ORDER BY total_revenue DESC;

-- ===================================================================
-- VIEW 3: CATEGORY PERFORMANCE ANALYSIS
-- Purpose: Compare performance across product categories
-- ===================================================================
CREATE OR REPLACE VIEW category_performance AS
SELECT 
    pc.category_name,
    COUNT(DISTINCT p.product_id) as products_in_category,
    COUNT(st.transaction_id) as total_sales,
    SUM(st.quantity_sold) as total_units_sold,
    SUM(st.total_amount) as category_revenue,
    AVG(st.total_amount) as avg_transaction_size,
    SUM(st.total_amount) / SUM(SUM(st.total_amount)) OVER() * 100 as revenue_percentage
FROM product_categories pc
LEFT JOIN products p ON pc.category_id = p.category_id
LEFT JOIN sales_transactions st ON p.product_id = st.product_id
GROUP BY pc.category_id, pc.category_name
ORDER BY category_revenue DESC;

-- ===================================================================
-- SECTION 2: CUSTOMER ANALYTICS VIEWS
-- ===================================================================

-- ===================================================================
-- VIEW 4: CUSTOMER SEGMENTATION
-- Purpose: Segment customers by purchase behavior
-- ===================================================================
CREATE OR REPLACE VIEW customer_segmentation AS
SELECT 
    c.customer_id,
    CONCAT(c.first_name, ' ', c.last_name) as customer_name,
    c.email,
    c.city,
    COUNT(st.transaction_id) as total_purchases,
    SUM(st.quantity_sold) as total_items_bought,
    SUM(st.total_amount) as lifetime_value,
    AVG(st.total_amount) as avg_order_value,
    MAX(st.sale_date) as last_purchase_date,
    DATEDIFF(CURDATE(), MAX(st.sale_date)) as days_since_last_purchase,
    CASE 
        WHEN SUM(st.total_amount) >= 50 AND COUNT(st.transaction_id) >= 3 THEN 'VIP Customer'
        WHEN SUM(st.total_amount) >= 25 AND COUNT(st.transaction_id) >= 2 THEN 'Regular Customer'
        WHEN SUM(st.total_amount) >= 10 THEN 'Occasional Customer'
        ELSE 'New Customer'
    END as customer_segment,
    CASE 
        WHEN DATEDIFF(CURDATE(), MAX(st.sale_date)) <= 7 THEN 'Active'
        WHEN DATEDIFF(CURDATE(), MAX(st.sale_date)) <= 30 THEN 'Recent'
        WHEN DATEDIFF(CURDATE(), MAX(st.sale_date)) <= 90 THEN 'At Risk'
        ELSE 'Inactive'
    END as customer_status
FROM customers c
LEFT JOIN sales_transactions st ON c.customer_id = st.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.email, c.city
ORDER BY lifetime_value DESC;

-- ===================================================================
-- VIEW 5: CUSTOMER PURCHASE PATTERNS
-- Purpose: Analyze when and how customers shop
-- ===================================================================
CREATE OR REPLACE VIEW customer_purchase_patterns AS
SELECT 
    DAYNAME(sale_date) as day_of_week,
    HOUR(transaction_time) as hour_of_day,
    COUNT(transaction_id) as transaction_count,
    SUM(total_amount) as revenue,
    AVG(total_amount) as avg_transaction_value,
    COUNT(DISTINCT customer_id) as unique_customers
FROM sales_transactions
GROUP BY DAYNAME(sale_date), HOUR(transaction_time)
ORDER BY 
    FIELD(DAYNAME(sale_date), 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'),
    HOUR(transaction_time);

-- ===================================================================
-- SECTION 3: INVENTORY ANALYTICS VIEWS
-- ===================================================================

-- ===================================================================
-- VIEW 6: INVENTORY HEALTH DASHBOARD
-- Purpose: Monitor inventory levels and identify reorder needs
-- ===================================================================
CREATE OR REPLACE VIEW inventory_health_dashboard AS
SELECT 
    p.product_id,
    p.product_name,
    pc.category_name,
    i.quantity_on_hand,
    i.reorder_level,
    i.max_stock_level,
    CASE 
        WHEN i.quantity_on_hand <= 0 THEN 'OUT_OF_STOCK'
        WHEN i.quantity_on_hand <= i.reorder_level THEN 'REORDER_NEEDED'
        WHEN i.quantity_on_hand <= (i.reorder_level * 1.5) THEN 'LOW_STOCK'
        WHEN i.quantity_on_hand >= i.max_stock_level THEN 'OVERSTOCK'
        ELSE 'HEALTHY'
    END as stock_status,
    ROUND((i.quantity_on_hand / i.max_stock_level) * 100, 1) as stock_percentage,
    v.vendor_name as primary_vendor,
    v.phone as vendor_phone,
    COALESCE(sales_velocity.avg_daily_sales, 0) as avg_daily_sales,
    CASE 
        WHEN COALESCE(sales_velocity.avg_daily_sales, 0) > 0 
        THEN ROUND(i.quantity_on_hand / sales_velocity.avg_daily_sales, 1)
        ELSE NULL
    END as days_of_stock_remaining
FROM products p
JOIN inventory i ON p.product_id = i.product_id
LEFT JOIN product_categories pc ON p.category_id = pc.category_id
LEFT JOIN vendors v ON p.primary_vendor_id = v.vendor_id
LEFT JOIN (
    SELECT 
        product_id,
        AVG(quantity_sold) as avg_daily_sales
    FROM sales_transactions
    GROUP BY product_id
) sales_velocity ON p.product_id = sales_velocity.product_id
ORDER BY 
    FIELD(stock_status, 'OUT_OF_STOCK', 'REORDER_NEEDED', 'LOW_STOCK', 'OVERSTOCK', 'HEALTHY'),
    p.product_name;

-- ===================================================================
-- VIEW 7: INVENTORY TURNOVER ANALYSIS
-- Purpose: Analyze how quickly inventory moves
-- ===================================================================
CREATE OR REPLACE VIEW inventory_turnover_analysis AS
SELECT 
    p.product_id,
    p.product_name,
    pc.category_name,
    COALESCE(SUM(st.quantity_sold), 0) as total_sold,
    COALESCE(AVG(i.quantity_on_hand), 0) as avg_inventory,
    CASE 
        WHEN AVG(i.quantity_on_hand) > 0 
        THEN ROUND(COALESCE(SUM(st.quantity_sold), 0) / AVG(i.quantity_on_hand), 2)
        ELSE 0
    END as turnover_ratio,
    CASE 
        WHEN AVG(i.quantity_on_hand) > 0 AND SUM(st.quantity_sold) > 0
        THEN ROUND(365 / (COALESCE(SUM(st.quantity_sold), 0) / AVG(i.quantity_on_hand)), 1)
        ELSE NULL
    END as days_to_turnover,
    CASE 
        WHEN AVG(i.quantity_on_hand) > 0 THEN
            CASE 
                WHEN COALESCE(SUM(st.quantity_sold), 0) / AVG(i.quantity_on_hand) >= 4 THEN 'Fast Moving'
                WHEN COALESCE(SUM(st.quantity_sold), 0) / AVG(i.quantity_on_hand) >= 2 THEN 'Medium Moving'
                WHEN COALESCE(SUM(st.quantity_sold), 0) / AVG(i.quantity_on_hand) >= 0.5 THEN 'Slow Moving'
                ELSE 'Very Slow Moving'
            END
        ELSE 'No Movement'
    END as movement_category
FROM products p
LEFT JOIN sales_transactions st ON p.product_id = st.product_id
LEFT JOIN inventory i ON p.product_id = i.product_id
LEFT JOIN product_categories pc ON p.category_id = pc.category_id
GROUP BY p.product_id, p.product_name, pc.category_name
ORDER BY turnover_ratio DESC;

-- ===================================================================
-- SECTION 4: VENDOR PERFORMANCE VIEWS
-- ===================================================================

-- ===================================================================
-- VIEW 8: VENDOR PERFORMANCE SCORECARD
-- Purpose: Evaluate vendor performance across multiple metrics
-- ===================================================================
CREATE OR REPLACE VIEW vendor_performance_scorecard AS
SELECT 
    v.vendor_id,
    v.vendor_name,
    v.city,
    v.state,
    COUNT(DISTINCT p.product_id) as products_supplied,
    COUNT(po.purchase_id) as total_orders,
    SUM(po.quantity_ordered) as total_units_ordered,
    SUM(po.total_cost) as total_spent,
    AVG(po.unit_cost) as avg_unit_cost,
    COUNT(CASE WHEN po.status = 'received' THEN 1 END) as orders_received,
    COUNT(CASE WHEN po.status = 'pending' THEN 1 END) as orders_pending,
    ROUND(COUNT(CASE WHEN po.status = 'received' THEN 1 END) / COUNT(po.purchase_id) * 100, 1) as fulfillment_rate,
    AVG(CASE 
        WHEN po.received_date IS NOT NULL 
        THEN DATEDIFF(po.received_date, po.purchase_date)
        ELSE NULL
    END) as avg_delivery_days,
    MIN(po.purchase_date) as first_order_date,
    MAX(po.purchase_date) as last_order_date
FROM vendors v
LEFT JOIN products p ON v.vendor_id = p.primary_vendor_id
LEFT JOIN purchase_orders po ON v.vendor_id = po.vendor_id
GROUP BY v.vendor_id, v.vendor_name, v.city, v.state
ORDER BY total_spent DESC;

-- ===================================================================
-- SECTION 5: FINANCIAL ANALYTICS VIEWS
-- ===================================================================

-- ===================================================================
-- VIEW 9: PROFITABILITY ANALYSIS
-- Purpose: Analyze profit margins by product and category
-- ===================================================================
CREATE OR REPLACE VIEW profitability_analysis AS
SELECT 
    p.product_id,
    p.product_name,
    pc.category_name,
    COALESCE(SUM(st.quantity_sold), 0) as units_sold,
    COALESCE(SUM(st.total_amount), 0) as total_revenue,
    COALESCE(SUM(po.total_cost), 0) as total_cost,
    COALESCE(SUM(st.total_amount), 0) - COALESCE(SUM(po.total_cost), 0) as gross_profit,
    CASE 
        WHEN COALESCE(SUM(st.total_amount), 0) > 0 
        THEN ROUND(((COALESCE(SUM(st.total_amount), 0) - COALESCE(SUM(po.total_cost), 0)) / COALESCE(SUM(st.total_amount), 0)) * 100, 2)
        ELSE 0
    END as profit_margin_percentage,
    CASE 
        WHEN COALESCE(SUM(po.total_cost), 0) > 0 
        THEN ROUND(((COALESCE(SUM(st.total_amount), 0) - COALESCE(SUM(po.total_cost), 0)) / COALESCE(SUM(po.total_cost), 0)) * 100, 2)
        ELSE 0
    END as roi_percentage,
    CASE 
        WHEN COALESCE(SUM(st.quantity_sold), 0) > 0 
        THEN ROUND((COALESCE(SUM(st.total_amount), 0) - COALESCE(SUM(po.total_cost), 0)) / COALESCE(SUM(st.quantity_sold), 0), 2)
        ELSE 0
    END as profit_per_unit
FROM products p
LEFT JOIN product_categories pc ON p.category_id = pc.category_id
LEFT JOIN sales_transactions st ON p.product_id = st.product_id
LEFT JOIN purchase_orders po ON p.product_id = po.product_id
GROUP BY p.product_id, p.product_name, pc.category_name
ORDER BY gross_profit DESC;

-- ===================================================================
-- VIEW 10: FINANCIAL KPI DASHBOARD
-- Purpose: Key financial performance indicators
-- ===================================================================
CREATE OR REPLACE VIEW financial_kpi_dashboard AS
SELECT 
    'Overall Performance' as metric_category,
    SUM(st.total_amount) as total_revenue,
    SUM(po.total_cost) as total_costs,
    SUM(st.total_amount) - SUM(po.total_cost) as gross_profit,
    ROUND(((SUM(st.total_amount) - SUM(po.total_cost)) / SUM(st.total_amount)) * 100, 2) as profit_margin_pct,
    COUNT(DISTINCT st.transaction_id) as total_transactions,
    COUNT(DISTINCT st.customer_id) as unique_customers,
    COUNT(DISTINCT st.product_id) as products_sold,
    ROUND(SUM(st.total_amount) / COUNT(DISTINCT st.transaction_id), 2) as avg_transaction_value,
    ROUND(SUM(st.total_amount) / COUNT(DISTINCT st.customer_id), 2) as avg_customer_value,
    SUM(st.quantity_sold) as total_units_sold
FROM sales_transactions st
LEFT JOIN purchase_orders po ON st.product_id = po.product_id;

-- ===================================================================
-- SECTION 6: DASHBOARD SUMMARY QUERIES
-- ===================================================================

-- ===================================================================
-- QUERY 1: EXECUTIVE SUMMARY
-- Purpose: High-level business metrics for executive dashboard
-- ===================================================================
SELECT '=== EXECUTIVE SUMMARY METRICS ===' as section;

SELECT 
    'Total Revenue' as metric,
    CONCAT('$', FORMAT(SUM(total_amount), 2)) as value,
    'Current Period' as period
FROM sales_transactions
UNION ALL
SELECT 
    'Total Customers' as metric,
    COUNT(DISTINCT customer_id) as value,
    'All Time' as period
FROM sales_transactions
UNION ALL
SELECT 
    'Total Products' as metric,
    COUNT(*) as value,
    'Current Catalog' as period
FROM products
UNION ALL
SELECT 
    'Active Vendors' as metric,
    COUNT(*) as value,
    'Current Partners' as period
FROM vendors
UNION ALL
SELECT 
    'Average Order Value' as metric,
    CONCAT('$', FORMAT(AVG(total_amount), 2)) as value,
    'Current Period' as period
FROM sales_transactions
UNION ALL
SELECT 
    'Total Transactions' as metric,
    COUNT(*) as value,
    'All Time' as period
FROM sales_transactions;

-- ===================================================================
-- QUERY 2: SALES TREND ANALYSIS
-- Purpose: Daily sales trends for dashboard charts
-- ===================================================================
SELECT '=== SALES TREND ANALYSIS ===' as section;

SELECT 
    sale_date,
    COUNT(transaction_id) as transactions,
    SUM(quantity_sold) as units_sold,
    SUM(total_amount) as daily_revenue,
    AVG(total_amount) as avg_transaction_value
FROM sales_transactions
GROUP BY sale_date
ORDER BY sale_date DESC;

-- ===================================================================
-- QUERY 3: TOP PERFORMERS
-- Purpose: Best performing products, customers, and categories
-- ===================================================================
SELECT '=== TOP PERFORMING PRODUCTS ===' as section;

SELECT 
    p.product_name,
    pc.category_name,
    SUM(st.total_amount) as revenue,
    SUM(st.quantity_sold) as units_sold,
    COUNT(st.transaction_id) as sales_count
FROM sales_transactions st
JOIN products p ON st.product_id = p.product_id
LEFT JOIN product_categories pc ON p.category_id = pc.category_id
GROUP BY p.product_id, p.product_name, pc.category_name
ORDER BY revenue DESC
LIMIT 5;

-- ===================================================================
-- QUERY 4: INVENTORY ALERTS
-- Purpose: Critical inventory situations requiring attention
-- ===================================================================
SELECT '=== INVENTORY ALERTS ===' as section;

SELECT 
    p.product_name,
    pc.category_name,
    i.quantity_on_hand,
    i.reorder_level,
    CASE 
        WHEN i.quantity_on_hand <= 0 THEN 'OUT OF STOCK'
        WHEN i.quantity_on_hand <= i.reorder_level THEN 'REORDER NEEDED'
        WHEN i.quantity_on_hand <= (i.reorder_level * 1.5) THEN 'LOW STOCK'
        ELSE 'ADEQUATE'
    END as alert_level,
    v.vendor_name,
    v.phone
FROM products p
JOIN inventory i ON p.product_id = i.product_id
LEFT JOIN product_categories pc ON p.category_id = pc.category_id
LEFT JOIN vendors v ON p.primary_vendor_id = v.vendor_id
WHERE i.quantity_on_hand <= (i.reorder_level * 1.5)
ORDER BY i.quantity_on_hand ASC;

-- ===================================================================
-- VIEW CREATION SUMMARY
-- ===================================================================
SELECT '=== ANALYTICS DASHBOARD VIEWS CREATED ===' as summary;
SELECT 'Views Created Successfully:' as status;
SELECT '✓ daily_sales_summary - Daily sales performance tracking' as view_1;
SELECT '✓ product_sales_performance - Product-level sales analysis' as view_2;
SELECT '✓ category_performance - Category comparison metrics' as view_3;
SELECT '✓ customer_segmentation - Customer behavior analysis' as view_4;
SELECT '✓ customer_purchase_patterns - Shopping pattern insights' as view_5;
SELECT '✓ inventory_health_dashboard - Stock level monitoring' as view_6;
SELECT '✓ inventory_turnover_analysis - Inventory movement tracking' as view_7;
SELECT '✓ vendor_performance_scorecard - Supplier evaluation' as view_8;
SELECT '✓ profitability_analysis - Product profit margins' as view_9;
SELECT '✓ financial_kpi_dashboard - Key financial metrics' as view_10;
SELECT 'Analytics Dashboard Status: READY FOR USE' as final_status;