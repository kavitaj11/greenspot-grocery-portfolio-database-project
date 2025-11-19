#!/usr/bin/env python3
"""
Greenspot Grocer Interactive Web Dashboard
Purpose: Streamlit-based interactive analytics dashboard
Created: November 2025
Author: Database Design Portfolio Project

Run with: streamlit run streamlit_dashboard.py
"""

import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Import configuration
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import DATABASE_CONFIG

# Page configuration
st.set_page_config(
    page_title="Greenspot Grocer Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E8B57;
        margin-bottom: 1rem;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_database_connection():
    """Create cached database connection"""
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def execute_query(query):
    """Execute SQL query"""
    conn = get_database_connection()
    if conn:
        try:
            df = pd.read_sql(query, conn)
            return df
        except Exception as e:
            st.error(f"Query execution failed: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

def get_executive_summary():
    """Get executive summary metrics"""
    query = """
    SELECT 
        SUM(st.total_amount) as total_revenue,
        COUNT(DISTINCT st.customer_id) as total_customers,
        COUNT(DISTINCT st.product_id) as products_sold,
        COUNT(st.transaction_id) as total_transactions,
        AVG(st.total_amount) as avg_order_value,
        SUM(st.quantity_sold) as total_units_sold
    FROM sales_transactions st
    """
    return execute_query(query)

def get_daily_sales():
    """Get daily sales data"""
    query = """
    SELECT 
        sale_date,
        COUNT(transaction_id) as transactions,
        SUM(quantity_sold) as units_sold,
        SUM(total_amount) as daily_revenue,
        AVG(total_amount) as avg_transaction_value
    FROM sales_transactions
    GROUP BY sale_date
    ORDER BY sale_date
    """
    return execute_query(query)

def get_product_performance():
    """Get product performance data"""
    query = """
    SELECT 
        p.product_name,
        pc.category_name,
        SUM(st.quantity_sold) as units_sold,
        SUM(st.total_amount) as revenue,
        COUNT(st.transaction_id) as sales_count,
        AVG(st.unit_price) as avg_price
    FROM products p
    LEFT JOIN sales_transactions st ON p.product_id = st.product_id
    LEFT JOIN product_categories pc ON p.category_id = pc.category_id
    GROUP BY p.product_id, p.product_name, pc.category_name
    HAVING SUM(st.total_amount) > 0
    ORDER BY revenue DESC
    """
    return execute_query(query)

def get_category_performance():
    """Get category performance data"""
    query = """
    SELECT 
        pc.category_name,
        COUNT(DISTINCT p.product_id) as products_count,
        SUM(st.quantity_sold) as total_units_sold,
        SUM(st.total_amount) as category_revenue,
        COUNT(st.transaction_id) as total_transactions
    FROM product_categories pc
    LEFT JOIN products p ON pc.category_id = p.category_id
    LEFT JOIN sales_transactions st ON p.product_id = st.product_id
    GROUP BY pc.category_id, pc.category_name
    HAVING SUM(st.total_amount) > 0
    ORDER BY category_revenue DESC
    """
    return execute_query(query)

def get_customer_data():
    """Get customer segmentation data"""
    query = """
    SELECT 
        c.customer_id,
        CONCAT(c.first_name, ' ', c.last_name) as customer_name,
        c.city,
        COUNT(st.transaction_id) as total_purchases,
        SUM(st.total_amount) as lifetime_value,
        AVG(st.total_amount) as avg_order_value,
        CASE 
            WHEN SUM(st.total_amount) >= 50 THEN 'VIP'
            WHEN SUM(st.total_amount) >= 25 THEN 'Regular'
            WHEN SUM(st.total_amount) >= 10 THEN 'Occasional'
            ELSE 'New'
        END as customer_segment
    FROM customers c
    LEFT JOIN sales_transactions st ON c.customer_id = st.customer_id
    GROUP BY c.customer_id, c.first_name, c.last_name, c.city
    ORDER BY lifetime_value DESC
    """
    return execute_query(query)

def get_inventory_status():
    """Get inventory status data"""
    query = """
    SELECT 
        p.product_name,
        pc.category_name,
        i.quantity_on_hand,
        i.reorder_level,
        CASE 
            WHEN i.quantity_on_hand <= 0 THEN 'Out of Stock'
            WHEN i.quantity_on_hand <= i.reorder_level THEN 'Reorder Needed'
            WHEN i.quantity_on_hand <= (i.reorder_level * 1.5) THEN 'Low Stock'
            ELSE 'Healthy'
        END as stock_status,
        v.vendor_name
    FROM products p
    JOIN inventory i ON p.product_id = i.product_id
    LEFT JOIN product_categories pc ON p.category_id = pc.category_id
    LEFT JOIN vendors v ON p.primary_vendor_id = v.vendor_id
    ORDER BY i.quantity_on_hand ASC
    """
    return execute_query(query)

# Main Dashboard
def main():
    """Main dashboard function"""
    
    # Header
    st.markdown('<h1 class="main-header">🛒 Greenspot Grocer Analytics Dashboard</h1>', 
                unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("📊 Dashboard Navigation")
    page = st.sidebar.selectbox(
        "Select Analysis Page",
        ["Executive Summary", "Sales Analytics", "Product Performance", 
         "Customer Insights", "Inventory Management", "Financial Analysis"]
    )
    
    # Executive Summary Page
    if page == "Executive Summary":
        st.header("📈 Executive Summary")
        
        # Get executive summary data
        exec_data = get_executive_summary()
        
        if not exec_data.empty:
            summary = exec_data.iloc[0]
            
            # Key Metrics Row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Total Revenue",
                    value=f"${summary['total_revenue']:,.2f}",
                    delta="All Time"
                )
            
            with col2:
                st.metric(
                    label="Total Customers",
                    value=f"{summary['total_customers']:,}",
                    delta="Active"
                )
            
            with col3:
                st.metric(
                    label="Total Transactions",
                    value=f"{summary['total_transactions']:,}",
                    delta="Completed"
                )
            
            with col4:
                st.metric(
                    label="Avg Order Value",
                    value=f"${summary['avg_order_value']:,.2f}",
                    delta="Per Transaction"
                )
            
            # Additional Metrics
            col5, col6 = st.columns(2)
            
            with col5:
                st.metric(
                    label="Products Sold",
                    value=f"{summary['products_sold']:,}",
                    delta="Unique Items"
                )
            
            with col6:
                st.metric(
                    label="Total Units Sold",
                    value=f"{summary['total_units_sold']:,}",
                    delta="All Products"
                )
        
        # Daily Sales Trend
        st.subheader("📊 Daily Sales Trend")
        daily_sales = get_daily_sales()
        
        if not daily_sales.empty:
            fig = px.line(daily_sales, x='sale_date', y='daily_revenue',
                         title='Daily Revenue Trend',
                         labels={'daily_revenue': 'Daily Revenue ($)', 'sale_date': 'Date'})
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # Sales Analytics Page
    elif page == "Sales Analytics":
        st.header("📊 Sales Analytics")
        
        daily_sales = get_daily_sales()
        
        if not daily_sales.empty:
            # Sales Metrics
            col1, col2 = st.columns(2)
            
            with col1:
                fig1 = px.line(daily_sales, x='sale_date', y='daily_revenue',
                              title='Daily Revenue Trend',
                              labels={'daily_revenue': 'Revenue ($)', 'sale_date': 'Date'})
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                fig2 = px.bar(daily_sales, x='sale_date', y='transactions',
                             title='Daily Transaction Count',
                             labels={'transactions': 'Transactions', 'sale_date': 'Date'})
                st.plotly_chart(fig2, use_container_width=True)
            
            # Units and Average Transaction Value
            col3, col4 = st.columns(2)
            
            with col3:
                fig3 = px.line(daily_sales, x='sale_date', y='units_sold',
                              title='Daily Units Sold',
                              labels={'units_sold': 'Units Sold', 'sale_date': 'Date'})
                st.plotly_chart(fig3, use_container_width=True)
            
            with col4:
                fig4 = px.bar(daily_sales, x='sale_date', y='avg_transaction_value',
                             title='Average Transaction Value',
                             labels={'avg_transaction_value': 'Avg Value ($)', 'sale_date': 'Date'})
                st.plotly_chart(fig4, use_container_width=True)
    
    # Product Performance Page
    elif page == "Product Performance":
        st.header("🏆 Product Performance")
        
        product_data = get_product_performance()
        
        if not product_data.empty:
            # Top Products Table
            st.subheader("Top Performing Products")
            st.dataframe(
                product_data.head(10)[['product_name', 'category_name', 'revenue', 'units_sold', 'sales_count']],
                use_container_width=True
            )
            
            # Product Performance Charts
            col1, col2 = st.columns(2)
            
            with col1:
                top_10 = product_data.head(10)
                fig1 = px.bar(top_10, x='revenue', y='product_name',
                             orientation='h', title='Top 10 Products by Revenue',
                             labels={'revenue': 'Revenue ($)', 'product_name': 'Product'})
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                fig2 = px.bar(top_10, x='units_sold', y='product_name',
                             orientation='h', title='Top 10 Products by Units Sold',
                             labels={'units_sold': 'Units Sold', 'product_name': 'Product'})
                st.plotly_chart(fig2, use_container_width=True)
    
    # Customer Insights Page
    elif page == "Customer Insights":
        st.header("👥 Customer Insights")
        
        customer_data = get_customer_data()
        
        if not customer_data.empty:
            # Customer Segmentation
            segment_counts = customer_data['customer_segment'].value_counts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig1 = px.pie(values=segment_counts.values, names=segment_counts.index,
                             title='Customer Segmentation')
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                fig2 = px.histogram(customer_data, x='lifetime_value', nbins=15,
                                   title='Customer Lifetime Value Distribution',
                                   labels={'lifetime_value': 'Lifetime Value ($)'})
                st.plotly_chart(fig2, use_container_width=True)
            
            # Top Customers Table
            st.subheader("Top Customers by Lifetime Value")
            st.dataframe(
                customer_data.head(10)[['customer_name', 'city', 'total_purchases', 'lifetime_value', 'customer_segment']],
                use_container_width=True
            )
    
    # Inventory Management Page
    elif page == "Inventory Management":
        st.header("📦 Inventory Management")
        
        inventory_data = get_inventory_status()
        
        if not inventory_data.empty:
            # Inventory Status Overview
            status_counts = inventory_data['stock_status'].value_counts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                colors = {'Out of Stock': 'red', 'Reorder Needed': 'orange', 
                         'Low Stock': 'yellow', 'Healthy': 'green'}
                fig1 = px.bar(x=status_counts.index, y=status_counts.values,
                             title='Inventory Status Distribution',
                             labels={'x': 'Stock Status', 'y': 'Number of Products'},
                             color=status_counts.index,
                             color_discrete_map=colors)
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                fig2 = px.pie(values=status_counts.values, names=status_counts.index,
                             title='Inventory Status Breakdown')
                st.plotly_chart(fig2, use_container_width=True)
            
            # Inventory Alerts
            alerts = inventory_data[inventory_data['stock_status'].isin(['Out of Stock', 'Reorder Needed', 'Low Stock'])]
            
            if not alerts.empty:
                st.subheader("⚠️ Inventory Alerts")
                st.dataframe(
                    alerts[['product_name', 'category_name', 'quantity_on_hand', 'reorder_level', 'stock_status', 'vendor_name']],
                    use_container_width=True
                )
            else:
                st.success("✅ All products have healthy stock levels!")
    
    # Financial Analysis Page
    elif page == "Financial Analysis":
        st.header("💰 Financial Analysis")
        
        category_data = get_category_performance()
        
        if not category_data.empty:
            # Category Revenue Performance
            col1, col2 = st.columns(2)
            
            with col1:
                fig1 = px.pie(category_data, values='category_revenue', names='category_name',
                             title='Revenue by Category')
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                fig2 = px.bar(category_data, x='category_name', y='category_revenue',
                             title='Category Revenue Comparison',
                             labels={'category_revenue': 'Revenue ($)', 'category_name': 'Category'})
                st.plotly_chart(fig2, use_container_width=True)
            
            # Category Performance Table
            st.subheader("Category Performance Summary")
            st.dataframe(
                category_data[['category_name', 'products_count', 'total_transactions', 'category_revenue']],
                use_container_width=True
            )
    
    # Footer
    st.markdown("---")
    st.markdown("📊 **Greenspot Grocer Analytics Dashboard** | Portfolio Project | November 2025")

if __name__ == "__main__":
    main()