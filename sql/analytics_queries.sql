-- =====================================================
-- Greenspot Grocer Analytics & Reporting Queries
-- =====================================================

USE greenspot_grocer;

-- =====================================================
-- 1. SALES ANALYTICS
-- =====================================================

-- Top selling products by revenue
SELECT 'TOP SELLING PRODUCTS BY REVENUE' as report_title;
SELECT 
    p.product_id,
    p.product_name,
    pc.category_name,
    SUM(st.quantity_sold) as total_quantity_sold,
    SUM(st.total_amount) as total_revenue,
    AVG(st.unit_price) as avg_price,
    COUNT(st.transaction_id) as transaction_count
FROM products p
JOIN sales_transactions st ON p.product_id = st.product_id
JOIN product_categories pc ON p.category_id = pc.category_id
GROUP BY p.product_id, p.product_name, pc.category_name
ORDER BY total_revenue DESC
LIMIT 10;

-- Sales by category
SELECT 'SALES BY CATEGORY' as report_title;
SELECT 
    pc.category_name,
    COUNT(DISTINCT p.product_id) as products_in_category,
    SUM(st.quantity_sold) as total_items_sold,
    SUM(st.total_amount) as category_revenue,
    AVG(st.unit_price) as avg_item_price
FROM product_categories pc
JOIN products p ON pc.category_id = p.category_id
LEFT JOIN sales_transactions st ON p.product_id = st.product_id
GROUP BY pc.category_name
ORDER BY category_revenue DESC;

-- Customer purchase patterns
SELECT 'CUSTOMER PURCHASE PATTERNS' as report_title;
SELECT 
    c.customer_id,
    COUNT(st.transaction_id) as total_purchases,
    SUM(st.quantity_sold) as total_items,
    SUM(st.total_amount) as total_spent,
    AVG(st.total_amount) as avg_transaction_value,
    MAX(st.sale_date) as last_purchase_date,
    DATEDIFF(CURDATE(), MAX(st.sale_date)) as days_since_last_purchase
FROM customers c
JOIN sales_transactions st ON c.customer_id = st.customer_id
GROUP BY c.customer_id
ORDER BY total_spent DESC;

-- =====================================================
-- 2. INVENTORY ANALYTICS
-- =====================================================

-- Current inventory status
SELECT 'CURRENT INVENTORY STATUS' as report_title;
SELECT 
    p.product_id,
    p.product_name,
    pc.category_name,
    i.quantity_on_hand,
    i.reorder_level,
    v.vendor_name,
    CASE 
        WHEN i.quantity_on_hand = 0 THEN 'OUT OF STOCK'
        WHEN i.quantity_on_hand <= i.reorder_level THEN 'REORDER NOW'
        WHEN i.quantity_on_hand <= (i.reorder_level * 2) THEN 'LOW STOCK'
        ELSE 'ADEQUATE'
    END as stock_status
FROM products p
JOIN inventory i ON p.product_id = i.product_id
JOIN product_categories pc ON p.category_id = pc.category_id
LEFT JOIN vendors v ON p.primary_vendor_id = v.vendor_id
ORDER BY 
    CASE 
        WHEN i.quantity_on_hand = 0 THEN 1
        WHEN i.quantity_on_hand <= i.reorder_level THEN 2
        WHEN i.quantity_on_hand <= (i.reorder_level * 2) THEN 3
        ELSE 4
    END, i.quantity_on_hand ASC;

-- Inventory value analysis
SELECT 'INVENTORY VALUE ANALYSIS' as report_title;
SELECT 
    pc.category_name,
    SUM(i.quantity_on_hand) as total_units,
    AVG(po.unit_cost) as avg_unit_cost,
    SUM(i.quantity_on_hand * po.unit_cost) as estimated_inventory_value
