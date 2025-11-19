-- =====================================================
-- Greenspot Grocer Database Schema
-- Normalized Relational Database Design
-- =====================================================

-- Create database
CREATE DATABASE IF NOT EXISTS greenspot_grocer;
USE greenspot_grocer;

-- Drop tables if they exist (for clean rebuild)
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS sales_transactions;
DROP TABLE IF EXISTS purchase_orders;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS vendors;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS product_categories;
SET FOREIGN_KEY_CHECKS = 1;

-- =====================================================
-- 1. Product Categories Table
-- =====================================================
CREATE TABLE product_categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 2. Vendors Table
-- =====================================================
CREATE TABLE vendors (
    vendor_id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_name VARCHAR(100) NOT NULL,
    address TEXT,
    city VARCHAR(50),
    state VARCHAR(20),
    zip_code VARCHAR(10),
    phone VARCHAR(20),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_vendor_name (vendor_name)
);

-- =====================================================
-- 3. Products Table
-- =====================================================
CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    description TEXT,
    category_id INT,
    unit_of_measure VARCHAR(20) NOT NULL,
    location_code VARCHAR(10),
    primary_vendor_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (category_id) REFERENCES product_categories(category_id),
    FOREIGN KEY (primary_vendor_id) REFERENCES vendors(vendor_id),
    INDEX idx_product_name (product_name),
    INDEX idx_category (category_id),
    INDEX idx_location (location_code)
);

-- =====================================================
-- 4. Customers Table
-- =====================================================
CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(50),
    state VARCHAR(20),
    zip_code VARCHAR(10),
    registration_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_customer_name (last_name, first_name),
    INDEX idx_customer_email (email)
);

-- =====================================================
-- 5. Inventory Table
-- =====================================================
CREATE TABLE inventory (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    quantity_on_hand INT NOT NULL DEFAULT 0,
    reorder_level INT DEFAULT 10,
    max_stock_level INT DEFAULT 100,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    UNIQUE KEY unique_product (product_id),
    INDEX idx_low_stock (quantity_on_hand)
);

-- =====================================================
-- 6. Purchase Orders Table
-- =====================================================
CREATE TABLE purchase_orders (
    purchase_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    vendor_id INT NOT NULL,
    quantity_ordered INT NOT NULL,
    unit_cost DECIMAL(10,2) NOT NULL,
    total_cost DECIMAL(10,2) GENERATED ALWAYS AS (quantity_ordered * unit_cost) STORED,
    purchase_date DATE NOT NULL,
    received_date DATE,
    status ENUM('pending', 'received', 'partial', 'cancelled') DEFAULT 'pending',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id),
    INDEX idx_purchase_date (purchase_date),
    INDEX idx_vendor_date (vendor_id, purchase_date),
    INDEX idx_product_date (product_id, purchase_date)
);

-- =====================================================
-- 7. Sales Transactions Table
-- =====================================================
CREATE TABLE sales_transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    customer_id INT,
    quantity_sold INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(10,2) GENERATED ALWAYS AS (quantity_sold * unit_price) STORED,
    sale_date DATE NOT NULL,
    transaction_time TIME DEFAULT (CURTIME()),
    payment_method ENUM('cash', 'credit', 'debit', 'check') DEFAULT 'cash',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    INDEX idx_sale_date (sale_date),
    INDEX idx_customer_date (customer_id, sale_date),
    INDEX idx_product_date (product_id, sale_date)
);

-- =====================================================
-- Insert Initial Product Categories
-- =====================================================
INSERT INTO product_categories (category_name, description) VALUES
('Dairy', 'Milk, eggs, cheese, and other dairy products'),
('Produce', 'Fresh fruits and vegetables'),
('Canned', 'Canned and preserved goods'),
('Meat', 'Fresh and frozen meat products'),
('Bakery', 'Bread, pastries, and baked goods'),
('Frozen', 'Frozen food products'),
('Pantry', 'Dry goods and pantry staples'),
('Beverages', 'Drinks and beverages'),
('Snacks', 'Snack foods and confectionery'),
('Health', 'Health and wellness products');

-- =====================================================
-- Create Views for Common Queries
-- =====================================================

-- Product inventory with category information
CREATE VIEW v_product_inventory AS
SELECT 
    p.product_id,
    p.product_name,
    p.description,
    pc.category_name,
    p.unit_of_measure,
    p.location_code,
    i.quantity_on_hand,
    i.reorder_level,
    v.vendor_name as primary_vendor
FROM products p
LEFT JOIN product_categories pc ON p.category_id = pc.category_id
LEFT JOIN inventory i ON p.product_id = i.product_id
LEFT JOIN vendors v ON p.primary_vendor_id = v.vendor_id;

-- Sales summary by product
CREATE VIEW v_sales_summary AS
SELECT 
    p.product_id,
    p.product_name,
    pc.category_name,
    COUNT(st.transaction_id) as total_transactions,
    SUM(st.quantity_sold) as total_quantity_sold,
    SUM(st.total_amount) as total_revenue,
    AVG(st.unit_price) as avg_price,
    MAX(st.sale_date) as last_sale_date
FROM products p
LEFT JOIN product_categories pc ON p.category_id = pc.category_id
LEFT JOIN sales_transactions st ON p.product_id = st.product_id
GROUP BY p.product_id, p.product_name, pc.category_name;

-- Purchase summary by vendor
CREATE VIEW v_purchase_summary AS
SELECT 
    v.vendor_id,
    v.vendor_name,
    COUNT(po.purchase_id) as total_orders,
    SUM(po.quantity_ordered) as total_quantity_ordered,
    SUM(po.total_cost) as total_spent,
    AVG(po.unit_cost) as avg_unit_cost,
    MAX(po.purchase_date) as last_order_date
FROM vendors v
LEFT JOIN purchase_orders po ON v.vendor_id = po.vendor_id
GROUP BY v.vendor_id, v.vendor_name;

-- =====================================================
-- Create Indexes for Performance
-- =====================================================
CREATE INDEX idx_sales_amount ON sales_transactions(total_amount);
CREATE INDEX idx_purchase_cost ON purchase_orders(total_cost);
CREATE INDEX idx_inventory_status ON inventory(quantity_on_hand, reorder_level);

-- =====================================================
-- Database Setup Complete
-- =====================================================
SELECT 'Greenspot Grocer database schema created successfully!' as status;