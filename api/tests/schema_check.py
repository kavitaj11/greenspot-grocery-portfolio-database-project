import mysql.connector
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config import get_database_config

DATABASE_CONFIG = get_database_config()

try:
    connection = mysql.connector.connect(**DATABASE_CONFIG)
    cursor = connection.cursor()
    
    # Get the structure of sales_transactions table
    cursor.execute("DESCRIBE sales_transactions")
    columns = cursor.fetchall()
    print("sales_transactions table structure:")
    for column in columns:
        print(f"  {column[0]} - {column[1]} - {column[2]} - {column[3]}")
    
    # Get sample data
    cursor.execute("SELECT * FROM sales_transactions LIMIT 3")
    sample_data = cursor.fetchall()
    print("\nSample data:")
    for row in sample_data:
        print(f"  {row}")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"Database error: {e}")
    import traceback
    traceback.print_exc()