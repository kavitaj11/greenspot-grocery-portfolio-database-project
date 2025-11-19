import mysql.connector
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config import get_database_config

DATABASE_CONFIG = get_database_config()

try:
    connection = mysql.connector.connect(**DATABASE_CONFIG)
    cursor = connection.cursor()
    
    # Test the executive summary query
    query = """
    SELECT 
        COUNT(DISTINCT st.transaction_id) as total_transactions,
        ROUND(SUM(st.total_amount), 2) as total_revenue,
        ROUND(AVG(st.total_amount), 2) as average_transaction_value,
        COUNT(DISTINCT st.customer_id) as unique_customers
    FROM sales_transactions st
    """
    
    cursor.execute(query)
    result = cursor.fetchone()
    print("Query executed successfully!")
    print(f"Result: {result}")
    
    # Test all tables exist
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"Available tables: {[table[0] for table in tables]}")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"Database error: {e}")
    import traceback
    traceback.print_exc()