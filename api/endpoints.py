"""
Analytics endpoints for Greenspot Grocer REST API
Contains all business intelligence and analytics REST endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import pandas as pd
from datetime import datetime, date
import mysql.connector
from config import DATABASE_CONFIG
from models import (
    ExecutiveSummary, ProductPerformance, CustomerInsight, 
    SalesMetrics, InventoryStatus
)

# Create router for analytics endpoints
router = APIRouter(prefix="/api/v1", tags=["Analytics"])

@router.get("/executive-summary", response_model=ExecutiveSummary)
async def get_executive_summary(current_user: str = Depends(verify_token)):
    """
    Get executive summary with key business metrics
    
    Returns:
    - Total revenue
    - Total customers
    - Total transactions  
    - Average order value
    - Top performing product
    - Top performing category
    """
    query = """
    SELECT 
        ROUND(SUM(oi.quantity * oi.unit_price), 2) as total_revenue,
        COUNT(DISTINCT o.customer_id) as total_customers,
        COUNT(DISTINCT o.order_id) as total_transactions,
        ROUND(AVG(order_totals.order_total), 2) as average_order_value
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN (
        SELECT order_id, SUM(quantity * unit_price) as order_total
        FROM order_items 
        GROUP BY order_id
    ) order_totals ON o.order_id = order_totals.order_id
    """
    
    summary_df = execute_query(query)
    
    # Get top product
    top_product_query = """
    SELECT p.product_name,
           SUM(oi.quantity * oi.unit_price) as revenue
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY p.product_id, p.product_name
    ORDER BY revenue DESC
    LIMIT 1
    """
    top_product_df = execute_query(top_product_query)
    
    # Get top category
    top_category_query = """
    SELECT c.category_name,
           SUM(oi.quantity * oi.unit_price) as revenue
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    JOIN categories c ON p.category_id = c.category_id
    GROUP BY c.category_id, c.category_name
    ORDER BY revenue DESC
    LIMIT 1
    """
    top_category_df = execute_query(top_category_query)
    
    if summary_df.empty:
        raise HTTPException(status_code=404, detail="No sales data found")
    
    return ExecutiveSummary(
        total_revenue=float(summary_df.iloc[0]['total_revenue']),
        total_customers=int(summary_df.iloc[0]['total_customers']),
        total_transactions=int(summary_df.iloc[0]['total_transactions']),
        average_order_value=float(summary_df.iloc[0]['average_order_value']),
        top_product=top_product_df.iloc[0]['product_name'] if not top_product_df.empty else "N/A",
        top_category=top_category_df.iloc[0]['category_name'] if not top_category_df.empty else "N/A"
    )

@router.get("/products/performance", response_model=List[ProductPerformance])
async def get_product_performance(
    limit: int = Query(10, ge=1, le=100, description="Number of products to return"),
    current_user: str = Depends(verify_token)
):
    """
    Get product performance metrics
    
    Parameters:
    - limit: Number of top products to return (1-100)
    
    Returns list of products with:
    - Product ID and name
    - Total revenue
    - Units sold
    - Average price
    - Category
    """
    query = """
    SELECT 
        p.product_id,
        p.product_name,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) as total_revenue,
        SUM(oi.quantity) as units_sold,
        ROUND(AVG(oi.unit_price), 2) as average_price,
        c.category_name as category
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    JOIN categories c ON p.category_id = c.category_id
    GROUP BY p.product_id, p.product_name, c.category_name
    ORDER BY total_revenue DESC
    LIMIT %s
    """
    
    df = execute_query(query, (limit,))
    
    if df.empty:
        return []
    
    return [
        ProductPerformance(
            product_id=int(row['product_id']),
            product_name=row['product_name'],
            total_revenue=float(row['total_revenue']),
            units_sold=int(row['units_sold']),
            average_price=float(row['average_price']),
            category=row['category']
        )
        for _, row in df.iterrows()
    ]

@router.get("/customers/insights", response_model=List[CustomerInsight])
async def get_customer_insights(
    limit: int = Query(10, ge=1, le=100, description="Number of customers to return"),
    current_user: str = Depends(verify_token)
):
    """
    Get customer insights and analytics
    
    Parameters:
    - limit: Number of top customers to return (1-100)
    
    Returns list of customers with:
    - Customer ID and name
    - Total amount spent
    - Transaction count
    - Average order value
    - Customer segment
    """
    query = """
    SELECT 
        c.customer_id,
        CONCAT(c.first_name, ' ', c.last_name) as customer_name,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) as total_spent,
        COUNT(DISTINCT o.order_id) as transaction_count,
        ROUND(AVG(order_totals.order_total), 2) as average_order_value
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN (
        SELECT order_id, SUM(quantity * unit_price) as order_total
        FROM order_items 
        GROUP BY order_id
    ) order_totals ON o.order_id = order_totals.order_id
    GROUP BY c.customer_id, c.first_name, c.last_name
    ORDER BY total_spent DESC
    LIMIT %s
    """
    
    df = execute_query(query, (limit,))
    
    if df.empty:
        return []
    
    # Simple customer segmentation
    def get_customer_segment(total_spent: float) -> str:
        if total_spent >= 100:
            return "VIP"
        elif total_spent >= 50:
            return "Regular"
        elif total_spent >= 20:
            return "Occasional"
        else:
            return "New"
    
    return [
        CustomerInsight(
            customer_id=int(row['customer_id']),
            customer_name=row['customer_name'],
            total_spent=float(row['total_spent']),
            transaction_count=int(row['transaction_count']),
            average_order_value=float(row['average_order_value']),
            customer_segment=get_customer_segment(float(row['total_spent']))
        )
        for _, row in df.iterrows()
    ]

@router.get("/sales/metrics", response_model=List[SalesMetrics])
async def get_sales_metrics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: str = Depends(verify_token)
):
    """
    Get daily sales metrics
    
    Parameters:
    - days: Number of days to analyze (1-365)
    
    Returns daily metrics:
    - Date
    - Daily revenue
    - Transaction count
    - Units sold
    """
    query = """
    SELECT 
        DATE(o.order_date) as date,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) as daily_revenue,
        COUNT(DISTINCT o.order_id) as transaction_count,
        SUM(oi.quantity) as units_sold
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
    GROUP BY DATE(o.order_date)
    ORDER BY date DESC
    """
    
    df = execute_query(query, (days,))
    
    if df.empty:
        return []
    
    return [
        SalesMetrics(
            date=row['date'].strftime('%Y-%m-%d'),
            daily_revenue=float(row['daily_revenue']),
            transaction_count=int(row['transaction_count']),
            units_sold=int(row['units_sold'])
        )
        for _, row in df.iterrows()
    ]

@router.get("/inventory/status", response_model=List[InventoryStatus])
async def get_inventory_status(current_user: str = Depends(verify_token)):
    """
    Get current inventory status
    
    Returns inventory status for all products:
    - Product ID and name
    - Current stock level
    - Reorder level
    - Reorder needed flag
    - Vendor information
    """
    query = """
    SELECT 
        p.product_id,
        p.product_name,
        p.stock_quantity as current_stock,
        p.reorder_level,
        CASE WHEN p.stock_quantity <= p.reorder_level THEN 1 ELSE 0 END as needs_reorder,
        v.vendor_name
    FROM products p
    LEFT JOIN vendors v ON p.vendor_id = v.vendor_id
    ORDER BY needs_reorder DESC, p.product_name
    """
    
    df = execute_query(query)
    
    if df.empty:
        return []
    
    return [
        InventoryStatus(
            product_id=int(row['product_id']),
            product_name=row['product_name'],
            current_stock=int(row['current_stock']),
            reorder_level=int(row['reorder_level']),
            needs_reorder=bool(row['needs_reorder']),
            vendor_name=row['vendor_name'] if row['vendor_name'] else "N/A"
        )
        for _, row in df.iterrows()
    ]

@router.get("/products/{product_id}/details")
async def get_product_details(
    product_id: int, 
    current_user: str = Depends(verify_token)
):
    """
    Get detailed information for a specific product
    """
    query = """
    SELECT 
        p.*,
        c.category_name,
        v.vendor_name,
        v.contact_info,
        COALESCE(SUM(oi.quantity), 0) as total_sold,
        COALESCE(SUM(oi.quantity * oi.unit_price), 0) as total_revenue
    FROM products p
    LEFT JOIN categories c ON p.category_id = c.category_id
    LEFT JOIN vendors v ON p.vendor_id = v.vendor_id
    LEFT JOIN order_items oi ON p.product_id = oi.product_id
    WHERE p.product_id = %s
    GROUP BY p.product_id
    """
    
    df = execute_query(query, (product_id,))
    
    if df.empty:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product = df.iloc[0]
    return {
        "product_id": int(product['product_id']),
        "product_name": product['product_name'],
        "category": product['category_name'],
        "price": float(product['price']),
        "stock_quantity": int(product['stock_quantity']),
        "reorder_level": int(product['reorder_level']),
        "vendor": {
            "name": product['vendor_name'],
            "contact": product['contact_info']
        },
        "sales_stats": {
            "total_sold": int(product['total_sold']),
            "total_revenue": float(product['total_revenue'])
        }
    }

@router.get("/categories/performance")
async def get_category_performance(current_user: str = Depends(verify_token)):
    """
    Get performance metrics by product category
    """
    query = """
    SELECT 
        c.category_name,
        COUNT(DISTINCT p.product_id) as product_count,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) as total_revenue,
        SUM(oi.quantity) as units_sold,
        ROUND(AVG(oi.unit_price), 2) as average_price
    FROM categories c
    LEFT JOIN products p ON c.category_id = p.category_id
    LEFT JOIN order_items oi ON p.product_id = oi.product_id
    GROUP BY c.category_id, c.category_name
    ORDER BY total_revenue DESC
    """
    
    df = execute_query(query)
    
    if df.empty:
        return []
    
    return [
        {
            "category_name": row['category_name'],
            "product_count": int(row['product_count']),
            "total_revenue": float(row['total_revenue']) if row['total_revenue'] else 0.0,
            "units_sold": int(row['units_sold']) if row['units_sold'] else 0,
            "average_price": float(row['average_price']) if row['average_price'] else 0.0
        }
        for _, row in df.iterrows()
    ]