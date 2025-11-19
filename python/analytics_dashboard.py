#!/usr/bin/env python3
"""
Greenspot Grocer Analytics Dashboard
Purpose: Interactive business intelligence dashboard with visualizations
Created: November 2025
Author: Database Design Portfolio Project

This dashboard provides comprehensive analytics and visualizations for:
- Sales Performance Analysis
- Customer Insights & Segmentation  
- Inventory Management Analytics
- Vendor Performance Metrics
- Financial KPI Tracking
"""

import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from datetime import datetime, timedelta
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Import configuration
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import DATABASE_CONFIG

class GreenspotAnalyticsDashboard:
    """
    Comprehensive analytics dashboard for Greenspot Grocer database
    
    Features:
    - Real-time data connection to MySQL database
    - Interactive visualizations with Plotly
    - Business intelligence metrics and KPIs
    - Multi-page dashboard with different analysis areas
    """
    
    def __init__(self):
        """Initialize dashboard with database connection"""
        self.conn = None
        self.connect_to_database()
        
    def connect_to_database(self):
        """Establish connection to MySQL database"""
        try:
            self.conn = mysql.connector.connect(**DATABASE_CONFIG)
            print("✅ Dashboard connected to database successfully")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
    
    def execute_query(self, query):
        """Execute SQL query and return pandas DataFrame"""
        try:
            df = pd.read_sql(query, self.conn)
            return df
        except Exception as e:
            print(f"❌ Query execution failed: {e}")
            return pd.DataFrame()
    
    def get_executive_summary(self):
        """Get high-level business metrics for executive dashboard"""
        query = """
        SELECT 
            SUM(st.total_amount) as total_revenue,
            COUNT(DISTINCT st.customer_id) as total_customers,
            COUNT(DISTINCT st.product_id) as products_sold,
            COUNT(st.transaction_id) as total_transactions,
            AVG(st.total_amount) as avg_order_value,
            MAX(st.sale_date) as last_sale_date,
            MIN(st.sale_date) as first_sale_date
        FROM sales_transactions st
        """
        return self.execute_query(query)
    
    def get_daily_sales_trend(self):
        """Get daily sales trends for time series analysis"""
        query = """
        SELECT 
            sale_date,
            COUNT(transaction_id) as transactions,
            SUM(quantity_sold) as units_sold,
            SUM(total_amount) as daily_revenue,
            AVG(total_amount) as avg_transaction_value,
            COUNT(DISTINCT customer_id) as unique_customers
        FROM sales_transactions
        GROUP BY sale_date
        ORDER BY sale_date
        """
        return self.execute_query(query)
    
    def get_product_performance(self):
        """Get product-level performance metrics"""
        query = """
        SELECT 
            p.product_name,
            pc.category_name,
            SUM(st.quantity_sold) as units_sold,
            SUM(st.total_amount) as revenue,
            COUNT(st.transaction_id) as sales_count,
            AVG(st.unit_price) as avg_price,
            i.quantity_on_hand as current_stock
        FROM products p
        LEFT JOIN sales_transactions st ON p.product_id = st.product_id
        LEFT JOIN product_categories pc ON p.category_id = pc.category_id
        LEFT JOIN inventory i ON p.product_id = i.product_id
        GROUP BY p.product_id, p.product_name, pc.category_name, i.quantity_on_hand
        ORDER BY revenue DESC
        """
        return self.execute_query(query)
    
    def get_category_performance(self):
        """Get category-level performance analysis"""
        query = """
        SELECT 
            pc.category_name,
            COUNT(DISTINCT p.product_id) as products_count,
            SUM(st.quantity_sold) as total_units_sold,
            SUM(st.total_amount) as category_revenue,
            AVG(st.total_amount) as avg_transaction_size,
            COUNT(st.transaction_id) as total_transactions
        FROM product_categories pc
        LEFT JOIN products p ON pc.category_id = p.category_id
        LEFT JOIN sales_transactions st ON p.product_id = st.product_id
        GROUP BY pc.category_id, pc.category_name
        ORDER BY category_revenue DESC
        """
        return self.execute_query(query)
    
    def get_customer_segmentation(self):
        """Get customer segmentation and lifetime value analysis"""
        query = """
        SELECT 
            c.customer_id,
            CONCAT(c.first_name, ' ', c.last_name) as customer_name,
            c.city,
            COUNT(st.transaction_id) as total_purchases,
            SUM(st.quantity_sold) as total_items,
            SUM(st.total_amount) as lifetime_value,
            AVG(st.total_amount) as avg_order_value,
            MAX(st.sale_date) as last_purchase_date,
            DATEDIFF(CURDATE(), MAX(st.sale_date)) as days_since_last_purchase,
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
        return self.execute_query(query)
    
    def get_inventory_status(self):
        """Get current inventory status and alerts"""
        query = """
        SELECT 
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
            v.vendor_name
        FROM products p
        JOIN inventory i ON p.product_id = i.product_id
        LEFT JOIN product_categories pc ON p.category_id = pc.category_id
        LEFT JOIN vendors v ON p.primary_vendor_id = v.vendor_id
        ORDER BY 
            FIELD(stock_status, 'OUT_OF_STOCK', 'REORDER_NEEDED', 'LOW_STOCK', 'OVERSTOCK', 'HEALTHY'),
            p.product_name
        """
        return self.execute_query(query)
    
    def get_vendor_performance(self):
        """Get vendor performance metrics"""
        query = """
        SELECT 
            v.vendor_name,
            v.city,
            v.state,
            COUNT(DISTINCT p.product_id) as products_supplied,
            COUNT(po.purchase_id) as total_orders,
            SUM(po.total_cost) as total_spent,
            AVG(po.unit_cost) as avg_unit_cost,
            ROUND(COUNT(CASE WHEN po.status = 'received' THEN 1 END) / COUNT(po.purchase_id) * 100, 1) as fulfillment_rate
        FROM vendors v
        LEFT JOIN products p ON v.vendor_id = p.primary_vendor_id
        LEFT JOIN purchase_orders po ON v.vendor_id = po.vendor_id
        GROUP BY v.vendor_id, v.vendor_name, v.city, v.state
        ORDER BY total_spent DESC
        """
        return self.execute_query(query)
    
    def get_profitability_analysis(self):
        """Get product profitability analysis"""
        query = """
        SELECT 
            p.product_name,
            pc.category_name,
            COALESCE(SUM(st.total_amount), 0) as total_revenue,
            COALESCE(SUM(po.total_cost), 0) as total_cost,
            COALESCE(SUM(st.total_amount), 0) - COALESCE(SUM(po.total_cost), 0) as gross_profit,
            CASE 
                WHEN COALESCE(SUM(st.total_amount), 0) > 0 
                THEN ROUND(((COALESCE(SUM(st.total_amount), 0) - COALESCE(SUM(po.total_cost), 0)) / COALESCE(SUM(st.total_amount), 0)) * 100, 2)
                ELSE 0
            END as profit_margin_pct
        FROM products p
        LEFT JOIN product_categories pc ON p.category_id = pc.category_id
        LEFT JOIN sales_transactions st ON p.product_id = st.product_id
        LEFT JOIN purchase_orders po ON p.product_id = po.product_id
        GROUP BY p.product_id, p.product_name, pc.category_name
        HAVING COALESCE(SUM(st.total_amount), 0) > 0
        ORDER BY gross_profit DESC
        """
        return self.execute_query(query)
    
    def create_sales_trend_chart(self, df_sales):
        """Create interactive sales trend visualization"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Daily Revenue Trend', 'Daily Transactions', 'Units Sold', 'Average Transaction Value'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Daily Revenue Trend
        fig.add_trace(
            go.Scatter(x=df_sales['sale_date'], y=df_sales['daily_revenue'],
                      mode='lines+markers', name='Daily Revenue',
                      line=dict(color='#1f77b4', width=3)),
            row=1, col=1
        )
        
        # Daily Transactions
        fig.add_trace(
            go.Bar(x=df_sales['sale_date'], y=df_sales['transactions'],
                   name='Transactions', marker_color='#ff7f0e'),
            row=1, col=2
        )
        
        # Units Sold
        fig.add_trace(
            go.Scatter(x=df_sales['sale_date'], y=df_sales['units_sold'],
                      mode='lines+markers', name='Units Sold',
                      line=dict(color='#2ca02c', width=2)),
            row=2, col=1
        )
        
        # Average Transaction Value
        fig.add_trace(
            go.Bar(x=df_sales['sale_date'], y=df_sales['avg_transaction_value'],
                   name='Avg Transaction Value', marker_color='#d62728'),
            row=2, col=2
        )
        
        fig.update_layout(
            title_text="Sales Performance Dashboard",
            showlegend=False,
            height=600,
            title_x=0.5
        )
        
        return fig
    
    def create_category_performance_chart(self, df_category):
        """Create category performance visualization"""
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Revenue by Category', 'Transaction Count by Category'),
            specs=[[{"type": "pie"}, {"type": "bar"}]]
        )
        
        # Revenue Pie Chart
        fig.add_trace(
            go.Pie(labels=df_category['category_name'], 
                   values=df_category['category_revenue'],
                   name="Revenue"),
            row=1, col=1
        )
        
        # Transaction Count Bar Chart
        fig.add_trace(
            go.Bar(x=df_category['category_name'], 
                   y=df_category['total_transactions'],
                   name="Transactions",
                   marker_color='#17becf'),
            row=1, col=2
        )
        
        fig.update_layout(
            title_text="Category Performance Analysis",
            showlegend=False,
            height=500,
            title_x=0.5
        )
        
        return fig
    
    def create_customer_segmentation_chart(self, df_customers):
        """Create customer segmentation visualization"""
        # Customer segment distribution
        segment_counts = df_customers['customer_segment'].value_counts()
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Customer Segmentation', 'Customer Lifetime Value Distribution'),
            specs=[[{"type": "pie"}, {"type": "histogram"}]]
        )
        
        # Segment Distribution Pie Chart
        fig.add_trace(
            go.Pie(labels=segment_counts.index, 
                   values=segment_counts.values,
                   name="Customer Segments"),
            row=1, col=1
        )
        
        # Lifetime Value Histogram
        fig.add_trace(
            go.Histogram(x=df_customers['lifetime_value'],
                        nbinsx=10,
                        name="Lifetime Value Distribution",
                        marker_color='#ff9999'),
            row=1, col=2
        )
        
        fig.update_layout(
            title_text="Customer Analytics Dashboard",
            showlegend=False,
            height=500,
            title_x=0.5
        )
        
        return fig
    
    def create_inventory_status_chart(self, df_inventory):
        """Create inventory status visualization"""
        # Count products by stock status
        status_counts = df_inventory['stock_status'].value_counts()
        
        # Define colors for different stock statuses
        status_colors = {
            'OUT_OF_STOCK': '#ff0000',
            'REORDER_NEEDED': '#ff6600', 
            'LOW_STOCK': '#ffcc00',
            'HEALTHY': '#00cc00',
            'OVERSTOCK': '#0066cc'
        }
        
        colors = [status_colors.get(status, '#cccccc') for status in status_counts.index]
        
        fig = go.Figure(data=[
            go.Bar(x=status_counts.index, 
                   y=status_counts.values,
                   marker_color=colors,
                   text=status_counts.values,
                   textposition='auto')
        ])
        
        fig.update_layout(
            title="Inventory Health Status",
            xaxis_title="Stock Status",
            yaxis_title="Number of Products",
            title_x=0.5,
            height=400
        )
        
        return fig
    
    def create_profitability_chart(self, df_profit):
        """Create profitability analysis visualization"""
        # Sort by gross profit for better visualization
        df_profit_sorted = df_profit.sort_values('gross_profit', ascending=True).tail(10)
        
        fig = go.Figure()
        
        # Add profit bars
        fig.add_trace(go.Bar(
            y=df_profit_sorted['product_name'],
            x=df_profit_sorted['gross_profit'],
            orientation='h',
            marker_color='#2ca02c',
            name='Gross Profit'
        ))
        
        fig.update_layout(
            title="Top 10 Most Profitable Products",
            xaxis_title="Gross Profit ($)",
            yaxis_title="Product",
            title_x=0.5,
            height=500
        )
        
        return fig
    
    def generate_dashboard_report(self):
        """Generate comprehensive dashboard report"""
        print("🚀 Generating Greenspot Grocer Analytics Dashboard...")
        print("=" * 60)
        
        # Get all data
        exec_summary = self.get_executive_summary()
        daily_sales = self.get_daily_sales_trend()
        product_perf = self.get_product_performance()
        category_perf = self.get_category_performance()
        customer_seg = self.get_customer_segmentation()
        inventory_status = self.get_inventory_status()
        vendor_perf = self.get_vendor_performance()
        profitability = self.get_profitability_analysis()
        
        # Executive Summary
        if not exec_summary.empty:
            summary = exec_summary.iloc[0]
            print("📊 EXECUTIVE SUMMARY")
            print("-" * 30)
            print(f"Total Revenue: ${summary['total_revenue']:,.2f}")
            print(f"Total Customers: {summary['total_customers']:,}")
            print(f"Products Sold: {summary['products_sold']:,}")
            print(f"Total Transactions: {summary['total_transactions']:,}")
            print(f"Average Order Value: ${summary['avg_order_value']:,.2f}")
            print(f"Sales Period: {summary['first_sale_date']} to {summary['last_sale_date']}")
            print()
        
        # Top Products
        if not product_perf.empty:
            print("🏆 TOP PERFORMING PRODUCTS")
            print("-" * 30)
            top_products = product_perf.head(5)
            for _, product in top_products.iterrows():
                print(f"• {product['product_name']}: ${product['revenue']:,.2f} ({product['units_sold']} units)")
            print()
        
        # Category Performance
        if not category_perf.empty:
            print("📈 CATEGORY PERFORMANCE")
            print("-" * 30)
            for _, category in category_perf.iterrows():
                print(f"• {category['category_name']}: ${category['category_revenue']:,.2f} ({category['total_transactions']} transactions)")
            print()
        
        # Customer Insights
        if not customer_seg.empty:
            print("👥 CUSTOMER SEGMENTATION")
            print("-" * 30)
            segment_dist = customer_seg['customer_segment'].value_counts()
            for segment, count in segment_dist.items():
                print(f"• {segment}: {count} customers")
            print()
        
        # Inventory Alerts
        if not inventory_status.empty:
            alerts = inventory_status[inventory_status['stock_status'].isin(['OUT_OF_STOCK', 'REORDER_NEEDED', 'LOW_STOCK'])]
            if not alerts.empty:
                print("⚠️  INVENTORY ALERTS")
                print("-" * 30)
                for _, alert in alerts.iterrows():
                    print(f"• {alert['product_name']}: {alert['stock_status']} ({alert['quantity_on_hand']} units)")
                print()
        
        # Vendor Performance
        if not vendor_perf.empty:
            print("🤝 VENDOR PERFORMANCE")
            print("-" * 30)
            for _, vendor in vendor_perf.iterrows():
                print(f"• {vendor['vendor_name']}: ${vendor['total_spent']:,.2f} spent, {vendor['fulfillment_rate']}% fulfillment rate")
            print()
        
        print("✅ Dashboard report generated successfully!")
        print("=" * 60)
    
    def save_dashboard_charts(self):
        """Save all dashboard charts as HTML files"""
        print("💾 Saving dashboard visualizations...")
        
        # Create output directory
        output_dir = "dashboard_charts"
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Get data
            daily_sales = self.get_daily_sales_trend()
            category_perf = self.get_category_performance()
            customer_seg = self.get_customer_segmentation()
            inventory_status = self.get_inventory_status()
            profitability = self.get_profitability_analysis()
            
            # Create and save charts
            if not daily_sales.empty:
                sales_fig = self.create_sales_trend_chart(daily_sales)
                sales_fig.write_html(f"{output_dir}/sales_trend_dashboard.html")
                print("✅ Sales trend dashboard saved")
            
            if not category_perf.empty:
                category_fig = self.create_category_performance_chart(category_perf)
                category_fig.write_html(f"{output_dir}/category_performance.html")
                print("✅ Category performance chart saved")
            
            if not customer_seg.empty:
                customer_fig = self.create_customer_segmentation_chart(customer_seg)
                customer_fig.write_html(f"{output_dir}/customer_segmentation.html")
                print("✅ Customer segmentation chart saved")
            
            if not inventory_status.empty:
                inventory_fig = self.create_inventory_status_chart(inventory_status)
                inventory_fig.write_html(f"{output_dir}/inventory_status.html")
                print("✅ Inventory status chart saved")
            
            if not profitability.empty:
                profit_fig = self.create_profitability_chart(profitability)
                profit_fig.write_html(f"{output_dir}/profitability_analysis.html")
                print("✅ Profitability analysis chart saved")
            
            print(f"📁 All charts saved to '{output_dir}' directory")
            
        except Exception as e:
            print(f"❌ Error saving charts: {e}")
    
    def close_connection(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("🔌 Database connection closed")

def main():
    """Main function to run the analytics dashboard"""
    print("🛒 Greenspot Grocer Analytics Dashboard")
    print("=" * 50)
    
    try:
        # Initialize dashboard
        dashboard = GreenspotAnalyticsDashboard()
        
        # Generate comprehensive report
        dashboard.generate_dashboard_report()
        
        # Save interactive charts
        dashboard.save_dashboard_charts()
        
        # Close connection
        dashboard.close_connection()
        
        print("\n🎉 Analytics dashboard completed successfully!")
        print("📊 Check the 'dashboard_charts' folder for interactive visualizations")
        
    except Exception as e:
        print(f"❌ Dashboard generation failed: {e}")
        raise

if __name__ == "__main__":
    main()