FROM product_categories pc
JOIN products p ON pc.category_id = p.category_id
JOIN inventory i ON p.product_id = i.product_id
JOIN (
    SELECT product_id, AVG(unit_cost) as unit_cost
    FROM purchase_orders
    GROUP BY product_id
) po ON p.product_id = po.product_id
GROUP BY pc.category_name
ORDER BY estimated_inventory_value DESC;

-- =====================================================
-- 3. VENDOR ANALYTICS
-- =====================================================

-- Vendor performance scorecard
SELECT 'VENDOR PERFORMANCE SCORECARD' as report_title;
SELECT 
    v.vendor_name,
    v.city,
    v.state,
    COUNT(DISTINCT p.product_id) as products_supplied,
    COUNT(po.purchase_id) as total_orders,
    SUM(po.total_cost) as total_business,
    AVG(po.unit_cost) as avg_unit_cost,
    DATEDIFF(CURDATE(), MAX(po.purchase_date)) as days_since_last_order
FROM vendors v
JOIN purchase_orders po ON v.vendor_id = po.vendor_id
JOIN products p ON po.product_id = p.product_id
GROUP BY v.vendor_id, v.vendor_name, v.city, v.state
ORDER BY total_business DESC;

-- Product sourcing analysis
SELECT 'PRODUCT SOURCING ANALYSIS' as report_title;
SELECT 
    p.product_id,
    p.product_name,
    COUNT(DISTINCT po.vendor_id) as vendor_count,
    MIN(po.unit_cost) as lowest_cost,
    MAX(po.unit_cost) as highest_cost,
    AVG(po.unit_cost) as avg_cost,
    (MAX(po.unit_cost) - MIN(po.unit_cost)) / MIN(po.unit_cost) * 100 as price_variance_percent
FROM products p
JOIN purchase_orders po ON p.product_id = po.product_id
GROUP BY p.product_id, p.product_name
HAVING COUNT(DISTINCT po.vendor_id) > 1
ORDER BY price_variance_percent DESC;

-- =====================================================
-- 4. FINANCIAL ANALYTICS
-- =====================================================

-- Profitability by product
SELECT 'PROFITABILITY BY PRODUCT' as report_title;
SELECT 
    p.product_id,
    p.product_name,
    pc.category_name,
    COALESCE(revenue.total_revenue, 0) as revenue,
    COALESCE(costs.total_cost, 0) as cost,
    COALESCE(revenue.total_revenue, 0) - COALESCE(costs.total_cost, 0) as profit,
    CASE 
        WHEN COALESCE(revenue.total_revenue, 0) > 0 THEN
            ROUND(((COALESCE(revenue.total_revenue, 0) - COALESCE(costs.total_cost, 0)) / revenue.total_revenue) * 100, 2)
        ELSE 0
    END as profit_margin_percent
FROM products p
JOIN product_categories pc ON p.category_id = pc.category_id
LEFT JOIN (
    SELECT product_id, SUM(total_amount) as total_revenue
    FROM sales_transactions
    GROUP BY product_id
) revenue ON p.product_id = revenue.product_id
LEFT JOIN (
    SELECT product_id, SUM(total_cost) as total_cost
    FROM purchase_orders
    GROUP BY product_id
) costs ON p.product_id = costs.product_id
WHERE revenue.total_revenue IS NOT NULL OR costs.total_cost IS NOT NULL
ORDER BY profit DESC;

-- Monthly financial summary
SELECT 'MONTHLY FINANCIAL SUMMARY' as report_title;
SELECT 
    DATE_FORMAT(sale_date, '%Y-%m') as month,
    COUNT(transaction_id) as transactions,
    SUM(quantity_sold) as items_sold,
    SUM(total_amount) as revenue,
    AVG(total_amount) as avg_transaction_value
FROM sales_transactions
WHERE sale_date IS NOT NULL
GROUP BY DATE_FORMAT(sale_date, '%Y-%m')
ORDER BY month;

-- =====================================================
-- 5. OPERATIONAL ANALYTICS
-- =====================================================

-- Product location efficiency
SELECT 'PRODUCT LOCATION ANALYSIS' as report_title;
SELECT 
    p.location_code,
    COUNT(p.product_id) as products_stored,
    SUM(i.quantity_on_hand) as total_items,
    AVG(i.quantity_on_hand) as avg_quantity_per_product
FROM products p
JOIN inventory i ON p.product_id = i.product_id
GROUP BY p.location_code
ORDER BY total_items DESC;

-- Sales velocity analysis
SELECT 'SALES VELOCITY ANALYSIS' as report_title;
SELECT 
    p.product_id,
    p.product_name,
    i.quantity_on_hand,
    SUM(st.quantity_sold) as total_sold,
    COUNT(DISTINCT st.sale_date) as days_with_sales,
    CASE 
        WHEN COUNT(DISTINCT st.sale_date) > 0 THEN
            ROUND(SUM(st.quantity_sold) / COUNT(DISTINCT st.sale_date), 2)
        ELSE 0
    END as avg_daily_sales,
    CASE 
        WHEN SUM(st.quantity_sold) > 0 AND COUNT(DISTINCT st.sale_date) > 0 THEN
            ROUND(i.quantity_on_hand / (SUM(st.quantity_sold) / COUNT(DISTINCT st.sale_date)), 1)
        ELSE NULL
    END as days_of_stock_remaining
FROM products p
JOIN inventory i ON p.product_id = i.product_id
LEFT JOIN sales_transactions st ON p.product_id = st.product_id
GROUP BY p.product_id, p.product_name, i.quantity_on_hand
ORDER BY days_of_stock_remaining ASC;

-- =====================================================
-- 6. GROWTH ANALYSIS
-- =====================================================

-- Product performance trends
SELECT 'PRODUCT GROWTH TRENDS' as report_title;
SELECT 
    p.product_name,
    early_sales.early_revenue,
    recent_sales.recent_revenue,
    recent_sales.recent_revenue - early_sales.early_revenue as revenue_growth,
    CASE 
        WHEN early_sales.early_revenue > 0 THEN
            ROUND(((recent_sales.recent_revenue - early_sales.early_revenue) / early_sales.early_revenue) * 100, 2)
        ELSE NULL
    END as growth_percentage
FROM products p
JOIN (
    SELECT product_id, SUM(total_amount) as early_revenue
    FROM sales_transactions
    WHERE sale_date <= '2022-02-07'
    GROUP BY product_id
) early_sales ON p.product_id = early_sales.product_id
JOIN (
    SELECT product_id, SUM(total_amount) as recent_revenue
    FROM sales_transactions
    WHERE sale_date > '2022-02-07'
    GROUP BY product_id
) recent_sales ON p.product_id = recent_sales.product_id
ORDER BY growth_percentage DESC;

-- Category growth analysis
SELECT 'CATEGORY GROWTH ANALYSIS' as report_title;
SELECT 
    pc.category_name,
    early.early_sales,
    recent.recent_sales,
    recent.recent_sales - early.early_sales as sales_growth,
    ROUND(((recent.recent_sales - early.early_sales) / early.early_sales) * 100, 2) as growth_rate
FROM product_categories pc
JOIN (
    SELECT p.category_id, SUM(st.total_amount) as early_sales
    FROM products p
    JOIN sales_transactions st ON p.product_id = st.product_id
    WHERE st.sale_date <= '2022-02-07'
    GROUP BY p.category_id
) early ON pc.category_id = early.category_id
JOIN (
    SELECT p.category_id, SUM(st.total_amount) as recent_sales
    FROM products p
    JOIN sales_transactions st ON p.product_id = st.product_id
    WHERE st.sale_date > '2022-02-07'
    GROUP BY p.category_id
) recent ON pc.category_id = recent.category_id
ORDER BY growth_rate DESC;